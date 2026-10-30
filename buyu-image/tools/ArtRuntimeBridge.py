"""Pure metadata bridge for native action sheets and the standalone art catalog.

No image reads, resampling, encoding, atlas packing or approval inference occur here.
Anchors/root use normalized top-left coordinates; Unity's bottom-left pivot is explicit.
"""
from pathlib import Path, PurePosixPath
import collections
import copy
import json

FX_NAMES = {'net':'渔网展开','ice':'玄冰封冻','thunder':'雷网爆发',
            'capture':'捕获灵光','hit':'水珠命中','gather':'聚鱼金流',
            'guard':'太极护持','surge':'激流涌浪'}
ACTION_NAMES = {'swim':'游动','capture':'捕获','attack':'攻击','enrage':'怒态',
                'idle':'待机','point':'指引','celebrate':'庆祝'}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def normalize_warnings(value, manifest, field='warnings'):
    """Preserve heterogeneous producer evidence without dict-spreading strings."""
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    result = []
    for warning in values:
        if warning is None:
            continue
        item = copy.deepcopy(warning) if isinstance(warning, dict) else {'value': warning}
        item.setdefault('id', 'producer_' + field)
        item['manifest'] = manifest
        item['sourceField'] = field
        result.append(item)
    return result


def native_jobs(root):
    path = Path(root) / 'docs/NATIVE_FRAME_JOBS_20261028.json'
    if not path.is_file():
        return {}
    return {PurePosixPath(j['outputFolder']).as_posix().rstrip('/'): j
            for j in read_json(path).get('jobs', [])}


def _pair(value):
    return (isinstance(value, (list, tuple)) and len(value) == 2
            and all(isinstance(v, (int, float)) for v in value))


def _anchor(value, canvas):
    if not _pair(value):
        return None
    if all(0 <= v <= 1 for v in value):
        return list(value)
    return [value[0] / canvas[0], value[1] / canvas[1]]


def _first(*values):
    return next((v for v in values if v is not None), None)


def native_context(manifest, job, manifest_path):
    """Resolve one scale/timeline for a whole clip, never fit individual frame bboxes."""
    items = manifest.get('items', [])
    first = items[0] if items else {}
    animation = manifest.get('animation', {})
    calibration = copy.deepcopy(_first(animation.get('displayCalibration'),
                                       manifest.get('displayCalibration'), {}))
    canvas = _first(animation.get('canvas'), animation.get('sharedCanvas'),
                    manifest.get('sharedCanvas'), [first.get('width'), first.get('height')])
    if not _pair(canvas) or min(canvas) <= 0:
        raise ValueError('Missing native canvas: ' + manifest_path)
    canvas = list(canvas)
    warnings = []
    scale_sources = [
        ('animation.displayCalibration.uniformDisplayScale', animation.get('displayCalibration', {}).get('uniformDisplayScale')),
        ('displayCalibration.uniformDisplayScale', manifest.get('displayCalibration', {}).get('uniformDisplayScale')),
        ('uniformDisplayScale', manifest.get('uniformDisplayScale')),
        ('items[0].uniformDisplayScale', first.get('uniformDisplayScale')),
        ('items[0].animation.displayCalibration.uniformDisplayScale', first.get('animation', {}).get('displayCalibration', {}).get('uniformDisplayScale')),
    ]
    scale_source, scale = next(((name, value) for name, value in scale_sources
                                if isinstance(value, (int, float)) and value > 0), (None, None))
    if scale is None:
        display = _first(manifest.get('displaySize'), first.get('displaySize'))
        if _pair(display):
            sx, sy = display[0] / canvas[0], display[1] / canvas[1]
            if abs(sx - sy) > 1e-6:
                raise ValueError('Nonuniform native displaySize: ' + manifest_path)
            scale, scale_source = sx, 'displaySize / shared native canvas'
        elif job.get('id') == 'dao-child/idle':
            height = first.get('qa', {}).get('nativeBodyHeight')
            if not isinstance(height, (int, float)) or height <= 0:
                raise ValueError('Idle rest body-height evidence missing: ' + manifest_path)
            scale, scale_source = 280 / height, 'items[0].qa.nativeBodyHeight; target body height 280'
            calibration.update({'method':'one_entry_rest_native_body_height_for_entire_clip',
                                'restFrame':0, 'nativeBodyHeight':height, 'targetBodyHeight':280,
                                'uniformDisplayScale':scale, 'metadataDerived':True})
        else:
            raise ValueError('Native clip has no evidenced display calibration: ' + manifest_path)
    if scale > 1:
        warnings.append({'id':'native_display_upscale_requested','scale':scale,'manifest':manifest_path})
    for i, item in enumerate(items):
        other = item.get('uniformDisplayScale')
        if isinstance(other, (int, float)) and abs(other - scale) > 1e-6:
            warnings.append({'id':'item_scale_differs_from_clip','frame':i,'value':other,
                             'clipScale':scale,'manifest':manifest_path})
    root = _first(_anchor(first.get('anchor'), canvas), _anchor(manifest.get('root'), canvas),
                  _anchor(animation.get('root'), canvas), _anchor(manifest.get('rootPixels'), canvas),
                  _anchor(animation.get('rootPixels'), canvas))
    if root is None:
        raise ValueError('Native clip has no evidenced root: ' + manifest_path)
    fps = _first(manifest.get('fps'), animation.get('fps'), first.get('animation', {}).get('fps'))
    loop = _first(manifest.get('loop'), animation.get('loop'), first.get('animation', {}).get('loop'))
    if not isinstance(fps, (int, float)) or fps <= 0 or not isinstance(loop, bool):
        raise ValueError('Native clip has no actual fps/loop: ' + manifest_path)
    durations = _first(manifest.get('durationsMs'), animation.get('durationsMs'),
                       animation.get('frameDurationsMs'))
    if durations is None:
        per_frame = [e.get('animation', {}).get('durationMs') for e in items]
        durations = per_frame if all(isinstance(x, (int, float)) and x > 0 for x in per_frame) else [
            round((i + 1) * 1000 / fps) - round(i * 1000 / fps) for i in range(len(items))]
    if len(durations) != len(items) or not all(isinstance(x, (int, float)) and x > 0 for x in durations):
        raise ValueError('Native frame-duration mismatch: ' + manifest_path)
    declared = _first(manifest.get('frames'), animation.get('frameCount'), animation.get('frames'))
    if isinstance(declared, int) and declared != len(items):
        warnings.append({'id':'declared_frame_count_mismatch','declared':declared,
                         'actual':len(items),'manifest':manifest_path})
    return {'canvas':canvas, 'uniformDisplayScale':scale, 'scaleEvidence':scale_source,
            'displaySize':[canvas[0]*scale, canvas[1]*scale], 'root':root,
            'fps':fps, 'loop':loop, 'durationsMs':list(durations),
            'displayCalibration':calibration, 'warnings':warnings}


