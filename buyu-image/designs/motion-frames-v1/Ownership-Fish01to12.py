"""Recover complete non-overlapping native poses across nominal grid lines. Pixel ownership evidence, no resampling."""
from pathlib import Path
import argparse,json,numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
p=argparse.ArgumentParser();p.add_argument("source");a=p.parse_args();source=Path(a.source).resolve()
j=json.loads(source.with_suffix(".inspect.json").read_text(encoding="utf-8-sig"));im=Image.open(source).convert("RGBA");arr=np.array(im);alpha=arr[:,:,3];lab,n=label(alpha>3);objects=find_objects(lab)
primary=[];pupils=[]
for f in j["frames"]:
 xy=[f["sourceRect"][0]+f["pupil"][0],f["sourceRect"][1]+f["pupil"][1]];pupils.append(xy);k=int(lab[xy[1],xy[0]])
 if not k:raise ValueError("Pupil outside opaque component")
 primary.append(k)
if len(set(primary))!=8:raise ValueError("Two frame bodies intersect or pupil selection wrong")
boxes=[]
for k in primary:
 sy,sx=objects[k-1];boxes.append([sx.start,sy.start,sx.stop,sy.stop])
ownerByLabel=np.full(n+1,-1,dtype=np.int16)
for i,k in enumerate(primary):ownerByLabel[k]=i
assignment=[]
for k,obj in enumerate(objects,1):
 if obj is None or k in primary:continue
 sy,sx=obj;c=[sx.start,sy.start,sx.stop,sy.stop];scores=[]
 for i,b in enumerate(boxes):
  dx=max(b[0]-c[2],c[0]-b[2],0);dy=max(b[1]-c[3],c[1]-b[3],0)
  cx=(c[0]+c[2])/2;cy=(c[1]+c[3])/2;bx=(b[0]+b[2])/2;by=(b[1]+b[3])/2
  scores.append((dx*dx+dy*dy,(cx-bx)**2+(cy-by)**2,i))
 i=min(scores)[2];ownerByLabel[k]=i;assignment.append({"component":k,"owner":i,"box":c})
owners=ownerByLabel[lab];owned=[];fail=[]
for i,f in enumerate(j["frames"]):
 yy,xx=np.where(owners==i);b=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];chosen=None
 for pad in range(8,-1,-1):
  r=[max(0,b[0]-pad),max(0,b[1]-pad),min(im.width,b[2]+pad),min(im.height,b[3]+pad)];reg=owners[r[1]:r[3],r[0]:r[2]]
  if not np.any((reg>=0)&(reg!=i)):chosen=r;break
 if chosen is None:fail.append({"frame":i,"id":"rect_contains_other_fish_pixels","bbox":b});continue
 edgeTouch=b[0]==0 or b[1]==0 or b[2]==im.width or b[3]==im.height
 if edgeTouch:fail.append({"frame":i,"id":"source_canvas_edge_content","bbox":b})
 old=f["sourceRect"];localPupil=[pupils[i][0]-chosen[0],pupils[i][1]-chosen[1]]
 floatPupil=[f["pupilFloat"][0]+old[0]-chosen[0],f["pupilFloat"][1]+old[1]-chosen[1]]
 f.update({"nominalGridRect":old,"nominalGridPupil":f["pupil"],"sourceRect":chosen,"pupil":localPupil,"pupilFloat":floatPupil,"nativeCell":[chosen[2]-chosen[0],chosen[3]-chosen[1]],"ownershipAlphaBBoxGlobal":b,"ownershipType":"complete_nonoverlapping_pose_rectangle","ownPixelCount":int(len(xx)),"allAssignedPixelsInsideRect":True,"foreignFishAlphaPixels":0,"nominalGridBorderAlpha":f["edgeAlphaMax"]})
 owned.append({"frame":i,"nominalGridRect":old,"ownershipRect":chosen,"completeBBox":b,"foreignFishAlphaPixels":0,"alphaPixelCount":len(xx),"sourceCanvasTouch":edgeTouch,"gridBorderWarningPreserved":f["edgeAlphaMax"]>16})
j["nominalGridBorderWarnings"]=j["borderWarnings"];j["ownership"]=owned;j["ownershipWarnings"]=fail
j["ownershipNote"]="Only mathematical cell-line crossing is recovered. All source alpha>3 components assigned once, actual pose rectangles contain zero other-fish alpha. No painted pixel moved/scaled/erased; <=3 cleanup already declared. Source-grid margin and edge warnings remain historical source gates."
j["borderWarnings"]=[f["frame"] for f in fail]
j["componentOwnership"]=assignment
j["originalInspectionSHA256"]=j["sha256"]
out=source.with_suffix(".ownership.json");out.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"source":str(source),"completePoses":len(owned),"ownershipWarnings":fail,"nominalGridWarnings":j["nominalGridBorderWarnings"],"rects":[f["ownershipRect"] for f in owned],"report":str(out)}))

