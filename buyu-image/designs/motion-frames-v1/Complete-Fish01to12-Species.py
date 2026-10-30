"""Finish one manually eye-reviewed species (two clips), fixed native game frames only."""
from pathlib import Path
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("id");p.add_argument("--pupil-visual-confirmed",action="store_true");a=p.parse_args()
if not a.pupil_visual_confirmed:raise ValueError("Need actual pupil ROI view before finish")
sel=json.loads((HERE/"FISH01TO12_SELECTION.json").read_text());sp=next(x for x in sel["species"] if x["id"]==a.id);plan=json.loads((HERE/a.id/"species-review-plan.json").read_text())
if plan["ownershipWarnings"]:raise ValueError("Unresolved ownership; do not hide behind padding")
for action,rel in sp["source"].items():
 src=ROOT/rel;args=[sys.executable,str(HERE/"Finalize-Fish01to12.py"),str(src),"--id",a.id,"--action",action,"--canvas",str(plan["canvas"]),"--eye-offset",*map(str,sp["eyeOffset"]),"--pupil-visual-confirmed","--producer-note",sp["producerNote"]+" Actual native/pupil ROI inspected. Root visual and Unity playback pending."]
 if action=="capture":args+=["--reference",f"assets/animations/{a.id}/swim/manifest.json"]
 if action=="capture" and a.id=="02-jinwei":args+=["--match-rest-density"]
 if action=="capture" and a.id=="12-yuewei":
  ev=HERE/a.id/"clip-density-evidence.json";density=json.loads(ev.read_text(encoding="utf-8"));args+=["--density-ratio",str(density["uniformCaptureSourceDensityRatio"]),"--density-evidence",ev.relative_to(ROOT).as_posix()]
 r=subprocess.run(args,check=True,capture_output=True,text=True);print(r.stdout.strip())
plan["actualPupilVisual"]="producer_inspected_combined_ROI";plan["registeredContactVisual"]="pending_actual_view";(HERE/a.id/"species-review-plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
r=subprocess.run([sys.executable,str(HERE/"Review-Fish01to12-Species.py"),a.id],check=True,capture_output=True,text=True);print(r.stdout.strip())

