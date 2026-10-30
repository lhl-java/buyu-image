"""Lightweight native sample inspection; generates QA only, never animation pixels."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[4]
DIR=Path(__file__).resolve().parent
OUT=ROOT/"assets/animations/01-qingqi/swim"
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(OUT/"manifest.json"); spec=read(DIR/"01-qingqi-swim.slice.json")
source=Image.open(ROOT/m["source"]).convert("RGBA")
qa=[]; warnings=[]
for i,item in enumerate(m["items"]):
 p=ROOT/item["file"]; im=Image.open(p).convert("RGBA"); a=im.getchannel("A"); b=a.point(lambda x:255 if x>3 else 0).getbbox()
 margins=[b[0]/im.width,b[1]/im.height,(im.width-b[2])/im.width,(im.height-b[3])/im.height]
 edge=max(a.crop((0,0,im.width,1)).getextrema()[1],a.crop((0,im.height-1,im.width,im.height)).getextrema()[1],a.crop((0,0,1,im.height)).getextrema()[1],a.crop((im.width-1,0,im.width,im.height)).getextrema()[1])
 rec={"id":item["id"],"sourceRect":item["operation"]["sourceRect"],"canvas":[im.width,im.height],"bodyBBoxAlphaGt3":list(b),"marginsLTRB":margins,"minMargin":min(margins),"edgeAlphaMax":edge,"sha256":sha(p)}
 qa.append(rec)
 if min(margins)<.12: warnings.append({"id":"source_margin_lt_12pct","frame":i,"actual":min(margins),"required":.12})
 item.pop("displaySize",None)
 item["targetBodyBox"]=[120,80]
 item["displaySizing"]={"preserveAspect":True,"uniformScaleAcrossAction":True,"upscalingAllowed":False,"status":"pending_root_selection"}
 item["status"]="candidate_pending_root_visual_and_registration"
 write(Path(str(p)+".generation.json"),item)
m["sharedCanvas"]=[444,444];m["root"]=[.5,.5];m["fps"]=12;m["loop"]=True;m["durationsMs"]=spec["animation"]["durationsMs"];m["animation"]=spec["animation"];m["sourceRects"]=[x["sourceRect"] for x in qa]
m["sourceMarginWarnings"]=warnings
m["qa"]={"technicalAlpha":"true_rgba","borderStatus":"pass" if not m["warnings"] else "fail","sourceMarginStatus":"pass" if not warnings else "fail","identityStatus":"pending_root_visual","actualMotionStatus":"pending_root_visual","registrationStatus":"pending_root_registration","loopPlaybackStatus":"not_yet_inspected_in_playback"}
m["status"]="candidate_pending_root_visual_and_registration"
write(OUT/"manifest.json",m)
report={"schemaVersion":1,"inspectedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source":m["source"],"sourceSHA256":sha(ROOT/m["source"]),"nativeSourceSize":list(source.size),"sourceAlphaExtrema":list(source.getchannel("A").getextrema()),"grid":[4,2],"sharedCanvas":[444,444],"padding":"Only right/bottom 0-1px per native grid cell to shared ceil canvas; no scaling.","frames":qa,"borderWarnings":m["warnings"],"sourceMarginWarnings":warnings,"noUpscaling":True,"uniqueFrameHashes":len({x["sha256"] for x in qa}),"uniquenessIsNotMotionEvidence":True,"actualMotionStatus":"pending_root_visual","rootRegistration":"Grid root is metadata only; generated head/torso landmarks not registered. Top/bottom row vertical drift must be inspected and corrected by root before animation acceptance.","playback":"Not yet reviewed; static QA cannot certify loop."}
write(DIR/"01-qingqi-swim.visual-qa.json",report)
# Contact sheet shows each full fixed canvas at uniform scale; no per-frame bbox normalization.
qaDir=ROOT/"tmp/art-qa";qaDir.mkdir(parents=True,exist_ok=True)
for label,bg in [("light",(242,237,219)),("dark",(16,28,42))]:
 canvas=Image.new("RGB",(1024,544),bg);draw=ImageDraw.Draw(canvas)
 for i,item in enumerate(m["items"]):
  im=Image.open(ROOT/item["file"]).convert("RGBA");im.thumbnail((256,256),Image.Resampling.LANCZOS)
  x=(i%4)*256;y=(i//4)*272
  canvas.paste(im,(x,y),im)
  draw.text((x+6,y+255),f"frame-{i:02d} / {i*45} deg",fill=(45,70,60) if label=="light" else (225,233,240))
 canvas.save(qaDir/f"01-qingqi-swim-{label}.png")
print(json.dumps({"source":m["source"],"borderWarnings":m["warnings"],"marginWarnings":warnings,"minMargin":min(x["minMargin"] for x in qa),"canvas":m["sharedCanvas"],"light":"tmp/art-qa/01-qingqi-swim-light.png","dark":"tmp/art-qa/01-qingqi-swim-dark.png"}))

