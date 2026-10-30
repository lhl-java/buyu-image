"""Light per-source geometry evidence. This never approves visual motion."""
from pathlib import Path
from PIL import Image
import argparse, datetime, hashlib, json
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--cols',type=int,default=2);p.add_argument('--rows',type=int,default=2);p.add_argument('--roi',nargs=4,type=int);p.add_argument('--output');p.add_argument('--dark-max',type=int,default=65);p.add_argument('--warm',action='store_true');p.add_argument('--summary',action='store_true');args=p.parse_args()
source=ROOT/args.source;im=Image.open(source).convert('RGBA');w,h=im.size;frames=[]
for i in range(args.cols*args.rows):
    rect=[round(i%args.cols*w/args.cols),round(i//args.cols*h/args.rows),round((i%args.cols+1)*w/args.cols),round((i//args.cols+1)*h/args.rows)]
    c=im.crop(rect);cw,ch=c.size;a=c.getchannel('A');box=a.point(lambda v:255 if v>3 else 0).getbbox();box16=a.point(lambda v:255 if v>16 else 0).getbbox()
    edge=max(a.crop(b).getextrema()[1] for b in [(0,0,cw,1),(0,ch-1,cw,ch),(0,0,1,ch),(cw-1,0,cw,ch)])
    margins=[box[0]/cw,box[1]/ch,(cw-box[2])/cw,(ch-box[3])/ch] if box else []
    components=[]
    if args.roi:
        x0,y0,x1,y1=args.roi;x1=min(x1,cw);y1=min(y1,ch)
        pixels=c.load();mask={(x,y) for y in range(y0,y1) for x in range(x0,x1) if max(pixels[x,y][:3])<args.dark_max and pixels[x,y][3]>220 and (not args.warm or pixels[x,y][0]>=pixels[x,y][1] and pixels[x,y][0]>=pixels[x,y][2])}
        while mask:
            q=[mask.pop()];pts=[]
            while q:
                z=q.pop();pts.append(z);x,y=z
                for v in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                    if v in mask:mask.remove(v);q.append(v)
            if len(pts)>8:
                xs=[z[0] for z in pts];ys=[z[1] for z in pts]
                components.append({'area':len(pts),'bbox':[min(xs),min(ys),max(xs)+1,max(ys)+1],'center':[sum(xs)/len(xs),sum(ys)/len(ys)]})
        components.sort(key=lambda q:q['area'],reverse=True)
    frames.append({'sourceFrame':i,'sourceRect':rect,'size':[cw,ch],'bbox3':box,'bbox16':box16,'edgeMaxAlpha':edge,'marginsLTRB':margins,'pupilCandidates':components[:4]})
report={'source':args.source,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'size':[w,h],'grid':[args.cols,args.rows],'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pupilDetection':{'roi':args.roi,'darkMaxExclusive':args.dark_max,'warmRAtLeastGAndB':args.warm,'alphaMinExclusive':220,'componentConnectivity':4},'frames':frames,'visualApproval':False,'warning':'Numeric alpha/ROI evidence only. A dark component can be mouth/crown; actual eye selection needs visual review. Padding cannot repair source clipping.'}
if args.output:
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'source':args.source,'frames':[{'i':f['sourceFrame'],'pupilCandidates':f['pupilCandidates'][:3]} for f in frames]} if args.summary else report,ensure_ascii=False))
