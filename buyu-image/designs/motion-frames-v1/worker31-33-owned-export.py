"""Export root's existing 31-33 native ownership poses. No generation, rescale or source edits."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
character,action=sys.argv[1:3]
d=ROOT/"designs/motion-frames-v1"/character/action
expath=d/"extract-v1.json"; qapath=d/"source-v1-qa.json"
ex=json.loads(expath.read_text(encoding="utf-8-sig"));qa=json.loads(qapath.read_text(encoding="utf-8-sig"))
out=ROOT/"assets/animations"/character/action;out.mkdir(parents=True,exist_ok=True)
CANVAS=(800,800); TARGET=(560,400); fps=12
names={"31-bingjing":"冰晶鲨","32-honglian":"红莲鳐","33-xuanwu":"玄武灵龟"}
closed={"31-bingjing":[3,4],"32-honglian":[4],"33-xuanwu":[4]}[character] if action=="capture" else []
notes={
"31-bingjing":"Actual source alpha ownership contact viewed: crystal tail/fin articulation and capture recoil/tuck. Source head/eye appearance and recovery need playback; capture03/04 are closed eyes so candidate0 is eyelid landmark, not pupil.",
"32-honglian":"Actual source alpha ownership contact viewed: mantle wing flex and tail curl, capture fin tuck. Swim03 outer canvas edge alpha5 only; alpha>16 outline complete, weak fringe retained and warning preserved. Capture04 closed eyelid is registration proxy.",
"33-xuanwu":"Actual source alpha ownership contact viewed: four flippers alternate and capture limbs/head tuck. Source33swim ownership masks exclude foreign adjacent actor pixels within bounds, preserving owned RGBA. Capture03/04 head retracts/appears smaller and04 closes eyes: root visual review required, no per-frame normalization."}
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def b16(im):return im.getchannel("A").point(lambda v:255 if v>16 else 0).getbbox()
if sha(ROOT/ex["source"])!=ex["sha256"]:raise ValueError("Root extraction source changed")
items=[]
for i,owned in enumerate(ex["frames"]):
 posepath=ROOT/owned["file"];pose=Image.open(posepath).convert("RGBA")
 q=qa["frames"][i]; landmark=q["pupilCandidates"][0]
 nominal=q["sourceRect"];sr=owned["sourceRect"]
 absolute=[nominal[0]+landmark["center"][0],nominal[1]+landmark["center"][1]]
 local=[absolute[0]-sr[0],absolute[1]-sr[1]]
 point=[round(v) for v in local]
 offset=[TARGET[0]-point[0],TARGET[1]-point[1]]
 if min(offset)<0 or offset[0]+pose.width>800 or offset[1]+pose.height>800:raise ValueError("Native ownership crop does not fit unscaled")
 frame=Image.new("RGBA",CANVAS,(0,0,0,0));frame.paste(pose,offset)
 if frame.crop([offset[0],offset[1],offset[0]+pose.width,offset[1]+pose.height]).tobytes()!=pose.tobytes():raise ValueError("Native crop pixels changed")
 box=b16(frame);m=[box[0]/800,box[1]/800,(800-box[2])/800,(800-box[3])/800]
 if min(m)<.12:raise ValueError("Need larger shared transparent canvas")
 file=out/f"frame-{i:02d}.png"
 if file.exists():raise FileExistsError(file)
 frame.save(file)
 rawbox=b16(pose);duration=round((i+1)*1000/fps)-round(i*1000/fps)
 item={"schemaVersion":1,"id":f"frame-{i:02d}","name":names[character]+f" {action} {i}","file":rel(file),"sha256":sha(file),"width":800,"height":800,"format":"RGBA PNG",
 "nativeSource":ex["source"],"derivedFrom":[{"file":owned["file"],"sha256":sha(posepath),"generationRecord":owned["file"]+".generation.json"},{"file":ex["source"],"sha256":ex["sha256"],"generationRecord":ex["source"]+".generation.json"}],
 "operation":{"type":"native_ownership_crop_integer_eye_landmark_registration_and_transparent_padding","sourceRect":sr,"nominalGridRect":owned["nominalSourceRect"],"nominalGridCross":owned["nominalGridCross"],
  "ownershipEvidence":{"report":rel(expath),"sourceMainAlphaComponent":owned["sourceMainAlphaComponent"],"ownedPixelCount":owned["ownedPixelCount"],"foreignPixelsRemovedFromCrop":owned["foreignPixelsRemovedFromCrop"],"nativeOwnedPixelsUnchanged":owned["nativeOwnedPixelsUnchanged"]},
  "registrationOffset":offset,"registeredCanvas":[800,800],"registrationReference":{"type":"closed_eyelid_centroid_proxy" if i in closed else "dark_eye_component_centroid_candidate","qaReport":rel(qapath),"qaReportSha256":sha(qapath),"candidateIndex":0,"sourceGlobalPointFloat":absolute,"poseLocalPointFloat":local,"poseLocalPointRounded":point,"targetPoint":list(TARGET),"warning":"QA candidate fragment/eyelid is an approximate visual landmark, not an exact anatomical pupil."},
  "alphaCleanup":"Inherit root ownership extraction: alpha<=3 discarded; every owned RGBA above3 preserved. No extra alpha cleanup.","resized":False,"upscaled":False,"poseWarped":False,"sourcePixelsRoundTripVerified":True},
 "anchor":[.7,.5],"status":"candidate_pending_root_visual_and_playback_review","actualModel":None,"actualQuality":None,"modelEvidence":"See original source generation record; this export is not a generation call.",
 "animation":{"id":character+"/"+action,"frames":8,"fps":fps,"loop":action=="swim","order":"root ownership row-major","root":[.7,.5],"phase":i/8,"durationMs":duration,"targetBodyBox":[240,180]},
 "qa":{"nativeBodyBoxAlpha16":rawbox,"nativeVisibleSize":[rawbox[2]-rawbox[0],rawbox[3]-rawbox[1]],"ownedPoseSize":[pose.width,pose.height],"rawTotalCanvasEdgeMaxAlpha":owned["totalCanvasEdgeMaxAlpha"],"rawWeakAlphaBoundaryWarning":owned["totalCanvasEdgeMaxAlpha"]>3,"registeredBoxAlpha16":box,"registeredMarginsFraction":m,"finalMargin12PercentPassed":True,
   "pupilComponent":{"area":landmark["area"],"bbox":landmark["bbox"],"centroid":landmark["center"],"isClosedEyelidProxy":i in closed},"actualSourceAlphaContactViewedByProducer":True,"motionAccepted":False,"loopOrRecoveryAccepted":False,"targetClientAccepted":False}
 }
 write(Path(str(file)+".generation.json"),item);items.append(item)
manifest={"schemaVersion":1,"source":ex["source"],"sourceWidth":ex["size"][0],"sourceHeight":ex["size"][1],"output":rel(out),"status":"candidate_pending_root_visual_and_playback_review","items":items,
 "animation":{"id":character+"/"+action,"frameCount":8,"fps":fps,"loop":action=="swim","canvas":[800,800],"pupilRegistrationTarget":list(TARGET),"root":[.7,.5],"durationMs":round(8*1000/fps),"durationsMs":[i["animation"]["durationMs"] for i in items],
  "closedEyeFrameIndices":closed,"densityCalibrationExcludeFrames":closed,"sourceScale":"Uniform native pixels; no per-frame bbox fit.","visualReview":notes[character],"pending":["Actual registered loop/recovery and head/limb identity review.","Black eye component/closed eyelid is only a candidate landmark; registration requires root playback.","Unity runtime acceptance not performed."],"releaseReady":False},
 "notes":["All source ownership pixels copied without resampling or warping. Integer translations remove layout offsets, not create articulation.","Static count, ownership assertions and preview do not establish animation pass.","Cross-clip uniform display density is candidate until root review."]}
write(out/"manifest.json",manifest)
# One actual alpha preview per clip, first or capture peak. Native, opaque RGB QA only, no atlas.
selected=4 if action=="capture" else 0
im=Image.open(out/f"frame-{selected:02d}.png").convert("RGBA")
preview=Image.new("RGB",(1600,800))
for j,col in enumerate([(244,240,224,255),(12,45,39,255)]):
 bg=Image.new("RGBA",CANVAS,col);bg.alpha_composite(im);preview.paste(bg.convert("RGB"),(j*800,0))
previewpath=d/"registered-alpha-review.png";preview.save(previewpath)
print(json.dumps({"id":character+"/"+action,"frames":8,"nativeVisibleSizes":[i["qa"]["nativeVisibleSize"] for i in items],"sourceEdges":[i["qa"]["rawTotalCanvasEdgeMaxAlpha"] for i in items],"closedEyeProxyFrames":closed,"alphaPreview":rel(previewpath),"status":manifest["status"]}))
