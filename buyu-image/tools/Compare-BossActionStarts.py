"""Light actual-alpha contact at declared display scales, not runtime acceptance."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path(__file__).resolve().parent.parent
actors=['34-jinlongli','35-longwang','36-xuanjing'];actions=['swim','capture','attack','enrage'];cell=(500,420)
out=Image.new('RGB',(cell[0]*4,cell[1]*3),(245,237,217));draw=ImageDraw.Draw(out)
for row,actor in enumerate(actors):
    for col,action in enumerate(actions):
        m=json.loads((ROOT/f'assets/animations/{actor}/{action}/manifest.json').read_text(encoding='utf-8-sig'));e=m['items'][0];sprite=Image.open(ROOT/e['file']).convert('RGBA');scale=e['uniformDisplayScale'];sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.LANCZOS)
        root=e.get('eyePixels',e['rootPixels']);position=(round(col*500+360-root[0]*scale),round(row*420+200-root[1]*scale));out.paste(sprite,position,sprite)
        draw.text((col*500+12,row*420+380),f'{actor}/{action}  source-scale={scale:.4f}',fill=(31,71,59))
dest=ROOT/'tmp/art-qa/boss-actions-declared-scale.jpg';dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest,quality=94)
print(str(dest))
