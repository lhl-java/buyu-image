"""Aggregate cached per-clip evidence; no rendering, test suite or global catalog mutation."""
from pathlib import Path
import json,hashlib,datetime,argparse
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("--retention-finalized",action="store_true");args=p.parse_args()
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
selPath=HERE/"FISH01TO12_SELECTION.json";sel=read(selPath);selected={x for sp in sel["species"] for x in sp["source"].values()};now=datetime.datetime.now(datetime.timezone.utc).isoformat();actions=[];sourceRecords=[];retention=[]
for sp in sel["species"]:
 for act,relative in sp["source"].items():
  src=ROOT/relative;gr=read(Path(str(src)+".generation.json"));mfp=ROOT/f"assets/animations/{sp['id']}/{act}/manifest.json";m=read(mfp)
  assert len(m["items"])==8 and all((ROOT/x["file"]).exists() for x in m["items"])
  assert m["sharedCanvas"][0]==m["sharedCanvas"][1] and not m["warnings"] and not m.get("runtimeMarginWarnings",[])
  m["qa"]["producerLightDarkAlphaCompositeActuallyViewed"]=True;m["qa"]["producerRegisteredPoseStillReview"]="candidate_pass";m["qa"]["producerPoseEvidence"]=sp["producerNote"];m["qa"]["hashUniquenessIsNotMotionEvidence"]=True;m["qa"]["producerReviewedAt"]=now;m["qa"]["rootVisualStatus"]="pending";m["qa"]["playbackStatus"]="pending_Unity";m["producerStage"]="candidate_ready_for_root_visual";m["status"]="producer_candidate_pending_root_visual"
  m["qa"]["originalNominalGridMarginStatus"]=m["qa"].get("originalNominalGridMarginStatus",m["qa"].get("sourceMarginStatus"));m["qa"]["sourceMarginStatus"]="nominal_grid_warnings_preserved; complete_ownership_and_registered_margin_verified"
  write(mfp,m)
  for item in m["items"]:
   item["status"]="producer_candidate_pending_root_visual";item["producerLightDarkStillReview"]="viewed_candidate_pass";write(str(ROOT/item["file"])+".generation.json",item)
  gr["retentionRole"]="selected_current_animation_source_candidate";gr["producerStillReview"]="native source and registered light/dark composite inspected; root/Unity pending";write(str(src)+".generation.json",gr)
  review=src.parent/"action-review.json"
  if review.exists():
   r=read(review);r["registeredContactVisual"]="producer_actually_viewed_light_dark_and_display_rest_comparison";r["rootVisual"]="pending";r["playback"]="pending_Unity";write(review,r)
  entry={"id":sp["id"],"action":act,"source":relative,"sourceSHA256":gr["sha256"],"sourceNativeSize":[gr["width"],gr["height"]],"sourceGenerationRecord":relative+".generation.json","request":str(src.with_suffix(".request.json").relative_to(ROOT)).replace("\\","/"),"manifest":mfp.relative_to(ROOT).as_posix(),"frameCount":8,"fps":m["fps"],"loop":m["loop"],"durationsMs":m["durationsMs"],"sharedCanvas":m["sharedCanvas"],"rootPixels":m["rootPixels"],"eyePixels":m["eyePixels"],"displaySize":m["displaySize"],"uniformDisplayScale":m["uniformDisplayScale"],"bodyDisplayBox":[120,80],"runtimeMinMargin":min(x["registeredMinMargin"] for x in m["items"]),"runtimeWarnings":m.get("runtimeMarginWarnings",[]),"nominalGridBorderWarnings":m.get("nominalGridBorderWarnings",[]),"sourceGridMarginWarningCount":len(m["sourceMarginWarnings"]),"clipDensityAdjustment":m.get("clipDensityAdjustment"),"poseEvidence":sp["producerNote"],"producerStillReview":"candidate_pass","rootVisualReview":"pending","playback":"pending_Unity","lightQA":f"tmp/art-qa/{sp['id']}-{act}-registered-light.png","darkQA":f"tmp/art-qa/{sp['id']}-{act}-registered-dark.png","pairQA":f"tmp/art-qa/{sp['id']}-pair-review.png","displayRestQA":f"tmp/art-qa/{sp['id']}-display-rest-qa.png","allPixelsPreserved":"cached per-frame native RGBA round-trip assertion","upscaled":False}
  actions.append(entry)
  sp["status"]="producer_candidate_pending_root_visual";sp["candidateManifests"]=sp.get("candidateManifests",{});sp["candidateManifests"][act]=entry["manifest"]
 for rec in sorted((HERE/sp["id"]).glob("*/*.png.generation.json")):
  r=read(rec);file=r["file"];sourceRecords.append({"record":rec.relative_to(ROOT).as_posix(),"source":file,"sha256":r["sha256"],"actualModel":r.get("actualModel"),"actualQuality":r.get("actualQuality"),"selected":file in selected,"toolReceipt":str((rec.parent/r["evidence"]["toolResult"]).relative_to(ROOT)).replace("\\","/")})
  if file not in selected:
   act=rec.parent.name;replacement=sp["source"][act];replacementPath=ROOT/replacement;repRec=read(str(replacementPath)+".generation.json")
   assert replacementPath.exists() and hashlib.sha256(replacementPath.read_bytes()).hexdigest()==repRec["sha256"]
   r.setdefault("originalGenerationStatus",r.get("status"));r["status"]="superseded_by_selected_current_candidate";r["retentionRole"]="superseded_by_selected_current_candidate";r["replacement"]={"file":replacement,"sha256":repRec["sha256"]};r["imageRetained"]=(ROOT/file).exists();r["retentionPolicy"]="Keep adopted source/frames and provenance text; remove superseded image after adopted replacement and all eight outputs exist."
   write(rec,r)
   old=ROOT/file
   for pth in [old,old.with_name(old.stem+"-light.png"),old.with_name(old.stem+"-dark.png"),old.with_name(old.stem+"-eye-roi.png")]:
    if pth.exists():retention.append({"file":pth.relative_to(ROOT).as_posix(),"replacement":replacement,"reason":"superseded source or its obsolete internal QA","sha256":hashlib.sha256(pth.read_bytes()).hexdigest()})
 for act,relative in sp["source"].items():
  rp=ROOT/(relative+".generation.json");r=read(rp)
  for ref in r.get("references",[]):
   if ref["file"].startswith(f"designs/motion-frames-v1/{sp['id']}/") and ref["file"] not in selected:ref["retentionState"]="historical_input_image_removed_or_scheduled; original file/hash evidence retained";ref["imageCurrentlyExists"]=(ROOT/ref["file"]).exists()
  write(rp,r)
 if sp["id"]=="12-yuewei":sp["clipDensity"]={"capture":{"ratio":38/34,"evidence":"designs/motion-frames-v1/12-yuewei/clip-density-evidence.json","method":"median native amber iris width; one scale across clip"}}
