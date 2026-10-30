"""Refine only27/31 eye anchors using bounded iris components; preserve all native visible RGBA."""
from pathlib import Path
from PIL import Image
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for ch in ["27-yingguang","31-bingjing"]:
 for act in ["swim","capture"]:
  folder=ROOT/"assets/animations"/ch/act;p=folder/"manifest.json";m=json.loads(p.read_text(encoding="utf-8"))
  T=m["animation"]["pupilRegistrationTarget"];closed=m["animation"].get("closedEyeFrameIndices",[])
  report=[]
  for index,i in enumerate(m["items"]):
   if index in closed:continue
   path=ROOT/i["file"];im=Image.open(path).convert("RGBA")
   x0,y0,x1,y1=T[0]-35,T[1]-35,T[0]+36,T[1]+36
   mask={(x,y) for y in range(y0,y1) for x in range(x0,x1) if max(im.getpixel((x,y))[:3])<170 and im.getpixel((x,y))[3]>220};comps=[]
   while mask:
    todo=[mask.pop()];pts=[]
    while todo:
     q=todo.pop();pts.append(q);x,y=q
     for n in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
      if n in mask:mask.remove(n);todo.append(n)
    xs=[v[0]for v in pts];ys=[v[1]for v in pts];b=[min(xs),min(ys),max(xs)+1,max(ys)+1];c=[sum(xs)/len(xs),sum(ys)/len(ys)]
    if len(pts)>=30 and b[0]>x0 and b[1]>y0 and b[2]<x1 and b[3]<y1:comps.append({"area":len(pts),"bbox":b,"centroid":c})
   comps.sort(key=lambda v:math.dist(v["centroid"],T))
   eye=comps[0];d=[T[0]-round(eye["centroid"][0]),T[1]-round(eye["centroid"][1])]
   if max(abs(v)for v in d)>12:raise ValueError("Eye refinement exceeds light registration allowance")
   refined=Image.new("RGBA",im.size,(0,0,0,0));refined.paste(im,tuple(d))
   # Compare the exact visible RGBA sequence at shifted coordinates, including every source alpha>3 pixel.
   original=[(x,y,im.getpixel((x,y)))for y in range(im.height)for x in range(im.width)if im.getpixel((x,y))[3]>3]
   if any(not(0<=x+d[0]<im.width and 0<=y+d[1]<im.height)or refined.getpixel((x+d[0],y+d[1]))!=v for x,y,v in original):raise ValueError("Visible native pixel lost or modified")
   refined.save(path);i["sha256"]=sha(path)
   op=i["operation"];oldoffset=op["registrationOffset"];newOffset=[oldoffset[0]+d[0],oldoffset[1]+d[1]];op["registrationOffset"]=newOffset
   ref=op["registrationReference"];ref["priorCandidateLocator"]=dict(ref);ref["type"]="bounded_dark_iris_component_centroid_candidate";ref["poseOrCellLocalPointFloat"]=[eye["centroid"][0]-oldoffset[0],eye["centroid"][1]-oldoffset[1]];ref["poseOrCellLocalPointRounded"]=[T[0]-newOffset[0],T[1]-newOffset[1]]
   ref["refinement"]={"relativeIntegerShift":d,"criterion":"RGB max<170,alpha>220; bounded component inside71px inspected eye ROI, nearest prior eye target","nativeVisibleRGBAUnchanged":True}
   i["qa"]["densityEyeComponent"]=dict(eye,type="bounded_dark_iris_interior",isAnatomicalOuterEyeDiameter=False)
   box=refined.getchannel("A").point(lambda a:255 if a>16 else 0).getbbox();w,h=im.size
   i["qa"]["registeredBoxAlpha16"]=box;i["qa"]["registeredMarginsFraction"]=[box[0]/w,box[1]/h,(w-box[2])/w,(h-box[3])/h]
   if min(i["qa"]["registeredMarginsFraction"])<.12:raise ValueError("Refined margin under12percent")
   write(Path(str(path)+".generation.json"),i);report.append({"frame":index,"shift":d,"boundedIrisBox":eye["bbox"],"width":eye["bbox"][2]-eye["bbox"][0]})
  m["animation"]["densityReferenceFrame"]=0
  m["animation"]["densityFeature"]="first_open_rest_bounded_dark_iris_interior"
  m["animation"]["pending"].append("Eye iris component is a validated visual locator candidate, not a final anatomy/playback pass; closed frames retain eyelid proxy.")
  write(p,m)
  write(ROOT/"designs/motion-frames-v1"/ch/act/"eye-registration-refinement.json",{"id":ch+"/"+act,"status":"candidate_pending_root_visual_and_playback_review","entries":report,"noGeneration":True,"noScale":True,"sourcePixelsUnchanged":True})
  print(json.dumps({"id":ch+"/"+act,"refinements":report}))
