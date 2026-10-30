"""Prepare image-to-video job text and budget metadata. Never sends network requests."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
fish=read(ROOT/'docs/FISH_MOTION_BACKLOG.json');guide=read(ROOT/'docs/GUIDE_MOTION_BACKLOG.json')
jobs=[]
subjects=[{'id':e['id'],'name':e['name'],'identity':e['description'],'sourceSprite':e['sourceSprite'],'actions':e['actions']} for e in fish['entries']]
subjects.append({'id':'dao-child','name':'捕鱼道童','identity':guide['identity'],'sourceSprite':guide['sourceMaster'],'actions':guide['actions']})
for subject in subjects:
    source=ROOT/subject['sourceSprite'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
    for action in subject['actions']:
        ident=subject['id']+'/'+action['id'];folder=ROOT/'motion-jobs'/subject['id']/action['id'];folder.mkdir(parents=True,exist_ok=True)
        prompt=('The same '+subject['identity']+'. Match the supplied identity master exactly: same face, eye shape, silhouette, anatomy, costume, colors, gold decorations and all equipment. '+
                'Keep a fixed orthographic camera and the original facing, no camera pan, zoom, cut, turn or new objects. Preserve the refined Daoist chibi hand-painted appearance. '+
                action['motion']+' '+action.get('startAndEnd','Start and recover at the identical master-rest pose.')+' '+
                'Perform one complete readable action and its recovery within the middle four seconds, with stable rest poses at both ends. '+
                'Keep every extremity inside the frame with 20 percent clear safety margin. Body root and body height remain fixed; fins, tail, tentacles or limbs must articulate, not rigidly translate, rotate or scale the entire still. '+
                'No letters, text, UI, effects covering the body, additional fish, morphing face, changing held weapon, pasted checkerboard or background scenery. '+
                'The separate matte/framing input is prepared only after route approval; preserve its flat key background and cast no shadows on it.')
        (folder/'prompt.txt').write_text(prompt,encoding='utf-8')
        request={'schemaVersion':1,'id':ident,'name':subject['name']+' '+action['id'],'sourceMaster':subject['sourceSprite'],'sourceSha256':digest,
            'sourceGenerationRecord':subject['sourceSprite']+'.generation.json','identityStatus':'selected_current_master_pending_sample_review',
            'model':'grok-imagine-video','resolution':'720p','durationSeconds':6,'referenceInput':None,'lastFrameInput':None,
            'inputPreparationStatus':'pending_route_choice_and_fixed_matte_framing','prompt':str((folder/'prompt.txt').relative_to(ROOT)).replace('\\','/'),
            'targetClip':{'fps':action.get('plannedFps',16),'durationSeconds':action['durationSeconds'],'frames':action['plannedFrames'],
                'type':action['type'],'root':action['rootAnchorNormalized'],'preserveSharedCanvas':True,'allowUpscale':False},
            'route':'not_selected','status':'prepared_pending_video_route_authorization','submitted':False,'actualModel':None,'actualCostUsd':None,
            'acceptance':['Identity, appendages and equipment preserved','Articulated body/fin/limb motion, not full-image affine transform',
                'Fixed source registration and consistent height','Clean matte on ivory/dark-jade','Reviewed loop/recovery and clip timing','Native finished detail with no upscaled output']}
        write(folder/'job.json',request);jobs.append({'id':ident,'job':str((folder/'job.json').relative_to(ROOT)).replace('\\','/'),'prompt':request['prompt'],'source':subject['sourceSprite'],'status':request['status']})
pilot=['01-qingqi/swim','dao-child/idle'];single=6*0.07+0.002
plan={'schemaVersion':1,'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'81 planned fish, boss and guide actions; no call has been made.',
    'artSource':'image-to-video route pending; existing host-generated stills are identity references','jobCount':len(jobs),'jobs':jobs,
    'pilot':{'jobs':pilot,'maximumCalls':2,'generationSecondsPerCall':6,'resolution':'720p','proposedBudgetUsd':1,
        'estimatedOutputAndOneImageInputUsd':round(single*2,3),'authorizationStatus':'pending_user_reply','submitted':False},
    'pricing':{'source':'https://docs.x.ai/developers/models/grok-imagine-video','checkedOn':'2026-10-28','outputUsdPerSecond720p':0.07,'imageInputUsdEach':0.002,
        'onePass81JobsEstimateUsd':round(single*len(jobs),3),'threeTakesAllJobsEstimateUsd':round(single*len(jobs)*3,3),
        'notes':'Planning estimates only. Other billed input, provider changes and retries may alter total. Whole-batch spend has not been authorized.'},
    'credentials':'Not present. Configure only in the local provider credential store; never put keys in a chat, job file, project or public repository.',
    'capabilityEvidence':'docs/MOTION_CAPABILITY_20261028.json','status':'prepared_not_generated','gameArtComplete':False}
write(ROOT/'docs/MOTION_BATCH_EXECUTION_PLAN.json',plan)
print(json.dumps({'jobs':len(jobs),'pilot':plan['pilot'],'pricing':plan['pricing'],'submitted':False},ensure_ascii=False))
