"""Refresh the UI mapping Markdown from current catalog/config metadata only.

Writes docs/UI_RUNTIME_ART_MAP.md only. Does not rewrite the historical JSON map,
touch PNGs, hash/decode images, pack atlases or infer interaction approval.
"""
from pathlib import Path
import datetime
import json
from ArtRuntimeBridge import read_json, catalog_stats

ROOT = Path(__file__).resolve().parent.parent


def cell(value):
    return str(value).replace('|','\\|').replace('\n',' ')


def main():
    from ArtAcceptanceState import accepted_unchanged
    if accepted_unchanged(ROOT):
        return write_accepted_map()
    catalog = read_json(ROOT/'assets/runtime-catalog.json')
    mapping = read_json(ROOT/'docs/UI_RUNTIME_ART_MAP.json')
    registry = read_json(ROOT/'config/ui-state-registration.json')
    bindings = read_json(ROOT/'config/skill-art-bindings.json')
    assets = {e['id']:e for e in catalog['assets']}
    clips = {c['id']:c for c in catalog['clips']}
    stats = catalog_stats(catalog['assets'],catalog['clips'])
    groups = {key:[e['assetId'] for e in refs] for key,refs in mapping['groups'].items() if key!='fx5'}
    groups['fx8'] = [e['id'] for e in catalog['assets'] if e['category']=='fx']
    slider = next(f for f in registry['families'] if f['id']=='slider-thumb')
    groups['slider-thumb'] = [s['assetId'] for s in slider['states']]
    groups['backpack'] = ['ui/additions/backpack']
    unresolved, missing_designs, referenced = set(), [], set()

    def check_asset(ident):
        referenced.add(ident)
        e = assets.get(ident)
        if not e or not (ROOT/e['file']).is_file() or not (ROOT/e['generationRecord']).is_file():
            unresolved.add(ident)

    for refs in groups.values():
        for ident in refs:
            check_asset(ident)
    notes = {
        '01-start':'标题与人物分别叠在纯港口背景；道童idle已导出候选，实际播放与交互尚未验收。',
        '03-lobby':'背包入口使用独立ui/additions/backpack；海域卡片裁切独立背景，锁定状态与入口热区由客户端管理。',
        '05-gameplay':'鱼/Boss78项与道童3项动作已导出648帧候选；当前releaseReady为0。8组FX使用当前catalog时序；炮台轴心、弹丸方向、鳍尾形变、循环与恢复需Unity播放审阅。',
        '15-signin':'道童静态主图及idle/celebrate动作候选均已落盘，动作切换、领取事件与循环/恢复待实际播放。',
        '16-events':'独立无字活动横幅已落盘；日期、标题、奖励与热区由客户端叠加，来源未知字段保持未确认。',
        '17-event-detail':'独立无字五岛底图已落盘；节点使用图中实际岛心坐标，连线、序号、奖励与状态由客户端叠加。',
        '23-profile':'人物静态主图与道童动作候选可分别接入；显示比例、脚根与动作切换仍需目标端验证。',
        '24-settings':'开关、勾选及两态太极滑块均有独立皮肤；滑块统一注册见config，拖动、数值、热区、焦点和状态切换仍待端内验收。',
        '31-components':'状态板仅为规范图；实际控件来自独立透明皮肤和当前family注册数据，未将整张状态板作为可点击界面。',
    }
    rows = []
    for screen in mapping['screens']:
        ident = screen['id']
        if not (ROOT/screen['sourceDesign']).is_file():
            missing_designs.append(screen['sourceDesign'])
        family_groups = ['fx8' if g=='fx5' else g for g in screen['componentGroups']]
        if ident=='03-lobby':
            family_groups.append('backpack')
        if ident in ['24-settings','31-components']:
            family_groups.append('slider-thumb')
        special = []
        for ref in screen['specialAssets']:
            asset_id = ref['assetId']
            check_asset(asset_id)
            role = '灵海仙渔主Logo' if asset_id == 'branding/brand-title' else ref.get('role','独立资源')
            special.append(cell(role)+'：`'+asset_id+'`')
        clients = list(screen.get('clientRendered',[]))
        clients = [s for s in clients if '动作尚未制作' not in s]
        if ident=='05-gameplay':
            clients = [s for s in clients if '78动作' not in s]
        if ident=='23-profile':
            clients = [s.replace('；人物动作尚未完成','；人物动作候选待播放审阅') for s in clients]
        description = '；'.join(clients+[notes.get(ident,screen.get('notes',''))]).strip('；')
        rows.append('| ['+cell(ident+' '+screen['title'])+'](../'+screen['sourceDesign']+') | '+
                    ', '.join('`'+g+'`' for g in family_groups)+' | '+
                    '；'.join(special)+' | '+cell(description)+' |')
    panel_id = mapping['scalingContract']['runtimePanel']['assetId']
    panel = assets[panel_id]
    caps = panel.get('nineSlice',panel.get('proposedNineSlice',mapping['scalingContract']['runtimePanel']['nativeCaps']))
    state_rows = []
    for family in registry['families']:
        for state in family['states']:
            check_asset(state['assetId'])
        state_rows.append('| `'+family['id']+'` | '+', '.join('`'+s['state']+'` → `'+s['assetId']+'`' for s in family['states'])+
                          ' | `'+str(family['logicalCanvas'])+'` / `'+str(family['logicalRoot'])+
                          '` | `'+str(family['sharedDisplayScale'])+'` |')
    skill_rows = []
    for binding in bindings['bindings']:
        check_asset(binding['icon'])
        art = '`'+binding['icon']+'`'
        if binding.get('castFx'):
            clip_id = binding['castFx']
            if clip_id not in clips:
                unresolved.add(clip_id)
            art += '；释放 `'+clip_id+'`'
        if binding.get('targetOverlay'):
            check_asset(binding['targetOverlay'])
            art += '；目标层 `'+binding['targetOverlay']+'`'
        if binding.get('activeOverlay'):
            overlay = binding['activeOverlay']
            art += '；持续层采用 `'+overlay['sourceClip']+'` 的frame '+str(overlay['sourceFrame'])
        skill_rows.append('| '+binding['name']+' | '+art+' | `'+binding['playback']+'` |')
    date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    text = f'''# 31个捕鱼界面的运行美术映射

核对日期：{date}。当前catalog为 **{stats['assetCount']}项＝{stats['staticAndFxAssetCount']}静态/FX＋{stats['animationFrameCount']}原生动作帧**；clips共{stats['clipCount']}组，包含{stats['nativeActionClipCount']}组角色动作与{stats['fxClipCount']}组FX。本表对应{len(mapping['screens'])}张UI设计稿。当前动作releaseReady为{stats['releaseReadyNativeActions']}；文件引用可解析不等于可点击界面或客户端验收通过。

界面用途及初始分组来自[JSON映射](UI_RUNTIME_ART_MAP.json)，当前资源和时序以[runtime-catalog.json](../assets/runtime-catalog.json)为准，控件状态以[ui-state-registration.json](../config/ui-state-registration.json)为准，技能绑定以[skill-art-bindings.json](../config/skill-art-bindings.json)为准。本工具只更新此MD，不改JSON中的历史时间与验收字段。

通用窗体使用`{panel_id}`，候选九宫格边距为`{caps}`，顺序为左/上/右/下原生像素。标题牌、关闭按钮和动态文字独立布局；中央徽章、圆形图形等比显示。候选九宫格与注册数据均须端内拉伸/切换审阅。

[Unity验收工程](../unity/BuyuClient/README.md)及源代码已创建，尚未启动编辑器、导入、编译或播放。本表描述独立美术与预期客户端绘制职责，31张整屏不会自动成为31个交互窗口。

| 界面与设计稿 | 共用组件组 | 独立美术与用途 | 客户端绘制 / 待验收项 |
|---|---|---|---|
'''+ '\n'.join(rows)+'''

## 当前控件状态注册

下表直接读取当前config。每个family按同一逻辑画布和root放置原生PNG，使用各状态`drawOffset`以及全family共用`sharedDisplayScale`。文本区域、热区和未绘制状态回退分别读取`contentRect`、`hitRect`、`stateFallbacks`；不可逐状态按光晕bbox缩放。

| Family | 实际状态与资产ID | 逻辑画布 / root（原生px） | 共用显示比例 |
|---|---|---|---|
'''+ '\n'.join(state_rows)+f'''

注册状态为`{registry['status']}`。当前保留{len(registry.get('warnings',[]))}项制作者警告（包括primary/secondary选中态形状差异）；元数据注册不证明切换无抖动。字体、动态换行、数字与安全区继续读取[文字配置](../config/ui-typography.json)和[字体包](../assets/fonts/fonts.json)。

## 六技能与当前FX

| 技能 | 当前独立资源 / clip | 播放语义 |
|---|---|---|
'''+ '\n'.join(skill_rows)+f'''

`fx8`在本表按当前catalog表示8组、128帧（渔网/冰封/雷网/捕获/命中/聚鱼/护持/激流）；角色动作由81个actor/action clip表示。每个clip的frames均为catalog资产ID。护持释放为one-shot，持续层使用单独登记的峰值帧，不能循环出现/消散帧冒充稳定护罩。追踪为空心目标层，鱼轨迹、命中、冷却与持续时间属于客户端逻辑。备用迅捷图形不替换激流。

## 当前引用检查与剩余验收

本次仅做文本/JSON元数据与文件存在性核对：{len(referenced)}个被引用资产ID，未解析引用{len(unresolved)}项，缺失选中设计稿{len(missing_designs)}项。没有读取/解码PNG或重新核验其hash、Alpha、像素、图集及实际播放。原始源边距/格位问题和动作候选状态仍以各manifest为准；不能把引用解析当作美术完成。

81组动作/648帧已导出候选，releaseReady仍为{stats['releaseReadyNativeActions']}；仍需真实播放审查身份、鳍尾/肢体相位、共享根点、跨动作尺度、循环接缝和捕获恢复。炮台轴心、弹丸方向、FX节奏、UI拉伸、文字、热区和全部控件交互也须Unity验证。

当前候选批次尚未发布。旧公开225项基线提交`e3fcb061a5672cfc967605befb98bcdd32e4cce8`及其[上传回执](PUBLIC_UPLOAD_RECEIPT.json)保持原范围，不能据此声称当前{stats['assetCount']}项或Unity工程已上传。历史13页atlas/218项像素回环也不扩展为新增资源的全量通过。
'''
    if unresolved:
        text += '\n待核对引用：'+', '.join('`'+s+'`' for s in sorted(unresolved))+'。\n'
    (ROOT/'docs/UI_RUNTIME_ART_MAP.md').write_text(text,encoding='utf-8')
    print(json.dumps({'written':['docs/UI_RUNTIME_ART_MAP.md'],'screens':len(mapping['screens']),
                      'catalogAssets':stats['assetCount'],'referencedAssets':len(referenced),
                      'unresolvedReferences':sorted(unresolved),'missingSelectedDesigns':missing_designs,
                      'pngReads':0,'jsonWrites':0,'runtimeIntegrationVerified':False},ensure_ascii=False))


