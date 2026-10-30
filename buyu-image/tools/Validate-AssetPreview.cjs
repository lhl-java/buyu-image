const fs=require('fs');const path=require('path');const crypto=require('crypto');const vm=require('vm');
const root=path.resolve(__dirname,'..'); const base=path.join(root,'assets-preview');
const html=fs.readFileSync(path.join(base,'index.html'),'utf8');
const app=fs.readFileSync(path.join(base,'app.js'),'utf8');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'assets/runtime-catalog.json'),'utf8').replace(/^\uFEFF/,''));
const problems=[];const checks=[];const assert=(condition,label)=>{checks.push({label,passed:Boolean(condition)});if(!condition)problems.push(label);};
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
assert(new Set(ids).size===ids.length,'HTML ids are unique');
for(const m of app.matchAll(/\$\('([^']+)'\)/g))assert(ids.includes(m[1]),'DOM reference exists: '+m[1]);
const links=[];
for(const m of html.matchAll(/\b(?:href|src)="([^"]+)"/g)){
  const link=m[1];if(link.startsWith('#')){assert(ids.includes(link.slice(1)),'HTML anchor '+link);continue;}
  if(/^[a-z]+:/i.test(link)){problems.push('Unexpected external URL '+link);continue;}
  const resolved=path.resolve(base,link.split('#')[0]);links.push({link,resolved,exists:fs.existsSync(resolved)});assert(fs.existsSync(resolved),'Local HTML file exists: '+link);
}
assert(!/fetch\s*\(/.test(app),'Offline preview does not fetch catalog');
const byId=new Map();let pngCount=0,recordCount=0,hashCount=0,dimensionCount=0,sourceCount=0;
for(const a of catalog.assets){
  assert(!byId.has(a.id),'Unique asset id '+a.id);byId.set(a.id,a);
  const p=path.resolve(root,a.file);assert(p.startsWith(root+path.sep),'Asset stays in project '+a.id);assert(fs.existsSync(p),'Asset file exists '+a.id);if(!fs.existsSync(p))continue;
  const buffer=fs.readFileSync(p);assert(buffer.toString('hex',0,8)==='89504e470d0a1a0a','PNG signature '+a.id);pngCount++;
  assert(buffer.readUInt32BE(16)===a.width&&buffer.readUInt32BE(20)===a.height,'Actual dimensions '+a.id);dimensionCount++;
  assert(sha(p)===a.sha256,'PNG hash '+a.id);hashCount++;
  const rp=path.resolve(root,a.generationRecord);assert(fs.existsSync(rp),'Generation record exists '+a.id);
  if(fs.existsSync(rp)){
    recordCount++;const rec=JSON.parse(fs.readFileSync(rp,'utf8').replace(/^\uFEFF/,''));
    if(rec.sha256)assert(rec.sha256===a.sha256,'Record hash '+a.id);
    for(const s of rec.derivedFrom||[]){const sp=path.resolve(root,s.file);assert(fs.existsSync(sp),'Direct source exists '+a.id);if(fs.existsSync(sp))assert(sha(sp)===s.sha256,'Direct source hash '+a.id);assert(fs.existsSync(path.resolve(root,s.generationRecord)),'Direct source record '+a.id);sourceCount++;}
  }
}
for(const clip of catalog.clips){const expected=clip.kind==='native_character_frames'?8:16;assert(clip.frames.length===expected,'Clip has contracted '+expected+' frames '+clip.id);const sizes=new Set();for(const f of clip.frames){assert(byId.has(f),'Clip frame resolves '+clip.id+' '+f);const a=byId.get(f);if(a)sizes.add(a.width+'x'+a.height);}assert(sizes.size===1,'Clip shares fixed canvas '+clip.id);}
for(const c of catalog.cannons){for(const part of ['base','barrel'])assert(byId.has(c[part]),'Cannon part resolves '+c.id+' '+part);}
const jsCatalog={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'assets/runtime-catalog.js'),'utf8'),jsCatalog);
assert(JSON.stringify(jsCatalog.window.BUYU_ART)===JSON.stringify(catalog),'JS catalog exactly matches JSON catalog');

