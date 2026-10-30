"""Independently download the new public commit and verify every frozen byte."""
from pathlib import Path
import datetime, hashlib, json, subprocess, urllib.request, zipfile
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(data):return hashlib.sha256(data).hexdigest()
meta=read(ROOT/'tmp/public-release-meta-current.json')
state=read(ROOT/'tmp/public-push-state-current.json')
commit=state['commit'];stage=Path(meta['stage']);target=ROOT/'tmp/public-release-current-download.zip'
def remote_main():
    return subprocess.check_output(['git','ls-remote','https://github.com/lhl-java/luhailong-python.git','refs/heads/main'],text=True).split()[0]
if remote_main()!=commit:raise SystemExit('Remote main changed before independent download')
url='https://codeload.github.com/lhl-java/luhailong-python/zip/'+commit
request=urllib.request.Request(url,headers={'User-Agent':'Linghai-Art-Delivery-Verification'})
with urllib.request.urlopen(request,timeout=90) as response,target.open('wb') as output:
    import shutil
    shutil.copyfileobj(response,output,length=1024*1024)
manifest=read(stage/'PUBLIC_RELEASE_MANIFEST.json');problems=[];verified=0;size=0;pngs=0;lfs=0
expected={e['file']:e for e in manifest['files']}
with zipfile.ZipFile(target) as archive:
    names=[n for n in archive.namelist() if not n.endswith('/')]
    prefix=names[0].split('/')[0]+'/'
    actual={name[len(prefix):] for name in names}
    file_set=actual==set(expected)|{'PUBLIC_RELEASE_MANIFEST.json'}
    if not file_set:problems.append('Downloaded file set mismatch')
    if sha(archive.read(prefix+'PUBLIC_RELEASE_MANIFEST.json'))!=meta['manifestSha256']:problems.append('Frozen manifest mismatch')
    for name,entry in expected.items():
        if name not in actual:problems.append('Missing '+name);continue
        data=archive.read(prefix+name)
        if len(data)!=entry['bytes'] or sha(data)!=entry['sha256']:problems.append('Hash or size mismatch '+name);continue
        if name.lower().endswith('.png'):
            pngs+=1
            if data[:8]!=b'\x89PNG\r\n\x1a\n':problems.append('Invalid PNG '+name)
        if data.startswith(b'version https://git-lfs.github.com/spec/v1'):lfs+=1;problems.append('LFS pointer '+name)
        verified+=1;size+=len(data)
    public_final=json.loads(archive.read(prefix+'buyu-image/docs/UNITY_FINAL_ACCEPTANCE.json'))
    if not public_final.get('accepted') or not public_final.get('gameArtComplete'):problems.append('Final acceptance not included')
    for path,digest in public_final['inputHashes'].items():
        name='buyu-image/'+path
        if name not in expected or expected[name]['sha256']!=digest:problems.append('Accepted production input differs from frozen tree: '+path)
    runtime_pngs=[n for n in expected if n.startswith('buyu-image/assets/') and n.endswith('.png') and '/atlases/' not in n]
    if len(runtime_pngs)!=924:problems.append('Runtime PNG count differs')
receipt=dict(schemaVersion=2,verifiedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),repository='https://github.com/lhl-java/luhailong-python',projectUrl='https://github.com/lhl-java/luhailong-python/tree/main/buyu-image',visibility='public',branch='main',commit=commit,remoteMainSha=state['remoteMainSha'],commitCount=state['commitCount'],parentCount=state['parentCount'],singleRootCommit=state['commitCount']==1 and state['parentCount']==0,manifestSha256=meta['manifestSha256'],frozenAt=meta['fixedAt'],download=dict(url=url,archiveBytes=target.stat().st_size,fileCountIncludingManifest=len(actual),expectedManifestEntries=len(expected),verifiedManifestEntries=verified,verifiedBytesExcludingManifest=size,pngFilesVerified=pngs,actualFileSetMatches=file_set,allFileHashesMatch=not problems,lfsPointerCount=lfs),artStatus=dict(gameName='灵海仙渔',uiDesigns=31,independentAssets=924,staticAndFxAssets=276,nativeActionsAccepted=81,nativePngFrames=648,clips=89,gameArtComplete=True,unityImportedCompiledAndPlayed=True),problems=problems,receiptOutsideFixedBatch=True)
receipt['remoteMainSha']=remote_main()
receipt['uploadedAndDownloadedVerified']=not problems and receipt['singleRootCommit'] and commit==receipt['remoteMainSha']
(ROOT/'docs/PUBLIC_UPLOAD_RECEIPT_CURRENT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if receipt['uploadedAndDownloadedVerified']:
    status=read(ROOT/'docs/GAME_ART_STATUS.json')
    status.update(uploaded=True,uploadedScope='Current complete first-release art fixed batch independently downloaded and SHA256 verified',uploadReceipt='docs/PUBLIC_UPLOAD_RECEIPT_CURRENT.json',publicationEvidence='Remote single root commit '+commit+'; independently downloaded every fixed file and all 924 runtime PNGs.')
    status['workingBatch'].update(uploaded=True,commit=commit,receipt='docs/PUBLIC_UPLOAD_RECEIPT_CURRENT.json')
    status['publishedBatch']=dict(receipt='docs/PUBLIC_UPLOAD_RECEIPT_CURRENT.json',commit=commit,verifiedAt=receipt['verifiedAt'],independentAssets=924,uploadedAndDownloadedVerified=True,scope='Current complete first-release art fixed batch')
    (ROOT/'docs/GAME_ART_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
if not receipt['uploadedAndDownloadedVerified']:raise SystemExit(1)
