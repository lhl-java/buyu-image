"""Lossless native ownership crop and sole registration for root-owned Daochild sources."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1];TMP=ROOT/"tmp/dao-child-export"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument("action",choices=["point","celebrate"]);p.add_argument("--source-visual-reviewed",action="store_true");a=p.parse_args()
if not a.source_visual_reviewed:raise ValueError("Actual source view required")
inspection=read(TMP/(a.action+"-source-inspection.json"))
if inspection["scaleContinuity"]!="candidate_pass":raise ValueError("Within-clip source density mismatch; root must repair source, not per-sheet/per-frame fit")
if any(j["ownershipWarnings"] for j in inspection["parts"]):raise ValueError("Unresolved source ownership")
out=ROOT/f"assets/animations/dao-child/{a.action}";out.mkdir(parents=True,exist_ok=True);canvas=[1000,1000];target=[500,850];anchor=[.5,.85]
restHeight=inspection["parts"][0]["frames"][0]["nativeBodyHeightIgnoringRaisedArms"];scale=280/restHeight;items=[];warnings=[]
for part in inspection["parts"]:
 src=ROOT/part["source"]
 if sha(src)!=part["sha256"]:raise ValueError("Source changed after inspection")
 im=Image.open(src).convert("RGBA")
 for f in part["frames"]:
  index=len(items);rect=f["ownershipRect"];cell=im.crop(rect);cell.putalpha(cell.getchannel("A").point(lambda v:0 if v<=3 else v));sourceRoot=f["rootLocal"];offset=[target[0]-sourceRoot[0],target[1]-sourceRoot[1]];result=Image.new("RGBA",tuple(canvas),(0,0,0,0));result.paste(cell,tuple(offset));b=cell.getchannel("A").getbbox();dest=[b[0]+offset[0],b[1]+offset[1],b[2]+offset[0],b[3]+offset[1]]
  assert min(dest)>=0 and dest[2]<=canvas[0] and dest[3]<=canvas[1]
  assert result.crop(dest).tobytes()==cell.crop(b).tobytes(),"Native RGBA loss"
  margins=[dest[0]/canvas[0],dest[1]/canvas[1],(canvas[0]-dest[2])/canvas[0],(canvas[1]-dest[3])/canvas[1]]
  if min(margins)<.12:raise ValueError("Registered margin below12%")
  path=out/f"frame-{index:02d}.png"
  if path.exists():
   old=read(str(path)+".generation.json")
   if old.get("animation",{}).get("id")!="dao-child/"+a.action:raise ValueError("Unrelated output collision")
  result.save(path);soles=[[s[0]-rect[0]+offset[0],s[1]-rect[1]+offset[1]] for s in f["sourceSolesGlobal"]]
  info={"schemaVersion":1,"id":f"frame-{index:02d}","file":rel(path),"sha256":sha(path),"width":1000,"height":1000,"format":"RGBA PNG","nativeSource":part["source"],"derivedFrom":[{"file":part["source"],"sha256":part["sha256"],"generationRecord":part["source"]+".generation.json"}],"operation":{"type":"native_complete_pose_ownership_crop_integer_sole_registration_transparent_padding","sourceRect":rect,"nominalGridRect":f["nominalGridRect"],"nominalGridEdgeMaxAlpha":f["nominalGridEdgeMaxAlpha"],"foreignPoseAlphaPixels":0,"allOwnedPixelsRetained":True,"registrationOffset":offset,"registrationReference":{"type":"midpoint_of_two_sole_contacts_and_lowest_solid_sole","sourceRootGlobal":f["rootGlobal"],"sourceRootLocal":sourceRoot,"sourceSolesGlobal":f["sourceSolesGlobal"],"targetRootPixels":target,"method":"Manually inspected green/ivory/gold shoe ROIs; current pose alpha>200 lowest row and x centroid of bottom5rows. Same method as idle."},"registeredCanvas":canvas,"alphaCleanup":"Values<=3 set0; all other RGBA pixels preserved","resized":False,"upscaled":False,"warped":False,"sourcePixelsRoundTripVerified":True},"anchor":anchor,"unityPivotNormalizedBottomLeft":[.5,.15],"displaySize":[1000*scale,1000*scale],"uniformDisplayScale":scale,"bodyDisplayHeight":280,"scaleReference":{"frame":0,"nativeVisibleBodyHeightIgnoringRaisedArms":restHeight,"targetVisibleBodyHeight":280,"method":"one whole-clip display scale from entry body/head; every frame reuses, no per-frame bbox scaling"},"registeredSoles":soles,"registeredRoot":target,"qa":{"registeredAlphaBBox":dest,"registeredMarginsLTRB":margins,"runtimeMinMargin":min(margins),"sourceGridWarningPreserved":f["nominalGridEdgeMaxAlpha"]>16,"sourceNativeBodyHeight":f["nativeBodyHeightIgnoringRaisedArms"],"sourceNativeSoleSpan":f["footPairSpan"],"sourceCanvasTouched":False,"motionAndTiming":"pending_root_and_Unity"},"animation":{"id":"dao-child/"+a.action,"frames":8,"fps":10,"loop":False,"order":"A row-major4 then B row-major4","frameIndex":index,"durationMs":100},"status":"producer_candidate_pending_root_visual_and_Unity","actualModel":None,"actualQuality":None,"modelEvidence":"No AI generation in this export. Actual source records retained by root."}
  write(str(path)+".generation.json",info);items.append(info)
m={"schemaVersion":1,"id":"dao-child/"+a.action,"source":[j["source"] for j in inspection["parts"]],"output":rel(out),"items":items,"frames":8,"fps":10,"loop":False,"durationsMs":[100]*8,"durationMs":800,"sharedCanvas":canvas,"root":anchor,"rootPixels":target,"unityPivotNormalizedBottomLeft":[.5,.15],"displaySize":[1000*scale,1000*scale],"bodyDisplayHeight":280,"uniformDisplayScale":scale,"sourceRects":[x["operation"]["sourceRect"] for x in items],"warnings":[],"nominalGridWarnings":[x["id"] for x in items if x["qa"]["sourceGridWarningPreserved"]],"qa":{"sourceDensityCandidate":inspection["ratiosBtoA"],"oneClipScale":True,"actualSourceStillsViewed":True,"actualRegisteredLightDarkView":"pending","minimumRuntimeMargin":min(x["qa"]["runtimeMinMargin"] for x in items),"allNativePixelRoundTripsPassed":True,"sourceOwnershipForeignPixels":0,"noNativeResizeUpscaleWarp":True,"rootVisual":"pending","UnityPlayback":"pending"},"animation":{"id":"dao-child/"+a.action,"frameCount":8,"fps":10,"loop":False,"frameDurationsMs":[100]*8,"root":target,"canvas":canvas,"geometricRegistrationOnly":True,"releaseReady":False,"playbackStatus":"pending_Unity"},"status":"producer_candidate_pending_root_visual_and_Unity","scope":"Only lossless extraction/registration/export. Root owns source AI generation; idle untouched."}
m["complete"]=len(items)==8
write(out/"manifest.json",m)
for name,bg in [("light",(242,237,219)),("dark",(16,28,42))]:
 sheet=Image.new("RGB",(1024,544),bg);d=ImageDraw.Draw(sheet)
 for i,item in enumerate(items):
  im=Image.open(ROOT/item["file"]).convert("RGBA");im.thumbnail((256,256),Image.Resampling.LANCZOS);x=i%4*256;y=i//4*272;sheet.paste(im,(x,y),im);d.text((x+5,y+256),item["id"],fill=(35,70,50) if name=="light" else (225,230,240))
 sheet.save(TMP/(a.action+"-registered-"+name+".png"))
combined=Image.new("RGB",(1024,1088),(240,235,220))
for i,name in enumerate(["light","dark"]):combined.paste(Image.open(TMP/(a.action+"-registered-"+name+".png")),(0,i*544))
combined.save(TMP/(a.action+"-registered-review.png"))
# Same displayed height as adopted idle. QA only, exported PNGs are not resized.
comparison=Image.new("RGB",(880,500),(242,237,219));d=ImageDraw.Draw(comparison)
idle=read(ROOT/"assets/animations/dao-child/idle/manifest.json");idleItem=idle["items"][0];idleH=idleItem["qa"]["nativeBodyHeight"]
for index,(labelName,path,s,root) in enumerate([("idle280",ROOT/idleItem["file"],280/idleH,idleItem["anchor"]),(a.action+"280",ROOT/items[0]["file"],scale,anchor)]):
 im=Image.open(path).convert("RGBA");size=[round(im.width*s),round(im.height*s)];im=im.resize(tuple(size),Image.Resampling.LANCZOS);x=220+440*index-round(size[0]*root[0]);y=400-round(size[1]*root[1]);comparison.paste(im,(x,y),im);d.text((10+440*index,10),labelName,fill=(30,65,45));d.line((440*index,400,440*(index+1),400),fill=(175,105,75))
comparison.save(TMP/(a.action+"-idle-display-qa.png"))
report={"action":a.action,"sources":inspection["summary"],"sourceDensity":inspection["ratiosBtoA"],"exportedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"manifest":rel(out/"manifest.json"),"frames":8,"fps":10,"loop":False,"canvas":canvas,"rootPixels":target,"displayScale":scale,"restVisibleBodyHeight":restHeight,"bodyDisplayHeight":280,"runtimeMinMargin":m["qa"]["minimumRuntimeMargin"],"nativePixelRoundTrip":True,"registeredVisual":"pending_actual_view","rootVisual":"pending","Unity":"pending","sourceAIGeneration":"root-owned; not invoked by exporter"}
write(TMP/(a.action+"-export-report.json"),report)
print(json.dumps({"action":a.action,"frames":8,"canvas":canvas,"root":target,"scale":scale,"displaySize":m["displaySize"],"runtimeMinMargin":m["qa"]["minimumRuntimeMargin"],"sourceDensity":inspection["ratiosBtoA"],"manifest":rel(out/"manifest.json")}))

