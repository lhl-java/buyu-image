"""Pack existing native PNGs without resampling; verify every atlas region byte-for-byte."""
from pathlib import Path
import collections, datetime, hashlib, json, shutil
from PIL import Image
from ArtRuntimeBridge import (native_jobs, normalize_manifest, build_native_clips,
                              build_fx_clips, catalog_stats)

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, data):
    p=Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def export_character():
    src=ROOT/'designs/characters/fishing-dao-child-v1/fishing-dao-child-v1.png'
    dst=ROOT/'assets/characters/dao-child/dao-child.png'
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
    with Image.open(src) as im:
        item={'id':'dao-child','name':'捕鱼道童','file':rel(dst),'width':im.width,'height':im.height,
              'sha256':sha(dst),'anchor':[0.5,0.88],'displaySize':[280,280],
              'status':'static_master_ready_native_actions_separately_reviewed','actualModel':None,'actualQuality':None,
              'derivedFrom':[{'file':rel(src),'sha256':sha(src),'generationRecord':rel(src)+'.generation.json'}],
              'operation':{'type':'byte_identical_copy','resized':False,'upscaled':False}}
    write(str(dst)+'.generation.json',item)
    write(dst.parent/'manifest.json',{'items':[item],'warnings':[],'complete':True,'source':rel(src)})

def collect():
    assets=[]; warnings=[]; problems=[]
    jobs=native_jobs(ROOT)
    for mp in sorted((ROOT/'assets').rglob('manifest.json')):
        if 'atlases' in mp.parts: continue
        m=read(mp)
        if 'items' not in m: continue
        entries,messages=normalize_manifest(ROOT,mp,m,jobs.get(rel(mp.parent)))
        warnings.extend(messages)
        for e in entries:
            path=ROOT/e['file']; category=e['category']
            if not path.is_file(): problems.append('Missing '+e['file']); continue
            if sha(path)!=e['sha256']: problems.append('Hash mismatch '+e['file'])
            with Image.open(path) as im:
                if im.size!=(e['width'],e['height']): problems.append('Size mismatch '+e['file'])
                a=im.convert('RGBA').getchannel('A')
                e['alphaRange']=list(a.getextrema())
                if a.getextrema()[0]==255 and category!='illustrations': problems.append('Sprite has opaque background '+e['file'])
                if category=='illustrations': e['opaqueIllustration']=True
            for source in e.get('derivedFrom',[]):
                sp=ROOT/source['file']
                if not sp.is_file(): problems.append('Missing source '+source['file'])
                elif sha(sp)!=source['sha256']: problems.append('Source hash mismatch '+source['file'])
                if not (ROOT/source['generationRecord']).is_file(): problems.append('Missing source record '+source['generationRecord'])
            if 'nineSlice' in e:
                l,t,r,b=e['nineSlice']
                if min(l,t,r,b)<0 or l+r>=e['width'] or t+b>=e['height']: problems.append('Invalid nineSlice '+e['file'])
            assets.append(e)
    for scene in sorted((ROOT/'assets/scenes').glob('*/scene.json')):
        e=read(scene); path=scene.parent/e['file']; image=Image.open(path)
        assets.append({'id':'scenes/'+e['id'],'localId':e['id'],'name':{'scene-shallow':'浅海渔湾','scene-coral':'珊瑚海域','scene-deep':'幽蓝深海','scene-palace':'龙宫海域','scene-harbor':'仙港大厅'}.get(e['id'],e['id']),
            'category':'scenes','file':rel(path),'width':image.width,'height':image.height,'sha256':sha(path),
            'anchor':[0.5,0.5],'displaySize':list(image.size),'manifest':rel(scene),'generationRecord':rel(path)+'.generation.json',
            'status':e['status'],'safePlayfield':e['safePlayfield'],'scalePolicy':e['scalePolicy']})
        if sha(path)!=e['sha256']: problems.append('Scene hash mismatch '+rel(path))
    # Shared bridge resolved producer display calibration before pixel checks.
    # Never fit native animation canvases to a generic static-asset bounding box.
    ids=[e['id'] for e in assets]
    if len(set(ids))!=len(ids): problems.append('Duplicate asset IDs')
    return assets,warnings,problems

