"""Export ONE native action from measured sheets using one fixed eye root.

No pose generation, resampling, rotating, bbox normalizing or motion approval.
Ownership extraction may recover intact poses that cross a nominal grid line.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,datetime,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
config=read(ROOT/args.config);actor=config['actor'];action=config['action'];canvas=config.get('canvas',[1000,1000]);eye=config.get('eyeRoot',[680,420]);out=ROOT/f'assets/animations/{actor}/{action}';out.mkdir(parents=True,exist_ok=True)
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat();frames=[];items=[];warnings=[];sources=[]
for sheet in config['sheets']:
    qa=read(ROOT/sheet['qa']);source=ROOT/qa['source'];assert sha(source)==qa['sha256'];im=Image.open(source).convert('RGBA');sources.append({'file':rel(source),'sha256':sha(source),'generationRecord':rel(source)+'.generation.json'})
    ownership=read(ROOT/sheet['ownership']) if sheet.get('ownership') else None
    for entry in qa['frames']:
        local=entry['sourceFrame'];nominal=entry['sourceRect'];candidateIndex=sheet.get('eyeCandidateIndices',[0]*len(qa['frames']))[local];landmark=sheet.get('eyePoints',[None]*len(qa['frames']))[local] or entry['pupilCandidates'][candidateIndex]['center'];globalPoint=[landmark[0]+nominal[0],landmark[1]+nominal[1]]
        if ownership:
            e=ownership['frames'][local];rect=e['sourceRect'];raw=Image.open(ROOT/e['file']).convert('RGBA');assert e['totalCanvasEdgeMaxAlpha']<=16,'Structural source canvas clipping'
            if e['totalCanvasEdgeMaxAlpha']>3:warnings.append({'id':'source_canvas_subvisual_fringe','frame':len(frames),'edgeMaxAlpha':e['totalCanvasEdgeMaxAlpha'],'note':'Core silhouette alpha>16 contained; faint fringe at total edge retained as source limitation, not declared zero-alpha border pass.'})
            sourcePoint=[globalPoint[0]-rect[0],globalPoint[1]-rect[1]];extraction={'type':'complete_native_actor_ownership','report':sheet['ownership'],'sourceRect':rect,'evidence':e}
        else:
            assert entry['edgeMaxAlpha']<=3,'Source crosses nominal cell, needs ownership extraction';rect=nominal;raw=im.crop(rect);sourcePoint=landmark;extraction={'type':'native_grid_crop','sourceRect':rect,'nominalGridCross':False}
        alpha=raw.getchannel('A').point(lambda v:0 if v<=3 else v);raw.putalpha(alpha)
        offset=[eye[0]-round(sourcePoint[0]),eye[1]-round(sourcePoint[1])];assert offset[0]>=0 and offset[1]>=0 and offset[0]+raw.width<=canvas[0] and offset[1]+raw.height<=canvas[1], 'Canvas cannot contain whole source crop'
        frame=Image.new('RGBA',tuple(canvas),(0,0,0,0));frame.paste(raw,tuple(offset));assert frame.crop((offset[0],offset[1],offset[0]+raw.width,offset[1]+raw.height)).tobytes()==raw.tobytes()
        bbox=frame.getchannel('A').getbbox();margins=[bbox[0]/canvas[0],bbox[1]/canvas[1],(canvas[0]-bbox[2])/canvas[0],(canvas[1]-bbox[3])/canvas[1]];assert min(margins)>=.12,'Final runtime margin insufficient'
        i=len(frames);path=out/f'frame-{i:02d}.png';frame.save(path)
        item={'schemaVersion':1,'id':f'frame-{i:02d}','name':config['name']+f' {i+1}/8','file':rel(path),'sha256':sha(path),'width':canvas[0],'height':canvas[1],'format':'RGBA PNG','derivedAt':NOW,'nativeSource':rel(source),'derivedFrom':[sources[-1]],'operation':{'type':'native_extraction_integer_eye_registration_and_padding','extraction':extraction,'sourceEyePoint':sourcePoint,'globalSourceEye':globalPoint,'registrationOffset':offset,'registeredCanvas':canvas,'targetEye':eye,'alphaCleanup':'alpha<=3 removed; other native pixels unchanged','sourcePixelsRoundTripVerified':True,'resized':False,'upscaled':False,'rotated':False,'poseWarped':False,'newNativeDetailClaimed':False},'anchor':[eye[0]/canvas[0],eye[1]/canvas[1]],'rootPixels':eye,'eyePixels':eye,'registeredAlphaBBox':list(bbox),'registeredMinMargin':min(margins),'status':'candidate_pending_playback_and_final_visual_review','actualModel':None,'actualQuality':None}
        item['sourceLandmarkEvidence']={'type':'closed_eyelid_proxy_center' if local in sheet.get('closedEyeFrames',[]) else 'visible_eye_pupil_ROI_component_center','qa':sheet['qa'],'sourceFrame':local,'candidateIndex':candidateIndex,'detection':qa.get('pupilDetection'),'limitation':'Eye registration removes layout drift; native head contour/scale changes remain for visual playback review. Closed eyelid proxies are not true pupils and must be excluded from pixel-density calibration.'}
        if entry.get('marginsLTRB') and min(entry['marginsLTRB'])<.12:warnings.append({'id':'raw_nominal_source_margin_lt_12pct','frame':i,'sourceMinMargin':min(entry['marginsLTRB']),'retained':True})
        frames.append(frame);items.append(item)
assert len(frames)==8,'Expected 8 real source phases'
rest=items[0]['registeredAlphaBBox'];visible=[rest[2]-rest[0],rest[3]-rest[1]];fit=config.get('bodyDisplayBox',[340,260]);scale=min(fit[0]/visible[0],fit[1]/visible[1],1)
fps=config['fps'];durations=[round((i+1)*1000/fps)-round(i*1000/fps) for i in range(8)]
animation={'id':actor+'/'+action,'frames':8,'fps':fps,'loop':config['loop'],'order':list(range(8)),'durationsMs':durations,'root':[eye[0]/canvas[0],eye[1]/canvas[1]],'sourceRoute':'builtin_native_AI_sheet_user_requested','sourcePixelsNeverResampled':True,'loopPlaybackStatus':'not_run_during_local_heavy_job_hold'}
for i,item in enumerate(items):
    item.update({'displaySize':[canvas[0]*scale,canvas[1]*scale],'bodyDisplayBox':fit,'uniformDisplayScale':scale,'displaySizing':{'method':'One scale from first full rest silhouette, reused across all8 frames; no per-frame bbox normalization','sourceVisibleReference':visible,'upscalingAllowed':False,'crossClipDensityReview':'pending_common_head_scale_review'},'animation':{**animation,'phase':i,'durationMs':durations[i]}});write(ROOT/(item['file']+'.generation.json'),item)
contacts=[]
for suffix,color,ink in [('light',(245,237,217),(31,71,59)),('dark',(21,52,45),(241,232,203))]:
    # 1:1 registered source pixels; this is QA contact assembly, no new art.
    contact=Image.new('RGB',(canvas[0]*4,(canvas[1]+24)*2),color);draw=ImageDraw.Draw(contact)
    for i,frame in enumerate(frames):
        x,y=(i%4)*canvas[0],(i//4)*(canvas[1]+24);contact.paste(frame,(x,y),frame);draw.text((x+8,y+canvas[1]+5),f'{actor}/{action} frame{i:02d}',fill=ink)
    cp=ROOT/f'tmp/art-qa/{actor}-{action}-registered-{suffix}.jpg';cp.parent.mkdir(parents=True,exist_ok=True);contact.save(cp,quality=90);contacts.append(rel(cp))
manifest={'schemaVersion':1,'source':[s['file'] for s in sources],'output':rel(out),'sourceEvidence':sources,'frameCount':8,'items':items,'animation':animation,'sharedCanvas':canvas,'rootPixels':eye,'eyePixels':eye,'anchor':[eye[0]/canvas[0],eye[1]/canvas[1]],'uniformDisplayScale':scale,'bodyDisplayBox':fit,'displaySize':[canvas[0]*scale,canvas[1]*scale],'warnings':warnings+[{'id':'native_head_shape_and_inter_sheet_density','severity':'pending_playback_review','note':'Integer translation cannot correct generated head contour or native scale drift; do not treat pixel bounds as motion approval.'}],'contactSheets':contacts,'qa':{'nativeOwnedPixelsPreserved':True,'registeredMarginStatus':'pass_12pct','sourceMarginStatus':'warnings_preserved','sourceCanvasClipping':'none_for_adopted_extractions','semanticOwnershipStatus':'pending_root_contact_sheet_review','poseAndIdentityStatus':'native_source_stills_observed_pending_registered_review','loopPlaybackStatus':'not_run_during_local_heavy_job_hold','unityPlaybackStatus':'not_run'},'status':'candidate_pending_playback_and_final_visual_review','releaseReady':False}
write(out/'manifest.json',manifest);print(json.dumps({'actor':actor,'action':action,'frames':len(items),'manifest':rel(out/'manifest.json'),'canvas':canvas,'minMargin':min(i['registeredMinMargin'] for i in items),'displayScale':scale,'status':manifest['status']}))
