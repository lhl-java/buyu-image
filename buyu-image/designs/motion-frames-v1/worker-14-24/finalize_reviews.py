"""Record completed producer static inspection. Metadata only; no pixel writes."""
from pathlib import Path
import json, datetime, collections

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
specs=json.loads((HERE/'adopted-sources.json').read_text(encoding='utf-8'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[]
def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for spec in specs:
    for action in ('swim','capture'):
        version=spec['swimVersion' if action=='swim' else 'captureVersion']
        folder=ROOT/'designs/motion-frames-v1'/spec['id']/action
        manifest_path=ROOT/'assets/animations'/spec['id']/action/'manifest.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        review_path=folder/('candidate-review'+version+'.json')
        review=json.loads(review_path.read_text(encoding='utf-8'))
        review.pop('sourceAndRegisteredLightDarkActuallyInspected',None)
        evidence={
            'sourceSheetActuallyInspected':True,
            'registeredLightAndDarkActuallyInspected':True,
            'inspectionType':'static contact sheets, actual generated source and actual exported alpha-composited frames',
            'lightContact':str((folder/('registered'+version+'-light.jpg')).relative_to(ROOT)).replace('\\','/'),
            'darkContact':str((folder/('registered'+version+'-dark.jpg')).relative_to(ROOT)).replace('\\','/'),
            'observedArticulation':spec['observation'],
            'edgeObservation':'The registered light and dark contacts show complete separate poses without an opaque rectangle or another frame fragment. Source grid / margin warnings are retained.',
            'livePlaybackActuallyRun':False,
            'finalArtApproval':False,
            'inspectedAt':now,
        }
        if spec['id'] in ('20-yuban','21-haiqiu','24-jindun'):
            evidence['landmarkCorrection']='Fixed face-only pupil ROI avoids dark camouflage / fin plate false landmarks; native pixels unchanged by integer registration.'
        review.update(evidence)
        review['reviewedAt']=now
        save(review_path,review)
        manifest['qa']['producerStaticVisualInspection']=evidence
        save(manifest_path,manifest)
        warning_counts=collections.Counter(w['id'] for w in manifest['warnings'])
        rows.append({
            'id':manifest['animation']['id'],'source':manifest['source'],
            'manifest':str(manifest_path.relative_to(ROOT)).replace('\\','/'),
            'review':str(review_path.relative_to(ROOT)).replace('\\','/'),
            'frames':len(manifest['items']),'fps':manifest['animation']['fps'],
            'durationsMs':manifest['animation']['durationsMs'],'loop':manifest['animation']['loop'],
            'registeredMinMargin':min(x['registeredMinMargin'] for x in manifest['items']),
            'sourceOwnership':manifest['sourcePixelOwnership'],
            'warningCounts':dict(warning_counts),'observation':spec['observation'],
            'registeredLightAndDarkActuallyInspected':True,
            'status':manifest['status'],
        })
summary={
    'schemaVersion':1,'scope':'13–24, swim and capture','clips':len(rows),
    'exportedFrames':sum(x['frames'] for x in rows),
    'sharedCanvas':[844,844],'rootPixels':[422,422],
    'fishLandmarkPixels':[590,350],'jelly14LandmarkPixels':[470,250],
    'noResamplingOrUpscaling':True,'nativeSourceDimensions':[1774,887],
    'registeredMinimumMargin':min(x['registeredMinMargin'] for x in rows),
    'producerRegisteredLightDarkInspectedClips':len(rows),
    'sourceMainComponentTotalCanvasBoundaryWarningCount':sum(x['warningCounts'].get('source_total_canvas_boundary',0) for x in rows),
    'sourceNominalGridWarningCount':sum(x['warningCounts'].get('nominal_grid_cross',0) for x in rows),
    'sourceMarginWarningCount':sum(x['warningCounts'].get('source_margin_lt_12pct',0) for x in rows),
    'runtimeMarginWarningCount':sum(x['warningCounts'].get('registered_margin_lt_12pct',0) for x in rows),
    'noSourceAlphaAbove3LostOrDuplicated':all(x['sourceOwnership']['lostPixels']==0 and x['sourceOwnership']['duplicatePixels']==0 for x in rows),
    'livePlaybackActuallyRun':False,'testsBrowserAtlasUnityRun':False,
    'finalArtApproval':False,'status':'producer_candidate_pending_root_registered_review',
    'limitations':[
        'Static visual inspection does not approve loop closure, frame timing or capture transition playback.',
        'Integer anatomical landmark translation does not repair generated head, shell, ornament or camera-scale drift.',
        'Native source margin below12% remains failed; transparent runtime padding does not retroactively pass source production.',
        'Nominal grid crossing is retained as a warning; complete separate poses were extracted by native pixel ownership.',
        'Actual image model / quality were not disclosed by the builtin tool and remain null in generation records.',
    ],
    'updatedAt':now,'items':rows,
}
save(HERE/'group-qa.json',summary)
print(json.dumps({k:summary[k] for k in ('clips','exportedFrames','registeredMinimumMargin','sourceMainComponentTotalCanvasBoundaryWarningCount','sourceNominalGridWarningCount','sourceMarginWarningCount','runtimeMarginWarningCount','noSourceAlphaAbove3LostOrDuplicated','finalArtApproval')},ensure_ascii=False))
