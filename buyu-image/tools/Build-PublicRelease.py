"""Freeze an accepted current art tree into a new immutable release directory."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil
from ArtAcceptanceState import accepted_unchanged
ROOT=Path(__file__).resolve().parent.parent
EXCLUDED={'.git','.cache','.venv','.work','__pycache__','node_modules','tmp','Library','Logs','Temp','UserSettings','Obj','Build','Builds','.vs','.idea'}
TOP={'.gitignore','AGENTS.md','README.md','assets','assets-preview','config','designs','docs','gallery','references','tools','unity'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);args=parser.parse_args()
 if not re.fullmatch(r'[a-z0-9-]{4,64}',args.batch):raise SystemExit('Invalid fixed batch label')
 stage=ROOT/'tmp'/args.batch
 if stage.exists():raise SystemExit('Fixed batch already exists; never hot-swap or rebuild it.')
 status=read(ROOT/'docs/GAME_ART_STATUS.json');final=read(ROOT/'docs/UNITY_FINAL_ACCEPTANCE.json')
 if not status.get('gameArtComplete') or not final.get('accepted') or status['nativeAnimations']['releaseReadyActions']!=81:raise SystemExit('Full art acceptance has not passed; do not publish as complete.')
 if not accepted_unchanged(ROOT):raise SystemExit('Accepted production input hashes have changed; repeat affected acceptance before publishing.')
 secret=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|sk-[A-Za-z0-9_-]{30,})')
 sources=[];total=0
 candidates=[]
 for directory,folders,names in os.walk(ROOT):
  folders[:]=sorted(f for f in folders if f not in EXCLUDED and (Path(directory)!=ROOT or f in TOP))
  candidates.extend(Path(directory)/name for name in names)
 for source in sorted(candidates):
  rp=source.relative_to(ROOT)
  if rp.parts[0] not in TOP or any(x in EXCLUDED for x in rp.parts) or not source.is_file():continue
  if source.is_symlink():raise SystemExit('Symlink refused: '+str(rp))
  if source.suffix.lower() in ['.pyc','.log','.pem','.pfx','.p12','.key','.csproj','.sln','.slnx','.pidb','.mdb','.pdb']:continue
  if source.name.startswith('.env') and source.name!='.env.example':continue
  if rp.as_posix() in ['docs/PUBLIC_UPLOAD_RECEIPT_CURRENT.json','docs/PUBLIC_CONTENT_AUDIT_CURRENT.json','docs/PUBLIC_RELEASE_MANIFEST.json']:continue
  size=source.stat().st_size
  if size>100*1024*1024:raise SystemExit('GitHub file size limit: '+str(rp))
  if source.suffix.lower() in ['.json','.txt','.md','.cs','.js','.py','.ps1','.html','.css','.yml','.yaml','.toml']:
   if secret.search(source.read_bytes()):raise SystemExit('Potential credential: '+str(rp))
  if source.open('rb').read(64).startswith(b'version https://git-lfs.github.com/spec/v1'):raise SystemExit('LFS pointer: '+str(rp))
  sources.append((source,rp));total+=size
 stage.mkdir(parents=True)
 files=[]
 for source,rp in sources:
  target=stage/'buyu-image'/rp;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  digest=sha(source)
  if sha(target)!=digest:raise SystemExit('Copy mismatch: '+str(rp))
  files.append({'file':target.relative_to(stage).as_posix(),'bytes':target.stat().st_size,'sha256':digest})
 readme='# 灵海仙渔\n\n道家Q版捕鱼首发美术与Unity接入验收工程，位于 [buyu-image/](buyu-image/README.md)。\n\n31项UI设计、276项静态/FX资源、81套648张动作帧，共924项运行PNG。实际Unity技术/播放/画面验收范围见 [最终验收](buyu-image/docs/UNITY_FINAL_ACCEPTANCE.json)。美术完成不表示联网、经济或商业游戏服务已实现。\n\n当前文件树采用单个无父提交；未自动附加开源许可。字体按随包OFL许可。固定字节清单为PUBLIC_RELEASE_MANIFEST.json。\n'
 (stage/'README.md').write_text(readme,encoding='utf-8')
 (stage/'.gitignore').write_text('**/tmp/\n**/Library/\n**/Logs/\n**/Temp/\n**/UserSettings/\n**/__pycache__/\n**/*.pyc\n**/.env\n',encoding='utf-8')
 for name in ['README.md','.gitignore']:
  p=stage/name;files.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p)})
 files.sort(key=lambda x:x['file']);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 manifest={'schemaVersion':2,'frozenAt':stamp,'repository':'https://github.com/lhl-java/luhailong-python','branch':'main','projectPrefix':'buyu-image/','gameArtComplete':True,'uiDesigns':31,'independentAssets':924,'staticAndFxAssets':276,'motionActionsAccepted':81,'motionPngFrames':648,'fileCountExcludingThisManifest':len(files),'bytesExcludingThisManifest':sum(x['bytes'] for x in files),'manifestSelfExcluded':True,'files':files}
 write(stage/'PUBLIC_RELEASE_MANIFEST.json',manifest)
 meta={'stage':str(stage),'manifestSha256':sha(stage/'PUBLIC_RELEASE_MANIFEST.json'),'filesIncludingManifest':len(files)+1,'bytesIncludingManifest':sum(x['bytes'] for x in files)+(stage/'PUBLIC_RELEASE_MANIFEST.json').stat().st_size,'fixedAt':stamp,'upstreamExpectedCommit':status['publishedBatch']['commit']}
 write(ROOT/'tmp/public-release-meta-current.json',meta)
 write(ROOT/'docs/PUBLIC_CONTENT_AUDIT_CURRENT.json',{'checkedAt':stamp,'fileCount':len(files),'candidateBytes':total,'blockingCredentialsDetected':False,'lfsPointerCount':0,'symlinkFiles':[],'fixedBatch':str(stage),'fullArtAcceptanceRequired':True})
 print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':main()
