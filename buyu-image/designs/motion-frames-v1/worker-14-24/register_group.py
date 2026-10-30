"""Native ownership extraction and one-landmark integer registration.

Only fish13–24. All source pixels with alpha>3 are assigned exactly once to
the nearest of8 separate alpha>16 anatomical components. This handles a
complete fin crossing a nominal grid line without deleting/repainting it.
It cannot repair true total-canvas truncation or intersecting subjects.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from scipy import ndimage
import numpy as np, json, hashlib, sys, datetime
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
config=json.loads((HERE/'adopted-sources.json').read_text(encoding='utf-8'))
selected=set(sys.argv[1:])
CANVAS=(844,844);BODYROOT=[422,422]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def write(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def anatomical_eye(rgba, rect):
    left,top,right,bottom=rect
    part=rgba[top:bottom,left:right]
    dark=(part[:,:,3]>=180)&(part[:,:,:3].max(axis=2)<80)
    labels,n=ndimage.label(dark);counts=np.bincount(labels.ravel());counts[0]=0
    groups=[]
    for ident,s in enumerate(ndimage.find_objects(labels),1):
        if s is None or counts[ident]<50 or counts[ident]>1800:continue
        yy,xx=s;w=xx.stop-xx.start;h=yy.stop-yy.start
        if not .6<=w/h<=1.7 or counts[ident]/(w*h)<.35:continue
        cy,cx=ndimage.center_of_mass(dark,labels,ident)
        groups.append({'center':[float(cx+left),float(cy+top)],'boundsLTRB':[xx.start+left,yy.start+top,xx.stop+left,yy.stop+top],'area':int(counts[ident])})
    if not groups:raise RuntimeError('No eye in fixed anatomical ROI '+str(rect))
    return max(groups,key=lambda g:g['area'])

def make_contact(frames,folder,stem,landmarks=None):
    w,h=frames[0].size
    for suffix,bg,ink in [('light',(245,237,217),(31,71,59)),('dark',(21,52,45),(241,232,203))]:
        board=Image.new('RGB',(w*4,(h+24)*2),bg);d=ImageDraw.Draw(board)
        for i,frame in enumerate(frames):
            x=(i%4)*w;y=(i//4)*(h+24);board.paste(frame,(x,y),frame)
            if landmarks:
                lx,ly=landmarks[i];lx+=x;ly+=y
                d.line((lx-5,ly,lx+5,ly),fill=(231,58,84),width=1);d.line((lx,ly-5,lx,ly+5),fill=(231,58,84),width=1)
            d.text((x+8,y+h+5),f'{i:02d} / candidate / no playback',fill=ink)
        board.save(folder/(stem+'-'+suffix+'.jpg'),quality=91)

for spec in config:
    creature=spec['id']
    if selected and creature not in selected:continue
    for action in ['swim','capture']:
        version=spec['swimVersion'] if action=='swim' else spec['captureVersion']
        folder=ROOT/'designs/motion-frames-v1'/creature/action
        source=folder/f'{creature}-{action}{version}.png'
        image=Image.open(source).convert('RGBA');pixels=np.array(image);alpha=pixels[:,:,3]
        pixels[:,:,3][alpha<=3]=0;alpha=pixels[:,:,3]
        solid_labels,n=ndimage.label(alpha>16);counts=np.bincount(solid_labels.ravel());counts[0]=0
        top_ids=np.argsort(counts)[-8:]
        assert counts[top_ids[0]]>10000,'Eight distinct anatomical subjects not found'
        boxes=ndimage.find_objects(solid_labels);mains=[]
        for ident in top_ids:
            yy,xx=boxes[ident-1];cy,cx=ndimage.center_of_mass(alpha>16,solid_labels,int(ident))
            mains.append({'label':int(ident),'area':int(counts[ident]),'center':[float(cx),float(cy)],'bbox':[xx.start,yy.start,xx.stop,yy.stop]})
        mains.sort(key=lambda m:m['center'][1]);mains=sorted(mains[:4],key=lambda m:m['center'][0])+sorted(mains[4:],key=lambda m:m['center'][0])
        roots=np.zeros(alpha.shape,dtype=np.uint8)
        for i,main in enumerate(mains):roots[solid_labels==main['label']]=i+1
        # Ownership only; all RGBA values with alpha>3 are preserved, never nearest-neighbor resampled.
        nearest=ndimage.distance_transform_edt(roots==0,return_distances=False,return_indices=True)
        ownership=roots[tuple(nearest)];ownership[alpha==0]=0
        assert np.count_nonzero(ownership)==np.count_nonzero(alpha),'Ownership lost source pixels'
        nominal=[];source_warnings=[];landmarks=[];eye_metrics=[]
        cellw=image.width/4;cellh=image.height/2
        for i,main in enumerate(mains):
            row,col=divmod(i,4);nr=[round(col*cellw),round(row*cellh),round((col+1)*cellw),round((row+1)*cellh)]
            nominal.append(nr)
            a=alpha[nr[1]:nr[3],nr[0]:nr[2]]
            edge=int(max(a[0,:].max(),a[-1,:].max(),a[:,0].max(),a[:,-1].max()))
            yy,xx=np.nonzero(a);margin=min(xx.min()/a.shape[1],yy.min()/a.shape[0],(a.shape[1]-xx.max()-1)/a.shape[1],(a.shape[0]-yy.max()-1)/a.shape[0])
            if edge>16:source_warnings.append({'id':'nominal_grid_cross','frame':i,'edgeMaxAlpha':edge,'note':'Ownership extraction used; nominal grid crossing alone is not a physical clip.'})
            if margin<.12:source_warnings.append({'id':'source_margin_lt_12pct','frame':i,'actual':float(margin),'required':.12})
            box=main['bbox']
            if box[0]==0 or box[1]==0 or box[2]==image.width or box[3]==image.height:source_warnings.append({'id':'source_total_canvas_boundary','frame':i,'bbox':box,'status':'unpassed_pending_visual_or_AI_repair'})
            if creature=='14-huanyue':
                # Dome crown: specific anatomical silhouette point, not whole-pose bbox centering.
                region=(solid_labels==main['label'])
                crown_y=box[1];ys,xs=np.nonzero(region & (np.indices(alpha.shape)[0]<crown_y+12))
                point=[float(np.median(xs)),float(crown_y+6)]
                eye={'center':point,'boundsLTRB':None,'area':None,'method':'top12px of the connected bell dome crown; approximate silhouette landmark, needs visual registration review'}
            else:
                right_limit=.84 if creature=='20-yuban' else (.90 if creature=='21-haiqiu' else .99)
                roi=[round(nr[0]+cellw*.60),round(nr[1]+cellh*.12),round(nr[0]+cellw*right_limit),round(nr[1]+cellh*.82)]
                if creature=='20-yuban':
                    roi=[nr[0]+295,nr[1]+(140 if row==0 else 110),nr[0]+355,nr[1]+(230 if row==0 else 210)]
                if creature=='21-haiqiu':
                    roi=[nr[0]+325,nr[1]+(170 if row==0 else 120),nr[0]+395,nr[1]+(270 if row==0 else 220)]
                if creature=='24-jindun':
                    # The dark lower fin plate can be larger than the pupil.
                    # Keep this ROI on the actual face, above that fin.
                    roi=[nr[0]+320,nr[1]+(180 if row==0 else 150),nr[0]+425,nr[1]+(280 if row==0 else 250)]
                eye=anatomical_eye(pixels,roi);point=eye['center'];eye['method']='largest round dark eye component inside fixed local head ROI; manually review landmark contact'
            landmarks.append(point);eye_metrics.append(eye)
        OUT=ROOT/'assets/animations'/creature/action;OUT.mkdir(parents=True,exist_ok=True)
        target=[470,250] if creature=='14-huanyue' else [590,350]
        fps=8 if creature in ['13-yunwengui','14-huanyue'] and action=='swim' else 12
        durations=[round((i+1)*1000/fps)-round(i*1000/fps) for i in range(8)]
        status='producer_candidate_pending_root_registered_review'
        if any(w['id']=='source_total_canvas_boundary' for w in source_warnings):status='producer_candidate_source_boundary_pending_review'
        animation={'id':creature+'/'+action,'frames':8,'fps':fps,'loop':action=='swim','order':'row-major','durationsMs':durations,'timingNote':'fps authoritative; cumulative boundaries rounded to integer milliseconds','root':[.5,.5],'registrationStatus':'integer_anatomical_landmark_registered_core_shape_pending','identityStatus':'pending_root_visual','motionStatus':'pending_root_visual','loopVisualStatus':'pending_root_playback' if action=='swim' else 'single_shot_pending_root_playback','sourceRoute':'builtin_native_AI_sheet_user_requested'}
        frames=[];items=[];registrations=[];local_points=[];source_frames=[]
        for i,(point,main) in enumerate(zip(landmarks,mains)):
            own=ownership==i+1;yy,xx=np.nonzero(own);rect=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
            crop=pixels[rect[1]:rect[3],rect[0]:rect[2]].copy();crop[~own[rect[1]:rect[3],rect[0]:rect[2]]]=0
            raw=Image.fromarray(crop,'RGBA');point_local=[point[0]-rect[0],point[1]-rect[1]];offset=[target[0]-round(point_local[0]),target[1]-round(point_local[1])]
            frame=Image.new('RGBA',CANVAS,(0,0,0,0));frame.paste(raw,tuple(offset))
            visible=(crop[:,:,3]>0);original_values=crop[visible]
            recovered=np.array(frame.crop((offset[0],offset[1],offset[0]+raw.width,offset[1]+raw.height)))
            assert np.array_equal(recovered[visible],original_values),'Native owned pixels clipped/changed'
            bbox=list(frame.getchannel('A').getbbox());margins=[bbox[0]/CANVAS[0],bbox[1]/CANVAS[1],(CANVAS[0]-bbox[2])/CANVAS[0],(CANVAS[1]-bbox[3])/CANVAS[1]]
            if min(margins)<.12:source_warnings.append({'id':'registered_margin_lt_12pct','frame':i,'actual':min(margins),'required':.12})
            file=OUT/f'frame-{i:02d}.png';frame.save(file)
            operation={'type':'native_complete_pose_ownership_crop_integer_landmark_registration','nominalGrid':{'cols':4,'rows':2},'nominalGridRect':nominal[i],'sourceRect':rect,'ownership':'All alpha>3 source pixels partitioned exactly once by nearest separate anatomical alpha>16 components. Native RGBA copied unchanged; zeroing pixels owned by other7poses only. No artwork component discarded.','ownershipPixelCount':int(np.count_nonzero(own)),'alphaCleanup':'Only alpha<=3 set to0','resized':False,'upscaled':False,'rotated':False,'registrationOffset':offset,'registeredCanvas':list(CANVAS),'registrationReference':{'type':eye_metrics[i]['method'],'sourcePointGlobal':point,'sourcePointLocal':point_local,'targetPoint':target,'rounding':'nearest integer','limitation':'Translation removes layout displacement; it cannot correct generated shape or camera-scale drift.'},'sourcePixelsRoundTripVerified':True,'newNativeDetailClaimed':False}
            item={'schemaVersion':1,'id':f'frame-{i:02d}','name':creature+' '+action+' '+str(i),'file':rel(file),'sha256':sha(file),'width':CANVAS[0],'height':CANVAS[1],'format':'RGBA PNG','nativeSource':rel(source),'derivedFrom':[{'file':rel(source),'sha256':sha(source),'generationRecord':rel(source)+'.generation.json'}],'operation':operation,'anchor':[.5,.5],'rootPixels':BODYROOT,'landmarkPixels':target,'registeredAlphaBBox':bbox,'registeredMinMargin':min(margins),'actualModel':None,'actualQuality':None,'modelEvidence':'No model call for native crop/ownership/padding; actual source version/quality undisclosed.','animation':animation,'status':status,'targetBodyBox':[180,130]}
            items.append(item);frames.append(frame);source_frames.append(raw);local_points.append(point_local)
            registrations.append({'frame':i,'sourceRect':rect,'sourceLandmarkGlobal':point,'sourceLandmarkLocal':point_local,'registrationOffset':offset,'targetLandmark':target,'bodyRoot':BODYROOT,'bbox':bbox,'marginsLTRB':margins,'pixelsRoundTrip':True})
        source_count=int(np.count_nonzero(alpha));assert sum(i['operation']['ownershipPixelCount'] for i in items)==source_count
        first=mains[0]['bbox'];rest=[first[2]-first[0],first[3]-first[1]]
        if action=='capture':
            swim=json.loads((OUT.parent/'swim/manifest.json').read_text(encoding='utf-8'));scale=swim['uniformDisplayScale'];scale_method='same species swim display scale reused, never capture per-frame bbox fit'
        else:scale=min(180/rest[0],130/rest[1],1);scale_method='one rest-frame solid anatomical silhouette scale reused for all8frames'
        for item in items:
            item.update({'uniformDisplayScale':scale,'displaySize':[CANVAS[0]*scale,CANVAS[1]*scale],'bodyDisplayBox':[180,130],'displaySizing':{'preserveAspect':True,'uniformScaleAcrossAction':True,'upscalingAllowed':False},'displayScaleReference':{'restNativeVisibleBox':rest,'fitMaxBox':[180,130],'method':scale_method,'upscaling':False}});write(ROOT/(item['file']+'.generation.json'),item)
        eye_sizes=[None if e['boundsLTRB'] is None else [e['boundsLTRB'][2]-e['boundsLTRB'][0],e['boundsLTRB'][3]-e['boundsLTRB'][1]] for e in eye_metrics]
        warnings=source_warnings+[{'id':'generated_core_shape_and_motion_pending_review','note':spec['observation']},{'id':'playback_unverified','note':'No live loop/single-shot playback during local heavy-job hold; distinct hashes are not motion evidence.'}]
        manifest={'schemaVersion':1,'source':rel(source),'sourceWidth':image.width,'sourceHeight':image.height,'sourceSha256':sha(source),'output':rel(OUT),'items':items,'animation':animation,'sharedCanvas':list(CANVAS),'rootPixels':BODYROOT,'landmarkPixels':target,'bodyRootEvidence':'One common logical body root relative to registered anatomical eye/bell crown; generated rigidity remains review.','registration':registrations,'eyeMeasurement':eye_metrics,'eyeNativeBoxSizes':eye_sizes,'sourcePixelOwnership':{'alphaThreshold':3,'sourcePixels':source_count,'exportedPixels':sum(i['operation']['ownershipPixelCount'] for i in items),'duplicatePixels':0,'lostPixels':0,'rgbAndAlphaForOwnedPixelsUnchanged':True},'order':list(range(8)),'warnings':warnings,'sourceMarginWarnings':[w for w in warnings if w['id']=='source_margin_lt_12pct'],'runtimeMarginWarnings':[w for w in warnings if w['id']=='registered_margin_lt_12pct'],'uniformDisplayScale':scale,'displaySize':[CANVAS[0]*scale,CANVAS[1]*scale],'bodyDisplayBox':[180,130],'qa':{'technicalAlpha':'true_rgba','sourceBorderStatus':'ownership_extracted_nominal_grid_crossings_retained_as_warnings','sourceTotalCanvasStatus':'unpassed' if status.endswith('boundary_pending_review') else 'main_anatomical_components_within_total_canvas','sourceMarginStatus':'fail_preserved_source_gate' if any(w['id']=='source_margin_lt_12pct' for w in warnings) else 'pass','registeredMarginStatus':'pass' if not any(w['id']=='registered_margin_lt_12pct' for w in warnings) else 'unpassed','identityStatus':'candidate_pending_root_visual','actualMotionStatus':'candidate_visible_articulation_pending_root_visual','registrationStatus':'integer_landmark_registered_core_shape_pending','loopPlaybackStatus':animation['loopVisualStatus']},'status':status}
        write(OUT/'manifest.json',manifest)
        make_contact(frames,folder,'registered'+version)
        make_contact(frames,folder,'landmarks'+version,[target]*8)
        review={'schemaVersion':1,'manifest':rel(OUT/'manifest.json'),'source':rel(source),'status':status,'sourceAndRegisteredLightDarkActuallyInspected':False,'actualVisualObservation':spec['observation'],'warnings':warnings,'sourceOwnership':manifest['sourcePixelOwnership'],'fps':fps,'durationsMs':durations,'loop':action=='swim','noResamplingOrUpscaling':True,'eyeNativeBoxSizes':eye_sizes,'testsBrowserAtlasUnityRun':False,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        write(folder/('candidate-review'+version+'.json'),review)
        print(json.dumps({'id':creature+'/'+action,'manifest':rel(OUT/'manifest.json'),'fps':fps,'frames':8,'status':status,'minMargin':min(i['registeredMinMargin'] for i in items),'eyeBoxSizes':eye_sizes,'physicalBoundaryWarnings':[w for w in warnings if w['id']=='source_total_canvas_boundary']},ensure_ascii=False))
