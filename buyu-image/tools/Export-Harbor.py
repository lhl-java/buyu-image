from pathlib import Path
import hashlib,json,shutil
from PIL import Image
root=Path(__file__).resolve().parent.parent
src=root/'designs/production-v1/scene-harbor/scene-harbor.png'
out=root/'assets/scenes/scene-harbor';out.mkdir(parents=True,exist_ok=True)
dst=out/'scene-harbor.png';shutil.copyfile(src,dst)
digest=hashlib.sha256(dst.read_bytes()).hexdigest();im=Image.open(dst)
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
write(Path(str(dst)+'.generation.json'),{'schemaVersion':1,'file':dst.relative_to(root).as_posix(),'width':im.width,'height':im.height,'sha256':digest,'derivedFrom':[{'file':src.relative_to(root).as_posix(),'sha256':digest,'generationRecord':src.relative_to(root).as_posix()+'.generation.json'}],'operation':{'type':'byte_identical_copy','resized':False,'upscaled':False},'actualModel':None,'actualQuality':None,'status':'static_background_visual_reviewed_pending_client_integration'})
write(out/'scene.json',{'schemaVersion':1,'id':'scene-harbor','file':dst.name,'nativeSize':list(im.size),'sha256':digest,'generationRecord':dst.name+'.generation.json','safePlayfield':{'units':'normalized','x':0.2,'y':0.15,'width':0.6,'height':0.6},'renderOrder':0,'scalePolicy':{'default':'contain','alternative':'cover','anchor':[0.5,0.5],'allowUpscale':False,'coverRequiresSafePlayfieldCheck':True},'content':'Login and lobby background only. No actors, HUD or text.','status':'static_background_visual_reviewed_pending_client_integration'})
print(json.dumps({'file':str(dst),'nativeSize':list(im.size),'sha256':digest}))
