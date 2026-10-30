"""Uniformly pad complete native-alpha FX frames without resampling or hiding cut edges."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--pad',type=int,default=40);args=p.parse_args()
mp=ROOT/'assets/fx'/args.id/'manifest.json';manifest=read(mp)
if manifest.get('warnings'):raise SystemExit('Do not pad a sheet with unresolved border warnings')
result=[]
for e in manifest['items']:
    fp=ROOT/e['file'];frame=Image.open(fp).convert('RGBA')
    if e['operation'].get('runtimeTransparentPadding'):
        if e['operation']['runtimeTransparentPadding']!=[args.pad]*4:raise SystemExit('Existing padding mismatch')
        result.append(e);continue
    old_size=list(frame.size);a=frame.getchannel('A');edges=[a.crop((0,0,frame.width,1)),a.crop((0,frame.height-1,frame.width,frame.height)),a.crop((0,0,1,frame.height)),a.crop((frame.width-1,0,frame.width,frame.height))]
    if max(s.getextrema()[1] for s in edges)>16:raise SystemExit('Padding may not conceal clipped edge: '+e['id'])
    pixel_hash=hashlib.sha256(frame.tobytes()).hexdigest();old_file_sha=sha(fp)
    padded=Image.new('RGBA',(frame.width+2*args.pad,frame.height+2*args.pad),(0,0,0,0));padded.paste(frame,(args.pad,args.pad))
    if padded.crop((args.pad,args.pad,args.pad+frame.width,args.pad+frame.height)).tobytes()!=frame.tobytes():raise SystemExit('Native source pixels changed')
    padded.save(fp);e['sha256']=sha(fp);e['width']=padded.width;e['height']=padded.height
    old_anchor=e.get('anchor',[0.5,0.5]);e['anchor']=[(old_anchor[0]*frame.width+args.pad)/padded.width,(old_anchor[1]*frame.height+args.pad)/padded.height]
    e['operation']['type']='native_grid_crop_then_uniform_transparent_padding'
    e['operation']['nativeExtractedFrameSize']=old_size;e['operation']['nativeExtractedFramePngSha256']=old_file_sha;e['operation']['nativeExtractedRgbaPixelsSha256']=pixel_hash
    e['operation']['runtimeTransparentPadding']=[args.pad]*4;e['operation']['paddingOrder']='left,top,right,bottom';e['operation']['paddingResampled']=False;e['operation']['sourcePixelsRoundtripIdentical']=True
    e['operation']['paddingReason']='Provide runtime safe empty border; source cell margin contract remains separately reported, not reclassified as passed.'
    e['operation']['nativeDetailClaim']='New canvas dimension is transparent padding only; source native detail remains '+str(old_size)
    e['status']='prepared_pending_visual_review';write(Path(str(fp)+'.generation.json'),e);result.append(e)
manifest['items']=result;manifest['runtimeTransparentPadding']=[args.pad]*4;manifest['paddingPreservesAllNativePixels']=True;write(mp,manifest)
print(json.dumps({'manifest':mp.relative_to(ROOT).as_posix(),'frames':len(result),'fixedCanvas':list(padded.size) if 'padded' in locals() else [result[0]['width'],result[0]['height']],'padding':args.pad,'nativePixelsUnchanged':True}))
