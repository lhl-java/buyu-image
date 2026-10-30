"""Inspect or export root-owned Daochild point/celebrate sheets. No image generation or source mutation."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,argparse
from scipy.ndimage import label,find_objects
ROOT=Path(__file__).resolve().parents[1];TMP=ROOT/"tmp/dao-child-export";TMP.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
def inspect_sheet(p):
 im=Image.open(p).convert("RGBA");arr=np.array(im);alpha=arr[:,:,3];lab,n=label(alpha>3);objs=find_objects(lab);w,h=im.size;prim=[];grid=[]
 for i in range(4):
  c,r=i%2,i//2;rect=[round(c*w/2),round(r*h/2),round((c+1)*w/2),round((r+1)*h/2)];grid.append(rect);x=rect[0]+340;y=rect[1]+420;k=int(lab[y,x])
  if not k:raise ValueError("Torso seed empty; inspect source coordinates")
  prim.append(k)
 if len(set(prim))!=4:raise ValueError("Bodies intersect or incorrect torso seed")
 boxes=[]
 for k in prim:
  sy,sx=objs[k-1];boxes.append([sx.start,sy.start,sx.stop,sy.stop])
 owner=np.full(n+1,-1,dtype=np.int16)
 for i,k in enumerate(prim):owner[k]=i
 for k,o in enumerate(objs,1):
  if o is None or k in prim:continue
  sy,sx=o;c=[sx.start,sy.start,sx.stop,sy.stop];score=[]
  for i,b in enumerate(boxes):
   dx=max(b[0]-c[2],c[0]-b[2],0);dy=max(b[1]-c[3],c[1]-b[3],0);score.append((dx*dx+dy*dy,((c[0]+c[2]-b[0]-b[2])/2)**2+((c[1]+c[3]-b[1]-b[3])/2)**2,i))
  owner[k]=min(score)[2]
 owners=owner[lab];frames=[];warn=[]
 for i,nom in enumerate(grid):
  yy,xx=np.where(owners==i);b=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];chosen=None
  for pad in range(8,-1,-1):
   rect=[max(0,b[0]-pad),max(0,b[1]-pad),min(w,b[2]+pad),min(h,b[3]+pad)];region=owners[rect[1]:rect[3],rect[0]:rect[2]]
   if not np.any((region>=0)&(region!=i)):chosen=rect;break
  if chosen is None:warn.append({"frame":i,"type":"foreign_pose_alpha_in_ownership_rect"});continue
  if b[0]==0 or b[1]==0 or b[2]==w or b[3]==h:warn.append({"frame":i,"type":"source_canvas_edge_touched","bbox":b})
  soles=[]
  for x0,x1 in [(130,340),(340,560)]:
   xlo=nom[0]+x0;xhi=min(w,nom[0]+x1);ylo=nom[1]+430;yhi=min(h,nom[1]+700)
   mask=(owners[ylo:yhi,xlo:xhi]==i)&(alpha[ylo:yhi,xlo:xhi]>200);sy,sx=np.where(mask)
   if len(sy)==0:raise ValueError("Shoe ROI empty")
   floor=int(sy.max());contactX=round(float(sx[sy>=floor-4].mean())+xlo);soles.append([contactX,floor+ylo])
  foot=[round((soles[0][0]+soles[1][0])/2),max(soles[0][1],soles[1][1])]
  ownMask=(owners==i)&(alpha>200);r0,g0,b0=arr[:,:,0].astype(int),arr[:,:,1].astype(int),arr[:,:,2].astype(int)
  solid16=(owners==i)&(alpha>16);s16y,s16x=np.where(solid16);bbox16=[int(s16x.min()),int(s16y.min()),int(s16x.max()+1),int(s16y.max()+1)]
  headSolid=solid16.copy();headSolid[:,:nom[0]+240]=False;headSolid[:,min(w,nom[0]+490):]=False;headSolid[min(h,b[1]+240):,:]=False;headY,headX=np.where(headSolid);headTop=int(headY.min())
  y0=headTop+15;hair=ownMask&(r0>45)&(r0<200)&(g0>15)&(g0<155)&(b0>5)&(b0<120)&(r0>1.1*g0)&(g0>1.05*b0);hair[:y0,:]=False;hair[min(h,headTop+110):,:]=False;hair[:,:nom[0]+160]=False;hair[:,min(w,nom[0]+500):]=False
  hy,hx=np.where(hair);hairBox=[int(hx.min()),int(hy.min()),int(hx.max()+1),int(hy.max()+1)];bodyHeight=bbox16[3]-headTop
  eye=ownMask&(arr[:,:,:3].max(2)<55);eye[:headTop+95,:]=False;eye[min(h,headTop+210):,:]=False;eye[:,:nom[0]+220]=False;eye[:,min(w,nom[0]+490):]=False;el,en=label(eye);es=np.bincount(el.ravel());es[0]=0;es[es>1500]=0;ks=np.argsort(es)[-2:];centres=[]
  for k in ks:
   ey,ex=np.where(el==k);centres.append([float(ex.mean()),float(ey.mean())])
  eyeDist=float(np.linalg.norm(np.array(centres[1])-np.array(centres[0])))
  cellA=Image.fromarray(alpha).crop(nom);cw,ch=cellA.size;edge=max(cellA.crop((0,0,cw,1)).getextrema()[1],cellA.crop((0,ch-1,cw,ch)).getextrema()[1],cellA.crop((0,0,1,ch)).getextrema()[1],cellA.crop((cw-1,0,cw,ch)).getextrema()[1])
  frames.append({"localFrame":i,"nominalGridRect":nom,"ownershipRect":chosen,"completeAlphaBBox":b,"bodyBoxAlpha16":bbox16,"headCentralAlpha16Top":headTop,"foreignPoseAlphaPixels":0,"sourceCanvasTouched":b[0]==0 or b[1]==0 or b[2]==w or b[3]==h,"sourceSolesGlobal":soles,"rootGlobal":foot,"rootLocal":[foot[0]-chosen[0],foot[1]-chosen[1]],"footPairSpan":soles[1][0]-soles[0][0],"hairBoxGlobal":hairBox,"hairWidthMethod":"brown hair pixels in headTop+15..110 band; excludes lower ribbons/cannon","headHairWidth":hairBox[2]-hairBox[0],"bodyHairTopToSoleHeight":bodyHeight,"nativeBodyHeightIgnoringRaisedArms":bodyHeight,"heightMethod":"alpha16 central head top to alpha16 complete body bottom; raised hand not used as top","eyeCentresGlobal":centres,"eyeDistanceProxy":eyeDist,"nominalGridEdgeMaxAlpha":edge})
 return {"source":rel(p),"sha256":sha(p),"size":[w,h],"alphaExtrema":list(Image.fromarray(alpha).getextrema()),"frames":frames,"ownershipWarnings":warn}
p=argparse.ArgumentParser();p.add_argument("action",choices=["point","celebrate"]);p.add_argument("--b-file");a=p.parse_args()
srcdir=ROOT/f"designs/motion-frames-v1/dao-child/{a.action}";sources=[srcdir/(a.action+"-a-v1.png"),Path(a.b_file).resolve() if a.b_file else srcdir/(a.action+"-b-v1.png")];parts=[inspect_sheet(s) for s in sources]
summary=[]
for j in parts:
 fs=j["frames"];summary.append({"source":j["source"],"nativeHeights":[x["bodyHairTopToSoleHeight"] for x in fs],"shoeSpans":[x["footPairSpan"] for x in fs],"hairWidths":[x["headHairWidth"] for x in fs],"eyeDistances":[round(x["eyeDistanceProxy"],3) for x in fs],"medianBodyHeight":float(np.median([x["bodyHairTopToSoleHeight"] for x in fs])),"medianFootSpan":float(np.median([x["footPairSpan"] for x in fs])),"medianHairWidth":float(np.median([x["headHairWidth"] for x in fs]))})
ratios={"medianBodyHeight":summary[1]["medianBodyHeight"]/summary[0]["medianBodyHeight"],"medianFootSpan":summary[1]["medianFootSpan"]/summary[0]["medianFootSpan"],"medianHairWidth":summary[1]["medianHairWidth"]/summary[0]["medianHairWidth"],"entryEyeDistance":parts[1]["frames"][0]["eyeDistanceProxy"]/parts[0]["frames"][0]["eyeDistanceProxy"]}
out={"action":a.action,"parts":parts,"summary":summary,"ratiosBtoA":ratios,"scaleContinuity":"candidate_pass" if max(abs(v-1) for v in [ratios["medianBodyHeight"],ratios["medianFootSpan"]])<=.03 else "requires_source_density_repair","rule":"No per-sheet/per-frame scale inside one clip. One clip scale only after coherent source density. Alpha ownership only, no resampling."}
write(TMP/(a.action+"-source-inspection.json"),out)
# Frame0 A/B at the same native pixels with sole baseline; QA only.
compare=Image.new("RGB",(1300,760),(242,237,219));draw=ImageDraw.Draw(compare)
for i,(source,j) in enumerate(zip(sources,parts)):
 im=Image.open(source).convert("RGBA");f=j["frames"][0];rect=f["ownershipRect"];cell=im.crop(rect);cell.putalpha(cell.getchannel("A").point(lambda v:0 if v<=3 else v));root=f["rootLocal"];x=325+i*650-root[0];y=690-root[1];compare.paste(cell,(x,y),cell);draw.line((i*650,690,(i+1)*650,690),fill=(180,100,75));draw.text((i*650+8,8),source.name+f" body={f['bodyHairTopToSoleHeight']} span={f['footPairSpan']}",fill=(25,65,45))
compare.save(TMP/(a.action+"-native-density.png"))
print(json.dumps({"action":a.action,"summary":summary,"ratiosBtoA":ratios,"scaleContinuity":out["scaleContinuity"],"ownershipWarnings":[x["ownershipWarnings"] for x in parts],"report":rel(TMP/(a.action+"-source-inspection.json"))}))

