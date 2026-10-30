from pathlib import Path
import argparse,datetime,hashlib,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('id');args=p.parse_args()
manifest=read(ROOT/'assets/fx'/args.id/'manifest.json');source=ROOT/manifest['source'];image=Image.open(source).convert('RGBA');frames=[];warnings=[];runtime_warnings=[];metrics=[]
for i,item in enumerate(manifest['items']):
    file=ROOT/item['file'];frame=Image.open(file).convert('RGBA');frames.append(frame)
    row,col=divmod(i,4);rect=[round(col*image.width/4),round(row*image.height/4),round((col+1)*image.width/4),round((row+1)*image.height/4)]
    cell=image.crop(rect);alpha=cell.getchannel('A');meaningful=alpha.point(lambda v:255 if v>3 else 0);bounds=meaningful.getbbox()
    if bounds:
        margins=[bounds[0]/cell.width,bounds[1]/cell.height,(cell.width-bounds[2])/cell.width,(cell.height-bounds[3])/cell.height]
        if min(margins)<0.12:warnings.append({'id':'cell_margin_below_contract','frame':i,'value':min(margins),'threshold':0.12,'file':source.relative_to(ROOT).as_posix()})
    else:margins=[1,1,1,1];warnings.append({'id':'empty_frame','frame':i,'file':item['file']})
    runtime_bounds=frame.getchannel('A').point(lambda v:255 if v>3 else 0).getbbox();runtime_margins=[runtime_bounds[0]/frame.width,runtime_bounds[1]/frame.height,(frame.width-runtime_bounds[2])/frame.width,(frame.height-runtime_bounds[3])/frame.height]
    if min(runtime_margins)<0.12:runtime_warnings.append({'id':'runtime_margin_below_contract','frame':i,'value':min(runtime_margins),'threshold':0.12,'file':item['file']})
    metrics.append({'frame':i,'sourceRect':rect,'nativeExportSize':list(frame.size),'alphaRange':list(alpha.getextrema()),'boundsAboveAlpha3':list(bounds) if bounds else None,'marginRatios':margins,'runtimeBoundsAboveAlpha3':list(runtime_bounds),'runtimeMarginRatios':runtime_margins,'alphaSum':sum(alpha.get_flattened_data()),'sha256':sha(file)})
unique={f.tobytes() for f in frames}
if len(unique)!=16:warnings.append({'id':'duplicate_frames','uniqueFrames':len(unique),'expected':16,'file':source.relative_to(ROOT).as_posix()})
sizes={f.size for f in frames}
if len(sizes)!=1:warnings.append({'id':'variable_canvas','sizes':[list(s) for s in sizes]})
out=ROOT/'tmp/art-qa';out.mkdir(parents=True,exist_ok=True)
for name,color in [('light',(241,234,215)),('dark',(15,48,46))]:
    sheet=Image.new('RGB',(1024,1024),color);d=ImageDraw.Draw(sheet)
    for i,frame in enumerate(frames):
        thumb=frame.copy();thumb.thumbnail((228,228),Image.Resampling.LANCZOS);x=(i%4)*256+(256-thumb.width)//2;y=(i//4)*256+(236-thumb.height)//2
        sheet.paste(thumb,(x,y),thumb);d.text(((i%4)*256+8,(i//4+1)*256-20),f'frame-{i:02}',fill=(30,73,60) if name=='light' else (226,235,211))
    sheet.save(out/(args.id+'.'+name+'.jpg'),quality=92)
report={'schemaVersion':1,'id':args.id,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'nativeSourceSize':list(image.size),'frames':16,'uniqueFrameCount':len(unique),'sharedCanvas':list(frames[0].size),'animation':manifest['items'][0].get('animation'),'allMarginsMinimum':min(min(m['marginRatios']) for m in metrics),'runtimeMarginsMinimum':min(min(m['runtimeMarginRatios']) for m in metrics),'peakAlphaSumFrame':max(range(16),key=lambda i:metrics[i]['alphaSum']),'measurements':metrics,'manifestWarnings':manifest.get('warnings',[]),'sourceWarnings':warnings,'runtimeWarnings':runtime_warnings,'sourceMarginContractPassed':not warnings,'runtimePaddingMarginPassed':not runtime_warnings,'numericPass':not runtime_warnings and not manifest.get('warnings',[]) and len(unique)==16 and len(sizes)==1,'visualReviewStatus':'pending_actual_view','runtimeIntegrationVerified':False,'actualModel':None,'actualQuality':None}
(source.parent/(args.id+'.visual-qa.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='measurements'},ensure_ascii=False))
