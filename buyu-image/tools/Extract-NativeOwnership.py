"""Extract disjoint native characters from one sheet; never synthesize or scale art.

Four or eight independent large alpha components are required. Small disconnected
pieces retain all native RGBA and are assigned to the nearest complete actor.
The resulting contact sheet and ownership rectangles still need human review.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import argparse,datetime,hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--cols',type=int,default=2);p.add_argument('--rows',type=int,default=2);p.add_argument('--prefix',required=True);args=p.parse_args()
source=ROOT/args.source;im=Image.open(source).convert('RGBA');a=np.array(im);h,w=a.shape[:2];active=a[:,:,3]>3
labels,n=ndimage.label(active,structure=np.ones((3,3),dtype=np.uint8));sizes=np.bincount(labels.ravel());sizes[0]=0
count=args.cols*args.rows;ids=np.argsort(sizes)[-count:].tolist()
if len(ids)!=count or min(sizes[ids])<5000:raise RuntimeError('Not enough independent complete actor components')
remaining=np.delete(sizes,ids)
if max(remaining,default=0)>5000:raise RuntimeError('Extra large component requires semantic ownership review')
centers={i:ndimage.center_of_mass(active,labels,i) for i in ids}
ids.sort(key=lambda i:centers[i][0]);ordered=[]
for row in range(args.rows):ordered.extend(sorted(ids[row*args.cols:(row+1)*args.cols],key=lambda i:centers[i][1]))
lookup=np.zeros(n+1,dtype=np.uint8)
for k,ident in enumerate(ordered):lookup[ident]=k+1
owners=lookup[labels];seed=owners>0
indices=ndimage.distance_transform_edt(~seed,return_distances=False,return_indices=True)
nearest=owners[tuple(indices)]
for ident in range(1,n+1):
    if lookup[ident]:continue
    component=labels==ident
    votes=np.bincount(nearest[component],minlength=count+1);votes[0]=0
    lookup[ident]=int(votes.argmax())
owners=lookup[labels];assert np.array_equal(owners>0,active)
prefix=ROOT/args.prefix;prefix.parent.mkdir(parents=True,exist_ok=True);entries=[]
debug=im.convert('RGB');debug=Image.new('RGB',im.size,(24,51,46));debug.paste(im,(0,0),im);draw=ImageDraw.Draw(debug)
for k in range(count):
    mask=owners==k+1;ys,xs=np.where(mask);rect=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    out=a[rect[1]:rect[3],rect[0]:rect[2]].copy();local=mask[rect[1]:rect[3],rect[0]:rect[2]]
    out[~local]=0;assert np.array_equal(out[local],a[rect[1]:rect[3],rect[0]:rect[2]][local])
    path=Path(str(prefix)+f'-pose-{k:02d}.png');Image.fromarray(out).save(path)
    edges=int(max(a[0,:,3][mask[0,:]].max(initial=0),a[-1,:,3][mask[-1,:]].max(initial=0),a[:,0,3][mask[:,0]].max(initial=0),a[:,-1,3][mask[:,-1]].max(initial=0)))
    nominal=[round(k%args.cols*w/args.cols),round(k//args.cols*h/args.rows),round((k%args.cols+1)*w/args.cols),round((k//args.cols+1)*h/args.rows)]
    cross=rect[0]<nominal[0] or rect[1]<nominal[1] or rect[2]>nominal[2] or rect[3]>nominal[3]
    entry={'sourceFrame':k,'file':path.relative_to(ROOT).as_posix(),'sourceRect':rect,'nominalSourceRect':nominal,'nominalGridCross':cross,'nativeVisibleSize':[rect[2]-rect[0],rect[3]-rect[1]],'ownedPixelCount':int(mask.sum()),'foreignPixelsRemovedFromCrop':int((active[rect[1]:rect[3],rect[0]:rect[2]]&~local).sum()),'totalCanvasEdgeMaxAlpha':edges,'nativeOwnedPixelsUnchanged':True,'sourceMainAlphaComponent':int(ordered[k])}
    entries.append(entry)
    record={'schemaVersion':1,'file':entry['file'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':out.shape[1],'height':out.shape[0],'format':'RGBA PNG','derivedFrom':[{'file':args.source,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'generationRecord':args.source+'.generation.json'}],'operation':{'type':'native_complete_actor_ownership_crop','evidence':entry,'alphaCleanup':'alpha<=3 discarded, other owned RGBA unchanged','resized':False,'upscaled':False,'newNativeDetailClaimed':False},'actualModel':None,'actualQuality':None,'status':'intermediate_pending_semantic_review'}
    Path(str(path)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    draw.rectangle(rect,outline=(240,204,90),width=1);draw.text((rect[0]+4,rect[1]+3),str(k),fill='white')
ownerpath=Path(str(prefix)+'-ownership.png');Image.fromarray(owners).save(ownerpath)
debugpath=Path(str(prefix)+'-ownership-review.jpg');debug.save(debugpath,quality=90)
report={'schemaVersion':1,'source':args.source,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'size':[w,h],'grid':[args.cols,args.rows],'frames':entries,'ownershipMap':ownerpath.relative_to(ROOT).as_posix(),'contactSheet':debugpath.relative_to(ROOT).as_posix(),'totalActivePixels':int(active.sum()),'retainedPixelCount':sum(e['ownedPixelCount'] for e in entries),'pixelOwnershipExclusiveAndComplete':True,'allNativeRGBAAboveAlpha3Preserved':True,'alphaCleanup':'Outside owned shape zero; alpha<=3 discarded, all owned RGBA unchanged.','resized':False,'motionApproved':False,'semanticOwnershipApproved':False,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
Path(str(prefix)+'.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(prefix)+'.json','frames':entries,'exclusiveAndComplete':True},ensure_ascii=False))
