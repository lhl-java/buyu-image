"""Slice native-alpha model sheets, keeping source geometry and truthful provenance."""
from pathlib import Path
import argparse, hashlib, json, datetime, math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path): return Path(path).resolve().relative_to(ROOT).as_posix()

def build(specpath):
    spec=read(specpath); source=ROOT/spec['source']; im=Image.open(source).convert('RGBA')
    rows,cols=spec['rows'],spec['cols']; out=ROOT/spec['output']; out.mkdir(parents=True,exist_ok=True)
    alpha=im.getchannel('A'); lo,hi=alpha.getextrema()
    if lo==255: raise ValueError('Source has no transparent background; regenerate rather than chroma guess')
    entries=[]; warnings=[]
    for i,item in enumerate(spec['items']):
        row,col=divmod(i,cols)
        if row>=rows: raise ValueError('More items than grid cells')
        rect=item.get('sourceRect',[round(col*im.width/cols),round(row*im.height/rows),round((col+1)*im.width/cols),round((row+1)*im.height/rows)])
        if len(rect)!=4 or not (0<=rect[0]<rect[2]<=im.width and 0<=rect[1]<rect[3]<=im.height): raise ValueError('Invalid ownership rect '+item['id'])
        cell=im.crop(rect); a=cell.getchannel('A')
        edge=max(max(a.crop((0,0,cell.width,1)).getextrema()),max(a.crop((0,cell.height-1,cell.width,cell.height)).getextrema()),max(a.crop((0,0,1,cell.height)).getextrema()),max(a.crop((cell.width-1,0,cell.width,cell.height)).getextrema()))
        if edge>16: warnings.append({'id':'cell_border_alpha','asset':item['id'],'value':edge,'threshold':16,'file':relative(source)})
        clean=a.point(lambda v:0 if v<=3 else v); cell.putalpha(clean)
        bounds=clean.getbbox()
        if not bounds: raise ValueError('Empty sprite '+item['id'])
        if item.get('keepCell',spec.get('keepCell',False)): crop=[0,0,cell.width,cell.height]
        else: crop=[max(0,bounds[0]-4),max(0,bounds[1]-4),min(cell.width,bounds[2]+4),min(cell.height,bounds[3]+4)]
        sprite=cell.crop(crop)
        canvas_padding=None
        if item.get('keepCell',spec.get('keepCell',False)):
            canvas_size=(math.ceil(im.width/cols),math.ceil(im.height/rows))
            if sprite.size!=canvas_size:
                normalized=Image.new('RGBA',canvas_size,(0,0,0,0));normalized.paste(sprite,(0,0));sprite=normalized
                canvas_padding='right/bottom transparent pad to shared ceil grid canvas; no resize'
        target=out/(item['id']+'.png'); sprite.save(target)
        info={'schemaVersion':1,'id':item['id'],'name':item.get('name',item['id']),'file':relative(target),'sha256':sha(target),'width':sprite.width,'height':sprite.height,'format':'RGBA PNG','nativeSource':relative(source),'derivedFrom':[{'file':relative(source),'sha256':sha(source),'generationRecord':relative(source)+'.generation.json'}],'operation':{'type':'native_ownership_crop' if item.get('sourceRect') else 'native_grid_crop','grid':{'rows':rows,'cols':cols},'sourceRect':rect,'cellCropRect':crop,'alphaCleanup':'Values <=3 set to zero; all other alpha and RGB preserved','resized':False,'upscaled':False},'anchor':item.get('anchor',[0.5,0.5]),'displaySize':item.get('displaySize',spec.get('displaySize',[128,128])),'status':'prepared_pending_visual_review','actualModel':None,'actualQuality':None,'modelEvidence':'See source generation record; no new model call for this slice.'}
        if item.get('sliceBorders'): info['nineSlice']=item['sliceBorders']
        if canvas_padding: info['operation']['canvasNormalization']=canvas_padding
        if spec.get('animation'): info['animation']=spec['animation']
        write(str(target)+'.generation.json',info); entries.append(info)
    manifest={'schemaVersion':1,'source':relative(source),'sourceWidth':im.width,'sourceHeight':im.height,'output':relative(out),'items':entries,'warnings':warnings,'complete':len(entries)==len(spec['items'])}
    write(out/'manifest.json',manifest)
    # QA composition only; never used as game art.
    thumb=256; canvas=Image.new('RGB',(cols*thumb,rows*thumb),(241,234,215)); d=ImageDraw.Draw(canvas)
    for i,e in enumerate(entries):
        sp=Image.open(ROOT/e['file']).convert('RGBA'); sp.thumbnail((thumb-20,thumb-36),Image.Resampling.LANCZOS)
        x=(i%cols)*thumb+(thumb-sp.width)//2; y=(i//cols)*thumb+(thumb-36-sp.height)//2
        canvas.paste(sp,(x,y),sp); d.text(((i%cols)*thumb+8,(i//cols+1)*thumb-24),e['id'],fill=(20,63,48))
    qa=ROOT/'tmp'/'art-qa'/(Path(specpath).stem+'.jpg'); qa.parent.mkdir(parents=True,exist_ok=True); canvas.save(qa,quality=90)
    print(json.dumps({'manifest':relative(out/'manifest.json'),'count':len(entries),'warnings':warnings,'qa':relative(qa)},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('spec');args=p.parse_args();build(args.spec)
