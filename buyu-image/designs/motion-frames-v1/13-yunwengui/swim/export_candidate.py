"""Export only this eight-frame candidate. Native crop + integer registration + padding.

This does not synthesize animation, resample pixels or approve motion. It retains
the original source-margin and body/loop-review warnings for the coordinator.
"""
raise SystemExit('Retired prototype exporter: use designs/motion-frames-v1/worker-14-24/register_group.py 13-yunwengui. Current canvas844 and swim8fps must be preserved.')
from pathlib import Path
from PIL import Image, ImageDraw
import datetime, hashlib, json, math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'assets/animations/13-yunwengui/swim'
SOURCE = HERE / '13-yunwengui-swim-v3.png'
REPORT = json.loads((HERE / 'source-v3-qa.json').read_text(encoding='utf-8'))
CANVAS = (604, 604)
ROOT_POINT = [302, 302]
EYE_POINT = [440, 247]
STATUS = 'producer_candidate_pending_root_registered_review'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rel(path):
    return Path(path).relative_to(ROOT).as_posix()

def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

assert sha(SOURCE) == REPORT['sha256'], 'Review source changed'
OUT.mkdir(parents=True, exist_ok=True)
source = Image.open(SOURCE).convert('RGBA')
frames, items, registration = [], [], []
source_reference = {'file': rel(SOURCE), 'sha256': sha(SOURCE), 'generationRecord': rel(SOURCE) + '.generation.json'}
animation = {
    'id': '13-yunwengui/swim', 'frames': 8, 'fps': 12, 'loop': True,
    'order': 'row-major', 'phasesDegrees': list(range(0, 360, 45)),
    'root': [.5, .5], 'durationsMs': [83, 84, 83, 83, 84, 83, 83, 84],
    'timingNote': 'fps=12 authoritative; cumulative boundaries rounded to milliseconds',
    'targetBodyBox': [180, 130], 'registrationStatus': 'integer_eye_registered_body_shape_pending_root_visual',
    'identityStatus': 'pending_root_visual', 'motionStatus': 'pending_root_visual',
    'loopVisualStatus': 'pending_root_playback', 'sourceRoute': 'builtin_native_AI_sheet_user_requested'
}

