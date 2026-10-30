from pathlib import Path
import hashlib,json,math
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent.parent
data=json.loads((root/'assets/runtime-catalog.json').read_text(encoding='utf-8-sig'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
assets=data['assets']; fish=[e for e in assets if e['category']=='fish']
scenes=[e for e in assets if e['category']=='scenes']
tile=192; cols=6; titleh=66; sceneh=132; top=titleh+sceneh*math.ceil(len(scenes)/3)
canvas=Image.new('RGB',(cols*tile,top+tile*math.ceil(len(fish)/cols)+48),(242,235,217));draw=ImageDraw.Draw(canvas)
draw.text((22,18),'捕鱼 · 五处场景与36种静态鱼类',font=font,fill=(26,73,62))
for i,e in enumerate(scenes):
    im=Image.open(root/e['file']).convert('RGBA');im.thumbnail((cols*tile//3-10,sceneh-30),Image.Resampling.LANCZOS)
    x=(i%3)*(cols*tile//3)+5;y=titleh+(i//3)*sceneh
    canvas.paste(im,(x,y),im);draw.text((x,y+sceneh-27),e['name'],font=small,fill=(26,73,62))
for i,e in enumerate(fish):
    im=Image.open(root/e['file']).convert('RGBA');im.thumbnail((tile-20,tile-42),Image.Resampling.LANCZOS)
    x=(i%cols)*tile+(tile-im.width)//2;y=top+(i//cols)*tile+(tile-38-im.height)//2
    canvas.paste(im,(x,y),im);draw.text(((i%cols)*tile+12,top+(i//cols+1)*tile-31),e['name'],font=small,fill=(26,73,62))
draw.text((16,canvas.height-35),'缩略审阅总览；原生PNG、来源、FX与控件请查看独立图集。鱼类动作尚未完成。',font=small,fill=(65,85,72))
out=root/'gallery/game-art-overview.jpg';canvas.save(out,quality=91)
record={'file':out.relative_to(root).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'width':canvas.width,'height':canvas.height,'operation':{'type':'reduced_contact_sheet_for_review','newGeneration':False,'upscaled':False},'derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['generationRecord']} for e in scenes+fish]}
Path(str(out)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'size':list(canvas.size),'fish':len(fish),'scenes':len(scenes)}))
