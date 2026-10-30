"""Read small native UI PNG alpha masks and write candidate registration metadata only.

No source PNG is rewritten, resized, rendered or copied. This is not runtime approval.
"""
from pathlib import Path
import argparse, datetime, json, math
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
STATUS='candidate_pending_visual_runtime_review'
GROUPS=[
    {'id':'primary','prefix':'ui/buttons/','reference':'normal','states':['normal','pressed','disabled','selected'],'bodyDisplayBox':[280,100],'contentInsets':[58,20,58,20],'hitShape':'rounded_rect'},
    {'id':'secondary','prefix':'ui/buttons/','reference':'normal','states':['normal','pressed','disabled','selected'],'bodyDisplayBox':[248,88],'contentInsets':[58,20,58,20],'hitShape':'rounded_rect'},
    {'id':'tab','prefix':'ui/buttons/','reference':'normal','states':['normal','selected'],'bodyDisplayBox':[220,82],'contentInsets':[42,18,42,18],'hitShape':'rounded_rect'},
    {'id':'close','prefix':'ui/buttons/','reference':'normal','states':['normal','pressed'],'bodyDisplayBox':[56,56],'contentInsets':[40,40,40,40],'hitShape':'ellipse'},
    {'id':'slot','prefix':'ui/hud/','reference':'normal','states':['normal','selected','locked','empty'],'bodyDisplayBox':[112,112],'contentInsets':[24,24,24,24],'hitShape':'rounded_rect'},
    {'id':'toggle','prefix':'ui/hud/','reference':'off','states':['off','on'],'bodyDisplayBox':[88,44],'contentInsets':[18,18,18,18],'hitShape':'rounded_rect'},
    {'id':'checkbox','prefix':'ui/hud/','reference':'off','states':['off','on'],'bodyDisplayBox':[38,38],'contentInsets':[24,24,24,24],'hitShape':'rounded_rect'},
    {'id':'slider-thumb','prefix':'ui/additions/','reference':'normal','states':['normal','pressed'],'bodyDisplayBox':[40,40],'contentInsets':[72,72,72,72],'hitShape':'ellipse'},
]

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def xywh(rect):return [rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]]
def centered(rect):return [(rect[0]+rect[2])/2,(rect[1]+rect[3])/2]
def pxround(value):return math.floor(value+0.5)
def inset(rect,dist):
    l,t,r,b=dist
    return [rect[0]+l,rect[1]+t,rect[2]-r,rect[3]-b]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',default='config/ui-state-registration.json')
    args=p.parse_args();output=(ROOT/args.output).resolve()
    if not output.is_relative_to(ROOT):raise SystemExit('Output must remain inside project')
    entries={}
    for manifest in ['assets/ui/buttons/manifest.json','assets/ui/hud/manifest.json','assets/ui/additions/manifest.json']:
        for e in read(ROOT/manifest)['items']:
            local=e['file'].removeprefix('assets/').removesuffix('.png')
            entries[local]=e
    families=[];warnings=[]
    for group in GROUPS:
        states=[]
        for state in group['states']:
            ident=group['prefix']+group['id']+'-'+state;e=entries[ident]
            with Image.open(ROOT/e['file']) as im:
                alpha=im.convert('RGBA').getchannel('A')
                if im.size!=(e['width'],e['height']):raise ValueError('Manifest dimensions changed: '+ident)
                boxes={str(t):alpha.point(lambda v:255 if v>=t else 0).getbbox() for t in [192,224,240]}
                if not boxes['224']:raise ValueError('No alpha>=224 core: '+ident)
                core=boxes['224'];maximum=alpha.getextrema()[1]
            states.append({'state':state,'assetId':ident,'file':e['file'],'generationRecord':e['file']+'.generation.json',
                'sourceSha256FromManifest':e['sha256'],'sourceNativeSize':[e['width'],e['height']],
                'candidateCoreRect':xywh(core),'coreCenter':centered(core),
                'coreMeasurement':{'method':'alpha_threshold_bbox','threshold':224,'thresholdIsArtHeuristic':True,
                    'maxAlpha':maximum,'boundsLTRBByAlpha':boxes,'opticalSilhouetteApproved':False},
                'status':STATUS})
        halfw=math.ceil(max(max(s['coreCenter'][0],s['sourceNativeSize'][0]-s['coreCenter'][0]) for s in states)+8)
        halfh=math.ceil(max(max(s['coreCenter'][1],s['sourceNativeSize'][1]-s['coreCenter'][1]) for s in states)+8)
        canvas=[halfw*2,halfh*2];root=[halfw,halfh]
        ref=next(s for s in states if s['state']==group['reference'])
        refsize=ref['candidateCoreRect'][2:]
        scale=min(1,group['bodyDisplayBox'][0]/refsize[0],group['bodyDisplayBox'][1]/refsize[1])
        for s in states:
            offset=[pxround(root[0]-s['coreCenter'][0]),pxround(root[1]-s['coreCenter'][1])]
            s['drawOffset']=offset;s['drawScale']=1
            s['drawRect']=[offset[0],offset[1],*s['sourceNativeSize']]
            s['registeredCoreCenter']=[s['coreCenter'][0]+offset[0],s['coreCenter'][1]+offset[1]]
            s['rootResidualPx']=[round(s['registeredCoreCenter'][i]-root[i],2) for i in range(2)]
            s['coreExtentDriftFromReference']=[round(s['candidateCoreRect'][i+2]/refsize[i]-1,5) for i in range(2)]
            if max(abs(x) for x in s['coreExtentDriftFromReference'])>0.03:
                warning={'id':'source_state_core_shape_drift','family':group['id'],'state':s['state'],'assetId':s['assetId'],
                    'relativeWidthHeight':s['coreExtentDriftFromReference'],'threshold':0.03,
                    'meaning':'Alpha heuristic sees native extent differences after registration; candidate for flicker review, not anatomy/art approval.'}
                warnings.append(warning)
            if offset[0]<0 or offset[1]<0 or offset[0]+s['sourceNativeSize'][0]>canvas[0] or offset[1]+s['sourceNativeSize'][1]>canvas[1]:
                raise ValueError('State does not fit shared candidate canvas: '+s['assetId'])
        r=ref['candidateCoreRect'];d=ref['drawOffset']
        reference_rect=[r[0]+d[0],r[1]+d[1],r[0]+r[2]+d[0],r[1]+r[3]+d[1]]
        content=inset(reference_rect,group['contentInsets'])
        if content[2]<=content[0] or content[3]<=content[1]:raise ValueError('Invalid candidate content rect')
        fallback={'hover':'reuse current semantic state; client color feedback only; no geometry change',
            'focus':'client focus indicator outside contentRect; no artwork rescale'}
        if 'pressed' not in group['states']:fallback['pressed']='reuse current semantic state with client tint; position unchanged'
        if 'disabled' not in group['states']:fallback['disabled']='reuse current semantic state with client desaturation/opacity; hit disabled'
        if 'selected' not in group['states']:fallback['selected']='no independent selected art; preserve current semantic state'
        families.append({'id':group['id'],'status':STATUS,'referenceState':group['reference'],
            'logicalCanvas':canvas,'logicalRoot':root,'logicalAnchor':[0.5,0.5],
            'referenceBodyRect':xywh(reference_rect),'contentRect':xywh(content),
            'contentRectRole':'item/icon area; no separate text on this control' if group['id'] in ['slot','toggle','checkbox','close','slider-thumb'] else 'candidate live-text safe area',
            'hitRect':xywh(reference_rect),'hitShape':group['hitShape'],
            'preferredBodyDisplayBox':group['bodyDisplayBox'],'sharedDisplayScale':round(scale,7),
            'displayCanvasSize':[round(canvas[0]*scale,3),round(canvas[1]*scale,3)],
            'scaleRule':'Compute one family scale from the reference body and use it unchanged for all states. Never fit each source/glow bbox separately.',
            'futurePaddingExport':{'allowed':True,'canvas':canvas,'placement':'state.drawOffset','resample':False,'upscale':False,
                'note':'Future optional RGBA padding only. No padded PNG is produced by this metadata tool.'},
            'stateFallbacks':fallback,'states':states})
    data={'schemaVersion':1,'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':STATUS,
        'coordinateSystem':{'units':'native source pixels','rectFormat':'x,y,width,height','origin':'top-left','drawOffset':'source PNG top-left inside shared logical canvas','integerPlacement':True,'maxCoreCenterRoundingErrorPx':0.5},
        'operation':{'type':'read_native_alpha_write_metadata','pngWrites':0,'sourceResize':False,'sourcePixelsModified':False,'renderedPreviews':0,'atlasRebuild':False},
        'inputs':['assets/ui/buttons/manifest.json','assets/ui/hud/manifest.json','assets/ui/additions/manifest.json','designs/production-v1/kit-buttons/kit-buttons.visual-qa.json','designs/production-v1/kit-hud/kit-hud.visual-qa.json'],
        'coreHeuristic':{'alphaThreshold':224,'avoidThreshold254':True,'reason':'Near-opaque texture is not uniformly alpha255; selected slot maxAlpha254 has sparse alpha254 coverage. Exact max-alpha bbox is not a reliable body silhouette.'},
        'families':families,'warnings':warnings,
        'acceptancePending':['Look at actual state switching at shared scale on light/dark and gameplay backgrounds.','Check true frame-body registration, text/icon safe areas and hit areas in target runtime.','Decide whether measured source-shape differences are intended; if visible body wobble persists, AI-edit only offending states against the reference body.','No individual glow-bbox fitting, no silent nonuniform scaling and no claim that metadata alone approves visual state continuity.']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(output),'families':len(families),'states':sum(len(f['states']) for f in families),'warnings':warnings,'status':STATUS},ensure_ascii=False))

if __name__=='__main__':main()
