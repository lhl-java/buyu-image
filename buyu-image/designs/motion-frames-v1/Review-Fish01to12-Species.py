"""Bounded one-species still QA contact and display-size comparison; not game art."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,argparse
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument("id");a=p.parse_args();qa=ROOT/"tmp/art-qa";out=Image.new("RGB",(2048,1088),(238,232,215))
for r,bg in enumerate(["light","dark"]):
 for c,act in enumerate(["swim","capture"]):
  im=Image.open(qa/f"{a.id}-{act}-registered-{bg}.png").convert("RGB");out.paste(im,(c*1024,r*544))
contact=qa/f"{a.id}-pair-review.png";out.save(contact)
game=Image.new("RGB",(480,264),(236,232,215));d=ImageDraw.Draw(game)
for i,act in enumerate(["swim","capture"]):
 m=json.loads((ROOT/f"assets/animations/{a.id}/{act}/manifest.json").read_text(encoding="utf-8-sig"));im=Image.open(ROOT/m["items"][0]["file"]).convert("RGBA");size=tuple(round(v) for v in m["displaySize"]);im=im.resize(size,Image.Resampling.LANCZOS);root=m["root"];x=i*240+120-round(size[0]*root[0]);y=130-round(size[1]*root[1]);game.paste(im,(x,y),im);d.text((i*240+6,6),act+" / one clip scale",fill=(30,65,50));d.line((i*240+116,130,i*240+124,130),fill=(190,90,65));d.line((i*240+120,126,i*240+120,134),fill=(190,90,65))
gamePath=qa/f"{a.id}-display-rest-qa.png";game.save(gamePath)
print(json.dumps({"nativeContact":str(contact),"restDisplayComparison":str(gamePath)}))

