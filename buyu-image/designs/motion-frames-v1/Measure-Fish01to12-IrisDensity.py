"""Measure one species' local amber iris width density; tiny ROIs only, no art edits."""
from pathlib import Path
from PIL import Image
import numpy as np,json,argparse,hashlib
from scipy.ndimage import label,find_objects,binary_closing
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("id");a=p.parse_args();sp=next(x for x in json.loads((HERE/"FISH01TO12_SELECTION.json").read_text())["species"] if x["id"]==a.id);evidence={}
for act,relative in sp["source"].items():
 src=ROOT/relative;j=json.loads(src.with_suffix(".ownership.json").read_text());im=Image.open(src).convert("RGBA");entries=[]
 for f in j["frames"]:
  x=f["sourceRect"][0]+f["pupil"][0];y=f["sourceRect"][1]+f["pupil"][1];roi=[x-23,y-23,x+24,y+24];arr=np.array(im.crop(roi)).astype(int);r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2];mask=(r>100)&(g>50)&(b<r*.75)&(g>b*1.3)&(r-g>-15)&(arr[:,:,3]>200);lab,n=label(binary_closing(mask));cs=[]
  for k,obj in enumerate(find_objects(lab),1):
   if obj is None:continue
   sy,sx=obj
   if sx.start<=23<sx.stop and sy.start<=23<sy.stop:cs.append({"box":[sx.start,sy.start,sx.stop,sy.stop],"width":sx.stop-sx.start,"height":sy.stop-sy.start,"area":int((lab==k).sum())})
  if not cs:raise ValueError("No enclosing amber iris component")
  c=min(cs,key=lambda z:z["width"]*z["height"]);entries.append({"frame":f["frame"],"roiGlobal":roi,"iris":c})
 widths=[x["iris"]["width"] for x in entries];evidence[act]={"source":relative,"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"entries":entries,"medianIrisWidth":float(np.median(widths))}
ratio=evidence["capture"]["medianIrisWidth"]/evidence["swim"]["medianIrisWidth"]
out={"schemaVersion":1,"id":a.id,"method":"Actual native 47px eye ROI warm-amber segmentation; binary closing1, smallest enclosing component; median of8 widths. Height ignored because highlights/shading split upper iris.","mask":"R>100,G>50,B<.75R,G>1.3B,R-G>-15,A>200","producerROIActuallyViewed":True,"evidence":evidence,"uniformCaptureSourceDensityRatio":ratio,"scope":"One constant capture clip display scale only. No per-frame scaling, no source upsampling. Native pixels preserved and root/eye offset adjusted by same density."}
dest=HERE/a.id/"clip-density-evidence.json";dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps({"file":str(dest),"swimMedianWidth":evidence["swim"]["medianIrisWidth"],"captureMedianWidth":evidence["capture"]["medianIrisWidth"],"densityRatio":ratio}))

