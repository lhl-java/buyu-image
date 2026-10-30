from pathlib import Path
import json
from PIL import Image, ImageDraw
root=Path(r'D:\work\buyu-image')
out=root/'assets/characters/portraits'
m=json.loads((out/'manifest.json').read_text(encoding='utf-8-sig'))
canvas=Image.new('RGB',(768,512),(17,49,42))
summary=[]
for i,e in enumerate(m['items']):
 im=Image.open(root/e['file']).convert('RGBA')
 a=im.getchannel('A')
 summary.append({'id':e['id'],'size':im.size,'alpha':a.getextrema(),'zeroPixels':a.histogram()[0]})
 im.thumbnail((230,220),Image.Resampling.LANCZOS)
 canvas.paste(im,((i%3)*256+(256-im.width)//2,(i//3)*256+(230-im.height)//2),im)
canvas.save(root/'designs/production-v1/portraits/alpha-dark-qa.jpg',quality=92)
(root/'designs/production-v1/portraits/alpha-check.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))