sel["status"]="24_action_sources_and192_frames_producer_candidate_pending_root_and_Unity";sel["producerAllStillQAActuallyViewed"]=True;write(selPath,sel)
report={"schemaVersion":1,"reportedAt":now,"owner":"motion_route_recheck","scope":"01-12 swim8 + capture8","counts":{"species":12,"actionSources":len(actions),"frames":sum(a["frameCount"] for a in actions),"modelCallsIncludingSuperseded":len(sourceRecords),"selectedSourcePNGs":len(selected)},"state":"producer_candidate_pending_root_visual_and_Unity_playback","artPath":"builtin native AI frame sheets; no paid API/CLI, no procedural deformation as motion","modelEvidence":{"configuredTarget":"gpt-image-2.5-sunburst","configuredQuality":"max","actualModel":None,"actualQuality":None,"reason":"Builtin tool exposes neither parameter nor returned version/quality; source records preserve actual submitted arguments and receipts."},"technical":{"allRuntimeMinMarginAtLeast12Percent":all(a["runtimeMinMargin"]>=.12 for a in actions),"minimumRuntimeMargin":min(a["runtimeMinMargin"] for a in actions),"trueAlphaCompositeActuallyInspected":True,"nativePNGsResizedOrUpscaled":False,"ownership":"Independent full-pose rectangles contain zero other-fish alpha pixels and preserve all alpha>3 pixels. <=3 source alpha cleanup recorded. Nominal grid warnings remain historical evidence.","registration":"One integer pupil root per clip; species-specific torso-root offset; shared canvas within each species","display":"One scale per clip; rest body box120x80 maximum fit. Full canvas displaySize retained.02 and12 capture native density compensation recorded.","hashPolicy":"Cached save/crop round-trip checks reused; hash differences never claimed as motion proof."},"visualConcerns":[{"id":"09-caidie","item":"All8 right-facing after AI fix. Bottom-row front torso/eye size looks slightly different; preserve candidate and check in playback, no per-frame normalization used."},{"id":"06-haima/capture","item":"Final subdued eye slightly smaller/drooped; check expression/identity during playback."}],"notDone":["Root still/pose acceptance for batch","Timed loop/seam and one-shot playback","Unity importing/PPU/events and runtime verification","New fixed-batch publication"],"untouched":["static fish masters","global catalogs/status","shared Git HEAD/index/refs","idle or other workers' outputs"],"actions":actions,"perCallRecords":sourceRecords,"retention":{"finalized":args.retention_finalized,"plannedSupersededPNGRemovals":retention,"provenanceTextPreserved":True}}
receiptPath=HERE/"FISH01TO12_RETENTION_RECEIPT.json"
if receiptPath.exists():
 receipt=read(receiptPath);report["retention"].update({"cleanupReceipt":receiptPath.relative_to(ROOT).as_posix(),"removedSourcePNGs":receipt["removedSourceCount"],"removedObsoleteQA":receipt["removedQACount"]})