def pack_atlases(assets):
    atlas_dir=ROOT/'assets/atlases'; atlas_dir.mkdir(parents=True,exist_ok=True)
    pages=[]; checks=[]; maxsize=2048; pad=2
    groups=collections.defaultdict(list)
    for e in assets:
        if e['category'] not in ['scenes','illustrations']: groups[e['category']].append(e)
    for group,items in sorted(groups.items()):
        pending=sorted(items,key=lambda x:(-x['height'],-x['width'],x['id']))
        page_idx=0
        while pending:
            placements=[]; rest=[]; x=y=pad; rowh=0
            for e in pending:
                w,h=e['width'],e['height']
                if max(w,h)>maxsize-2*pad: raise ValueError('Oversized atlas sprite '+e['id'])
                if x+w+pad>maxsize: x=pad; y+=rowh+2*pad; rowh=0
                if y+h+pad>maxsize: rest.append(e); continue
                placements.append((e,x,y)); x+=w+2*pad; rowh=max(rowh,h)
            if not placements: raise ValueError('Atlas pack made no progress')
            width=max(px+e['width']+pad for e,px,py in placements)
            height=max(py+e['height']+pad for e,px,py in placements)
            canvas=Image.new('RGBA',(width,height),(0,0,0,0)); frames={}
            for e,px,py in placements:
                with Image.open(ROOT/e['file']) as im: canvas.paste(im.convert('RGBA'),(px,py))
                frame={'x':px,'y':py,'w':e['width'],'h':e['height']}
                frames[e['id']]={'frame':frame,'rotated':False,'trimmed':False,'sourceSize':{'w':e['width'],'h':e['height']},'pivot':e['anchor'],'source':e['file'],'sourceSha256':e['sha256']}
                e['atlas']={'file':f'assets/atlases/{group}-{page_idx:02}.png','rect':frame}
            file=atlas_dir/f'{group}-{page_idx:02}.png'; canvas.save(file)
            with Image.open(file) as decoded:
                for e,px,py in placements:
                    with Image.open(ROOT/e['file']) as source:
                        equal=decoded.crop((px,py,px+e['width'],py+e['height'])).tobytes()==source.convert('RGBA').tobytes()
                    checks.append({'id':e['id'],'atlas':rel(file),'exactPixelRoundtrip':equal})
                    if not equal: raise ValueError('Atlas pixels changed '+e['id'])
            meta={'schemaVersion':1,'frames':frames,'meta':{'image':file.name,'size':{'w':width,'h':height},'format':'RGBA8888','scale':1,'padding':pad,'noRotation':True,'generatedAt':NOW,'operation':'native pixel packing; no resampling or redraw'}}
            write(file.with_suffix('.json'),meta)
            write(str(file)+'.generation.json',{'file':rel(file),'sha256':sha(file),'width':width,'height':height,'operation':{'type':'native_atlas_packing','resampled':False,'upscaled':False},'derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['generationRecord']} for e,_,_ in placements],'actualModel':None,'actualQuality':None,'modelEvidence':'No model call; see individual sources.'})
            pages.append({'file':rel(file),'metadata':rel(file.with_suffix('.json')),'width':width,'height':height,'count':len(placements),'sha256':sha(file)})
            page_idx+=1; pending=rest
    return pages,checks

def clips_and_cannons(assets):
    lookup={e['localId']:e for e in assets if e['category']=='cannons'}; clips=[]; cannons=[]
    for fx in ['net','ice','thunder','capture','hit','gather','guard','surge']:
        members=sorted([e for e in assets if e['file'].startswith('assets/fx/fx-'+fx+'/')],key=lambda e:e['localId'])
        if len(members)!=16: continue
        sizes={(e['width'],e['height']) for e in members}
        if len(sizes)!=1: raise ValueError('FX canvas varies '+fx)
        frames=[Image.open(ROOT/e['file']).convert('RGBA') for e in members]
        preview=ROOT/'assets-preview/clips'/('fx-'+fx+'.webp');preview.parent.mkdir(parents=True,exist_ok=True)
        durations=[63 if i%2==0 else 62 for i in range(16)]
        frames[0].save(preview,save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True,method=4)
        write(str(preview)+'.generation.json',{'file':rel(preview),'sha256':sha(preview),'operation':{'type':'lossless_webp_animation_encode','resampled':False,'upscaled':False,'durationsMs':durations,'previewLoop':True,'gameLoop':False},'derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['generationRecord']} for e in members],'actualModel':None,'actualQuality':None,'status':'review_preview_only'})
        clips.append({'id':'fx-'+fx,'name':{'net':'渔网展开','ice':'玄冰封冻','thunder':'雷网爆发','capture':'捕获灵光','hit':'水珠命中','gather':'聚鱼金流','guard':'太极护持','surge':'激流涌浪'}[fx],
             'fps':16,'loop':False,'durationMs':1000,'frameDurationUs':62500,'root':[0.5,0.5],
             'canvas':list(sizes.pop()),'frames':[e['id'] for e in members],'preview':rel(preview),
             'previewPlayback':'repeating review playback; game clip is one-shot',
             'status':'native_fx_frames_ready_pending_motion_review'})
    for prefix,name in [('hulu','葫芦炮'),('yunwen','云纹炮'),('lianhua','莲华炮'),('leizhen','雷霆炮'),('hanjing','玄冰炮'),('longyu','龙吟炮')]:
        if prefix+'-base' in lookup and prefix+'-barrel' in lookup:
            cannons.append({'id':prefix,'name':name,'base':lookup[prefix+'-base']['id'],'barrel':lookup[prefix+'-barrel']['id'],
                'zeroAngleDegrees':0,'forward':[0,-1],'rotationRoot':[0.5,0.70],'renderOrder':{'base':30,'barrel':31},
                'integrationStatus':'candidate_pivot_requires_target_client_check'})
    encoded={c['id']:c for c in clips}
    clips=build_fx_clips(ROOT,assets)
    for clip in clips:
        if clip['id'] in encoded:
            clip['preview']=encoded[clip['id']]['preview']
            clip['previewPlayback']='Repeating review preview; game clip is one-shot.'
    clips.extend(build_native_clips(ROOT,assets))
    return clips,cannons

def main():
    from ArtAcceptanceState import preserve_accepted
    if preserve_accepted(ROOT): return
    # Existing adopted character files/manifests are authoritative; packing must not rewrite them.
    assets,warnings,problems=collect(); pages,checks=pack_atlases(assets); clips,cannons=clips_and_cannons(assets)
    counts=dict(collections.Counter(e['category'] for e in assets))
    stats=catalog_stats(assets,clips)
    catalog={'schemaVersion':1,'builtAt':NOW,'nativeOnly':True,'style':'道家Q版高清手绘','assets':assets,'clips':clips,'cannons':cannons,'atlases':pages,
        'renderOrder':{'scenes':0,'fish':10,'projectiles':20,'fx':25,'cannonBase':30,'cannonBarrel':31,'ui':100,'modal':200},
        'counts':counts,'statistics':stats,'warnings':warnings,'gameArtComplete':False,
        'motionRoute':'builtin_native_AI_frames_user_requested',
        'projectile':{'asset':'icons/bullet','headAnchor':[0.31,0.61],'artForward':[-0.70710678,0.70710678],'displayBox':[42,38],'rotateArtworkToVelocity':True,'integrationStatus':'candidate_requires_target_client_check'},
        'uiStateRegistration':'config/ui-state-registration.json','typography':'config/ui-typography.json',
        'skillArtBindings':read(ROOT/'config/skill-art-bindings.json'),
        'remainingGates':['Native action candidates require actual playback and identity/pose review.','Target Unity integration, display calibration, cannon pivots and FX timing require in-game verification.']}
    write(ROOT/'assets/runtime-catalog.json',catalog)
    (ROOT/'assets/runtime-catalog.js').write_text('window.BUYU_ART = '+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    report={'builtAt':NOW,'counts':counts,'assetCount':len(assets),'atlasPages':len(pages),'atlasPixelRoundtripCount':len(checks),
         'staticAndFxAssetCount':stats['staticAndFxAssetCount'],'animationFrameCount':stats['animationFrameCount'],
         'nativeActionClipCount':stats['nativeActionClipCount'],'releaseReadyNativeActions':stats['releaseReadyNativeActions'],
         'atlasPixelRoundtripAllEqual':all(e['exactPixelRoundtrip'] for e in checks),'problems':problems,'warnings':warnings,
         'staticFileChecksPassed':not problems,'producerWarningsPreserved':True,'gameArtComplete':False,'note':'File/alpha/pixel checks do not approve anatomy, motion or target-client integration. Preserved producer source-grid warnings are separate from current file/pixel failures.'}
    write(ROOT/'docs/GAME_ART_PACK_VALIDATION.json',report)
    write(ROOT/'assets/atlases/packing-validation.json',{'checks':checks})
    print(json.dumps(report,ensure_ascii=False))
    if problems: raise SystemExit(1)

if __name__=='__main__': main()
