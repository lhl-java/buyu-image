"""Register Qingqi swim to one shared pupil root, preserving all native RGBA pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[4]
DIR=Path(__file__).resolve().parent;OUT=ROOT/"assets/animations/01-qingqi/swim"
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(OUT/"manifest.json");src=Image.open(ROOT/m["source"]).convert("RGBA")
pupils=[[349,281],[347,281],[340,281],[332,281],[352,194],[350,196],[348,199],[337,196]]
floatCenters=[[348.868,280.664],[346.8586206896552,281.15862068965515],[340.00354609929076,281.1666666666667],[332.34432234432234,281.4908424908425],[351.59923664122135,193.64885496183206],[350.22222222222223,196.25185185185185],[348.07421875,199.05859375],[336.9850746268657,195.6902985074627]]
canvasSize=576;eye=[368,276];root=[288,288]
evidence=[];warnings=[]
for i,item in enumerate(m["items"]):
 rect=item["operation"]["sourceRect"];cell=src.crop(rect);a=cell.getchannel("A");cell.putalpha(a.point(lambda v:0 if v<=3 else v))
 offset=[eye[0]-pupils[i][0],eye[1]-pupils[i][1]]
 full=Image.new("RGBA",(canvasSize,canvasSize),(0,0,0,0)); full.paste(cell,tuple(offset))
 # Check full cell fits so not even alpha=1 pixels could be cropped; no mask-paste interpolation.
 b=cell.getchannel("A").getbbox()
 assert b[0]+offset[0]>=0 and b[1]+offset[1]>=0 and b[2]+offset[0]<=canvasSize and b[3]+offset[1]<=canvasSize
 # The entire source cell may extend beyond output in y, but only fully transparent pixels do.
 region=[b[0]+offset[0],b[1]+offset[1],b[2]+offset[0],b[3]+offset[1]]
 assert full.crop(region).tobytes()==cell.crop(b).tobytes()
 bbox=full.getchannel("A").point(lambda v:255 if v>3 else 0).getbbox()
 margins=[bbox[0]/canvasSize,bbox[1]/canvasSize,(canvasSize-bbox[2])/canvasSize,(canvasSize-bbox[3])/canvasSize]
 if min(margins)<.12:warnings.append({"frame":i,"id":"registered_margin_lt12pct","actual":min(margins)})
 p=ROOT/item["file"];full.save(p)
 item["sha256"]=sha(p);item["width"]=canvasSize;item["height"]=canvasSize
 item["operation"].update({"type":"native_grid_crop_integer_pupil_registration","sourceRect":rect,"cellCropRect":[0,0,cell.width,cell.height],"registrationOffset":offset,"registeredCanvas":[canvasSize,canvasSize],"registrationReference":{"type":"black_pupil_connected_component_centroid","sourcePointFloat":floatCenters[i],"sourcePointRounded":pupils[i],"targetPoint":eye,"rounding":"nearest integer","detection":"within manually inspected local eye ROI; largest RGB max<55 and alpha>220 component"},"resized":False,"upscaled":False,"sourcePixelsRoundTripVerified":True,"transparentOnlyClipping":True})
 item["anchor"]=[.5,.5];item["rootPixels"]=root;item["eyePixels"]=eye
 item["status"]="producer_candidate_pending_root_registered_review"
 item["registeredAlphaBBox"]=list(bbox);item["registeredMinMargin"]=min(margins)
 evidence.append({"frame":i,"sourcePupilFloat":floatCenters[i],"sourcePupilRounded":pupils[i],"registrationOffset":offset,"targetPupil":eye,"bodyRoot":root,"bbox":list(bbox),"marginsLTRB":margins,"pixelsRoundTrip":True})
# One rest frame determines display scale. Every frame uses this same scale.
rest=m["items"][0]["registeredAlphaBBox"];restSize=[rest[2]-rest[0],rest[3]-rest[1]]
scale=min(120/restSize[0],80/restSize[1])
for item in m["items"]:
 item["displaySize"]=[canvasSize*scale,canvasSize*scale]
 item["bodyDisplayBox"]=[120,80]
 item["uniformDisplayScale"]=scale
 item["displayScaleReference"]={"frame":0,"restNativeVisibleBox":restSize,"fitMaxBox":[120,80],"actualRestDisplayBox":[x*scale for x in restSize],"method":"one aspect-preserving scale from rest visible box; reused across every frame","upscaling":False}
 write(Path(str(ROOT/item["file"])+".generation.json"),item)
m.update({"sharedCanvas":[canvasSize,canvasSize],"root":[.5,.5],"rootPixels":root,"eyePixels":eye,"bodyRootOffsetFromEye":[-80,12],"registration":evidence,"displaySize":[canvasSize*scale,canvasSize*scale],"bodyDisplayBox":[120,80],"uniformDisplayScale":scale,"runtimeMarginWarnings":warnings,"status":"producer_candidate_pending_root_registered_review"})
m["animation"].update({"sharedCanvas":[canvasSize,canvasSize],"root":[.5,.5],"rootPixels":root,"eyePixels":eye,"registrationStatus":"producer_registered_pupil_integer_translation_root_review_pending","identityStatus":"root_source_pose_coherence_candidate_pass","motionStatus":"root_source_pose_coherence_candidate_pass","loopVisualStatus":"pending_Unity_playback"})
m["qa"].update({"registeredMarginStatus":"pass" if not warnings else "fail","identityStatus":"root_source_pose_coherence_candidate_pass","actualMotionStatus":"root_source_pose_coherence_candidate_pass","registrationStatus":"producer_registered_pending_root_visual","loopPlaybackStatus":"pending_Unity_playback","sourceMarginStatus":"fail_preserved_historical_source_gate"})
write(OUT/"manifest.json",m)
report={"schemaVersion":1,"registeredAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source":m["source"],"sourceSHA256":sha(ROOT/m["source"]),"nativeGridFrame":[444,444],"sharedCanvas":[canvasSize,canvasSize],"whyNot512":"512 could not meet12percent left margin. Intermediate544 was uniformly expanded to576 for both swim and capture so the capture extreme pose also fits. No native scale change.","pupilEvidence":evidence,"runtimeWarnings":warnings,"sourceMarginWarnings":m["sourceMarginWarnings"],"pixelPreservation":"All nonzero source sprite RGBA crop bytes round-trip equal after only alpha<=3 cleanup and integer placement. No interpolation or scaling.","displaySize":m["displaySize"],"bodyDisplayBox":[120,80],"restNativeVisibleBox":restSize,"uniformDisplayScale":scale,"poseCoherence":"root inspected native and light8-frame sample; candidate pass","producerVisual":"pending actual registered contact-sheet review","playback":"pending_Unity"}
write(DIR/"01-qingqi-swim.registration.json",report)
qaDir=ROOT/"tmp/art-qa"
for name,bg in [("light",(242,237,219)),("dark",(16,28,42))]:
 out=Image.new("RGB",(1024,544),bg);draw=ImageDraw.Draw(out)
 for i,item in enumerate(m["items"]):
  im=Image.open(ROOT/item["file"]).convert("RGBA");im.thumbnail((256,256),Image.Resampling.LANCZOS);x=i%4*256;y=i//4*272
  out.paste(im,(x,y),im);draw.text((x+4,y+256),f"frame-{i:02d}",fill=(30,70,55) if name=="light" else (225,230,240))
 out.save(qaDir/f"01-qingqi-swim-registered-{name}.png")
print(json.dumps({"canvas":[canvasSize,canvasSize],"eye":eye,"root":root,"runtimeWarnings":warnings,"minMargin":min(x["registeredMinMargin"] for x in m["items"]),"uniformScale":scale,"displaySize":m["displaySize"],"restVisibleDisplayBox":[x*scale for x in restSize]}))

