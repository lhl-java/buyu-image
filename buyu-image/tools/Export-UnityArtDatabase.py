"""Export current metadata for the Unity review project; never alter source pixels."""
import argparse
import copy
import datetime
import json
from pathlib import Path
import struct


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def png_size(path):
    with path.open('rb') as source:
        header = source.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('Not a real PNG: ' + str(path))
    return list(struct.unpack('>II', header[16:24]))


def frame(asset, duration=0):
    anchor = asset.get('anchor', [.5, .5])
    display = asset.get('displaySize')
    if not display or len(display) != 2 or min(display) <= 0:
        raise ValueError('Missing normalized display size: ' + asset['id'])
    result = dict(file=asset['file'], width=asset['width'], height=asset['height'],
                  pivotX=anchor[0], pivotY=anchor[1], displayWidth=display[0],
                  displayHeight=display[1], durationMs=duration, sha256=asset['sha256'])
    qa = asset.get('qa', {})
    bounds = (asset.get('registeredAlphaBBox') or qa.get('registeredAlphaBBox') or qa.get('registeredBoxAlpha16')
              or qa.get('registeredBodyBoxAlpha16'))
    if bounds:
        result['alphaBounds'] = bounds
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    from ArtAcceptanceState import preserve_accepted
    if preserve_accepted(root): return
    catalog = read_json(root / 'assets/runtime-catalog.json')
    brand = read_json(root / 'config/game-brand.json') if (root / 'config/game-brand.json').is_file() else {}
    by_id = {item['id']: item for item in catalog['assets']}
    if len(by_id) != len(catalog['assets']):
        raise ValueError('Duplicate catalog IDs')
    if brand.get('logoAssetId') and brand['logoAssetId'] not in by_id:
        raise ValueError('Official logo asset is absent from the current catalog')
    assets = []
    for asset in catalog['assets']:
        data = frame(asset)
        data.update(id=asset['id'], name=asset.get('name', asset['id']),
                    category=asset['category'], status=asset.get('status', 'candidate'))
        border = asset.get('nineSlice')
        if border:
            if len(border) != 4:
                raise ValueError('Malformed nineSlice: ' + asset['id'])
            data['nineSlice'] = [border[0], border[3], border[2], border[1]]
        assets.append(data)
    clips = []
    for clip in catalog['clips']:
        durations = clip.get('durationsMs', [])
        if durations and len(durations) != len(clip['frames']):
            raise ValueError('Duration count differs from frame count: ' + clip['id'])
        frames = []
        for i, asset_id in enumerate(clip['frames']):
            source = by_id[asset_id]
            duration = durations[i] if durations else source.get('runtimeFrame', {}).get('durationMs', 0)
            frames.append(frame(source, duration))
        clips.append(dict(id=clip['id'], name=clip.get('name', clip['id']),
                          actorId=clip.get('actorId', ''), action=clip.get('action', 'fx'),
                          manifest=clip['manifest'], fps=clip['fps'], loop=clip['loop'],
                          status=clip.get('status', 'candidate'), frames=frames))
    screens = []
    for task in read_json(root / 'docs/UI_SUITE_20261026.json')['tasks']:
        width, height = png_size(root / task['selectedFile'])
        screens.append(dict(id=task['id'], name=task['title'], file=task['selectedFile'],
                            width=width, height=height))
    cannons = [dict(id=c['id'], name=c['name'], baseAssetId=c['base'], barrelAssetId=c['barrel'])
               for c in catalog['cannons']]
    registered = {c['id']: c for c in read_json(root / 'config/cannon-registration.json')['cannons']}
    for cannon in cannons:
        if cannon['baseAssetId'] not in by_id or cannon['barrelAssetId'] not in by_id:
            raise ValueError('Cannon references a missing asset: ' + cannon['id'])
        registration = registered[cannon['id']]
        if registration['barrelSha256'] != by_id[cannon['barrelAssetId']]['sha256']:
            raise ValueError('Cannon registration belongs to a different source: ' + cannon['id'])
        cannon['muzzle'] = registration['muzzleNormalized']
    ui_families = []
    for family in read_json(root / 'config/ui-state-registration.json')['families']:
        states = []
        for state in family['states']:
            if state['assetId'] not in by_id:
                raise ValueError('UI state references a missing asset: ' + state['assetId'])
            states.append({key: copy.deepcopy(state[key]) for key in ['state', 'assetId', 'drawOffset']})
        ui_families.append(dict(id=family['id'], logicalCanvas=family['logicalCanvas'], hitRect=family['hitRect'],
                                contentRect=family['contentRect'], sharedDisplayScale=family['sharedDisplayScale'],
                                states=states))
    result = dict(generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  status='accepted_first_release_art' if catalog.get('gameArtComplete') else 'candidate_pending_Unity_import_and_playback', gameArtComplete=bool(catalog.get('gameArtComplete')),
                  fontFile='assets/fonts/NotoSansCJKsc-Regular.otf', gameName=brand.get('name', '捕鱼'),
                  logoAssetId=brand.get('logoAssetId', 'branding/brand-title'), assets=assets,
                  clips=clips, screens=screens, cannons=cannons, uiFamilies=ui_families,
                  projectile=copy.deepcopy(catalog.get('projectile')))
    destination = root / 'unity/BuyuClient/Assets/Resources/Buyu/art-database.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    evidence = dict(schemaVersion=1, createdAt=result['generatedAt'], output=str(destination.relative_to(root)).replace('\\', '/'),
                    source='assets/runtime-catalog.json', assets=len(assets), clips=len(clips),
                    nativeActions=sum(bool(c['actorId']) for c in clips), frames=sum(len(c['frames']) for c in clips),
                    screens=len(screens), cannons=len(cannons), uiFamilies=len(ui_families),
                    uiStates=sum(len(f['states']) for f in ui_families), sourcePixelsChanged=False,
                    checks='Metadata references, positive display sizes, frame durations and PNG headers only.',
                    UnityImportRun=False, playbackReviewed=False, gameArtComplete=False)
    report = root / 'docs/UNITY_DATABASE_EXPORT.json'
    report.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(evidence, ensure_ascii=True))


if __name__ == '__main__':
    main()
