"""Owner01-12 lightweight crop, integer pupil registration and provenance. No resampling of game pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("--id",required=True);p.add_argument("--action",choices=["swim","capture"],required=True);p.add_argument("--canvas",type=int,default=0);p.add_argument("--reference");p.add_argument("--match-rest-density",action="store_true");p.add_argument("--density-ratio",type=float);p.add_argument("--density-evidence");p.add_argument("--eye-offset",type=int,nargs=2,default=[80,-12]);p.add_argument("--pupil-visual-confirmed",action="store_true");p.add_argument("--producer-note",required=True);a=p.parse_args()
if not a.pupil_visual_confirmed:raise ValueError("Actual ROI eye review required before registration")
source=Path(a.source).resolve();info=read(source.with_suffix(".ownership.json") if source.with_suffix(".ownership.json").exists() else source.with_suffix(".inspect.json"));im=Image.open(source).convert("RGBA")
if info["borderWarnings"]:raise ValueError("Border alpha >16; repair AI source rather than pad over clipping")
frames=[]
for f in info["frames"]:
 c=im.crop(f["sourceRect"]);c.putalpha(c.getchannel("A").point(lambda v:0 if v<=3 else v));frames.append(c)
ref=read(ROOT/a.reference) if a.reference else None
rest=frames[0].getchannel("A").getbbox();restSize=[rest[2]-rest[0],rest[3]-rest[1]]
scale=ref["uniformDisplayScale"] if ref else min(120/restSize[0],80/restSize[1]);density=None
if ref and a.match_rest_density:
 rb=ref["items"][0]["registeredAlphaBBox"];rs=[rb[2]-rb[0],rb[3]-rb[1]];ratios=[restSize[0]/rs[0],restSize[1]/rs[1]];ratio=(ratios[0]*ratios[1])**.5;scale/=ratio;baseOffset=a.eye_offset[:];a.eye_offset=[round(v*ratio) for v in a.eye_offset];density={"method":"one clip-level density estimate from matching entry/rest pose native visible width and height; never per-frame bbox fitting","referenceNativeRestBox":rs,"clipNativeRestBox":restSize,"axisRatios":ratios,"uniformDensityRatio":ratio,"referenceScale":ref["uniformDisplayScale"],"clipScale":scale,"referenceEyeOffset":baseOffset,"clipNativeEyeOffset":a.eye_offset,"reasonEyeOffsetAdjusted":"same displayed eye-to-body-root offset after clip density adjustment; nearest integer native registration","visualIdentityReview":"pending_root"}
elif ref and a.density_ratio:
 ratio=a.density_ratio;scale/=ratio;baseOffset=a.eye_offset[:];a.eye_offset=[round(v*ratio) for v in a.eye_offset];density={"method":"one clip display scale from measured native amber-iris median width; never per-frame scaling","evidence":a.density_evidence,"uniformDensityRatio":ratio,"referenceScale":ref["uniformDisplayScale"],"clipScale":scale,"referenceEyeOffset":baseOffset,"clipNativeEyeOffset":a.eye_offset,"visualIdentityReview":"pending_root"}
def fit(s):
 target=[s//2+a.eye_offset[0],s//2+a.eye_offset[1]]
 for f,c in zip(info["frames"],frames):
  b=c.getchannel("A").getbbox();o=[target[0]-f["pupil"][0],target[1]-f["pupil"][1]]
  m=[(b[0]+o[0])/s,(b[1]+o[1])/s,(s-b[2]-o[0])/s,(s-b[3]-o[1])/s]
  if min(m)<.12:return False
 return True
canvas=a.canvas or (ref["sharedCanvas"][0] if ref else 576)
if a.canvas and not fit(canvas):raise ValueError("Requested canvas insufficient")
while not fit(canvas):canvas+=32
target=[canvas//2+a.eye_offset[0],canvas//2+a.eye_offset[1]];root=[canvas//2,canvas//2]
if ref and canvas!=ref["sharedCanvas"][0]:raise ValueError(f"Need upgrade whole species shared canvas to {canvas} first")
out=ROOT/"assets/animations"/a.id/a.action;out.mkdir(parents=True,exist_ok=True)
items=[];checks=[]
for i,(f,c) in enumerate(zip(info["frames"],frames)):
 offset=[target[0]-f["pupil"][0],target[1]-f["pupil"][1]]
 result=Image.new("RGBA",(canvas,canvas),(0,0,0,0));result.paste(c,tuple(offset));b=c.getchannel("A").getbbox();dest=[b[0]+offset[0],b[1]+offset[1],b[2]+offset[0],b[3]+offset[1]]
 assert result.crop(dest).tobytes()==c.crop(b).tobytes(),"RGBA pixel loss"
 margin=min(dest[0]/canvas,dest[1]/canvas,(canvas-dest[2])/canvas,(canvas-dest[3])/canvas)
 fp=out/f"frame-{i:02d}.png";result.save(fp)
 record={"schemaVersion":1,"id":f"frame-{i:02d}","file":rel(fp),"sha256":sha(fp),"width":canvas,"height":canvas,"format":"RGBA PNG","nativeSource":rel(source),"derivedFrom":[{"file":rel(source),"sha256":info["sha256"],"generationRecord":rel(source)+".generation.json"}],"operation":{"type":"native_grid_crop_integer_pupil_registration","sourceRect":f["sourceRect"],"cellCropRect":[0,0,c.width,c.height],"registrationOffset":offset,"registeredCanvas":[canvas,canvas],"registrationReference":{"type":"black_pupil_component_centroid","sourcePointFloat":f["pupilFloat"],"sourcePointRounded":f["pupil"],"targetPoint":target,"method":f["pupilMethod"],"roiActuallyInspected":True},"resized":False,"upscaled":False,"alphaCleanup":"<=3 set0; all other RGBA pixels preserved","sourcePixelsRoundTripVerified":True},"anchor":[.5,.5],"rootPixels":root,"eyePixels":target,"displaySize":[canvas*scale,canvas*scale],"bodyDisplayBox":[120,80],"uniformDisplayScale":scale,"scaleReference":a.reference or "rest frame00 native visible box","registeredAlphaBBox":dest,"registeredMinMargin":margin,"status":"producer_candidate_pending_root_visual","actualModel":None,"actualQuality":None,"modelEvidence":"No model call for crop/translation. Source record preserves actual unknown builtin model/quality."}
 record["operation"].update({"nominalGridRect":f.get("nominalGridRect",f["sourceRect"]),"nominalGridBorderAlpha":f.get("nominalGridBorderAlpha",f["edgeAlphaMax"]),"ownershipType":f.get("ownershipType","nominal_grid"),"foreignFishAlphaPixels":f.get("foreignFishAlphaPixels",None),"allAssignedPixelsInsideRect":f.get("allAssignedPixelsInsideRect",None)});record["clipDensityAdjustment"]=density
 write(str(fp)+".generation.json",record);items.append(record);checks.append({"frame":i,"pupil":f["pupil"],"registeredPupil":target,"offset":offset,"minMargin":margin,"pixelRoundTrip":True})
animation={"frames":8,"fps":12,"loop":a.action=="swim","durationsMs":[83,84,83,83,84,83,83,84],"order":"row-major","root":[.5,.5],"rootPixels":root,"eyePixels":target,"sharedCanvas":[canvas,canvas],"phaseDegrees":[i*45 for i in range(8)] if a.action=="swim" else None,"poseMeaning":"8-phase swim cycle" if a.action=="swim" else "entry, startle, upward struggle, counter-flex, shorter struggle, fatigue, settling, subdued","identityStatus":"pending_root_visual","motionStatus":"pending_root_visual","registrationStatus":"producer_pupil_registered_pending_root_visual","playbackStatus":"pending_Unity","timingNote":"12FPS authoritative; integer durations cumulative-boundary rounded"}
manifest={"schemaVersion":1,"source":rel(source),"sourceWidth":im.width,"sourceHeight":im.height,"output":rel(out),"id":a.id,"action":a.action,"items":items,"sourceRects":[f["sourceRect"] for f in info["frames"]],"sharedCanvas":[canvas,canvas],"root":[.5,.5],"rootPixels":root,"eyePixels":target,"fps":12,"loop":a.action=="swim","durationsMs":animation["durationsMs"],"displaySize":[canvas*scale,canvas*scale],"bodyDisplayBox":[120,80],"uniformDisplayScale":scale,"displayScaleReference":a.reference or {"frame":0,"restVisibleBox":restSize,"actualRestDisplayBox":[x*scale for x in restSize]},"warnings":[],"runtimeMarginWarnings":[],"sourceMarginWarnings":[{"frame":f["frame"],"actual":f["minMargin"],"required":.12} for f in info["frames"] if f["minMargin"]<.12],"animation":animation,"status":"producer_candidate_pending_root_visual","complete":True,"qa":{"trueAlpha":True,"actualPupilROIReviewed":True,"registeredPixelRoundTrip":True,"minimumRuntimeMargin":min(i["registeredMinMargin"] for i in items),"sourceMarginStatus":"pass" if not info["sourceMarginWarnings"] else "fail_preserved","runtimeMarginStatus":"pass","producerVisualNote":a.producer_note,"rootVisualStatus":"pending","playbackStatus":"pending_Unity"}}
manifest["nominalGridBorderWarnings"]=info.get("nominalGridBorderWarnings",info["borderWarnings"]);manifest["ownershipWarnings"]=info.get("ownershipWarnings",[]);manifest["clipDensityAdjustment"]=density;manifest["bodyRootOffsetFromEye"]=[-a.eye_offset[0],-a.eye_offset[1]]
write(out/"manifest.json",manifest)
qaDir=ROOT/"tmp/art-qa";qaDir.mkdir(parents=True,exist_ok=True)
for name,bg in [("light",(242,237,219)),("dark",(16,28,42))]:
 sheet=Image.new("RGB",(1024,544),bg);d=ImageDraw.Draw(sheet)
 for i,item in enumerate(items):
  t=Image.open(ROOT/item["file"]).convert("RGBA");t.thumbnail((256,256),Image.Resampling.LANCZOS);x=i%4*256;y=i//4*272;sheet.paste(t,(x,y),t);d.text((x+4,y+256),f"frame-{i:02d}",fill=(35,70,50) if name=="light" else (225,230,240))
 sheet.save(qaDir/f"{a.id}-{a.action}-registered-{name}.png")
report={"source":rel(source),"sourceSHA256":info["sha256"],"action":a.action,"registeredAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sharedCanvas":[canvas,canvas],"rootPixels":root,"eyePixels":target,"registration":checks,"uniformScale":scale,"sourceMarginWarnings":manifest["sourceMarginWarnings"],"runtimeWarnings":[],"producerVisualNote":a.producer_note,"registeredContactVisual":"pending_actual_view","identityAndMotion":"pending_root_visual","playback":"pending_Unity","references":ref["source"] if ref else None}
write(source.parent/"action-review.json",report)
print(json.dumps({"id":a.id,"action":a.action,"canvas":canvas,"displaySize":manifest["displaySize"],"minRuntimeMargin":manifest["qa"]["minimumRuntimeMargin"],"sourceMarginWarnings":info["sourceMarginWarnings"],"manifest":rel(out/"manifest.json")}))

