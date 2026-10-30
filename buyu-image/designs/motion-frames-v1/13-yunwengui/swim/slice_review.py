"""Small eight-frame native-grid inspection. No model call or animation synthesis."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,math,datetime,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
VERSION=sys.argv[1] if len(sys.argv)>1 else 'v3'
SOURCE=HERE/('13-yunwengui-swim-'+VERSION+'.png')
im=Image.open(SOURCE).convert('RGBA');cw,ch=math.ceil(im.width/4),math.ceil(im.height/2)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pupil(cell):
    # Only a registration measurement; no component is removed from artwork.
    x0,y0,x1,y1=round(cell.width*.60),round(cell.height*.15),round(cell.width*.99),round(cell.height*.55)
    px=cell.load();points=set()
    for y in range(y0,y1):
        for x in range(x0,x1):
            r,g,b,a=px[x,y]
            if a>=200 and r<120 and g<100 and b<80 and r>g*1.05:points.add((x,y))
    groups=[]
    while points:
        start=points.pop();stack=[start];group=[start]
        while stack:
            x,y=stack.pop()
            for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if n in points:points.remove(n);stack.append(n);group.append(n)
        if len(group)>=20:groups.append(group)
    if not groups:return None
    group=max(groups,key=len);xs=[p[0] for p in group];ys=[p[1] for p in group]
    return {'center':[sum(xs)/len(xs),sum(ys)/len(ys)],'boundsLTRB':[min(xs),min(ys),max(xs)+1,max(ys)+1],'area':len(group),'method':'largest warm-dark component only in fixed head ROI; metadata measurement, not image filtering'}
cells=[];entries=[];warnings=[]
for i in range(8):
    row,col=divmod(i,4);rect=[round(col*im.width/4),round(row*im.height/2),round((col+1)*im.width/4),round((row+1)*im.height/2)]
    raw=im.crop(rect);a=raw.getchannel('A');edge=max(a.crop((0,0,raw.width,1)).getextrema()[1],a.crop((0,raw.height-1,raw.width,raw.height)).getextrema()[1],a.crop((0,0,1,raw.height)).getextrema()[1],a.crop((raw.width-1,0,raw.width,raw.height)).getextrema()[1])
    raw.putalpha(a.point(lambda v:0 if v<=3 else v));cell=Image.new('RGBA',(cw,ch),(0,0,0,0));cell.paste(raw,(0,0))
    bounds=cell.getchannel('A').getbbox();margins=[bounds[0]/cw,bounds[1]/ch,(cw-bounds[2])/cw,(ch-bounds[3])/ch]
    if edge>16:warnings.append({'id':'source_cell_border_alpha','sourceFrame':i,'value':edge,'threshold':16})
    if min(margins)<.12:warnings.append({'id':'source_cell_margin','sourceFrame':i,'value':min(margins),'threshold':.12})
    e={'sourceFrame':i,'sourceRect':rect,'nativeCellSize':list(raw.size),'normalizedSharedCanvas':[cw,ch],'boundsAboveAlpha3':list(bounds),'marginRatios':margins,'edgeMaxAlpha':edge,'pupil':pupil(cell)}
    entries.append(e);cells.append(cell)
for suffix,bg,ink in [('light',(245,237,217),(31,71,59)),('dark',(21,52,45),(241,232,203))]:
    sheet=Image.new('RGB',(cw*4,(ch+24)*2),bg);d=ImageDraw.Draw(sheet)
    for i,cell in enumerate(cells):
        x=(i%4)*cw;y=(i//4)*(ch+24);sheet.paste(cell,(x,y),cell);d.text((x+8,y+ch+6),'source-'+str(i),fill=ink)
    sheet.save(HERE/('source-'+VERSION+'-'+suffix+'.jpg'),quality=91)
report={'schemaVersion':1,'source':SOURCE.relative_to(ROOT).as_posix(),'sha256':sha(SOURCE),'nativeSize':list(im.size),'sharedCanvas':[cw,ch],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frames':entries,'warnings':warnings,'alphaCleanup':'Only <=3 set to0 in derived cell copy; source image untouched','actualMotionApproved':False,'rootRegistrationPending':True,'noResamplingOrUpscaling':True}
(HERE/('source-'+VERSION+'-qa.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'nativeSize':report['nativeSize'],'sharedCanvas':report['sharedCanvas'],'warnings':warnings,'pupils':[e['pupil'] for e in entries]},ensure_ascii=False))
