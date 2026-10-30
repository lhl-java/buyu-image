"""Metadata progress only; never infer motion approval from file count."""
from pathlib import Path
import datetime,json
from ArtAcceptanceState import preserve_accepted
ROOT=Path(__file__).resolve().parent.parent
if preserve_accepted(ROOT): raise SystemExit(0)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
plan=read(ROOT/'docs/NATIVE_FRAME_JOBS_20261028.json');rows=[]
for job in plan['jobs']:
    if job['characterId'][:2].isdigit() and int(job['characterId'][:2])>=31 or job['characterId']=='dao-child' and job['action'] in ['point','celebrate']:job['owner']='root'
write(ROOT/'docs/NATIVE_FRAME_JOBS_20261028.json',plan)
for job in plan['jobs']:
    path=ROOT/job['outputFolder']/'manifest.json';row={'id':job['id'],'owner':job['owner'],'plannedFrames':job['frames'],'manifest':path.relative_to(ROOT).as_posix(),'exportedFrames':0,'status':'native_source_or_export_pending','releaseReady':False}
    if path.is_file():
        m=read(path);row.update({'exportedFrames':len(m.get('items',[])),'status':m.get('status','unknown_candidate_status'),'releaseReady':m.get('releaseReady',False),'qa':m.get('qa',{})})
    rows.append(row)
progress={'schemaVersion':1,'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plannedActions':len(rows),'plannedFrames':sum(r['plannedFrames'] for r in rows),'exportedCandidateActions':sum(r['exportedFrames']==r['plannedFrames'] for r in rows),'exportedCandidateFrames':sum(r['exportedFrames'] for r in rows),'releaseReadyActions':sum(r['releaseReady'] for r in rows),'countEvidence':'Current per-action manifests read; aggregate file/pixel checks and actual motion playback not performed by this metadata step.','actions':rows,'gameArtComplete':False}
write(ROOT/'docs/NATIVE_FRAME_PROGRESS.json',progress)
status=read(ROOT/'docs/GAME_ART_STATUS.json');status['updatedAt']=progress['updatedAt'];status['workingBatch']['frameProgress']='docs/NATIVE_FRAME_PROGRESS.json';status['workingBatch']['exportedCandidateActions']=progress['exportedCandidateActions'];status['workingBatch']['exportedCandidateFrames']=progress['exportedCandidateFrames'];status['workingBatch']['motionReleaseReadyActions']=progress['releaseReadyActions'];status['workingBatch']['uploaded']=False
status['problems']=[p for p in status.get('problems',[]) if not isinstance(p,dict) or p.get('id')!='static_fish_rectangular_backing']
status['reviewCorrections']=[{'id':'raw_view_transparent_rgb_false_positive','status':'corrected','evidence':'31–36 original master corner alpha=0; 25–30 confirmed by worker. Raw view exposed RGB stored under transparent alpha. Actual matte compositing is required for opacity review; no rectangular backing defect confirmed and no replacement required.'}]
for r in status['remaining']:
    if r['id'] in ['fish-motion','guide-motion']:
        subset=[x for x in rows if x['id'].startswith('dao-child/')==(r['id']=='guide-motion')];r['exportedCandidateActions']=sum(x['exportedFrames']==x['plannedFrames'] for x in subset);r['completedActions']=sum(x['releaseReady'] for x in subset)
write(ROOT/'docs/GAME_ART_STATUS.json',status)
print(json.dumps({k:v for k,v in progress.items() if k not in ['actions']},ensure_ascii=False))
