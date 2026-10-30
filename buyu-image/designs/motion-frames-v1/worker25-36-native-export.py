"""Worker25-36 lightweight native PNG registration. Not a test suite or renderer."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys,math
ROOT=Path(__file__).resolve().parents[2]
spec_path=ROOT/sys.argv[1]
s=json.loads(spec_path.read_text(encoding="utf-8-sig"))
source=ROOT/s["source"]; im=Image.open(source).convert("RGBA")
rows,cols=s["grid"]; w,h=im.size
cw,ch=s["canvas"]; target=s["pupilTarget"]; fps=s["fps"]
out=ROOT/s["output"]; out.mkdir(parents=True,exist_ok=True)
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def box16(p):return p.getchannel("A").point(lambda v:255 if v>16 else 0).getbbox()
def edge(a):
 x,y=a.size
 return max(a.crop(b).getextrema()[1] for b in [(0,0,x,1),(0,y-1,x,y),(0,0,1,y),(x-1,0,x,y)])
def pupil(cell,roi,expected):
 x0,y0,x1,y1=roi
 mask={(x,y) for y in range(y0,y1) for x in range(x0,x1) if max(cell.getpixel((x,y))[:3])<55 and cell.getpixel((x,y))[3]>220}
 comps=[]
 while mask:
  q=[mask.pop()]; pts=[]
  while q:
   z=q.pop();pts.append(z);x,y=z
   for n in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if n in mask:mask.remove(n);q.append(n)
  xs=[p[0] for p in pts];ys=[p[1] for p in pts]
  b=[min(xs),min(ys),max(xs)+1,max(ys)+1]
  c=[sum(xs)/len(xs),sum(ys)/len(ys)]
  minw,minh=s.get("pupilMinSize",[14,14])
  if len(pts)>=s.get("pupilMinArea",80) and minw<=b[2]-b[0]<=50 and minh<=b[3]-b[1]<=45:
   comps.append({"area":len(pts),"bbox":b,"centroid":c})
 if not comps:raise ValueError("No compact pupil in inspected ROI")
 comps.sort(key=lambda c:(c["centroid"][0]-expected[0])**2+(c["centroid"][1]-expected[1])**2)
 found=comps[0]
 if math.dist(found["centroid"],expected)>25:raise ValueError("Detected pupil differs from manually inspected eye")
 return found
items=[]
for i in range(rows*cols):
 x,y=i%cols,i//cols
 nominal=[round(x*w/cols),round(y*h/rows),round((x+1)*w/cols),round((y+1)*h/rows)]
 nominal_edge=edge(im.crop(nominal).getchannel("A"))
 rect=s.get("sourceRects",[None]*(rows*cols))[i] or nominal
 cell=im.crop(rect); rawbox=box16(cell); rawedge=edge(cell.getchannel("A"))
 if rawedge>s.get("maxSourceEdgeAlpha",3):raise ValueError(f"Unsafe raw source cell edge frame{i}: alpha{rawedge}; review ownership or repair genuine cutoff")
 found=pupil(cell,s["pupilRoi"],s["pupilExpected"][i])
 point=[round(v) for v in found["centroid"]]
 offset=[target[0]-point[0],target[1]-point[1]]
 cell.putalpha(cell.getchannel("A").point(lambda v:0 if v<=3 else v))
 if min(offset)<0 or offset[0]+cell.width>cw or offset[1]+cell.height>ch:raise ValueError("Full source cell must fit unscaled")
 frame=Image.new("RGBA",(cw,ch),(0,0,0,0));frame.paste(cell,offset)
 if frame.crop([offset[0],offset[1],offset[0]+cell.width,offset[1]+cell.height]).tobytes()!=cell.tobytes():raise ValueError("Native pixels changed")
 b=box16(frame);m=[b[0]/cw,b[1]/ch,(cw-b[2])/cw,(ch-b[3])/ch]
 if min(m)<.12:raise ValueError("Registered frame requires more transparent padding")
 p=out/f"frame-{i:02d}.png"
 if p.exists():raise FileExistsError(p)
 frame.save(p)
 duration=round((i+1)*1000/fps)-round(i*1000/fps)
 item={"schemaVersion":1,"id":f"frame-{i:02d}","name":s["name"]+f" {s['action']} {i}","file":rel(p),"sha256":sha(p),"width":cw,"height":ch,"format":"RGBA PNG",
  "nativeSource":s["source"],"derivedFrom":[{"file":s["source"],"sha256":sha(source),"generationRecord":s["source"]+".generation.json"}],
  "operation":{"type":"native_grid_crop_integer_pupil_registration","grid":{"rows":rows,"cols":cols},"sourceRect":rect,"registrationOffset":offset,"registeredCanvas":[cw,ch],
   "registrationReference":{"type":"black_pupil_connected_component_centroid","sourcePointFloat":found["centroid"],"sourcePointRounded":point,"targetPoint":target,"pupilBounds":found["bbox"],"detectionRoi":s["pupilRoi"],"detection":"RGB max<55,alpha>220; compact connected component nearest manually viewed pupil seed"},
   "nominalGridRect":nominal,"sourceRectType":"custom_ownership_between_separated_characters" if rect!=nominal else "nominal_grid",
   "alphaCleanup":"Values<=3 set to zero; all other RGB and alpha preserved","resized":False,"upscaled":False,"poseWarped":False,"sourcePixelsRoundTripVerified":True,"sourceBoundaryClippingAssessment":"visible_alpha_gt16_clear_of_boundary;weak_alpha_boundary_warning" if rawedge>3 else "only_alpha0_3_at_boundary"},
  "anchor":[target[0]/cw,target[1]/ch],"status":"candidate_pending_root_visual_and_playback_review","actualModel":None,"actualQuality":None,"modelEvidence":"See source record; this is a native derivative, not new generation.",
  "animation":{"id":s["id"],"frames":rows*cols,"fps":fps,"loop":s["loop"],"order":"row-major","root":[target[0]/cw,target[1]/ch],"phase":i/(rows*cols),"durationMs":duration,"targetBodyBox":s["displayBox"]},
  "qa":{"nativeBodyBoxAlpha16":rawbox,"nativeVisibleSize":[rawbox[2]-rawbox[0],rawbox[3]-rawbox[1]],"rawCellEdgeMaxAlpha":rawedge,"nominalGridEdgeMaxAlpha":nominal_edge,"registeredBoxAlpha16":b,"registeredMarginsFraction":m,"finalMargin12PercentPassed":True,"pupilComponent":found,"actualSourceViewedByProducer":True,"loopOrRecoveryAccepted":False,"targetClientAccepted":False}
 }
 write(Path(str(p)+".generation.json"),item);items.append(item)
manifest={"schemaVersion":1,"source":s["source"],"sourceWidth":w,"sourceHeight":h,"output":s["output"],"status":"candidate_pending_root_visual_and_playback_review","items":items,
 "animation":{"id":s["id"],"frameCount":len(items),"fps":fps,"loop":s["loop"],"canvas":s["canvas"],"pupilRegistrationTarget":target,"root":[target[0]/cw,target[1]/ch],"durationMs":round(len(items)*1000/fps),
   "durationsMs":[v["animation"]["durationMs"] for v in items],"sourceScale":"Uniform native pixels, no per-frame bbox normalization.","visualReview":s["visualReview"],"pending":s.get("pending",[]),"releaseReady":False},
 "notes":["Native AI articulated body/appendage frames; crop/translation/padding only aligns layout and does not create animation.","Raw source padding may be smaller than final contract; only final transparent padding meets12%.","No PNG upsample, full-image rotation/scale or per-frame body warp."]}
write(out/"manifest.json",manifest)
print(json.dumps({"id":s["id"],"frames":len(items),"nativeVisibleSizes":[i["qa"]["nativeVisibleSize"] for i in items],"pupilBoxes":[i["qa"]["pupilComponent"]["bbox"] for i in items],"edgeMax":[i["qa"]["rawCellEdgeMaxAlpha"] for i in items],"status":manifest["status"]},ensure_ascii=False))
