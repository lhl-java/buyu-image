"""One species at a time: lightweight source evidence and registration planning."""
from pathlib import Path
from PIL import Image
import argparse,subprocess,sys,json
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("id");a=p.parse_args();selection=json.loads((HERE/"FISH01TO12_SELECTION.json").read_text(encoding="utf-8"));sp=next(x for x in selection["species"] if x["id"]==a.id)
infos={}
for action,relative in sp["source"].items():
 src=ROOT/relative;ins=src.with_suffix(".inspect.json")
 if not ins.exists():subprocess.run([sys.executable,str(HERE/"Inspect-Fish01to12.py"),str(src)],check=True,capture_output=True,text=True)
 subprocess.run([sys.executable,str(HERE/"Ownership-Fish01to12.py"),str(src)],check=True,capture_output=True,text=True)
 infos[action]=json.loads(src.with_suffix(".ownership.json").read_text(encoding="utf-8"))
canvas=576;ox,oy=sp["eyeOffset"]
def fit(size):
 target=[size//2+ox,size//2+oy]
 for action,j in infos.items():
  if j["ownershipWarnings"]:return False
  im=Image.open(ROOT/sp["source"][action]).convert("RGBA")
  for f in j["frames"]:
   c=im.crop(f["sourceRect"]);b=c.getchannel("A").point(lambda v:255 if v>3 else 0).getbbox();dx=target[0]-f["pupil"][0];dy=target[1]-f["pupil"][1]
   if min((b[0]+dx)/size,(b[1]+dy)/size,(size-b[2]-dx)/size,(size-b[3]-dy)/size)<.12:return False
 return True
warn={k:v["ownershipWarnings"] for k,v in infos.items() if v["ownershipWarnings"]}
if not warn:
 while not fit(canvas):
  canvas+=32
  if canvas>1536:raise ValueError("Registration canvas unreasonable; inspect ownership")
else:canvas=None
eyes=Image.new("RGB",(640,640),(240,235,220))
for i,action in enumerate(["swim","capture"]):
 pth=ROOT/sp["source"][action];eye=Image.open(pth.with_name(pth.stem+"-eye-roi.png")).convert("RGB");eyes.paste(eye,(0,i*320))
eyePath=HERE/a.id/"source-eye-review.png";eyes.save(eyePath)
plan={"id":a.id,"source":sp["source"],"canvas":canvas,"eyeOffset":sp["eyeOffset"],"eyeTarget":[canvas//2+ox,canvas//2+oy] if canvas else None,"root":[canvas//2,canvas//2] if canvas else None,"ownershipWarnings":warn,"nominalGridWarnings":{k:v["nominalGridBorderWarnings"] for k,v in infos.items()},"sourceGridMarginWarnings":{k:v["sourceMarginWarnings"] for k,v in infos.items()},"actualPupilVisual":"pending","eyeReviewImage":eyePath.relative_to(ROOT).as_posix(),"notes":sp["producerNote"]}
(HERE/a.id/"species-review-plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(plan))