for entry in REPORT['frames']:
    i = entry['sourceFrame']
    raw = source.crop(entry['sourceRect'])
    raw.putalpha(raw.getchannel('A').point(lambda value: 0 if value <= 3 else value))
    pupil = entry['pupil']['center']
    rounded = [round(pupil[0]), round(pupil[1])]
    offset = [EYE_POINT[0] - rounded[0], EYE_POINT[1] - rounded[1]]
    assert offset[0] >= 0 and offset[1] >= 0
    assert offset[0] + raw.width <= CANVAS[0] and offset[1] + raw.height <= CANVAS[1]
    frame = Image.new('RGBA', CANVAS, (0, 0, 0, 0))
    frame.paste(raw, tuple(offset))  # No mask: copy native RGBA without recompositing.
    round_trip = frame.crop((offset[0], offset[1], offset[0] + raw.width, offset[1] + raw.height))
    assert round_trip.tobytes() == raw.tobytes(), 'Native pixels changed'
    bounds = list(frame.getchannel('A').getbbox())
    margins = [bounds[0]/CANVAS[0], bounds[1]/CANVAS[1], (CANVAS[0]-bounds[2])/CANVAS[0], (CANVAS[1]-bounds[3])/CANVAS[1]]
    assert min(margins) >= .12, 'Candidate padding margin below gate'
    file = OUT / f'frame-{i:02d}.png'
    frame.save(file)
    operation = {
        'type': 'native_grid_crop_integer_pupil_registration_transparent_padding',
        'grid': {'cols': 4, 'rows': 2}, 'sourceRect': entry['sourceRect'],
        'cellCropRect': [0, 0, raw.width, raw.height],
        'alphaCleanup': 'Values <=3 set to zero; all other alpha and RGB preserved',
        'resized': False, 'upscaled': False, 'rotated': False,
        'registrationOffset': offset, 'registeredCanvas': list(CANVAS),
        'registrationReference': {
            'type': 'warm_dark_pupil_connected_component_centroid',
            'sourcePointFloat': pupil, 'sourcePointRounded': rounded,
            'targetPoint': EYE_POINT, 'rounding': 'nearest integer',
            'detection': entry['pupil']['method'],
            'limitation': 'Eye lock removes source layout drift; it cannot eliminate generated head/shell shape changes.'
        },
        'sourcePixelsRoundTripVerified': True, 'transparentOnlyClipping': True,
        'newNativeDetailClaimed': False
    }
    item = {
        'schemaVersion': 1, 'id': f'frame-{i:02d}', 'name': f'云纹龟游动相位 {i*45}°',
        'file': rel(file), 'sha256': sha(file), 'width': CANVAS[0], 'height': CANVAS[1],
        'format': 'RGBA PNG', 'derivedAt': NOW, 'nativeSource': rel(SOURCE),
        'derivedFrom': [source_reference], 'operation': operation,
        'anchor': [.5, .5], 'rootPixels': ROOT_POINT, 'eyePixels': EYE_POINT,
        'registeredAlphaBBox': bounds, 'registeredMinMargin': min(margins),
        'status': STATUS, 'actualModel': None, 'actualQuality': None,
        'modelEvidence': 'No model call for crop/padding. Actual source model and quality were not disclosed; see source generation record.',
        'animation': animation, 'targetBodyBox': [180, 130],
        'displaySizing': {'preserveAspect': True, 'uniformScaleAcrossAction': True, 'upscalingAllowed': False, 'status': 'candidate_one_scale_from_rest_visible_box'}
    }
    registration.append({'frame': i, 'sourcePupilFloat': pupil, 'sourcePupilRounded': rounded, 'registrationOffset': offset, 'targetPupil': EYE_POINT, 'bodyRoot': ROOT_POINT, 'bbox': bounds, 'marginsLTRB': margins, 'pixelsRoundTrip': True})
    frames.append(frame)
    items.append(item)

rest_bounds = items[0]['registeredAlphaBBox']
rest_size = [rest_bounds[2] - rest_bounds[0], rest_bounds[3] - rest_bounds[1]]
scale = min(180/rest_size[0], 130/rest_size[1], 1)
display_reference = {'frame': 0, 'restNativeVisibleBox': rest_size, 'fitMaxBox': [180, 130], 'actualRestDisplayBox': [rest_size[0]*scale, rest_size[1]*scale], 'method': 'one aspect-preserving scale from complete rest visible box; reused across every frame, including all flipper phases', 'upscaling': False}
for item in items:
    item.update({'displaySize': [CANVAS[0]*scale, CANVAS[1]*scale], 'bodyDisplayBox': [180, 130], 'uniformDisplayScale': scale, 'displayScaleReference': display_reference})
    save_json(ROOT / (item['file'] + '.generation.json'), item)

