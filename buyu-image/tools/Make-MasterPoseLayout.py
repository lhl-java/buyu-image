"""Create a reference-only layout of an existing master. Never a final animation asset."""
from pathlib import Path
import argparse,datetime,hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('master');p.add_argument('output');p.add_argument('--cols',type=int,default=2);p.add_argument('--rows',type=int,default=2);p.add_argument('--width',type=int,default=1254);p.add_argument('--height',type=int,default=1254);args=p.parse_args()
source=ROOT/args.master;out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(source).convert('RGBA');a=im.getchannel('A');bbox=a.point(lambda v:255 if v>3 else 0).getbbox();sprite=im.crop(bbox)
original=sprite.size;cw=args.width/args.cols;ch=args.height/args.rows;sprite.thumbnail((round(cw*.7),round(ch*.7)),Image.Resampling.LANCZOS)
canvas=Image.new('RGBA',(args.width,args.height),(0,0,0,0));placements=[]
for row in range(args.rows):
    for col in range(args.cols):
        x=round(col*cw+(cw-sprite.width)/2);y=round(row*ch+(ch-sprite.height)/2)
        canvas.paste(sprite,(x,y));placements.append([x,y,sprite.width,sprite.height])
canvas.save(out)
record={'schemaVersion':1,'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'purpose':'Image model geometry/identity edit reference only; identical stills are NOT animation frames or game art.',
    'operation':{'type':'reference_only_master_layout_composite','masterCropRect':bbox,'referenceCropSize':original,'referencePlacedSize':sprite.size,'canvas':[args.width,args.height],'grid':[args.cols,args.rows],'placements':placements,'finalGameAsset':False},
    'derivedFrom':[{'file':args.master,'sha256':sha(source),'generationRecord':args.master+'.generation.json'}],'actualModel':None,'actualQuality':None,'newModelCall':False}
Path(str(out)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reference':str(out),'masterVisibleSize':original,'referencePlacedSize':sprite.size,'notAnimation':True}))
