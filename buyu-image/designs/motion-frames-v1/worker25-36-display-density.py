"""One uniform display density per clip, shared head pivot; never resizes PNGs."""
from pathlib import Path
import json,statistics,sys
ROOT=Path(__file__).resolve().parents[2]
character=sys.argv[1]
paths=[ROOT/f"assets/animations/{character}/{a}/manifest.json" for a in ("swim","capture")]
ms=[json.loads(p.read_text(encoding="utf-8")) for p in paths]
requested=20.0
metrics=[]
for m in ms:
 items=m["items"]; excluded=m["animation"].get("closedEyeFrameIndices",[])
 density_items=[i for k,i in enumerate(items) if k not in excluded]
 widths=[i["qa"].get("densityEyeComponent",i["qa"]["pupilComponent"])["bbox"][2]-i["qa"].get("densityEyeComponent",i["qa"]["pupilComponent"])["bbox"][0] for i in density_items]; median=statistics.median(widths)
 if "densityReferenceFrame" in m["animation"]:
  feature=items[m["animation"]["densityReferenceFrame"]]["qa"]["densityEyeComponent"]["bbox"]
  median=feature[2]-feature[0]
 maxw=max(i["qa"]["nativeVisibleSize"][0] for i in items);maxh=max(i["qa"]["nativeVisibleSize"][1] for i in items)
 box=items[0]["animation"]["targetBodyBox"]
 maxscale=min(1.0,box[0]/maxw,box[1]/maxh)
 metrics.append((median,maxw,maxh,maxscale))
target=min(requested,*[d[0]*d[3] for d in metrics])
target=int(target*1000)/1000
for path,m,d in zip(paths,ms,metrics):
 median,maxw,maxh,maxscale=d;scale=target/median
 pivot=m["animation"]["pupilRegistrationTarget"];canvas=m["animation"]["canvas"]
 norm=[pivot[0]/canvas[0],pivot[1]/canvas[1]]
 cal={"status":"candidate_pending_root_visual_runtime_review","method":"one_uniform_scale_per_clip_from_"+m["animation"].get("densityFeature","median_native_black_pupil_width_as_head_size_proxy"),"nativeReferenceEyeFeatureWidth":median,"sharedTargetDisplayedEyeFeatureWidth":target,"uniformDisplayScale":scale,"upscale":False,"perFrameBboxFit":False,"sharedVisualPivotPixels":pivot,"sharedVisualPivotNormalized":norm,"displayBodyMaxPixels":[maxw*scale,maxh*scale],"warning":"Eye component is an approximate density proxy; exact outer head and actual action transitions require playback review. Use registered eye pivot when applying clip scales."}
 m["animation"]["displayCalibration"]=cal;m["animation"]["root"]=norm
 for i in m["items"]:
  i["anchor"]=norm;i["animation"]["root"]=norm;i["animation"]["displayCalibration"]=cal
  Path(str(ROOT/i["file"])+".generation.json").write_text(json.dumps(i,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"id":m["animation"]["id"],"scale":scale,"targetPupil":target,"displayEnvelope":cal["displayBodyMaxPixels"]}))