def write_accepted_map():
    catalog=read_json(ROOT/'assets/runtime-catalog.json')
    mapping=read_json(ROOT/'docs/UI_RUNTIME_ART_MAP.json')
    registry=read_json(ROOT/'config/ui-state-registration.json')
    assets={a['id']:a for a in catalog['assets']}
    rows=[];missing=[]
    for screen in mapping['screens']:
        refs=[]
        for ref in screen['specialAssets']:
            ident=ref['assetId']
            if ident not in assets or not (ROOT/assets[ident]['file']).is_file():missing.append(ident)
            refs.append(('正式Logo' if ident=='branding/brand-title' else ref.get('role',ident))+'：`'+ident+'`')
        if not (ROOT/screen['sourceDesign']).is_file():missing.append(screen['sourceDesign'])
        groups=['fx8' if g=='fx5' else g for g in screen['componentGroups']]
        if screen['id']=='03-lobby':groups.append('backpack')
        if screen['id'] in ['24-settings','31-components']:groups.append('slider-thumb')
        rows.append('| ['+cell(screen['id']+' '+screen['title'])+'](../'+screen['sourceDesign']+') | '+', '.join('`'+g+'`' for g in groups)+' | '+'；'.join(cell(v) for v in refs)+' |')
    states=['| `'+f['id']+'` | '+', '.join('`'+s['state']+'` → `'+s['assetId']+'`' for s in f['states'])+' | `'+str(f['logicalCanvas'])+'` | `'+str(f['sharedDisplayScale'])+'` |' for f in registry['families']]
    text='''# 31个界面的首发运行美术映射

本批首发美术已经实际Unity导入、编译、播放和agent画面验收；924项PNG、89组clip、81套角色动作均有最终证据，见[UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。下表为设计参考与独立资源的对应，不把31张截图当作31个生产交互窗口。

动态文案、正式标题Logo、数据、奖励、冷却、红点、滚动、锁定、交互和状态由客户端叠加；原设计截图的测试文字不作为业务数据。4海域/港口及两张无字活动插画有独立文件，活动路径使用实际岛心坐标。

| 界面与设计稿 | 组件分组 | 独立美术与用途 |
|---|---|---|
'''+ '\n'.join(rows)+'''

## 共用控件

| Family | 独立状态资源 | 逻辑画布 | 全家族统一比例 |
|---|---|---|---|
'''+ '\n'.join(states)+'''

数据读取[状态注册](../config/ui-state-registration.json)，按logicalRoot/drawOffset/sharedDisplayScale放置，文字使用contentRect，热区使用hitRect。8类22状态、实际指针事件和文字安全区已验收。primary/secondary选中态源形状差异记录保留，未逐状态按bbox缩放；hover/focus按明示回退规则。

通用窗体、列表行、提示面板已在640/960/1200宽度实际拉伸。nineSlice为源像素L/T/R/B，tooltip为64四边，list-row为[112,56,112,56]，其余值从当前catalog读取。标题、圆形徽章和图标等比显示，文字另行排版。

## 动作、技能与炮台

36鱼种各游动/捕获，3Boss额外攻击/怒态，道童idle/point/celebrate，共81动作648帧；40循环、41单次，按manifest逐帧时长播放。8组FX共128帧、16FPS、单次，护持持续层用另记峰值帧。六技能绑定见[配置](../config/skill-art-bindings.json)，客户端负责目标、轨迹、命中、持续时间和冷却。

6套炮管root与原生炮口见[cannon-registration.json](../config/cannon-registration.json)，已实际检查18个角度样本；弹丸头锚/原始朝向见catalog.projectile，运行演示按炮管子节点发射并完成捕获。帧使用全clip统一显示比例，不能按逐帧透明包围框fit。

字体包含Noto Sans/Serif CJK SC及OFL；两字体各57样例字符可用。最终实际渲染、所有动作帧和原始技术报告随[acceptance](acceptance/README.md)交付。原始技术报告保持自身技术范围字段，完成结论由上层视觉审阅封存。
'''
    if missing:raise ValueError('Missing current mappings: '+str(missing))
    (ROOT/'docs/UI_RUNTIME_ART_MAP.md').write_text(text,encoding='utf-8')
    print(json.dumps({'screens':len(rows),'missingReferences':missing,'acceptedEvidenceReused':True}))

if __name__=='__main__':
    main()
