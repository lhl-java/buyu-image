"""Record current native-frame metadata readiness without rendering or approving art.

Historical pack validation and publication receipts retain their original scope.
This script does not hash/decode PNGs, pack atlases, encode previews or play animations.
"""
from pathlib import Path
import datetime
import json
from ArtRuntimeBridge import read_json, native_jobs, catalog_stats

ROOT = Path(__file__).resolve().parent.parent
STATIC_CONTRACT = {'branding':1,'cannons':12,'characters':7,'fish':36,'fx':128,
                   'icons':36,'ornaments':9,'skills':6,'ui':34,'scenes':5,'illustrations':2}


def write(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    from ArtAcceptanceState import preserve_accepted
    if preserve_accepted(ROOT): return
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    brand_path = ROOT/'config/game-brand.json'
    brand = read_json(brand_path) if brand_path.is_file() else {}
    catalog = read_json(ROOT/'assets/runtime-catalog.json')
    check = read_json(ROOT/'docs/GAME_ART_PACK_VALIDATION.json')
    status_path = ROOT/'docs/GAME_ART_STATUS.json'
    status = read_json(status_path) if status_path.is_file() else {}
    stats = catalog_stats(catalog['assets'], catalog['clips'])
    jobs = native_jobs(ROOT)
    native = [c for c in catalog['clips'] if c.get('kind')=='native_character_frames']
    static_counts = {k:v for k,v in stats['counts'].items() if k!='animations'}
    problems = list(status.get('problems', []))
    for category, expected in STATIC_CONTRACT.items():
        if static_counts.get(category,0) != expected:
            problems.append({'id':'static_contract_count','category':category,'expected':expected,
                             'actual':static_counts.get(category,0)})
    ids = [a['id'] for a in catalog['assets']]
    if len(ids)!=len(set(ids)):
        problems.append({'id':'duplicate_catalog_asset_ids'})
    for clip in native:
        if any(frame not in set(ids) for frame in clip['frames']):
            problems.append({'id':'clip_frame_not_in_catalog','clip':clip['id']})
    historical = {'validation':'docs/GAME_ART_PACK_VALIDATION.json','builtAt':check.get('builtAt'),
                  'assetCount':check.get('assetCount'),'atlasPages':check.get('atlasPages'),
                  'spritePixelRoundtrips':check.get('atlasPixelRoundtripCount'),
                  'allPackedPixelsUnchanged':check.get('atlasPixelRoundtripAllEqual'),
                  'scope':'Historical recorded pack only; no current aggregate pass inferred.'}
    current_full_pack = (not catalog.get('metadataRefresh') and
                         check.get('assetCount')==stats['assetCount'] and
                         check.get('counts')==stats['counts'] and
                         check.get('builtAt')==catalog.get('builtAt'))
    metadata_scope = {'mode':'metadata_only' if not current_full_pack else 'full_pack_record_referenced',
                      'aggregatePixelChecksRun':False,'playbackRun':False,
                      'catalog':'assets/runtime-catalog.json','statistics':stats,
                      'evidence':'Producer manifests and current catalog; export counts do not establish motion acceptance.'}
    status.update({'schemaVersion':2,'updatedAt':now,'project':brand.get('name','捕鱼')+'·道家Q版',
                   'localDirectory':str(ROOT),'gameArtComplete':False,
                   'staticAndFxAssets':{'actual':stats['staticAndFxAssetCount'],
                       'expected':sum(STATIC_CONTRACT.values()),'counts':static_counts,
                       'expectedCounts':STATIC_CONTRACT,
                       'status':'candidate_metadata_current_pending_aggregate_and_runtime_review',
                       'fileChecksPassed':check.get('staticFileChecksPassed') if current_full_pack else None,
                       'validation':'docs/GAME_ART_PACK_VALIDATION.json',
                       'validationScope':'current_full_pack' if current_full_pack else 'historical_only',
                       'historicalValidation':historical},
                   'nativeAnimations':{'route':'builtin_native_AI_frames_user_requested',
                       'plannedActions':len(jobs),'plannedPngFrames':sum(j.get('frames',0) for j in jobs.values()),
                       'exportedCandidateActions':len(native),'exportedCandidateFrames':stats['animationFrameCount'],
                       'releaseReadyActions':stats['releaseReadyNativeActions'],
                       'loopingActions':stats['loopingNativeClips'],'oneShotActions':stats['oneShotNativeClips'],
                       'status':'candidate_exports_pending_playback_and_target_Unity_review',
                       'contract':'docs/ANIMATION_FRAME_CONTRACT.md','progress':'docs/NATIVE_FRAME_PROGRESS.json'},
                   'metadataValidation':metadata_scope,'problems':problems,
                   'warnings':catalog.get('warnings',[])})
    old_pack = status.get('pack',{})
    old_pack.update({'catalog':'assets/runtime-catalog.json','preview':'assets-preview/index.html',
                     'currentCatalogAssets':stats['assetCount'],'currentCatalogClips':stats['clipCount'],
                     'currentBatchPacked':current_full_pack,
                     'validationScope':'current_full_pack' if current_full_pack else 'historical_only',
                     'historicalValidation':historical})
    # Legacy fields remain explicitly scoped; the 13 pages /218 roundtrips are not the new924 pack.
    status['pack'] = old_pack
    remaining = {r['id']:r for r in status.get('remaining',[])}
    for ident, guide, detail in [('fish-motion',False,'docs/FISH_MOTION_BACKLOG.json'),
                                  ('guide-motion',True,'docs/GUIDE_MOTION_BACKLOG.json')]:
        planned = [j for j in jobs.values() if (j['characterId']=='dao-child')==guide]
        clips = [c for c in native if (c['actorId']=='dao-child')==guide]
        entry = remaining.get(ident,{'id':ident})
        entry.update({'plannedActions':len(planned),'completedActions':sum(c['releaseReady'] for c in clips),
                      'exportedCandidateActions':len(clips),'exportedCandidateFrames':sum(c['frameCount'] for c in clips),
                      'status':'native_frame_candidates_pending_playback_and_Unity_review','details':detail})
        remaining[ident] = entry
    client = remaining.get('client-art-validation',{'id':'client-art-validation'})
    client.update({'status':'pending_target_Unity_playback_and_art_validation','details':'docs/GAME_ART_INTEGRATION.md'})
    remaining['client-art-validation'] = client
    status['remaining'] = list(remaining.values())
    capability = status.get('capability',{})
    capability.update({'imageRoute':'builtin image_gen',
                       'motionRoute':'builtin image_gen native action sheets, explicitly chosen by user',
                       'videoNoLongerRequired':True})
    status['capability'] = capability
    batch = status.get('workingBatch',{})
    batch.update({'contract':'docs/ANIMATION_FRAME_CONTRACT.md','staticAndFxTargetPngCount':sum(STATIC_CONTRACT.values()),
                  'staticAndFxCandidatePngCount':stats['staticAndFxAssetCount'],'catalogAssets':stats['assetCount'],
                  'catalogClips':stats['clipCount'],'motionActions':len(jobs),
                  'plannedMotionPngFrames':sum(j.get('frames',0) for j in jobs.values()),
                  'exportedCandidateActions':len(native),'exportedCandidateFrames':stats['animationFrameCount'],
                  'motionReleaseReadyActions':stats['releaseReadyNativeActions'],
                  'frameProgress':'docs/NATIVE_FRAME_PROGRESS.json',
                  'aggregateValidation':'deferred_during_shared_heavy_work_slot' if not current_full_pack else 'current_pack_file_checks_recorded_motion_unapproved',
                  'uploaded':False})
    status['workingBatch'] = batch
    # Keep the original public receipt byte-for-byte; uploaded=true describes only that fixed old batch.
    receipt_path = ROOT/'docs/PUBLIC_UPLOAD_RECEIPT.json'
    receipt = read_json(receipt_path) if receipt_path.is_file() else {}
    if receipt:
        status['publishedBatch'] = {'receipt':'docs/PUBLIC_UPLOAD_RECEIPT.json','commit':receipt.get('commit'),
            'verifiedAt':receipt.get('verifiedAt'),'independentAssets':receipt.get('artStatus',{}).get('independentAssets'),
            'uploadedAndDownloadedVerified':receipt.get('uploadedAndDownloadedVerified'),
            'scope':'Historical fixed batch; current workingBatch is not uploaded.'}
        status['uploadedScope'] = 'publishedBatch only; see workingBatch.uploaded for current candidates'
    write(status_path,status)

    job_path = ROOT/'docs/GAME_ART_JOBS.json'
    if job_path.is_file():
        art_jobs = read_json(job_path)
        for job in art_jobs.get('jobs',[]):
            prefix = job['output'].rstrip('/')+'/'
            matches = [e for e in catalog['assets'] if e['category']!='animations' and e['file'].startswith(prefix)]
            if job['id'] in ['event-banner','event-route']:
                matches = [e for e in matches if e['localId']==job['id']]
            job.update({'deliveredAssets':[e['id'] for e in matches],'deliveredAssetCount':len(matches),
                        'status':'static_or_fx_candidate_pending_runtime_review' if matches else 'pending'})
        art_jobs.update({'status':'native_frames_exported_pending_playback_and_runtime_review',
                         'statusRecord':'docs/GAME_ART_STATUS.json','gameArtComplete':False})
        write(job_path,art_jobs)
    rows='\n'.join(f'| {category} | {static_counts.get(category,0)} / {expected} |'
                   for category,expected in STATIC_CONTRACT.items())
    delivery=f'''# {brand.get('name','捕鱼')}游戏美术当前交付

游戏名称与Logo见 [品牌设置](../config/game-brand.json)及[Logo交付](GAME_LOGO_DELIVERY.md)。当前Logo与新一批资源均未包含在历史公开批次中。

本地目录为 `D:\\work\\buyu-image`。当前目录包含 **{stats['staticAndFxAssetCount']} 项静态/FX资源、{len(native)} 组角色动作候选、{stats['animationFrameCount']} 张原生动作帧**，合计 {stats['assetCount']} 项运行资源。动画目录共 {stats['clipCount']} 组 clips：{stats['fxClipCount']} 组FX及{len(native)}组角色动作。最终状态见 [GAME_ART_STATUS.json](GAME_ART_STATUS.json)。当前整款美术尚未通过完整验收。

| 静态/FX类别 | 已落盘 / 当前合同 |
|---|---:|
{rows}

角色动作采用用户明确选择的原生AI动作帧路线。源表提供真实姿态变化，提取与整数注册保留源像素；显示比例以各动作统一校准值计算，完整透明画布尺寸与可见身体尺寸分开。{stats['loopingNativeClips']}组循环、{stats['oneShotNativeClips']}组单次动作的时序来自实际manifest。已导出候选不等于播放通过，当前 releaseReady 动作为 **{stats['releaseReadyNativeActions']} / {len(native)}**。身份与姿态连贯、循环接缝、捕获恢复、Alpha融合及目标Unity显示仍须实际检查。原始边距/格位及制作者警告保留于各动作清单和总索引。

[运行资源索引](../assets/runtime-catalog.json)包含真实帧ID、fps、逐帧时长、根点与显示比例；根点坐标为左上原点归一化，另提供Unity左下pivot。[原生动作进度](NATIVE_FRAME_PROGRESS.json)、[动作合同](ANIMATION_FRAME_CONTRACT.md)、[本地素材审阅台](../assets-preview/index.html)与[31项整屏设计](../gallery/index.html)用于接手。

[Unity工程](../unity/BuyuClient/README.md)及[接续说明](UNITY_ART_ACCEPTANCE_HANDOFF_20261028.md)记录资源和实际验收状态；项目文件已准备不代表已完成Unity导入、编译、播放或整套美术终审。

本次只刷新元数据，未重新解码检查全量图片、打包图集、编码预览或播放动作。[已有打包验证](GAME_ART_PACK_VALIDATION.json)记录时间为 {check.get('builtAt')}，仅覆盖历史 {check.get('assetCount')} 项资源、{check.get('atlasPages')} 页atlas、{check.get('atlasPixelRoundtripCount')} 项像素回环；这些旧通过证据不能扩展为当前 {stats['assetCount']} 项的全量通过。

公开仓库为 [lhl-java/luhailong-python](https://github.com/lhl-java/luhailong-python)，项目在buyu-image子目录。历史公开批次提交 `{receipt.get('commit','未记录')}` 的独立下载核验见 [上传回执](PUBLIC_UPLOAD_RECEIPT.json)；该回执保持原批次范围，**当前新候选批次尚未上传**。宿主未披露的实际图像型号与质量继续记为未确认；来源记录不因配置升级改写。
'''
    (ROOT/'docs/GAME_ART_DELIVERY.md').write_text(delivery,encoding='utf-8')
    print(json.dumps(dict(stats,metadataOnly=True,problemCount=len(problems),
                          currentBatchUploaded=False,gameArtComplete=False),ensure_ascii=False))
    if problems:
        raise SystemExit(1)


if __name__=='__main__':
    main()
