from pathlib import Path
import datetime,hashlib,json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
banner=ROOT/'designs/production-v1/event-banner/event-banner.png'
if not banner.exists():
    recovered=Path('C:/Users/luyua/.codex/generated_images/01a17732-5ab6-7fe3-b0d9-546ecf65c47f/exec-8d43a414-176f-434a-8de2-d1d2681203cc.png')
    shutil.copyfile(recovered,banner)
    req=read(banner.parent/'event-banner.request.json');im=Image.open(banner)
    record={'schemaVersion':1,'file':banner.relative_to(ROOT).as_posix(),'sha256':sha(banner),'width':im.width,'height':im.height,'format':'PNG',
        'generatedAt':None,'startedAt':None,'recoveredAt':now,'sourceFileLastWriteUtc':datetime.datetime.fromtimestamp(recovered.stat().st_mtime,datetime.timezone.utc).isoformat(),
        'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'config/image-generation.json'),
        'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':req['referenced_image_paths']},
        'actualModel':None,'actualQuality':None,'unverifiedReason':'Original in-flight worker result was interrupted. Native output recovered from that worker image directory; result receipt and precise generation timestamps unavailable. Filename is not proof of returned model/quality.',
        'evidence':{'sourceOutput':str(recovered),'sourceOutputSha256':sha(recovered),'sourceFilenameId':recovered.stem,'toolResultId':None,'receiptStatus':'unavailable_after_interruption','recoveryNote':'event-banner.recovery.txt','request':'event-banner.request.json'},
        'prompt':'event-banner.prompt.txt','references':[{'file':str(Path(p).relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'role':'Saved submitted request: approved main UI style references and existing event artwork identity.'} for p in req['referenced_image_paths']],
        'resampled':False,'status':'visual_reviewed_pending_user_review',
        'visualReview':'Actual recovered native output inspected: gold-headband Daochild, white fox, pearl-shell net, bamboo rod and long-tail red-gold koi; clear left water area, no baked text or UI frame. Byte-identical recovered output, not a new call.'}
    write(Path(str(banner)+'.generation.json'),record)
    (banner.parent/'event-banner.recovery.txt').write_text('Recovered actual output after original worker interruption.\nSource: '+str(recovered)+'\nSHA256: '+sha(recovered)+'\nRecovery time: '+now+'\nNo original tool response receipt is available. Source filename retained for traceability only; generation time/model/quality not inferred. Saved request and original worker progress identified the banner task; visible image was checked against it.\n',encoding='utf-8')
out=ROOT/'assets/illustrations';out.mkdir(parents=True,exist_ok=True);items=[]
for ident,name,box in [('event-banner','灵海寻宝活动横幅',[960,400]),('event-route','灵海寻宝空节点岛图',[560,700])]:
    src=ROOT/f'designs/production-v1/{ident}/{ident}.png';dst=out/(ident+'.png');shutil.copyfile(src,dst);im=Image.open(src)
    e={'schemaVersion':1,'id':ident,'name':name,'file':dst.relative_to(ROOT).as_posix(),'width':im.width,'height':im.height,'sha256':sha(dst),'anchor':[0.5,0.5],'displaySize':box,
        'nativeSource':src.relative_to(ROOT).as_posix(),'derivedFrom':[{'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'generationRecord':src.relative_to(ROOT).as_posix()+'.generation.json'}],
        'operation':{'type':'byte_identical_copy','resized':False,'upscaled':False},'actualModel':None,'actualQuality':None,'status':'visual_reviewed_pending_user_and_client_review','visualReview':read(Path(str(src)+'.generation.json'))['visualReview']}
    if ident=='event-route':e['nodeCentersNormalized']=[[0.27,0.215],[0.735,0.322],[0.755,0.515],[0.275,0.62],[0.745,0.805]]
    write(Path(str(dst)+'.generation.json'),e);items.append(e)
write(out/'manifest.json',{'schemaVersion':1,'items':items,'warnings':[],'complete':True,'opaqueIllustrations':True,'nativeNoResampling':True})
print(json.dumps({'items':[{'file':e['file'],'size':[e['width'],e['height']],'sha256':e['sha256']} for e in items]},ensure_ascii=False))