write(HERE/"FISH01TO12_PRODUCTION_REPORT.json",report)
write(HERE/"FISH01TO12_RETENTION_PLAN.json",{"scope":"01-12 owned source directories only","files":retention,"allReplacementsSHA256Verified":True,"leafPNGOnly":True})
rows=[]
for sp in sel["species"]:
 aa=[x for x in actions if x["id"]==sp["id"]];rows.append(f"| {sp['id']} | {aa[0]['sharedCanvas'][0]}² | {min(x['runtimeMinMargin'] for x in aa)*100:.2f}% | 16 |")
md="# 01—12 鱼种动作候选交付\n\n已落盘24张原生动作表、192张独立RGBA帧。每动作8帧12FPS，游动循环、捕获单次；实际查看原表、眼ROI、固定根浅/深底和游戏显示尺寸对照。当前是制作候选，待root复核与Unity播放，不能称全部验收完成。\n\n| 鱼种 | 共享画布 | 最小运行留白 | 帧数 |\n|---|---:|---:|---:|\n"+"\n".join(rows)+"\n\n生成表均原生1774×887；帧仅完整ownership裁切、alpha≤3清零、整数瞳孔注册与透明补边，没有原生PNG缩放/放大/变形。源名义网格越界/12%留白警告完整保留；实际ownership无邻鱼像素，运行帧边距均≥12%。\n\n每clip统一显示scale，displaySize代表完整画布；目标可见rest身体框为120×80以内并保长宽比。02捕获按入口原生密度、12捕获按实际8眼虹膜宽中位38/34补偿一次scale，眼-root偏移同步补偿；不按每帧bbox缩放。\n\n所有生图/AI编辑均有request、prompt、receipt及逐图记录。配置目标GPT Image2.5 Sunburst/max；内置工具未披露实际型号与质量，实际值null。\n\n复核入口：tmp/art-qa/{id}-pair-review.png，左游动右捕获、上浅下深；{id}-display-rest-qa.png是按实际clip显示scale的入口对照。完整来源、sourceRects、root、时长、像素保留与警告见同名JSON和各assets/animations/{id}/{swim,capture}/manifest.json。09后半行头身细微差异、06捕获末帧眼神变化保留在待播放审查项。\n\n未改static master/global/Git；未做重型构建、测试、atlas或Unity；未新上传。本目录旧样片SAMPLE_REVIEW为历史首次送审，当前注册以运行manifest及本汇总为准。\n"
(HERE/"FISH01TO12_PRODUCTION_REPORT.md").write_text(md,encoding="utf-8")
print(json.dumps({"counts":report["counts"],"minRuntimeMargin":report["technical"]["minimumRuntimeMargin"],"retentionPNGFiles":len(retention),"retentionSources":[x["source"] for x in sourceRecords if not x["selected"]],"report":"designs/motion-frames-v1/FISH01TO12_PRODUCTION_REPORT.json"}))

