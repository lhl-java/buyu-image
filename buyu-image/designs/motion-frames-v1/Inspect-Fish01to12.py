"""Lightweight per-sheet alpha and pupil evidence; no game raster generation."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import label
import json,argparse,hashlib
p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("--eye-guesses");p.add_argument("--eye-radius",type=int,default=22);a=p.parse_args();guesses=json.loads(a.eye_guesses) if a.eye_guesses else None
source=Path(a.source).resolve();im=Image.open(source).convert("RGBA");w,h=im.size;frames=[]
eyes=Image.new("RGB",(640,320),(240,235,220));ed=ImageDraw.Draw(eyes)
contacts={n:Image.new("RGB",(1024,544),bg) for n,bg in [("light",(242,237,219)),("dark",(16,28,42))]}
for i in range(8):
 rect=[round(i%4*w/4),round(i//4*h/2),round((i%4+1)*w/4),round((i//4+1)*h/2)]
 cell=im.crop(rect);alpha=cell.getchannel("A");edge=max(alpha.crop((0,0,cell.width,1)).getextrema()[1],alpha.crop((0,cell.height-1,cell.width,cell.height)).getextrema()[1],alpha.crop((0,0,1,cell.height)).getextrema()[1],alpha.crop((cell.width-1,0,cell.width,cell.height)).getextrema()[1]);cell.putalpha(alpha.point(lambda v:0 if v<=3 else v));b=cell.getchannel("A").getbbox();arr=np.array(cell);mask=(arr[:,:,:3].max(2)<55)&(arr[:,:,3]>220)
 if guesses:
  gx,gy=guesses[i];yy0,xx0=np.indices(mask.shape);mask &= ((xx0-gx)**2+(yy0-gy)**2<=a.eye_radius**2)
 else: mask[:,:round(cell.width*.52)]=False
 lab,n=label(mask);sizes=np.bincount(lab.ravel());sizes[0]=0;sizes[sizes>1000]=0
 if guesses:
  candidates=[]
  for k0 in range(1,len(sizes)):
   if sizes[k0]>=30:
    ys,xs=np.where(lab==k0);candidates.append(((xs.mean()-gx)**2+(ys.mean()-gy)**2,k0))
  k=min(candidates)[1]
 else:k=int(sizes.argmax())
 yy,xx=np.where(lab==k);center=[float(xx.mean()),float(yy.mean())];pt=[round(v) for v in center];roi=[pt[0]-22,pt[1]-22,pt[0]+23,pt[1]+23];eye=cell.crop(roi).resize((144,144),Image.Resampling.NEAREST);bg=Image.new("RGBA",eye.size,(240,235,220,255));bg.alpha_composite(eye);eyes.paste(bg.convert("RGB"),(i%4*160,i//4*160));ed.text((i%4*160,i//4*160+146),f"frame{i}",fill=(20,50,40))
 margins=[b[0]/cell.width,b[1]/cell.height,(cell.width-b[2])/cell.width,(cell.height-b[3])/cell.height]
 frames.append({"frame":i,"sourceRect":rect,"nativeCell":list(cell.size),"bbox":list(b),"minMargin":min(margins),"edgeAlphaMax":edge,"pupilFloat":center,"pupil":pt,"pupilComponentPixels":int(sizes[k]),"pupilSearchRadius":a.eye_radius if guesses else None,"pupilSearchCenter":guesses[i] if guesses else None,"pupilMethod":f"RGBmax<55 and A>220 pupil component; restricted to local radius{a.eye_radius}px and nearest centroid when eye guesses supplied, otherwise largest right48percent component below1000px; actual ROI visual confirmation required"})
 for name,c in contacts.items():
  t=cell.copy();t.thumbnail((256,256),Image.Resampling.LANCZOS);c.paste(t,(i%4*256,i//4*272),t);d=ImageDraw.Draw(c);d.text((i%4*256+4,i//4*272+256),f"frame-{i:02d}",fill=(30,65,50) if name=="light" else (225,230,240))
for name,c in contacts.items():c.save(source.with_name(source.stem+"-"+name+".png"))
eyes.save(source.with_name(source.stem+"-eye-roi.png"))
out={"source":str(source),"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"size":list(im.size),"alpha":im.getchannel("A").getextrema(),"frames":frames,"sourceMarginWarnings":[x["frame"] for x in frames if x["minMargin"]<.12],"borderWarnings":[x["frame"] for x in frames if x["edgeAlphaMax"]>16],"pupilROIVisual":"pending"}
source.with_suffix(".inspect.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out))