warnings = [
    {'id': 'source_margin_lt_12pct', 'severity': 'source_gate_fail', 'details': REPORT['warnings'], 'note': 'Runtime transparent padding satisfies export margins but does not make the native source-margin gate pass.'},
    {'id': 'source_core_shape_drift', 'severity': 'pending_visual_review', 'note': 'Source pupils varied by approximately 13px horizontally and 51px vertically. Integer eye registration removes layout displacement; neck/head/shell contour variation remains a review item.'},
    {'id': 'stroke_transition_3_to_4', 'severity': 'pending_motion_review', 'note': 'Foreflipper changes from broad forward reach to folded downward recovery; visually distinct but transition remains abrupt at the source contact-sheet review.'},
    {'id': 'loop_transition_7_to_0', 'severity': 'pending_playback', 'note': 'Final folded fin differs from first open fin; exact loop smoothness has not been played back during local heavy-job hold.'}
]
manifest = {
    'schemaVersion': 1, 'source': rel(SOURCE), 'sourceWidth': source.width, 'sourceHeight': source.height,
    'sourceSha256': sha(SOURCE), 'output': rel(OUT), 'items': items, 'animation': animation,
    'frameCount': 8, 'sharedCanvas': list(CANVAS), 'rootPixels': ROOT_POINT, 'eyePixels': EYE_POINT,
    'bodyRootOffsetFromEye': [-138, 55],
    'bodyRootEvidence': 'Single logical shell-body root inferred relative to frame0 eye; integer eye registration only. Body rigidity remains pending visual review.',
    'nativeBodyEvidence': 'Manual native inspection: shell plus head horizontally approximately 315–335px excluding flippers/tail, safely above180px. No anatomical segmentation or upsampling was used.',
    'registration': registration, 'order': list(range(8)), 'sourceCropRects': [e['sourceRect'] for e in REPORT['frames']],
    'displaySize': [CANVAS[0]*scale, CANVAS[1]*scale], 'bodyDisplayBox': [180, 130], 'uniformDisplayScale': scale,
    'warnings': warnings, 'sourceMarginWarnings': REPORT['warnings'], 'runtimeMarginWarnings': [],
    'qa': {'technicalAlpha': 'true_rgba', 'sourceBorderStatus': 'pass_alpha_max1', 'sourceMarginStatus': 'fail_preserved_source_gate', 'registeredMarginStatus': 'pass', 'identityStatus': 'candidate_pending_root_visual', 'actualMotionStatus': 'candidate_visible_articulated_flippers_pending_root_visual', 'registrationStatus': 'integer_eye_registered_core_shape_pending', 'loopPlaybackStatus': 'not_run_during_local_heavy_job_hold'},
    'status': STATUS, 'sourceReview': rel(HERE / 'source-v3-qa.json'),
    'contactSheets': [rel(HERE/'registered-v3-light.jpg'), rel(HERE/'registered-v3-dark.jpg')]
}
save_json(OUT / 'manifest.json', manifest)

for suffix, color, ink in [('light', (245,237,217), (31,71,59)), ('dark', (21,52,45), (241,232,203))]:
    contact = Image.new('RGB', (CANVAS[0]*4, (CANVAS[1]+24)*2), color)
    draw = ImageDraw.Draw(contact)
    for i, frame in enumerate(frames):
        x, y = (i%4)*CANVAS[0], (i//4)*(CANVAS[1]+24)
        contact.paste(frame, (x,y), frame)
        draw.text((x+8, y+CANVAS[1]+6), f'frame-{i:02d} / candidate / 12fps', fill=ink)
    contact.save(HERE / f'registered-v3-{suffix}.jpg', quality=91)

review = {
    'schemaVersion': 1, 'reviewedAt': NOW, 'status': STATUS, 'manifest': rel(OUT/'manifest.json'),
    'sourceLightAndDarkActuallyInspected': True, 'registeredLightAndDarkActuallyInspected': False,
    'actualMotionObservation': 'Near foreflipper changes broad open left/down/right reach across0–3 and narrow folded recovery across4–7. Rear flippers alter angles. Tail changes subtly. No frame duplicated as final.',
    'warnings': warnings, 'candidateMinMargin': min(i['registeredMinMargin'] for i in items),
    'noResampling': True, 'allNativePixelsAboveAlpha3Preserved': True,
    'renderTestsBrowserAtlasUnityRun': False,
    'note': 'This producer review does not pass identity, body rigidity or loop playback. Coordinator review required before expanding the fish batch.'
}
save_json(HERE / 'candidate-review.json', review)
print(json.dumps({'manifest': rel(OUT/'manifest.json'), 'frames': len(items), 'canvas': list(CANVAS), 'minimumMargin': review['candidateMinMargin'], 'uniformDisplayScale': scale, 'status': STATUS}, ensure_ascii=False))