class Element{
  constructor(tag='div',id=''){this.tagName=tag;this.id=id;this.children=[];this.listeners={};this.dataset={};this.style={};this.hidden=false;this.disabled=false;this.value='';this.checked=false;this.classes=new Set();this.classList={add:(v)=>this.classes.add(v),remove:(v)=>this.classes.delete(v),contains:v=>this.classes.has(v)};}
  addEventListener(t,f){(this.listeners[t]??=[]).push(f);}
  dispatch(t,event={}){for(const f of this.listeners[t]||[])f({target:this,...event});}
  append(...els){for(const e of els){if(e.tagName==='fragment')this.children.push(...e.children);else this.children.push(e);}}
  replaceChildren(...els){this.children=[];this.append(...els);}
  add(option){this.children.push(option);if(this.children.length===1&&!this.value)this.value=option.value;}
  showModal(){this.open=true;}close(){this.open=false;}
  getBoundingClientRect(){return {left:10,right:100,top:10,bottom:100};}
}
function domRun(data){
  const elements=new Map(ids.map(id=>[id,new Element('div',id)]));
  elements.get('category').value='all';elements.get('backdrop').value='checker';elements.get('search').value='';elements.get('angle').value='0';elements.get('frame-seek').value='0';elements.get('catalog-error').hidden=true;
  const document={body:new Element('body'),hidden:false,listeners:{},getElementById:id=>elements.get(id),createElement:t=>new Element(t),createDocumentFragment:()=>new Element('fragment'),addEventListener(t,f){(this.listeners[t]??=[]).push(f);},dispatch(t){for(const f of this.listeners[t]||[])f();}};
  for(const element of elements.values()){element.clientWidth=960;element.clientHeight=540;element.offsetWidth=960;element.offsetHeight=540;}
  let frameCallback;const context={window:{BUYU_ART:data,addEventListener(){}},document,Option:class extends Element{constructor(text,value){super('option');this.textContent=text;this.value=value;}},requestAnimationFrame:f=>{frameCallback=f;}};
  vm.runInNewContext(app,context,{filename:'assets-preview/app.js'});
  return {elements,document,tick:time=>frameCallback(time)};
}
const sim=domRun(catalog),el=id=>sim.elements.get(id),events=[];
const check=(v,label)=>{events.push({label,passed:Boolean(v)});assert(v,'DOM simulation: '+label);};
check(el('asset-grid').children.length===catalog.assets.length,'Initial library renders every asset');
el('category').value='fish';el('category').dispatch('change');check(el('asset-grid').children.length===36,'Fish category renders 36 assets');
el('category').value='all';el('search').value='__no_asset_can_match__';el('search').dispatch('input');check(el('asset-grid').children.length===0&&!el('no-results').hidden,'No-results state');
el('search').value=catalog.assets[0].id;el('search').dispatch('input');check(el('asset-grid').children.length===1,'Unique ID search');
el('asset-grid').children[0].dispatch('click');check(el('asset-dialog').open&&el('dialog-image').src==='../'+catalog.assets[0].file,'Asset modal opens actual PNG');
el('native-image').dispatch('click');check(el('dialog-viewport').classList.contains('native'),'Native-size toggle');
el('fit-image').dispatch('click');check(!el('dialog-viewport').classList.contains('native'),'Fit toggle');
el('close-dialog').dispatch('click');check(!el('asset-dialog').open,'Modal closes');
el('backdrop').value='dark';el('backdrop').dispatch('change');check(sim.document.body.dataset.backdrop==='dark','Dark backdrop selector');
el('play-fx').dispatch('click');sim.tick(0);sim.tick(125);check(Number(el('frame-seek').value)===2,'FX advances two native frames at16 FPS');
el('frame-seek').value='14';el('frame-seek').dispatch('input');el('play-fx').dispatch('click');sim.tick(1000);sim.tick(1250);check(Number(el('frame-seek').value)===15&&el('play-fx').textContent==='播放','One-shot stops on last frame');
el('loop-fx').checked=true;el('frame-seek').value='14';el('frame-seek').dispatch('input');sim.document.dispatch('visibilitychange');el('play-fx').dispatch('click');sim.tick(2000);sim.tick(2250);check(Number(el('frame-seek').value)===2&&el('play-fx').textContent==='暂停','Loop wraps to actual frame two after 250ms');
el('reset-fx').dispatch('click');check(Number(el('frame-seek').value)===0&&el('play-fx').textContent==='播放','FX reset returns to first frame');
for(const clip of catalog.clips){el('clip-select').value=clip.id;el('clip-select').dispatch('change');check(el('fx-image').src==='../'+byId.get(clip.frames[0]).file,'Clip selection '+clip.id);}
for(const c of catalog.cannons){el('cannon-select').value=c.id;el('cannon-select').dispatch('change');check(el('cannon-base').src==='../'+byId.get(c.base).file&&el('cannon-barrel').src==='../'+byId.get(c.barrel).file,'Cannon selection '+c.id);}
el('angle').value='92';el('angle').dispatch('input');check(el('cannon-barrel').style.transform.includes('rotate(92deg)'),'Manual cannon rotation');
el('reset-cannon').dispatch('click');check(el('cannon-barrel').style.transform.includes('rotate(0deg)'),'Cannon reset');
el('rotate-cannon').dispatch('click');sim.tick(2300);check(el('cannon-barrel').style.transform!=='translate(-50%,-70%) rotate(0deg)','Automatic cannon rotation advances');
sim.document.hidden=true;sim.document.dispatch('visibilitychange');const before=el('cannon-barrel').style.transform;sim.tick(2350);check(before===el('cannon-barrel').style.transform,'Hidden document pauses rotation');
const missing=domRun(undefined);check(!missing.elements.get('catalog-error').hidden&&missing.elements.get('play-fx').disabled,'Missing catalog readable fallback');
const report={schemaVersion:1,checkedAt:new Date().toISOString(),catalogBuiltAt:catalog.builtAt,catalogSha256:sha(path.join(root,'assets/runtime-catalog.json')),assetCount:catalog.assets.length,clipCount:catalog.clips.length,cannonCount:catalog.cannons.length,counts:{pngCount,dimensionCount,hashCount,recordCount,directSourceCount:sourceCount,htmlLocalLinkCount:links.length,domChecks:events.length,totalChecks:checks.length},htmlLocalLinks:links.map(x=>({link:x.link,exists:x.exists})),domSimulationChecks:events,problems,passed:problems.length===0,browserOpened:false,serverStarted:false,visualBrowserValidation:false,limits:['Lightweight DOM simulation validates application branches, not browser layout, CSS rendering or in-game animation.','Art acceptance is recorded separately in docs/UNITY_FINAL_ACCEPTANCE.json; this simulation itself grants no visual approval.'],previewFiles:['assets-preview/index.html','assets-preview/styles.css','assets-preview/app.js'].map(file=>({file,sha256:sha(path.join(root,file))}))};
fs.writeFileSync(path.join(root,'docs/ASSET_PREVIEW_VALIDATION.json'),JSON.stringify(report,null,2));
process.stdout.write(JSON.stringify(report,null,2));if(problems.length)process.exitCode=1;
