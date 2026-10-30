"""Write deterministic ownership/job contracts for the user-selected native frame workflow."""
from pathlib import Path
import datetime,json
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
fish=read(ROOT/'docs/FISH_MOTION_BACKLOG.json');guide=read(ROOT/'docs/GUIDE_MOTION_BACKLOG.json');catalog=read(ROOT/'assets/runtime-catalog.json');byFile={e['file']:e for e in catalog['assets']}
jobs=[]
for e in fish['entries']:
    n=int(e['id'].split('-')[0]);worker='motion_route_recheck' if n<=12 else 'ui_state_preview' if n<=24 else 'whole_game_gap_audit'
    for a in e['actions']:
        owner='root' if a['id'] in ['attack','enrage'] else worker
        jobs.append({'id':e['id']+'/'+a['id'],'characterId':e['id'],'name':e['name'],'action':a['id'],'owner':owner,
            'sourceMaster':e['sourceSprite'],'sourceGenerationRecord':e['sourceGenerationRecord'],'identity':e['description'],
            'frames':a['plannedFrames'],'fps':a['plannedFps'],'loop':a['type']=='loop','durationSeconds':a['durationSeconds'],
            'displayBox':byFile[e['sourceSprite']].get('displayBox',byFile[e['sourceSprite']]['displaySize']),
            'sourceFolder':'designs/motion-frames-v1/'+e['id']+'/'+a['id'],
            'outputFolder':'assets/animations/'+e['id']+'/'+a['id'],'status':'pilot_in_progress' if e['id'] in ['01-qingqi','13-yunwengui'] and a['id']=='swim' else 'awaiting_pilot_review'})
for a in guide['actions']:
    jobs.append({'id':'dao-child/'+a['id'],'characterId':'dao-child','name':'捕鱼道童','action':a['id'],'owner':'whole_game_gap_audit',
        'sourceMaster':guide['sourceMaster'],'sourceGenerationRecord':guide['sourceGenerationRecord'],'identity':guide['identity'],
        'frames':a['plannedFrames'],'fps':a['plannedFps'],'loop':a['type']=='loop','durationSeconds':a['durationSeconds'],'displayBox':[280,280],
        'sourceFolder':'designs/motion-frames-v1/dao-child/'+a['id'],'outputFolder':'assets/animations/dao-child/'+a['id'],
        'status':'pilot_in_progress' if a['id']=='idle' else 'awaiting_pilot_review'})
plan={'schemaVersion':1,'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'referenceRepository':'https://github.com/0x0funky/agent-sprite-forge',
    'selectedRoute':'builtin image_gen directly generated articulated action frames','selectionEvidence':'Explicit user instruction on2026-10-28; video route not required and no separately billed video call authorized.',
    'contract':'docs/ANIMATION_FRAME_CONTRACT.md','expectedActions':81,'expectedPngFrames':sum(j['frames'] for j in jobs),'jobs':jobs,
    'unity':{'projectDirectory':'unity/','createAfter':'all native action art and static/FX resources ready','status':'not_created_yet','note':'User explicitly requested this task to create Unity project after art, no missing external client prerequisite.'},
    'aggregateQaStatus':'deferred_until_shared_heavy_work_slot_returned','gameArtComplete':False}
(ROOT/'docs/NATIVE_FRAME_JOBS_20261028.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'actions':len(jobs),'frames':plan['expectedPngFrames'],'owners':sorted(set(j['owner'] for j in jobs))}))
