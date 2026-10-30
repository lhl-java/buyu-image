"""Verify public GitHub archive bytes against the immutable published manifest."""
from pathlib import Path,PurePosixPath
import datetime,hashlib,json,urllib.request,zipfile
ROOT=Path(__file__).resolve().parent.parent
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
meta=read(ROOT/'tmp/public-release-meta.json');stage=Path(meta['stage']);state=read(ROOT/'tmp/public-push-state.json');commit=state['commit']
target=ROOT/'tmp/public-release-download.zip'
url='https://codeload.github.com/lhl-java/luhailong-python/zip/'+commit
urllib.request.urlretrieve(url,target)
manifest=read(stage/'PUBLIC_RELEASE_MANIFEST.json');problems=[];verified=0;checked_bytes=0;png_count=0
with zipfile.ZipFile(target) as archive:
    files=[n for n in archive.namelist() if not n.endswith('/')]
    prefix=files[0].split('/')[0]+'/'
    expected={e['file']:e for e in manifest['files']}
    actual={n[len(prefix):] for n in files}
    if actual!=set(expected)|{'PUBLIC_RELEASE_MANIFEST.json'}:problems.append('Downloaded file set mismatch')
    remote_manifest=archive.read(prefix+'PUBLIC_RELEASE_MANIFEST.json')
    if sha(remote_manifest)!=meta['manifestSha256']:problems.append('Published manifest hash mismatch')
    for file,e in expected.items():
        if file not in actual:problems.append('Missing '+file);continue
        data=archive.read(prefix+file)
        if len(data)!=e['bytes'] or sha(data)!=e['sha256']:problems.append('Bytes/hash mismatch '+file);continue
        if file.lower().endswith('.png'):
            png_count+=1
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):problems.append('PNG is not native PNG '+file)
        if data.startswith(b'version https://git-lfs.github.com/spec/v1\n'):problems.append('LFS pointer '+file)
        verified+=1;checked_bytes+=len(data)
receipt={'schemaVersion':1,'verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'repository':'https://github.com/lhl-java/luhailong-python','projectUrl':'https://github.com/lhl-java/luhailong-python/tree/main/buyu-image',
    'visibility':'public','branch':'main','commit':commit,'commitCount':state['commitCount'],'parentCount':state['parentCount'],
    'remoteMainSha':state['remoteMainSha'],'remoteShaMatches':commit==state['remoteMainSha'],
    'singleRootCommit':state['commitCount']==1 and state['parentCount']==0,
    'manifestSha256':meta['manifestSha256'],'frozenAt':meta['fixedAt'],
    'download':{'url':url,'archiveBytes':target.stat().st_size,'fileCountIncludingManifest':len(actual),'verifiedManifestEntries':verified,
        'expectedManifestEntries':len(expected),'verifiedBytesExcludingManifest':checked_bytes,'pngFilesVerified':png_count,
        'actualFileSetMatches':actual==set(expected)|{'PUBLIC_RELEASE_MANIFEST.json'},'allFileHashesMatch':not problems,
        'lfsPointerCount':sum(p.startswith('LFS pointer') for p in problems)},
    'artStatus':{'uiDesigns':31,'independentAssets':225,'motionActionsPending':81,'gameArtComplete':False},
    'problems':problems,'uploadedAndDownloadedVerified':not problems and commit==state['remoteMainSha'] and state['commitCount']==1 and state['parentCount']==0,
    'receiptOutsideFixedBatch':True}
(ROOT/'docs/PUBLIC_UPLOAD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
if not receipt['uploadedAndDownloadedVerified']:raise SystemExit(1)
