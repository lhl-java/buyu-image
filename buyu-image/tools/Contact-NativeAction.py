"""QA-only contact sheet from existing PNGs. No art, motion or validation claim."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--prefix',required=True);args=p.parse_args()
m=json.loads((ROOT/args.manifest).read_text(encoding='utf-8-sig'));items=m['items'];cols=4;cell=400
for suffix,color,ink in [('light',(245,237,217),(31,71,59)),('dark',(21,52,45),(241,232,203))]:
    out=Image.new('RGB',(cell*cols,(cell+22)*2),color);draw=ImageDraw.Draw(out)
    for i,item in enumerate(items):
        frame=Image.open(ROOT/item['file']).convert('RGBA');frame.thumbnail((cell,cell),Image.Resampling.LANCZOS);x=(i%cols)*cell;y=(i//cols)*(cell+22);out.paste(frame,(x,y),frame);draw.text((x+6,y+cell+5),f'frame-{i:02d}',fill=ink)
    dest=ROOT/(args.prefix+'-'+suffix+'.jpg');dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest,quality=92)
    Path(str(dest)+'.generation.json').write_text(json.dumps({'file':dest.relative_to(ROOT).as_posix(),'operation':{'type':'QA_contact_sheet_display_thumbnails','sourceManifest':args.manifest,'sourceFrames':[i['file'] for i in items],'resampledForReviewOnly':True,'finalGameAsset':False,'newModelCall':False,'motionApproved':False}},ensure_ascii=False,indent=2),encoding='utf-8')
print(args.prefix+'-{light,dark}.jpg')
