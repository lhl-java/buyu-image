/* Offline asset inspector. Artwork is loaded only from the local runtime catalog. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const catalog = window.BUYU_ART;
  const labels = {fish:'鱼类',scenes:'海域场景',scene:'海域场景',cannons:'炮台部件',ui:'UI 控件',icons:'道具与功能图标',skills:'正式技能',ornaments:'玩法饰件',fx:'特效帧',animations:'角色与鱼类动作帧',characters:'角色',portraits:'头像'};
  const categoryLabel = (value) => labels[value] || value || '未分类';
  const fileUrl = (file) => '../' + String(file || '').replace(/\\/g, '/');
  const formatSize = (asset) => `${asset.width || '?'} × ${asset.height || '?'} px`;
  document.body.dataset.backdrop = 'checker';
  if (!catalog || !Array.isArray(catalog.assets)) {
    $('catalog-error').hidden = false;
    ['clip-select','clip-prev','clip-next','play-fx','reset-fx','frame-prev','frame-next','frame-seek','loop-fx','frame-scale','rotate-cannon','reset-cannon'].forEach((id) => { $(id).disabled = true; });
    return;
  }
  const assets = catalog.assets;
  const byId = new Map(assets.map((a) => [a.id, a]));
  const clips = Array.isArray(catalog.clips) ? catalog.clips : [];
  const cannons = Array.isArray(catalog.cannons) ? catalog.cannons : [];
  $('asset-count').textContent = assets.length;
  $('clip-count').textContent = clips.length;
  $('cannon-count').textContent = cannons.length;
  const categories = [...new Set(assets.map((a) => a.category || '未分类'))];
  for (const category of categories) {
    const option = new Option(`${categoryLabel(category)} · ${assets.filter((a) => (a.category || '未分类') === category).length}`, category);
    $('category').add(option);
  }
  function showAsset(asset) {
    $('dialog-title').textContent = asset.name || asset.id;
    $('dialog-meta').textContent = `${formatSize(asset)} · ${categoryLabel(asset.category)} · 锚点 ${(asset.anchor || [0.5,0.5]).join(', ')}`;
    $('dialog-image').src = fileUrl(asset.file);
    $('dialog-image').alt = asset.name || asset.id;
    $('dialog-image').width = asset.width || 0;
    $('dialog-image').height = asset.height || 0;
    $('dialog-viewport').classList.remove('native');
    $('dialog-path').textContent = asset.file;
    $('open-image').href = fileUrl(asset.file);
    $('asset-dialog').showModal();
  }
  function renderAssets() {
    const query = $('search').value.trim().toLocaleLowerCase();
    const category = $('category').value;
    const shown = assets.filter((a) => (category === 'all' || (a.category || '未分类') === category) && [a.id,a.name,a.category,categoryLabel(a.category)].join(' ').toLocaleLowerCase().includes(query));
    const fragment = document.createDocumentFragment();
    for (const asset of shown) {
      const card = document.createElement('button');
      card.type = 'button'; card.className = 'asset-card'; card.title = `查看 ${asset.name || asset.id} 原生 PNG`;
      const thumb = document.createElement('span'); thumb.className = 'asset-thumbnail';
      const img = document.createElement('img'); img.src = fileUrl(asset.file); img.alt = asset.name || asset.id; img.loading = 'lazy'; img.decoding = 'async';
      img.addEventListener('error', () => { img.alt = '图片文件无法读取：' + asset.file; card.classList.add('missing'); });
      thumb.append(img);
      const copy = document.createElement('span'); copy.className = 'asset-copy';
      const name = document.createElement('strong'); name.textContent = asset.name || asset.id;
      const id = document.createElement('span'); id.className = 'id'; id.textContent = asset.id;
      const details = document.createElement('span'); details.className = 'asset-details';
      const size = document.createElement('span'); size.textContent = formatSize(asset);
      const type = document.createElement('span'); type.textContent = categoryLabel(asset.category);
      details.append(size,type); copy.append(name,id,details); card.append(thumb,copy);
      card.addEventListener('click', () => showAsset(asset)); fragment.append(card);
    }
    $('asset-grid').replaceChildren(fragment);
    $('result-count').textContent = `${shown.length} / ${assets.length} 项`;
    $('no-results').hidden = shown.length > 0;
  }
  $('search').addEventListener('input', renderAssets);
  $('category').addEventListener('change', renderAssets);
  $('backdrop').addEventListener('change', () => { document.body.dataset.backdrop = $('backdrop').value; });
  $('close-dialog').addEventListener('click', () => $('asset-dialog').close());
  $('fit-image').addEventListener('click', () => { $('dialog-viewport').classList.remove('native'); });
  $('native-image').addEventListener('click', () => { $('dialog-viewport').classList.add('native'); });
  $('asset-dialog').addEventListener('click', (event) => { if (event.target === $('asset-dialog')) { const r = event.target.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) event.target.close(); } });
  let activeClip = null, frameIndex = 0, playing = false, frameElapsed = 0;
  const clipFrames = () => activeClip && Array.isArray(activeClip.frames) ? activeClip.frames : [];
  const positive = (value, fallback) => Number.isFinite(Number(value)) && Number(value) > 0 ? Number(value) : fallback;
  function frameDuration(index) {
    const asset = byId.get(clipFrames()[index]);
    const duration = activeClip && Array.isArray(activeClip.durationsMs) ? activeClip.durationsMs[index] : null;
    return positive(duration, positive(asset && asset.runtimeFrame && asset.runtimeFrame.durationMs, 1000 / positive(activeClip && activeClip.fps,16)));
  }
  function frameGeometry(asset) {
    const native = $('frame-scale').value === 'native';
    const size = native ? [asset.width,asset.height] : asset.displaySize;
    const fallbackScale = positive(activeClip && activeClip.uniformDisplayScale,1);
    const width = positive(size && size[0], positive(asset.width,1) * (native ? 1 : fallbackScale));
    const height = positive(size && size[1], positive(asset.height,1) * (native ? 1 : fallbackScale));
    const anchor = asset.anchor || (activeClip && (activeClip.anchor || activeClip.root)) || [.5,.5];
    return {width,height,anchor};
  }
  function layoutFrame(asset) {
    const geometry = frameGeometry(asset);
    // Reserve the whole declared canvas; never fit an individual visible bbox.
    const geometries = clipFrames().map((id) => byId.get(id)).filter(Boolean).map(frameGeometry);
    const canvasWidth = Math.max(1,...geometries.map((g) => g.width));
    const canvasHeight = Math.max(1,...geometries.map((g) => g.height));
    const planeWidth = Math.max(560, $('fx-stage').clientWidth, Math.ceil(canvasWidth + 96));
    const planeHeight = Math.max(460, $('fx-stage').clientHeight, Math.ceil(canvasHeight + 96));
    const rootX = (planeWidth - canvasWidth) / 2 + canvasWidth * geometry.anchor[0];
    const rootY = (planeHeight - canvasHeight) / 2 + canvasHeight * geometry.anchor[1];
    const image = $('fx-image');
    const plane = $('frame-plane');
    plane.style.width = `${planeWidth}px`; plane.style.height = `${planeHeight}px`;
    image.style.left = `${rootX}px`; image.style.top = `${rootY}px`;
    image.style.width = `${geometry.width}px`; image.style.height = `${geometry.height}px`;
    image.style.transform = `translate(${-geometry.anchor[0] * 100}%,${-geometry.anchor[1] * 100}%)`;
    $('frame-origin').style.left = `${rootX}px`; $('frame-origin').style.top = `${rootY}px`;
    return geometry;
  }
  function renderFrame() {
    if (!activeClip) return;
    const frames = clipFrames();
    const asset = byId.get(frames[frameIndex]);
    $('fx-empty').hidden = Boolean(asset); $('fx-image').hidden = !asset;
    $('frame-origin').hidden = !asset;
    let geometry = null;
    if (asset) {
      geometry = layoutFrame(asset);
      $('fx-image').src = fileUrl(asset.file); $('fx-image').alt = `${activeClip.name || activeClip.id} · 第 ${frameIndex + 1} 帧`;
    }
    $('frame-source').hidden = !asset;
    if (asset) $('frame-source').href = fileUrl(asset.file);
    $('frame-seek').value = frameIndex;
    $('frame-info').textContent = `第 ${frameIndex + 1} / ${frames.length} 帧 · ${frameDuration(frameIndex).toFixed(2).replace(/\.00$/,'')} ms${asset ? '\n原生 ' + formatSize(asset) + `；画布显示 ${geometry.width.toFixed(2)} × ${geometry.height.toFixed(2)} px\n固定根点 [${geometry.anchor.join(', ')}]（左上坐标）\n${asset.file}` : ' · 帧资源缺失'}`;
  }
  function updatePlayButton() { $('play-fx').textContent = playing ? '暂停' : '播放'; }
  function selectClip() {
    activeClip = clips.find((c) => c.id === $('clip-select').value) || null;
    frameIndex = 0; playing = false; frameElapsed = 0; updatePlayButton();
    if (!activeClip) return;
    $('clip-info').textContent = `${activeClip.name || activeClip.id}\n${clipFrames().length} 帧 · ${activeClip.fps || 16} FPS · 清单${activeClip.loop ? '循环' : '单次'}播放\n${activeClip.manifest || ''}\n${activeClip.releaseReady ? '已通过 Unity 首发美术验收；逐项证据见 docs/UNITY_FINAL_ACCEPTANCE.json。' : '候选素材：尚未通过 Unity 播放与循环接点验收。'}`;
    $('loop-fx').checked = Boolean(activeClip.loop);
    $('frame-seek').max = Math.max(0, clipFrames().length - 1); renderFrame();
    $('frame-image-error').hidden = true;
    $('fx-stage').scrollLeft = Math.max(0, ($('frame-plane').offsetWidth - $('fx-stage').clientWidth) / 2);
    $('fx-stage').scrollTop = Math.max(0, ($('frame-plane').offsetHeight - $('fx-stage').clientHeight) / 2);
  }
  function stepClip(direction) {
    if (!clips.length) return;
    const current = clips.findIndex((entry) => entry.id === $('clip-select').value);
    $('clip-select').value = clips[(Math.max(0,current) + direction + clips.length) % clips.length].id;
    selectClip();
  }
  function stepFrame(direction) {
    const frames = clipFrames();
    if (!frames.length) return;
    playing = false; frameElapsed = 0;
    frameIndex = Math.max(0,Math.min(frames.length - 1,frameIndex + direction));
    updatePlayButton(); renderFrame();
  }
  clips.forEach((c) => $('clip-select').add(new Option(c.name || c.id,c.id)));
  $('clip-select').addEventListener('change',selectClip);
  $('clip-prev').addEventListener('click', () => stepClip(-1));
  $('clip-next').addEventListener('click', () => stepClip(1));
  $('frame-prev').addEventListener('click', () => stepFrame(-1));
  $('frame-next').addEventListener('click', () => stepFrame(1));
  $('play-fx').addEventListener('click', () => { if (!clipFrames().length) return; if (!playing && frameIndex === clipFrames().length - 1) { frameIndex = 0; frameElapsed = 0; } playing = !playing; updatePlayButton(); renderFrame(); });
  $('reset-fx').addEventListener('click', () => { playing = false; frameIndex = 0; frameElapsed = 0; updatePlayButton(); renderFrame(); });
  $('frame-seek').addEventListener('input', () => { playing = false; frameElapsed = 0; frameIndex = Number($('frame-seek').value); updatePlayButton(); renderFrame(); });
  $('frame-scale').addEventListener('change',renderFrame);
  window.addEventListener('resize',renderFrame);
  $('fx-image').addEventListener('error', () => { $('frame-image-error').hidden = false; });
  $('fx-image').addEventListener('load', () => { $('frame-image-error').hidden = true; });
  if (!clips.length) ['clip-select','clip-prev','clip-next','play-fx','reset-fx','frame-prev','frame-next','frame-seek','loop-fx','frame-scale'].forEach((id) => { $(id).disabled = true; });
  let angle = 0, rotating = false;
  const partData = (ref) => typeof ref === 'string' ? byId.get(ref) : ref && (byId.get(ref.id) || ref);
  function setPart(element, asset) {
    element.hidden = !asset;
    if (!asset) return;
    element.src = fileUrl(asset.file);
    const size = asset.displaySize || [160,160], anchor = asset.anchor || [0.5,0.5];
    element.style.width = `${size[0]}px`; element.style.height = `${size[1]}px`;
    element.style.transformOrigin = `${anchor[0] * 100}% ${anchor[1] * 100}%`;
    element.dataset.anchorX = anchor[0]; element.dataset.anchorY = anchor[1];
    element.style.transform = `translate(${-anchor[0] * 100}%,${-anchor[1] * 100}%) rotate(0deg)`;
  }
  function renderAngle() {
    const barrel = $('cannon-barrel');
    barrel.style.transform = `translate(${-Number(barrel.dataset.anchorX || .5) * 100}%,${-Number(barrel.dataset.anchorY || .5) * 100}%) rotate(${angle}deg)`;
    $('angle').value = Math.round(angle); $('angle-output').textContent = `${Math.round(angle)}°`;
  }
  function selectCannon() {
    const cannon = cannons.find((c) => c.id === $('cannon-select').value);
    if (!cannon) return;
    const base = partData(cannon.base), barrel = partData(cannon.barrel);
    setPart($('cannon-base'),base); setPart($('cannon-barrel'),barrel);
    $('cannon-empty').hidden = Boolean(base && barrel);
    angle = 0; renderAngle();
    $('cannon-info').textContent = `底座：${base ? formatSize(base) : '资源缺失'}\n炮管：${barrel ? formatSize(barrel) : '资源缺失'}\n旋转锚点：${barrel ? (barrel.anchor || [.5,.5]).join(', ') : '—'}`;
  }
  cannons.forEach((c) => $('cannon-select').add(new Option(c.name || c.id,c.id)));
  $('cannon-select').addEventListener('change',selectCannon);
  $('angle').addEventListener('input', () => { rotating = false; $('rotate-cannon').textContent = '自动旋转'; angle = Number($('angle').value); renderAngle(); });
  $('rotate-cannon').addEventListener('click', () => { rotating = !rotating; $('rotate-cannon').textContent = rotating ? '停止旋转' : '自动旋转'; });
  $('reset-cannon').addEventListener('click', () => { rotating = false; angle = 0; $('rotate-cannon').textContent = '自动旋转'; renderAngle(); });
  if (!cannons.length) ['cannon-select','angle','rotate-cannon','reset-cannon'].forEach((id) => { $(id).disabled = true; });
  let lastTimestamp = null;
  function tick(timestamp) {
    const delta = lastTimestamp === null ? 0 : Math.max(0,timestamp - lastTimestamp); lastTimestamp = timestamp;
    if (!document.hidden && playing && clipFrames().length) {
      frameElapsed += delta;
      // Skip complete cycles mathematically after a stalled browser frame.
      const totalDuration = clipFrames().reduce((total,_,index) => total + frameDuration(index),0);
      if ($('loop-fx').checked && frameElapsed > totalDuration) frameElapsed %= totalDuration;
      let changed = false;
      while (playing && frameElapsed >= frameDuration(frameIndex)) {
        frameElapsed -= frameDuration(frameIndex);
        if (frameIndex < clipFrames().length - 1) { frameIndex += 1; changed = true; }
        else if ($('loop-fx').checked) { frameIndex = 0; changed = true; }
        else { playing = false; frameElapsed = 0; updatePlayButton(); }
      }
      if (changed) renderFrame();
    }
    if (!document.hidden && rotating) { angle = ((angle + Math.min(100,delta) * .035 + 180) % 360) - 180; renderAngle(); }
    requestAnimationFrame(tick);
  }
  document.addEventListener('visibilitychange', () => { lastTimestamp = null; });
  renderAssets(); selectClip(); selectCannon(); requestAnimationFrame(tick);
})();

/* Registered-control inspector: metadata + original PNGs, no per-state bbox fitting. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const registration = window.BUYU_UI_STATES;
  const families = registration && Array.isArray(registration.families) ? registration.families : [];
  const controlIds = ['ui-family-select','ui-state-select','ui-state-prev','ui-state-next','ui-state-scale','ui-state-sample','ui-state-show-text','ui-state-guides'];
  if (!families.length) {
    $('ui-state-error').hidden = false;
    controlIds.forEach((id) => { $(id).disabled = true; });
    return;
  }
  const familyNames = {primary:'主按钮',secondary:'次按钮',tab:'页签',close:'关闭按钮',slot:'物品格',toggle:'开关',checkbox:'勾选框','slider-thumb':'太极滑块'};
  const stateNames = {normal:'正常',pressed:'按下',disabled:'禁用',selected:'选中',locked:'锁定',empty:'空位',off:'关闭',on:'开启'};
  const textFamilies = new Set(['primary','secondary','tab']);
  const textSizes = {primary:28,secondary:26,tab:24};
  const fileUrl = (file) => '../' + String(file || '').replace(/\\/g,'/');
  const percent = (value) => Number.isFinite(Number(value)) ? `${(Number(value) * 100).toFixed(3)}%` : '未记录';
  let family = null;
  let stateIndex = 0;

  function positionRect(element, rect, scale) {
    const value = Array.isArray(rect) ? rect : [0,0,0,0];
    element.style.left = `${value[0] * scale}px`;
    element.style.top = `${value[1] * scale}px`;
    element.style.width = `${value[2] * scale}px`;
    element.style.height = `${value[3] * scale}px`;
  }
  function renderWarnings() {
    const list = $('ui-state-warnings');
    const warnings = Array.isArray(registration.warnings) ? registration.warnings : [];
    list.replaceChildren();
    if (!warnings.length) {
      const entry = document.createElement('li');
      entry.textContent = '注册文件未列超阈值告警；这仍不等于实际状态切换已通过。';
      list.append(entry);
      return;
    }
    for (const warning of warnings) {
      const entry = document.createElement('li');
      if (family && warning.family === family.id) entry.className = 'current-family';
      const drift = warning.relativeWidthHeight || [];
      entry.textContent = `${warning.id} · ${familyNames[warning.family] || warning.family} / ${stateNames[warning.state] || warning.state}：本体候选宽度变化 ${percent(drift[0])}，高度变化 ${percent(drift[1])}；阈值 ${percent(warning.threshold)}。${warning.assetId || ''}`;
      list.append(entry);
    }
  }
  function renderState() {
    if (!family || !Array.isArray(family.states) || !family.states.length) return;
    const state = family.states[stateIndex];
    const sharedScale = Math.max(0.01, Math.min(1, Number(family.sharedDisplayScale) || 1));
    const scale = $('ui-state-scale').value === 'native' ? 1 : sharedScale;
    const canvas = family.logicalCanvas || [1,1];
    const root = family.logicalRoot || [canvas[0] / 2, canvas[1] / 2];
    const offset = state.drawOffset || [0,0];
    const size = state.sourceNativeSize || [0,0];
    const space = $('ui-state-space');
    const image = $('ui-state-image');
    $('ui-state-plane').style.minWidth = `${Math.ceil(canvas[0] * scale + 96)}px`;
    $('ui-state-plane').style.minHeight = `${Math.max(360, Math.ceil(canvas[1] * scale + 96))}px`;
    space.style.width = `${canvas[0] * scale}px`;
    space.style.height = `${canvas[1] * scale}px`;
    space.style.transform = `translate(${-root[0] * scale}px,${-root[1] * scale}px)`;
    space.dataset.guides = $('ui-state-guides').checked ? 'on' : 'off';
    space.hidden = false;
    positionRect(image, [offset[0],offset[1],size[0],size[1]], scale);
    image.width = size[0]; image.height = size[1];
    image.src = fileUrl(state.file);
    image.alt = `${familyNames[family.id] || family.id} · ${stateNames[state.state] || state.state} · 原生 PNG`;
    positionRect($('ui-state-content'), family.contentRect, scale);
    positionRect($('ui-state-hit'), family.hitRect, scale);
    $('ui-state-origin').style.left = `${root[0] * scale}px`;
    $('ui-state-origin').style.top = `${root[1] * scale}px`;
    const text = $('ui-state-text');
    positionRect(text, family.contentRect, scale);
    text.textContent = $('ui-state-sample').value;
    text.hidden = !$('ui-state-show-text').checked || !textFamilies.has(family.id);
    text.style.fontSize = `${(textSizes[family.id] || 22) * scale / sharedScale}px`;
    text.style.color = family.id === 'primary' ? '#FFF4D6' : '#183F36';
    text.style.textShadow = family.id === 'primary' ? '0 1px 1px #17392fa6' : 'none';
    $('ui-state-select').value = state.state;
    $('ui-state-source').href = fileUrl(state.file);
    $('ui-state-info').textContent = `${familyNames[family.id] || family.id} / ${stateNames[state.state] || state.state} · 第 ${stateIndex + 1} / ${family.states.length} 态\n逻辑画布 ${canvas.join(' × ')}，根点 [${root.join(', ')}]\n当前统一缩放 ${scale.toFixed(6)}；组参考缩放 ${sharedScale.toFixed(6)}\n原图 ${size.join(' × ')}，drawOffset [${offset.join(', ')}]\ncontentRect [${(family.contentRect || []).join(', ')}]\nhitRect [${(family.hitRect || []).join(', ')}]\n${state.file}\n${textFamilies.has(family.id) ? '文字使用同组固定内容区；超长文案可能溢出，不自动挤压。' : '本组不叠加按钮文案，保留原图内置语义图形。'}`;
    renderWarnings();
  }
  function selectFamily() {
    family = families.find((entry) => entry.id === $('ui-family-select').value) || families[0];
    stateIndex = 0;
    $('ui-state-select').replaceChildren();
    for (const state of family.states || []) {
      $('ui-state-select').add(new Option(`${stateNames[state.state] || state.state} · ${state.state}`, state.state));
    }
    renderState();
  }
  function stepState(direction) {
    if (!family || !family.states.length) return;
    stateIndex = (stateIndex + direction + family.states.length) % family.states.length;
    renderState();
  }
  families.forEach((entry) => $('ui-family-select').add(new Option(`${familyNames[entry.id] || entry.id} · ${(entry.states || []).length} 态`, entry.id)));
  $('ui-family-select').addEventListener('change', selectFamily);
  $('ui-state-select').addEventListener('change', () => {
    if (!family) return;
    const next = family.states.findIndex((entry) => entry.state === $('ui-state-select').value);
    stateIndex = Math.max(0,next); renderState();
  });
  $('ui-state-prev').addEventListener('click', () => stepState(-1));
  $('ui-state-next').addEventListener('click', () => stepState(1));
  ['ui-state-scale','ui-state-show-text','ui-state-guides'].forEach((id) => $(id).addEventListener('change',renderState));
  $('ui-state-sample').addEventListener('input',renderState);
  $('ui-state-image').addEventListener('error', () => { $('ui-state-image-error').hidden = false; });
  $('ui-state-image').addEventListener('load', () => { $('ui-state-image-error').hidden = true; });
  selectFamily();
})();
