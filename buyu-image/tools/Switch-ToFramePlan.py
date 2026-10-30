"""Apply the user's explicit native image-frame route; no generation or paid calls."""
from pathlib import Path
import datetime,json
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
fish=read(ROOT/'docs/FISH_MOTION_BACKLOG.json')
fish['generationContract']='User-selected native image-generated action sheets, cut and registered as PNG frames; video optional, not a prerequisite. See ANIMATION_FRAME_CONTRACT.md.'
fish['status']='native_frame_production_in_progress';fish['methodChoice']={'date':'2026-10-28','route':'builtin image_gen native action sheets','reference':'https://github.com/0x0funky/agent-sprite-forge','selectedBy':'explicit_user_instruction','videoApiAuthorized':False}
for e in fish['entries']:
    e['status']='pending_native_frame_generation'
    for a in e['actions']:
        a.setdefault('previousVideoSamplingPlan',{'fps':a['plannedFps'],'frames':a['plannedFrames'],'durationSeconds':a['durationSeconds']})
        frames=8
        slow=e['id'] in ['06-haima','13-yunwengui','14-huanyue','26-moyu','30-jinjia','33-xuanwu','36-xuanjing']
        fps=12 if a['id']=='capture' else (8 if slow or a['id']=='enrage' else 10 if a['id']=='attack' else 12)
        a['plannedFrames']=frames;a['plannedFps']=fps;a['durationSeconds']=frames/fps;a['status']='pending_native_frame_generation'
        a['generationRoute']='builtin_native_action_sheet';a['output']=None
        a['acceptance']=[s for s in a['acceptance'] if 'static-sheet claim' not in s]
        a['acceptance']+=['Real articulated pose changes across native generated frames, not full-image affine transforms','Every frame physically contained and registered on one source scale','Actual loop/recovery review; a hash difference alone is not a motion pass']
write(ROOT/'docs/FISH_MOTION_BACKLOG.json',fish)
guide=read(ROOT/'docs/GUIDE_MOTION_BACKLOG.json');guide['status']='native_frame_production_in_progress';guide['generationRoute']='builtin_native_action_sheets_per_explicit_user_choice'
for a in guide['actions']:
    a.setdefault('previousVideoSamplingPlan',{'fps':a['plannedFps'],'frames':a['plannedFrames'],'durationSeconds':a['durationSeconds']})
    a['plannedFrames']=8;a['plannedFps']=8 if a['id']=='idle' else 10;a['durationSeconds']=8/a['plannedFps'];a['status']='pending_native_frame_generation'
    a['acceptance']=[s for s in a['acceptance'] if 'One image-to-video' not in s]+['Actual native articulated pose frames, not affine transforms of the entire still','Fixed source scale and shared root throughout sheet and across actions']
write(ROOT/'docs/GUIDE_MOTION_BACKLOG.json',guide)
oldplan=read(ROOT/'docs/MOTION_BATCH_EXECUTION_PLAN.json');oldplan['status']='superseded_by_user_native_frame_sheet_route';oldplan['supersededAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();oldplan['pilot']['authorizationStatus']='no_paid_route_selected_user_requested_frame_art';oldplan['supersedingContract']='docs/ANIMATION_FRAME_CONTRACT.md';write(ROOT/'docs/MOTION_BATCH_EXECUTION_PLAN.json',oldplan)
status=read(ROOT/'docs/GAME_ART_STATUS.json');status['gameArtComplete']=False;status['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();status['capability']['motionRoute']='builtin image_gen native action sheets, explicitly chosen by user';status['capability']['videoNoLongerRequired']=True
for gate in status['remaining']:
    if gate['id'] in ['fish-motion','guide-motion']:gate['status']='native_frame_production_in_progress'
    elif gate['id']=='client-art-validation':gate['status']='unity_project_after_art_completion_per_user_instruction'
status['workingBatch']={'contract':'docs/ANIMATION_FRAME_CONTRACT.md','staticAndFxTargetPngCount':276,'motionActions':81,'plannedMotionPngFrames':sum(a['plannedFrames'] for e in fish['entries'] for a in e['actions'])+sum(a['plannedFrames'] for a in guide['actions']),
    'uiStateRegistration':'config/ui-state-registration.json','fontPackage':'assets/fonts/fonts.json','aggregateValidation':'deferred_during_shared_heavy_work_slot'}
write(ROOT/'docs/GAME_ART_STATUS.json',status)
print(json.dumps({'fishActions':sum(len(e['actions']) for e in fish['entries']),'guideActions':len(guide['actions']),'plannedPngFrames':status['workingBatch']['plannedMotionPngFrames'],'method':'native_frame_sheet','paidCalls':0},ensure_ascii=False))
