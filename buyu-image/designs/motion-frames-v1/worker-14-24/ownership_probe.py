"""Light native-sheet connectivity probe, without changing source pixels."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np, json, sys
ROOT=Path(__file__).resolve().parents[3]
creature,action=sys.argv[1:3];version=sys.argv[3] if len(sys.argv)>3 else ''
assert 14<=int(creature.split('-')[0])<=24
folder=ROOT/'designs/motion-frames-v1'/creature/action
source=folder/f'{creature}-{action}{version}.png'
image=Image.open(source).convert('RGBA');alpha=np.asarray(image)[:,:,3]
labels,n=ndimage.label(alpha>16)
counts=np.bincount(labels.ravel());counts[0]=0
ids=np.argsort(counts)[-8:]
boxes=ndimage.find_objects(labels)
entries=[]
for ident in ids:
    region=boxes[ident-1];y,x=region
    yy,xx=np.nonzero(labels[region]==ident)
    bbox=[x.start,y.start,x.stop,y.stop]
    entries.append({'label':int(ident),'area':int(counts[ident]),'bbox':bbox,'center':[float(xx.mean()+x.start),float(yy.mean()+y.start)],'touchesTotalCanvas':bool(x.start==0 or y.start==0 or x.stop==image.width or y.stop==image.height)})
entries.sort(key=lambda v:v['center'][1]);entries=sorted(entries[:4],key=lambda v:v['center'][0])+sorted(entries[4:],key=lambda v:v['center'][0])
result={'source':source.relative_to(ROOT).as_posix(),'threshold':16,'largest8Components':entries,'meaning':'Connectivity evidence only: no automatic motion pass, component deletion, or clipping repair.'}
(folder/('ownership-probe'+version+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'source':result['source'],'components':entries},ensure_ascii=False))
