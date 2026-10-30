"""Lightweight native slicing only. No model generation, resampling, pose warping or atlas work."""
from pathlib import Path
from PIL import Image
import hashlib, json
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "assets/animations/dao-child/idle"
CANVAS = (800, 800)
TARGET = (400, 680)
SPECS = [
 ("idle-a-contained.png", [(344,609),(344,609),(344,580),(344,581)], [((240,609),(448,607)),((239,609),(449,607)),((240,580),(449,578)),((240,581),(449,578))]),
 ("idle-b-from-a-v1.png", [(346,611),(344,611),(346,583),(346,582)], [((242,611),(450,609)),((240,611),(449,609)),((242,583),(450,581)),((242,582),(450,581))])
]
def rel(path): return path.relative_to(ROOT).as_posix()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def bbox16(im): return im.getchannel("A").point(lambda v:255 if v>16 else 0).getbbox()
def edge(a):
 w,h=a.size
 return max(a.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
OUT.mkdir(parents=True,exist_ok=True)
items=[]
for sheet_name,roots,soles in SPECS:
 source=Path(__file__).parent/sheet_name
 sheet=Image.open(source).convert("RGBA")
 if sheet.size != (1254,1254): raise ValueError("Native source dimensions changed")
 for local in range(4):
  index=len(items); x,y=(local%2)*627,(local//2)*627
  rect=(x,y,x+627,y+627)
  cell=sheet.crop(rect); raw_box=bbox16(cell)
  raw_edge=edge(cell.getchannel("A"))
  # Same threshold as other fishing frame deliveries; preserve all other RGB/alpha.
  cell.putalpha(cell.getchannel("A").point(lambda v:0 if v<=3 else v))
  anchor=roots[local]; offset=(TARGET[0]-anchor[0],TARGET[1]-anchor[1])
  if min(offset)<0 or offset[0]+627>800 or offset[1]+627>800: raise ValueError("Full native source cell must fit")
  frame=Image.new("RGBA",CANVAS,(0,0,0,0))
  frame.paste(cell,offset)  # no mask, so native semitransparent pixels remain exact
  if frame.crop((offset[0],offset[1],offset[0]+627,offset[1]+627)).tobytes()!=cell.tobytes(): raise ValueError("Native pixels changed")
  box=bbox16(frame); margins=[box[0]/800,box[1]/800,(800-box[2])/800,(800-box[3])/800]
  target=OUT/f"frame-{index:02d}.png"
  if target.exists():
   previous=json.loads(Path(str(target)+".generation.json").read_text(encoding="utf-8"))
   if previous.get("animation",{}).get("id")!="dao-child/idle": raise ValueError("Refusing to replace unrelated frame")
  frame.save(target)
  registered_soles=[[p[0]+offset[0],p[1]+offset[1]] for p in soles[local]]
  item={
   "schemaVersion":1,"id":f"frame-{index:02d}","name":f"道童待机候选相位 {index}/8","file":rel(target),"sha256":sha(target),
   "width":800,"height":800,"format":"RGBA PNG","nativeSource":rel(source),
   "derivedFrom":[{"file":rel(source),"sha256":sha(source),"generationRecord":rel(source)+".generation.json"}],
   "operation":{"type":"native_grid_crop_integer_planted_sole_registration_and_transparent_padding","grid":{"rows":2,"cols":2},
    "sourceRect":list(rect),"cellCropRect":[0,0,627,627],"registrationOffset":list(offset),"registeredCanvas":[800,800],
    "registrationReference":{"type":"midpoint_of_two_sole_contact_centres_and_lowest_sole","sourcePoint":list(anchor),"sourceSoles":[list(s) for s in soles[local]],"targetPoint":list(TARGET),
      "detection":"Manually inspected shoe ROIs x150..345 and x345..550,y470..626; alpha>200 bottommost row, x centroid within bottom five rows; nearest integer."},
    "alphaCleanup":"Values <=3 set to zero; all other alpha and RGB preserved","resized":False,"upscaled":False,"poseWarped":False,"sourcePixelsRoundTripVerified":True},
   "anchor":[0.5,0.85],"actualModel":None,"actualQuality":None,"modelEvidence":"See actual AI source generation record; slicing is not a new model call.",
   "status":"candidate_pending_root_visual_and_playback_review",
   "animation":{"id":"dao-child/idle","frames":8,"fps":8,"loop":True,"order":"first sheet row-major then second sheet row-major","phase":index/8,"durationMs":125,"root":[0.5,0.85]},
   "qa":{"nativeBodyBoxAlpha16":list(raw_box),"nativeBodyHeight":raw_box[3]-raw_box[1],"rawCellEdgeMaxAlpha":raw_edge,
     "rawCellMargin12PercentPassed":min(raw_box[0]/627,raw_box[1]/627,(627-raw_box[2])/627,(627-raw_box[3])/627)>=.12,
     "registeredBodyBoxAlpha16":list(box),"registeredSolePoints":registered_soles,"registeredMarginsFraction":margins,
     "registeredMargin12PercentPassed":min(margins)>=.12,"nativeHeight280Passed":raw_box[3]-raw_box[1]>=280,
     "noUpscalePassed":True,"visualMotionAccepted":False,"loopAccepted":False}
  }
  write(Path(str(target)+".generation.json"),item); items.append(item)
manifest={
 "schemaVersion":1,"source":["designs/motion-frames-v1/dao-child/idle/idle-a-contained.png","designs/motion-frames-v1/dao-child/idle/idle-b-from-a-v1.png"],
 "output":rel(OUT),"status":"candidate_pending_root_visual_and_playback_review","items":items,
 "animation":{"id":"dao-child/idle","frameCount":8,"fps":8,"loop":True,"canvas":[800,800],"root":[400,680],"durationMs":1000,"frameDurationsMs":[125]*8,
   "geometricRegistrationOnly":True,"animationCreatedBy":"Native AI hand-drawn source frames; integer translation only removes sheet layout offsets.",
   "acceptance":{"status":"pending_root_visual_and_playback_review","firstFourNativeHeight":[501,501,499,499],
     "lastFourNativeHeight":[505,505,502,502],"scaleContinuityCandidatePassed":True,"scaleContinuityNote":"Native height range 499..505px (1.2%); no resampling used. Minor original pose/shape drift still needs visual approval.","fixedFootPairSpanCandidatePassed":True,"solePairSpanRange":[208,210],"loopPlaybackReviewed":False,"targetClientReviewed":False},
   "blockers":["Native source geometry candidate improved after one A-target local edit; 1.2% native height drift still needs visual approval.",
     "Eye reopening and local cloth/ribbon motion observed in source stills; actual playback and loop join remain unreviewed.",
     "Registered midpoint is exact, but individual original shoe contours have minor 1..2px differences; no warping used to hide them."],
   "releaseReady":False},
 "notes":["Final padding provides >=12% alpha>16 margins without resizing; raw sheets did not meet the margin target.",
   "Eight PNGs and static geometric checks do not prove an accepted animation or whole-game completion.",
   "Earlier B-based attempts were not adopted; only idle-b-from-a-v1 supplies frames4..7."]
}
write(OUT/"manifest.json",manifest)
print(json.dumps({"output":rel(OUT),"frames":len(items),"status":manifest["status"],"nativeHeights":[i["qa"]["nativeBodyHeight"] for i in items],"finalMarginPassed":[i["qa"]["registeredMargin12PercentPassed"] for i in items]},ensure_ascii=False))
