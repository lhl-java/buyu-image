"""Refresh standalone catalog metadata only; no pixel checks, encoding or atlas work."""
from pathlib import Path
import datetime
import json
from ArtRuntimeBridge import (read_json, native_jobs, normalize_manifest,
                              build_native_clips, build_fx_clips, catalog_stats)

ROOT = Path(__file__).resolve().parent.parent


def main():
    from ArtAcceptanceState import preserve_accepted
    if preserve_accepted(ROOT): return
    path = ROOT/'assets/runtime-catalog.json'
    old = read_json(path)
    previous = {e['file']:e for e in old['assets']}
    jobs = native_jobs(ROOT)
    assets, warnings, manifests, changed = [], [], [], []
    for mp in sorted((ROOT/'assets').rglob('manifest.json')):
        if 'atlases' in mp.parts:
            continue
        m = read_json(mp)
        if not isinstance(m.get('items'), list):
            continue
        manifests.append(mp.relative_to(ROOT).as_posix())
        folder = mp.parent.relative_to(ROOT).as_posix()
        entries, messages = normalize_manifest(ROOT, mp, m, jobs.get(folder))
        warnings.extend(messages)
        for e in entries:
            cached = previous.get(e['file'])
            unchanged = cached and all(cached.get(k)==e.get(k) for k in ['sha256','width','height'])
            if unchanged:
                # Display metadata always comes from the current producer, never old 128px defaults.
                for key in ['atlas','alphaRange']:
                    if key in cached:
                        e[key] = cached[key]
                if 'atlas' in cached or 'alphaRange' in cached:
                    e['cachedPixelEvidence'] = {'status':'historical_unchanged_source_metadata_reused',
                                                'aggregateValidationRun':False}
            else:
                changed.append(e['id'])
            if not (ROOT/e['file']).is_file():
                warnings.append({'id':'missing_file','file':e['file']})
            if not (ROOT/e['generationRecord']).is_file():
                warnings.append({'id':'missing_generation_record','file':e['generationRecord']})
            e['metadataRefreshValidation'] = 'Producer metadata referenced; this refresh does not recheck image hashes, pixels or playback.'
            assets.append(e)
    # Scenes retain the last full collector's source-specific metadata.
    assets.extend(e for e in old['assets'] if e['category']=='scenes')
    clips = build_fx_clips(ROOT, assets) + build_native_clips(ROOT, assets, jobs)
    stats = catalog_stats(assets, clips)
    catalog = dict(old)
    catalog.update({'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'assets':assets,'clips':clips,'counts':stats['counts'],'statistics':stats,
                    'warnings':warnings,'gameArtComplete':False,
                    'remainingGates':['Native action candidates require actual playback and identity/pose review.',
                                      'Target Unity integration, display calibration, cannon pivots and FX timing remain unapproved.'],
                    'motionRoute':'builtin_native_AI_frames_user_requested',
                    'metadataRefresh':{'mode':'metadata_only','renderedImages':0,'atlasRepacked':False,
                                       'encodedClips':0,'aggregatePixelChecksRun':False,
                                       'producerManifests':manifests,'newOrChangedAssets':changed,
                                       'reason':'Shared local heavy-job hold; no aggregate validation or playback approval inferred.'}})
    check_path = ROOT/'docs/GAME_ART_PACK_VALIDATION.json'
    if check_path.is_file():
        check = read_json(check_path)
        catalog['historicalPackValidation'] = {'record':check_path.relative_to(ROOT).as_posix(),
            'builtAt':check.get('builtAt'),'assetCount':check.get('assetCount'),
            'atlasPages':check.get('atlasPages'),'atlasPixelRoundtripCount':check.get('atlasPixelRoundtripCount'),
            'scope':'Historical validation only; not a validation of the current metadata refresh.',
            'coversCurrentCatalog':False}
    catalog['uiStateRegistration']='config/ui-state-registration.json'
    catalog['typography']='config/ui-typography.json'
    if (ROOT/'assets/fonts/fonts.json').is_file():
        catalog['fontPackage']='assets/fonts/fonts.json'
    if (ROOT/'config/skill-art-bindings.json').is_file():
        catalog['skillArtBindings']=read_json(ROOT/'config/skill-art-bindings.json')
    path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'assets/runtime-catalog.js').write_text('window.BUYU_ART = '+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(json.dumps(dict(stats, warningCount=len(warnings), newOrChanged=len(changed),
                          aggregateValidationRun=False),ensure_ascii=False))


if __name__ == '__main__':
    main()
