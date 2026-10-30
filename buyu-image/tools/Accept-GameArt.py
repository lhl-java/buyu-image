"""Seal the first-release art scope after real Unity checks and explicit agent visual review.

Never obtains visual approval from file counts. Requires the separately authored review
record and the actual Editor/PlayMode reports. Original technical reports stay unchanged.
"""
from pathlib import Path
import datetime, json, shutil
from ArtAcceptanceState import digest
from ArtRuntimeBridge import catalog_stats

ROOT=Path(__file__).resolve().parent.parent
EVIDENCE='docs/acceptance'
FINAL='docs/UNITY_FINAL_ACCEPTANCE.json'
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,d):
    path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def require(value,message):
    if not value: raise ValueError(message)
def snapshot(source,dest):
    path=ROOT/dest;path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/source,path)

def main():
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    catalog=read('assets/runtime-catalog.json');assets=catalog['assets'];clips=catalog['clips']
    native=[c for c in clips if c.get('kind')=='native_character_frames']
    review=read(EVIDENCE+'/AGENT_VISUAL_REVIEW.json')
    technical=read('unity/BuyuClient/Logs/BuyuArtValidation.json')
    runtime=read('unity/BuyuClient/Logs/RuntimeAcceptance/report.json')
    supplement=read('unity/BuyuClient/Logs/RuntimeSupplement/report.json')
    ui=read('unity/BuyuClient/Logs/RuntimeUiFinal/report.json')
    pack=read('docs/GAME_ART_PACK_VALIDATION.json')
    require(len(assets)==924 and len(clips)==89 and len(native)==81,'Art contract count differs')
    require(technical['technicalImportPassed'] and technical['counts']['errors']==0 and technical['counts']['spritesVerified']==924,'Unity import/compile checks failed')
    for report in [runtime,supplement,ui]:
        require(report['actualPlayMode'] and report['actualGraphicsRendered'] and not report['errors'],'Actual PlayMode report failed')
        require(report['uiPointerChecks']==16 and report['captureEvents']>=1,'UI or capture event failed')
    actual={c['id']:c for c in runtime['clips']}
    require(set(actual)=={c['id'] for c in clips} and all(c['playbackPassed'] and c['observedFrames']==c['frames'] for c in actual.values()),'All real-time frames/wrap/callback checks must pass')
    require(len(ui.get('cannonMuzzleSamples',[]))==18,'Registered cannon mouths not checked at all angles')
    require(review.get('accepted') and set(review['clipIdsActuallyReviewed'])==set(actual),'Explicit per-clip agent visual review missing')
    require(review['uiScreensActuallyReviewed']==31 and review['uiFamiliesActuallyReviewed']==8 and review['cannonsActuallyReviewed']==6,'Visual scope incomplete')
    require(pack['assetCount']==924 and pack['atlasPages']==146 and pack['atlasPixelRoundtripCount']==917 and pack['atlasPixelRoundtripAllEqual'] and pack['staticFileChecksPassed'] and not pack['problems'],'Full native pack validation failed')
    # File identity recheck makes the earlier expensive pixel pass reusable after metadata-only cap edits.
    for item in assets+catalog['atlases']:
        require(digest(ROOT/item['file'])==item['sha256'],'Production PNG changed: '+item['file'])
    for item in assets:
        require((ROOT/item['generationRecord']).is_file(),'Missing provenance: '+item['id'])
        for source in item.get('derivedFrom',[]):
            require(digest(ROOT/source['file'])==source['sha256'],'Adopted native source changed: '+source['file'])
    for name in ['designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png']:
        require((ROOT/name).read_bytes()[:8]==b'\x89PNG\r\n\x1a\n','Required reference is not a real PNG')
    for mp in sorted({a['manifest'] for a in assets if a.get('manifest')}):
        manifest=read(mp)
        manifest.update(status='accepted_first_release_art',finalAcceptance=FINAL,acceptedAt=now)
        if any(c.get('manifest')==mp for c in native):
            manifest['releaseReady']=True
            manifest['playbackReview']=FINAL
            if isinstance(manifest.get('animation'),dict):manifest['animation']['releaseReady']=True
        for item in manifest.get('items',[]):
            item['status']='accepted_first_release_art'
        write(mp,manifest)
    for a in assets:a['status']='accepted_first_release_art'
    for c in clips:
        c.update(status='accepted_first_release_art',releaseReady=True,playbackReview=FINAL)
    registered={c['id']:c for c in read('config/cannon-registration.json')['cannons']}
    for c in catalog['cannons']:
        c.update(muzzle=registered[c['id']]['muzzleNormalized'],muzzleRegistration='config/cannon-registration.json',integrationStatus='accepted_Unity_three_angles')
    catalog['projectile']['integrationStatus']='accepted_Unity_capture_demonstration'
    catalog.update(gameArtComplete=True,remainingGates=[],finalAcceptance=FINAL,acceptedAt=now,statistics=catalog_stats(assets,clips))
    catalog['metadataRefresh']['reason']='Metadata changes retain source pixels; full pack and actual Unity acceptance are separately sealed in '+FINAL
    catalog['historicalPackValidation']['coversCurrentCatalog']=True
    catalog['historicalPackValidation']['scope']='All 924 source PNG and 146 atlas SHA256 identities rechecked after metadata-only changes; reuse the 917 exact pixel roundtrips from this pack.'
    write('assets/runtime-catalog.json',catalog)
    (ROOT/'assets/runtime-catalog.js').write_text('window.BUYU_ART = '+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    registry=read('config/ui-state-registration.json')
    registry.update(status='accepted_Unity_shared_registration',acceptancePending=[],finalAcceptance=FINAL)
    for family in registry['families']:
        family['status']='accepted_Unity_shared_registration'
        for state in family['states']:state['status']='accepted_Unity_art'
    write('config/ui-state-registration.json',registry)
    (ROOT/'assets-preview/ui-states.js').write_text('window.BUYU_UI_STATES = '+json.dumps(registry,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    bindings=read('config/skill-art-bindings.json')
    bindings.update(status='accepted_art_bindings',finalAcceptance=FINAL)
    # Gameplay durations/target selection remain code responsibilities; their original notes are retained.
    write('config/skill-art-bindings.json',bindings)
    suite=read('docs/UI_SUITE_20261026.json')
    for task in suite['tasks']:task.update(status='accepted_first_release_art_design',finalAcceptance=FINAL)
    write('docs/UI_SUITE_20261026.json',suite)
    progress=read('docs/NATIVE_FRAME_PROGRESS.json')
    progress.update(updatedAt=now,releaseReadyActions=81,gameArtComplete=True,finalAcceptance=FINAL)
    for row in progress['actions']:row.update(status='accepted_Unity_art',releaseReady=True,acceptance=FINAL)
    write('docs/NATIVE_FRAME_PROGRESS.json',progress)
    by_clip={c['id']:c for c in native}
    for file,guide in [('docs/FISH_MOTION_BACKLOG.json',False),('docs/GUIDE_MOTION_BACKLOG.json',True)]:
        backlog=read(file);backlog.update(status='accepted_first_release_art',finalAcceptance=FINAL)
        rows=[{'id':'dao-child','actions':backlog['actions']}] if guide else backlog['entries']
        for row in rows:
            row['status']='accepted_first_release_art'
            for action in row['actions']:
                clip=by_clip[row['id']+'/'+action['id']]
                action.update(status='accepted_Unity_art',output=clip['manifest'],releaseReady=True,actualFps=clip['fps'],actualFrameCount=clip['frameCount'],actualDurationMs=clip['durationMs'],acceptance=FINAL)
        write(file,backlog)
    jobs=read('docs/GAME_ART_JOBS.json')
    for job in jobs['jobs']:job.update(status='accepted_first_release_art',acceptance=FINAL)
    jobs.update(status='accepted_first_release_art',gameArtComplete=True,finalAcceptance=FINAL)
    write('docs/GAME_ART_JOBS.json',jobs)
    status=read('docs/GAME_ART_STATUS.json');stats=catalog['statistics']
    status.update(updatedAt=now,gameArtComplete=True,remaining=[],finalAcceptance=FINAL,uploaded=False,uploadedScope='Current accepted batch awaiting frozen publication; historical receipt retained separately.')
    status['uiDesigns'].update(status='accepted_first_release_art_design',acceptance=FINAL)
    status['staticAndFxAssets'].update(status='accepted_Unity_art',fileChecksPassed=True,validationScope='current_924_native_PNG_hashes_rechecked')
    status['pack'].update(atlasPages=146,spritePixelRoundtrips=917,allPackedPixelsUnchanged=True,currentBatchPacked=True,validationScope='current_all_PNG_and_atlas_hashes_rechecked',acceptance=FINAL)
    status['nativeAnimations'].update(status='accepted_Unity_art',releaseReadyActions=81,acceptance=FINAL)
    status['workingBatch'].update(motionReleaseReadyActions=81,aggregateValidation='passed_full_pack_and_Unity',uploaded=False,gameArtComplete=True,acceptance=FINAL)
    status['unityProject'].update(status='import_compilation_PlayMode_and_art_review_passed',importRun=True,compiled=True,played=True,validation=FINAL)
    status['brand']['runtimeRendered']=True
    status['metadataValidation'].update(statistics=stats,finalAcceptance=FINAL)
    write('docs/GAME_ART_STATUS.json',status)
    # Keep the exact original reports, including their deliberately technical-only pending flags.
    for src,name in [('unity/BuyuClient/Logs/BuyuArtValidation.json','unity-import.json'),('unity/BuyuClient/Logs/RuntimeAcceptance/report.json','runtime-all-89.json'),('unity/BuyuClient/Logs/RuntimeSupplement/report.json','runtime-fx-boss-supplement.json'),('unity/BuyuClient/Logs/RuntimeUiFinal/report.json','runtime-ui-cannon-final.json')]:snapshot(src,EVIDENCE+'/'+name)
    for c in clips:
        name=c['id'].replace('/','-')+'.jpg'
        source='unity/BuyuClient/Logs/RuntimeSupplement/motion/'+name
        if not (ROOT/source).is_file():source='unity/BuyuClient/Logs/RuntimeAcceptance/motion/'+name
        snapshot(source,EVIDENCE+'/motion/'+name)
    for folder in ['ui','cannons','stretch']:
        for source in (ROOT/'unity/BuyuClient/Logs/RuntimeUiFinal'/folder).glob('*.png'):
            snapshot(source.relative_to(ROOT).as_posix(),EVIDENCE+'/'+folder+'/'+source.name)
    for source in (ROOT/'unity/BuyuClient/Logs/RuntimeAcceptance/screens').glob('*.png'):
        snapshot(source.relative_to(ROOT).as_posix(),EVIDENCE+'/screens/'+source.name)
    for name in ['fishing-before.png','fishing-after.png']:
        snapshot('unity/BuyuClient/Logs/RuntimeUiFinal/'+name,EVIDENCE+'/'+name)
    # Regenerate engine metadata from accepted manifests, with no source PNG edits.
    import importlib.util
    spec=importlib.util.spec_from_file_location('unity_export',ROOT/'tools/Export-UnityArtDatabase.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.main()
    inputs=set(a['file'] for a in assets)|set(a['manifest'] for a in assets if a.get('manifest'))
    inputs|={p.relative_to(ROOT).as_posix() for p in (ROOT/'config').glob('*.json')}
    inputs|={p.relative_to(ROOT).as_posix() for p in (ROOT/'unity/BuyuClient/Assets').rglob('*.cs')}
    inputs|={t['selectedFile'] for t in suite['tasks']}
    inputs|={a['file'] for a in catalog['atlases']}
    inputs|={'assets/runtime-catalog.json','unity/BuyuClient/Assets/Resources/Buyu/art-database.json','assets/fonts/NotoSansCJKsc-Regular.otf','assets/fonts/NotoSerifCJKsc-Regular.otf'}
    inputs|={'designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png'}
    final=dict(schemaVersion=1,acceptedAt=now,accepted=True,gameArtComplete=True,scope='First-release 2D art contract: 31 UI designs, 276 static/FX PNGs, 81 native 8-frame actions. Unity Editor art acceptance, not a full network game implementation or standalone build.',counts=stats,unityVersion=technical['unityVersion'],importChecks=technical['counts'],runtimeClipsPassed=89,uiPointerChecks=ui['uiPointerChecks'],registeredCannonAngles=18,visualReview=EVIDENCE+'/AGENT_VISUAL_REVIEW.json',technicalReports=[EVIDENCE+'/'+n for n in ['unity-import.json','runtime-all-89.json','runtime-fx-boss-supplement.json','runtime-ui-cannon-final.json']],packValidation='docs/GAME_ART_PACK_VALIDATION.json',pixelRoundtrips=917,atlasPages=146,sourcePNGAndAtlasHashesRechecked=True,unresolvedBlockingArtIssues=[],sourceWarningsRetained=True,actualImageModel=None,actualImageQuality=None,humanVisualReviewClaimed=False,inputHashes={name:digest(ROOT/name) for name in sorted(inputs)})
    write(FINAL,final)
    print(json.dumps({'accepted':True,'assets':924,'nativeActions':81,'runtimeClips':89,'inputHashes':len(inputs),'evidence':FINAL}))

if __name__=='__main__':main()