def normalize_manifest(root, path, manifest, job=None):
    """Return normalized catalog assets and warnings, preserving producer fields."""
    root = Path(root)
    manifest_path = Path(path).relative_to(root).as_posix()
    context = native_context(manifest, job, manifest_path) if job else None
    warnings = normalize_warnings(manifest.get('warnings'), manifest_path)
    for field in ['sourceWarnings','sourceMarginWarnings','nominalGridBorderWarnings','runtimeMarginWarnings']:
        warnings.extend(normalize_warnings(manifest.get(field), manifest_path, field))
    if context:
        warnings.extend(context['warnings'])
        warnings.extend(normalize_warnings(context['displayCalibration'].get('warning'),
                                           manifest_path, 'animation.displayCalibration.warning'))
    assets = []
    for index, entry in enumerate(manifest['items']):
        e = copy.deepcopy(entry)
        file = PurePosixPath(e['file'])
        e.update({'localId':entry['id'], 'id':file.parent.relative_to('assets').as_posix()+'/'+entry['id'],
                  'category':file.parts[1], 'manifest':manifest_path,
                  'generationRecord':e['file']+'.generation.json'})
        if context:
            e.update({'actorId':job['characterId'], 'action':job['action'], 'clipId':job['id'],
                      'frameIndex':index, 'uniformDisplayScale':context['uniformDisplayScale'],
                      'displaySize':list(context['displaySize']), 'displayBox':list(context['displaySize']),
                      'displayCalibration':copy.deepcopy(context['displayCalibration']),
                      'displayScaleEvidence':context['scaleEvidence'],
                      'anchor':_anchor(entry.get('anchor'), context['canvas']) or list(context['root']),
                      'anchorCoordinateSystem':'normalized_top_left',
                      'releaseReady':bool(manifest.get('releaseReady', manifest.get('animation', {}).get('releaseReady', False)))})
            e['unityPivot'] = [e['anchor'][0], 1-e['anchor'][1]]
            e['scalePolicy'] = {'mode':'one_uniform_scale_per_clip','allowUpscale':False,
                                'perFrameBboxFit':False,'sourcePngResampled':False}
            e['runtimeFrame'] = {'index':index,'fps':context['fps'],'loop':context['loop'],
                                 'durationMs':context['durationsMs'][index]}
            if manifest.get('bodyDisplayBox') is not None:
                e['bodyDisplayBox'] = copy.deepcopy(manifest['bodyDisplayBox'])
        else:
            box = e.get('displayBox', e.get('displaySize', [128,128]))
            e['displayBox'] = copy.deepcopy(box)
            scale = min(1, box[0]/e['width'], box[1]/e['height'])
            e['displaySize'] = [round(e['width']*scale), round(e['height']*scale)]
            if e['category'] == 'ui':
                e['scalePolicy'] = {'mode':'uniform','allowUpscale':False}
                if e['localId'] in ['list-row','tooltip-panel','panel-runtime']:
                    e['scalePolicy'] = {'mode':'nine_slice_candidate','allowUpscale':False,
                                        'cornersNativePixels':True,'targetClientVerificationRequired':True}
                elif 'nineSlice' in e:
                    e['proposedNineSlice'] = e.pop('nineSlice')
                    e['scalePolicy']['reason'] = 'Preserve title/crest and round ornaments with uniform scale.'
        assets.append(e)
    return assets, warnings


