"""Bounded native 8-frame crop/QA/export for worker-owned fish14–24 only.
No pixel resampling, synthetic motion, bbox fitting or global catalog changes.
"""
raise SystemExit('Retired nominal-grid exporter: use register_group.py. Current native ownership extraction and canvas844 must be preserved.')
from pathlib import Path
from PIL import Image, ImageDraw
import argparse, datetime, hashlib, json, math

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('creature')
parser.add_argument('action', choices=['swim','capture'])
parser.add_argument('--version', default='')
parser.add_argument('--anchors', help='JSON array of8 manually inspected source-local root/eye points; no automatic bbox centering')
parser.add_argument('--target', default='[540,300]', help='One common target landmark for all8frames; use same point across species actions')
parser.add_argument('--eye-roi', help='Optional fixed source-local eye ROI [left,top,right,bottom]; measurement only, never masks artwork')
parser.add_argument('--notes', default='Source contact review pending.')
args = parser.parse_args()
assert 14 <= int(args.creature.split('-')[0]) <= 24, 'Outside worker scope'
HERE = ROOT / 'designs/motion-frames-v1' / args.creature / args.action
source = HERE / f'{args.creature}-{args.action}{args.version}.png'
im = Image.open(source).convert('RGBA')
cw, ch = math.ceil(im.width/4), math.ceil(im.height/2)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).relative_to(ROOT).as_posix()
def write(p, data): Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
cells, metrics, warnings = [], [], []
for i in range(8):
    row, col = divmod(i,4)
    rect = [round(col*im.width/4), round(row*im.height/2), round((col+1)*im.width/4), round((row+1)*im.height/2)]
    raw = im.crop(rect)
    a = raw.getchannel('A')
    edge = max(a.crop((0,0,raw.width,1)).getextrema()[1], a.crop((0,raw.height-1,raw.width,raw.height)).getextrema()[1], a.crop((0,0,1,raw.height)).getextrema()[1], a.crop((raw.width-1,0,raw.width,raw.height)).getextrema()[1])
    raw.putalpha(a.point(lambda v: 0 if v<=3 else v))
    cell = Image.new('RGBA',(cw,ch),(0,0,0,0)); cell.paste(raw,(0,0))
    bounds = cell.getchannel('A').getbbox()
    if not bounds: raise RuntimeError('Empty source frame '+str(i))
    margins = [bounds[0]/cw,bounds[1]/ch,(cw-bounds[2])/cw,(ch-bounds[3])/ch]
    if edge>16: warnings.append({'id':'source_cell_border_alpha','frame':i,'actual':edge,'threshold':16})
    if min(margins)<.12: warnings.append({'id':'source_margin_lt_12pct','frame':i,'actual':min(margins),'threshold':.12})
    cells.append(cell)
    metrics.append({'frame':i,'sourceRect':rect,'nativeCell':list(raw.size),'alphaBBox':list(bounds),'marginsLTRB':margins,'edgeMaxAlpha':edge})
