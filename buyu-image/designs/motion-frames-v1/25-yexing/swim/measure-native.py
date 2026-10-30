from PIL import Image
import json
p=Image.open(r'designs/motion-frames-v1/25-yexing/swim/25-yexing-swim-contained.png').convert('RGBA'); w,h=p.size
out=[]
for i in range(8):
 rect=(round(i%4*w/4),round(i//4*h/2),round((i%4+1)*w/4),round((i//4+1)*h/2))
 c=p.crop(rect);a=c.getchannel('A');cw,ch=c.size
 box=a.point(lambda x:255 if x>16 else 0).getbbox()
 mask={(x,y) for y in range(150,290) for x in range(300,min(435,cw)) if max(c.getpixel((x,y))[:3])<55 and c.getpixel((x,y))[3]>220}
 comps=[]
 while mask:
  q=[mask.pop()];pts=[]
  while q:
   z=q.pop();pts.append(z);x,y=z
   for v in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if v in mask:mask.remove(v);q.append(v)
  comps.append(pts)
 comps.sort(key=len,reverse=True); candidates=[]
 for pts in comps[:3]:
  xs=[z[0] for z in pts];ys=[z[1] for z in pts]
  candidates.append({'area':len(pts),'bbox':[min(xs),min(ys),max(xs)+1,max(ys)+1],'centroid':[sum(xs)/len(xs),sum(ys)/len(ys)]})
 out.append({'i':i,'rect':rect,'bbox16':box,'edge':max(a.crop(b).getextrema()[1] for b in [(0,0,cw,1),(0,ch-1,cw,ch),(0,0,1,ch),(cw-1,0,cw,ch)]),'pupilCandidates':candidates})
print(json.dumps(out))
