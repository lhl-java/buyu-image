"""Reference layout only: native unscaled approved master repeated in a4x2 grid.
This is never an animation/frame output; image_gen must redraw articulated phases.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
for batch in [3,4]:
    for master in (ROOT/'assets/fish'/f'batch-{batch}').glob('*.png'):
        n=int(master.name.split('-')[0])
        if not 14<=n<=24:continue
        image=Image.open(master).convert('RGBA');cell=600
        assert max(image.size)<cell
        board=Image.new('RGBA',(cell*4,cell*2),(0,0,0,0))
        offset=[round((cell-image.width)/2),round((cell-image.height)/2)]
        for i in range(8):board.paste(image,((i%4)*cell+offset[0],(i//4)*cell+offset[1]))
        folder=ROOT/'designs/motion-frames-v1'/master.stem
        folder.mkdir(parents=True,exist_ok=True)
        output=folder/'geometry-reference.png';board.save(output)
        meta={'file':output.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'purpose':'AI geometry reference only;8 repeated copies are NOT animation or runtime assets','derivedFrom':master.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(master.read_bytes()).hexdigest(),'operation':'native RGBA copy8times into2400x1200 transparent4x2 reference; no resize, no drawn art, no synthetic motion','cellSize':[cell,cell],'sourceNativeSize':list(image.size),'offsetWithinCell':offset,'resized':False,'runtimeApproved':False}
        output.with_suffix('.png.reference.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('Created11 reference layouts; not runtime animation outputs.')