def build_native_clips(root, assets, jobs=None):
    """Build actor/action clips from actual manifests; planner supplies identity only."""
    root = Path(root)
    jobs = jobs if jobs is not None else native_jobs(root)
    by_file = {e['file']:e for e in assets}
    clips = []
    for folder, job in jobs.items():
        path = root/folder/'manifest.json'
        if not path.is_file():
            continue
        m = read_json(path)
        manifest_path = path.relative_to(root).as_posix()
        c = native_context(m, job, manifest_path)
        members = [by_file[e['file']] for e in m.get('items', [])]
        if any((e['width'], e['height']) != tuple(c['canvas']) for e in members):
            raise ValueError('Native clip canvas varies: ' + job['id'])
        a = m.get('animation', {})
        clips.append({'id':job['id'],'actorId':job['characterId'],'action':job['action'],
                      'name':job.get('name',job['characterId'])+'·'+ACTION_NAMES.get(job['action'],job['action']),
                      'kind':'native_character_frames','sourceRoute':'builtin_native_AI_sheet_user_requested',
                      'manifest':manifest_path,'source':copy.deepcopy(m.get('source')),
                      'fps':c['fps'],'loop':c['loop'],'frameCount':len(members),
                      'durationMs':sum(c['durationsMs']),'durationsMs':c['durationsMs'],
                      'canvas':c['canvas'],'root':c['root'],'anchor':c['root'],
                      'anchorCoordinateSystem':'normalized_top_left',
                      'unityPivot':[c['root'][0],1-c['root'][1]],
                      'uniformDisplayScale':c['uniformDisplayScale'],'displaySize':c['displaySize'],
                      'bodyDisplayBox':m.get('bodyDisplayBox', members[0].get('bodyDisplayBox') if members else None),
                      'displayCalibration':c['displayCalibration'],'displayScaleEvidence':c['scaleEvidence'],
                      'frames':[e['id'] for e in members],
                      'status':m.get('status','candidate_pending_root_visual_and_playback_review'),
                      'releaseReady':bool(m.get('releaseReady',a.get('releaseReady',False))),
                      'playbackReview':'pending_target_Unity_playback',
                      'sourceAnimationMetadata':copy.deepcopy(a),
                      'metadataEvidence':'Frame order, fps, loop and durations read from current producer manifest; no playback approval inferred.'})
    return clips


def build_fx_clips(root, assets):
    clips = []
    for suffix, name in FX_NAMES.items():
        ident = 'fx-'+suffix
        members = sorted((e for e in assets if e['file'].startswith('assets/fx/'+ident+'/')),key=lambda e:e['localId'])
        if len(members) != 16:
            continue
        sizes = {(e['width'], e['height']) for e in members}
        if len(sizes) != 1:
            raise ValueError('FX canvas varies: ' + ident)
        clips.append({'id':ident,'name':name,'kind':'fx_frames','manifest':members[0]['manifest'],
                      'fps':16,'loop':False,'frameCount':16,'durationMs':1000,
                      'durationsMs':[63 if i%2==0 else 62 for i in range(16)],
                      'frameDurationUs':62500,'root':members[0].get('anchor',[.5,.5]),
                      'anchorCoordinateSystem':'normalized_top_left','canvas':list(sizes.pop()),
                      'frames':[e['id'] for e in members],
                      'status':'producer_frames_ready_pending_full_motion_and_runtime_review',
                      'releaseReady':False})
    return clips


def catalog_stats(assets, clips):
    counts = dict(collections.Counter(e['category'] for e in assets))
    native = [c for c in clips if c.get('kind') == 'native_character_frames']
    return {'assetCount':len(assets),'staticAndFxAssetCount':sum(e['category']!='animations' for e in assets),
            'animationFrameCount':counts.get('animations',0),'counts':counts,
            'clipCount':len(clips),'fxClipCount':sum(c.get('kind')=='fx_frames' for c in clips),
            'nativeActionClipCount':len(native),'loopingNativeClips':sum(c['loop'] for c in native),
            'oneShotNativeClips':sum(not c['loop'] for c in native),
            'releaseReadyNativeActions':sum(c.get('releaseReady',False) for c in native)}
