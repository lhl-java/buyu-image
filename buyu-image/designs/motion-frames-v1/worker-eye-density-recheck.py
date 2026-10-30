from PIL import Image
from pathlib import Path
import json
out=[]
for ch,act in [('27-yingguang','swim'),('27-yingguang','capture'),('31-bingjing','swim'),('31-bingjing','capture')]:
 arr=[]
 for i in range(8):
  p=Path('assets/animations')/ch/act/('frame-%02d.png'%i);im=Image.open(p).convert('RGBA');target=(384,320) if ch.startswith('27') else (560,400)
  x0,y0,x1,y1=target[0]-35,target[1]-35,target[0]+36,target[1]+36
  row=[]
  for threshold in [100,140,170,200]:
   mask={(x,y) for y in range(y0,y1) for x in range(x0,x1) if max(im.getpixel((x,y))[:3])<threshold and im.getpixel((x,y))[3]>220}; comps=[]
   while mask:
    q=[mask.pop()];pts=[]
    while q:
     z=q.pop();pts.append(z);x,y=z
     for n in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
      if n in mask:mask.remove(n);q.append(n)
    xs=[p[0]for p in pts];ys=[p[1]for p in pts];b=[min(xs),min(ys),max(xs)+1,max(ys)+1];c=[sum(xs)/len(xs),sum(ys)/len(ys)]
    if len(pts)>=30 and b[0]>x0 and b[1]>y0 and b[2]<x1 and b[3]<y1:comps.append((len(pts),b,c))
   comps.sort(key=lambda v:(v[2][0]-target[0])**2+(v[2][1]-target[1])**2)
   row.append({'t':threshold,'best':comps[0] if comps else None})
  arr.append({'i':i,'measurements':row})
 out.append({'id':ch+'/'+act,'frames':arr})
print(json.dumps(out))