def contact(frames, stem):
    w,h=frames[0].size
    for suffix,bg,ink in [('light',(245,237,217),(31,71,59)),('dark',(21,52,45),(241,232,203))]:
        board=Image.new('RGB',(w*4,(h+24)*2),bg);d=ImageDraw.Draw(board)
        for i, frame in enumerate(frames):
            x=(i%4)*w;y=(i//4)*(h+24);board.paste(frame,(x,y),frame);d.text((x+8,y+h+5),f'{i:02d} / {args.creature} {args.action}',fill=ink)
        board.save(HERE/(stem+'-'+suffix+'.jpg'),quality=91)
contact(cells,'source'+args.version)
qa={'schemaVersion':1,'source':rel(source),'sha256':sha(source),'nativeSize':list(im.size),'cellCanvas':[cw,ch],'frames':metrics,'warnings':warnings,'actualMotionReview':args.notes,'actualMotionApproved':False,'loopPlaybackStatus':'not_run_during_heavy_job_hold','noResampling':True}
if args.eye_roi:
    roi=json.loads(args.eye_roi);eye_results=[]
    for cell in cells:
        px=cell.load();points=set()
        for y in range(roi[1],min(roi[3],cell.height)):
            for x in range(roi[0],min(roi[2],cell.width)):
                r,g,b,a=px[x,y]
                if a>=180 and max(r,g,b)<80:points.add((x,y))
        groups=[]
        while points:
            start=points.pop();stack=[start];group=[start]
            while stack:
                x,y=stack.pop()
                for neighbor in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if neighbor in points:points.remove(neighbor);stack.append(neighbor);group.append(neighbor)
            if len(group)>=25:
                xs=[p[0] for p in group];ys=[p[1] for p in group];w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1
                if .6<=w/h<=1.7 and len(group)/(w*h)>=.35 and len(group)<1600:
                    groups.append({'center':[sum(xs)/len(xs),sum(ys)/len(ys)],'boundsLTRB':[min(xs),min(ys),max(xs)+1,max(ys)+1],'area':len(group)})
        if not groups:eye_results.append(None)
        else:eye_results.append(max(groups,key=lambda g:g['area']))
    qa['eyeMeasurement']={'roi':roi,'results':eye_results,'method':'largest roughlyround dark component inside fixed head ROI, manual approval required; metadata only, no source masking'}
write(HERE/('source'+args.version+'-qa.json'),qa)
if not args.anchors:
    print(json.dumps({'source':rel(source),'nativeSize':list(im.size),'edgeMaxAlpha':[m['edgeMaxAlpha'] for m in metrics],'warnings':warnings,'eyes':qa.get('eyeMeasurement')},ensure_ascii=False));raise SystemExit(0)
assert not any(m['edgeMaxAlpha']>16 for m in metrics), 'Source border requires repair before candidate export'
points=json.loads(args.anchors);assert len(points)==8
CANVAS=(744,744);TARGET=json.loads(args.target);BODYROOT=[372,372]
OUT=ROOT/'assets/animations'/args.creature/args.action;OUT.mkdir(parents=True,exist_ok=True)
fps=8 if args.action=='swim' and args.creature=='14-huanyue' else 12
durations=[round((i+1)*1000/fps)-round(i*1000/fps) for i in range(8)]
animation={'id':args.creature+'/'+args.action,'frames':8,'fps':fps,'loop':args.action=='swim','order':'row-major','phasesDegrees':list(range(0,360,45)) if args.action=='swim' else None,'durationsMs':durations,'timingNote':'fps authoritative, durations rounded from cumulative boundaries','root':[.5,.5],'registrationStatus':'integer_landmark_registered_core_shape_pending_root_visual','identityStatus':'pending_root_visual','motionStatus':'pending_root_visual','loopVisualStatus':'pending_root_playback' if args.action=='swim' else 'single_shot_pending_root_playback','sourceRoute':'builtin_native_AI_sheet_user_requested'}
status='producer_candidate_pending_root_registered_review';items=[];registered=[];regs=[]
for i,(cell,metric,point) in enumerate(zip(cells,metrics,points)):
    p=[round(point[0]),round(point[1])];offset=[TARGET[0]-p[0],TARGET[1]-p[1]]
    bounds=cell.getchannel('A').getbbox()
    assert bounds[0]+offset[0]>=0 and bounds[1]+offset[1]>=0 and bounds[2]+offset[0]<=CANVAS[0] and bounds[3]+offset[1]<=CANVAS[1], 'Nontransparent clipping'
    frame=Image.new('RGBA',CANVAS,(0,0,0,0));frame.paste(cell,tuple(offset))
    # Only any transparent source-cell padding may lie outside target. Verify the entire visible bounding box unchanged.
    recovered=frame.crop((bounds[0]+offset[0],bounds[1]+offset[1],bounds[2]+offset[0],bounds[3]+offset[1]))
    assert recovered.tobytes()==cell.crop(bounds).tobytes(), 'Native visible pixels changed'
    rb=list(frame.getchannel('A').getbbox());margins=[rb[0]/CANVAS[0],rb[1]/CANVAS[1],(CANVAS[0]-rb[2])/CANVAS[0],(CANVAS[1]-rb[3])/CANVAS[1]]
    assert min(margins)>=.12, 'Increase fixed shared canvas or adjust ONE common root, never perframe scale'
    path=OUT/f'frame-{i:02d}.png';frame.save(path)
    operation={'type':'native_grid_crop_integer_manual_landmark_registration_transparent_padding','grid':{'cols':4,'rows':2},'sourceRect':metric['sourceRect'],'cellCropRect':[0,0,*metric['nativeCell']],'alphaCleanup':'Only alpha<=3 set to0; all other alpha and RGB retained','resized':False,'upscaled':False,'rotated':False,'registrationOffset':offset,'registeredCanvas':list(CANVAS),'registrationReference':{'type':'manually_inspected_fixed_anatomical_landmark','sourcePointFloat':point,'sourcePointRounded':p,'targetPoint':TARGET,'rounding':'nearest integer','limitation':'Integer translation fixes layout displacement only; head/body shape drift remains a review gate.'},'sourcePixelsRoundTripVerified':True,'transparentOnlyClipping':True,'newNativeDetailClaimed':False}
    item={'schemaVersion':1,'id':f'frame-{i:02d}','name':args.creature+' '+args.action+' '+str(i),'file':rel(path),'sha256':sha(path),'width':CANVAS[0],'height':CANVAS[1],'format':'RGBA PNG','nativeSource':rel(source),'derivedFrom':[{'file':rel(source),'sha256':sha(source),'generationRecord':rel(source)+'.generation.json'}],'operation':operation,'anchor':[.5,.5],'rootPixels':BODYROOT,'landmarkPixels':TARGET,'registeredAlphaBBox':rb,'registeredMinMargin':min(margins),'status':status,'actualModel':None,'actualQuality':None,'modelEvidence':'No new model call for slice; source actual model/quality undisclosed.','animation':animation,'displaySizing':{'preserveAspect':True,'uniformScaleAcrossAction':True,'upscalingAllowed':False,'status':'pending_one_common_species_scale'},'targetBodyBox':[180,130]}
    items.append(item);registered.append(frame);regs.append({'frame':i,'sourceLandmark':point,'registrationOffset':offset,'targetLandmark':TARGET,'bodyRoot':BODYROOT,'bbox':rb,'marginsLTRB':margins,'pixelsRoundTrip':True})
rest=items[0]['registeredAlphaBBox'];size=[rest[2]-rest[0],rest[3]-rest[1]]
# Reuse swim scale for capture; never fit capture frames independently.
swim_manifest=OUT.parent/'swim/manifest.json'
if args.action=='capture' and swim_manifest.exists():
    swim_data=json.loads(swim_manifest.read_text(encoding='utf-8'));scale=swim_data['uniformDisplayScale'];scale_method='same species swim uniform scale reused for capture; no capture bbox fitting'
else:
    scale=min(180/size[0],130/size[1],1);scale_method='one scale from rest visible silhouette, reused for every frame'
for item in items:
    item.update({'uniformDisplayScale':scale,'displaySize':[CANVAS[0]*scale,CANVAS[1]*scale],'bodyDisplayBox':[180,130],'displayScaleReference':{'frame':0,'restNativeVisibleBox':size,'fitMaxBox':[180,130],'method':scale_method,'upscaling':False}});write(ROOT/(item['file']+'.generation.json'),item)
manifest={'schemaVersion':1,'source':rel(source),'sourceSha256':sha(source),'sourceWidth':im.width,'sourceHeight':im.height,'output':rel(OUT),'items':items,'animation':animation,'sharedCanvas':list(CANVAS),'rootPixels':BODYROOT,'landmarkPixels':TARGET,'bodyRootEvidence':'Logical root fixed relative to manually inspected anatomical landmark; rigidity pending root visual review.','registration':regs,'order':list(range(8)),'sourceMarginWarnings':[w for w in warnings if w['id']=='source_margin_lt_12pct'],'runtimeMarginWarnings':[],'warnings':warnings+[{'id':'core_shape_and_motion_pending_root_visual','note':args.notes}],'uniformDisplayScale':scale,'displaySize':[CANVAS[0]*scale,CANVAS[1]*scale],'bodyDisplayBox':[180,130],'qa':{'technicalAlpha':'true_rgba','sourceBorderStatus':'pass','sourceMarginStatus':'fail_preserved_source_gate' if warnings else 'pass','registeredMarginStatus':'pass','actualMotionStatus':'candidate_articulated_poses_pending_root_visual','registrationStatus':'integer_landmark_registered_core_shape_pending','loopPlaybackStatus':animation['loopVisualStatus']},'status':status}
write(OUT/'manifest.json',manifest);contact(registered,'registered'+args.version)
write(HERE/('candidate-review'+args.version+'.json'),{'schemaVersion':1,'manifest':rel(OUT/'manifest.json'),'source':rel(source),'actualVisualObservation':args.notes,'sourceAndRegisteredLightDarkActuallyInspected':False,'status':status,'warnings':manifest['warnings'],'noResampling':True,'fps':fps,'durationsMs':durations,'nativeSize':list(im.size),'nativeMinimumBody180':'pending_manual_visual_measurement','registeredMinimumMargin':min(i['registeredMinMargin'] for i in items),'testsBrowserAtlasUnityRun':False})
print(json.dumps({'manifest':rel(OUT/'manifest.json'),'frames':8,'fps':fps,'loop':animation['loop'],'canvas':list(CANVAS),'minMargin':min(i['registeredMinMargin'] for i in items),'uniformDisplayScale':scale,'warnings':warnings},ensure_ascii=False))
