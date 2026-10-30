"""Write the current accepted delivery overview; preserve dated production evidence."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def put(p,t):(ROOT/p).write_text(t,encoding='utf-8')

def main():
    final=read('docs/UNITY_FINAL_ACCEPTANCE.json')
    if not final.get('accepted'):raise SystemExit('Final art acceptance is required')
    counts=final['counts']['counts']
    rows='\n'.join(f'| {k} | {v} |' for k,v in counts.items())
    put('README.md','''# 灵海仙渔 · 道家Q版捕鱼首发美术

**本批首发美术完成，已在本机 Unity 6000.6.0f1 完成实际导入、编译和逐项验收。** 交付 31 项UI设计、276项静态/FX资源、81套648张原生动作帧，共924项运行PNG；另有146页图集。最终范围与输入哈希见 [最终验收](docs/UNITY_FINAL_ACCEPTANCE.json)。

![灵海仙渔](assets/branding/linghai-xianyu-logo-v1.png)

## 直接查看

- [Unity工程与运行步骤](unity/BuyuClient/README.md)，打开 Assets/Scenes/BuyuArtReview.unity，点击Play。
- [独立素材与动作审阅台](assets-preview/index.html)，无需服务器；支持筛选、逐帧、明暗叠底和炮台旋转。
- [31项UI完整图集](gallery/index.html)、[界面资源映射](docs/UI_RUNTIME_ART_MAP.md)。
- [交付说明](docs/GAME_ART_DELIVERY.md)、[实际状态](docs/GAME_ART_STATUS.json)、[逐项画面与报告](docs/acceptance/README.md)。

## 交付内容

36鱼种静态精灵及游动/捕获，3个Boss额外攻击/怒态，道童待机/指向/庆祝；6套炮台12部件；4海域与1港口；6头像与道童全身；34个UI组件、36图标、6技能、9饰件、2活动插画、正式Logo；8组共128帧FX。81套角色动作各8帧，共40循环、41单次；含FX共89个clip。

所有PNG保持实际原生像素，注册仅用整数平移和透明补边；每个clip统一显示比例，不按逐帧包围框缩放。正式名称为《灵海仙渔》，Logo原生1774×887。品牌、炮口、UI状态、技能及字体配置在config目录。两款Noto CJK字体附OFL。

美术完成范围对应本批首发合同。31张整屏是布局与视觉设计；动态文字、数据、交互窗口及游戏业务仍由客户端实现。随包Unity工程提供实际可运行的美术审阅和离线捕鱼演示，验收未覆盖联网服务、经济系统、声音音乐、商店宣传素材或Standalone构建。

## 上传与接手

公开仓库：[lhl-java/luhailong-python](https://github.com/lhl-java/luhailong-python)，项目位于buyu-image。当前冻结包通过 [PUBLIC_RELEASE_MANIFEST.json](../PUBLIC_RELEASE_MANIFEST.json) 核对每个文件；实际远端提交及下载验收以本地docs/PUBLIC_UPLOAD_RECEIPT_CURRENT.json为准，该回执在Push后产生，不递归收入本次提交。旧225项批次回执继续作为历史证据。

新电脑保留整个buyu-image结构，先读 [长期指令](AGENTS.md)、[美术定调](docs/ART_DIRECTION.md)和[模型记录政策](docs/IMAGE_MODEL_POLICY.md)，确认邮件/组队两主参考实际存在。实际图像工具未披露的型号/质量保持未确认，不把配置目标写成已锁定结果。

后续参考素材放 [references/incoming](references/incoming/) 下对应ui/characters/fish/cannons/requirements目录。制作工具会在验收输入完全未变时复用已通过状态；修改PNG、时序、根点、尺寸或接入代码后必须复验受影响项。
''')
    put('docs/GAME_ART_DELIVERY.md',f'''# 灵海仙渔首发美术交付

本批 **gameArtComplete=true**，81/81套角色动作releaseReady，全部89套clip已实际进入Unity PlayMode。完成证据为[最终验收](UNITY_FINAL_ACCEPTANCE.json)，逐项图片和原始技术报告在[acceptance](acceptance/README.md)。这份结论仅适用于记录的输入哈希。

| 运行资源类别 | 数量 |
|---|---:|
{rows}

合计924项＝276静态/FX＋648角色动作帧。角色动作按用户选择直接用图像模型生成原生姿态表，不要求视频。81动作各8帧，40组loop、41组one-shot；另8组FX各16帧，16FPS、1秒单次。

Unity实际核对955张导入贴图（924资源＋31设计图）、924个Sprite、89个clip、8类22状态、2字体各57个样例字符；1087项检查无错误。PlayMode覆盖每个动作的全部帧、循环回绕及单次完成回调；实际GraphicRaycaster完成16项指针检查，炮台18个角度样本与捕鱼捕获事件通过。画面审阅与技术结果分别保留，未声称有人类手动验收。

原生打包验证为146页图集、917项逐像素回环全部一致；5场景和2插画独立存放。最终重新核对所有924张源PNG和146张图集SHA256，复用未变像素证据；后续九宫格/炮口修改仅为元数据，不重复编造像素打包结果。

修正了secondary选中文字对比、提示面板64px角边、列表112/56/112/56边距、海面铺满与炮台安全位置。6套炮管各有原生炮口坐标，旋转后子节点定位发射点。源网格/边距和状态形状警告保留，逐项画面复核处理见[视觉记录](acceptance/AGENT_VISUAL_REVIEW.json)。

31张整屏继续作为美术/布局参考，正式透明素材、字体与运行状态独立接入；旧整屏中的示例文案不作为业务数据。完整联网客户端、声音、商业化系统、商店宣传与Standalone构建不在本批美术合同内。

发布目的地为[lhl-java/luhailong-python](https://github.com/lhl-java/luhailong-python)的buyu-image目录。最新冻结文件清单位于仓库根PUBLIC_RELEASE_MANIFEST.json；本机独立下载回执为PUBLIC_UPLOAD_RECEIPT_CURRENT.json，Push后单独保存。历史225项基线回执不证明本次上传。
''')
    put('unity/BuyuClient/README.md','''# 灵海仙渔 Unity 美术验收工程

已使用本机 **Unity6000.6.0f1**（f7f8ed4d1e24）完成真实导入、C#编译、PlayMode和首发美术验收。正式结论及精确范围见 [最终验收](../../docs/UNITY_FINAL_ACCEPTANCE.json)与[画面证据](../../docs/acceptance/README.md)。

## 打开与运行

用对应版本打开本目录，等待资源导入，打开 `Assets/Scenes/BuyuArtReview.unity` 后点Play。菜单 Buyu / Create or Open Art Review Scene 也可打开。场景已实际生成并随包提交，现存场景不会被自动重建。Unity需本机已激活的许可。

两个本地UPM包直接引用仓库文件：com.lhl.buyu.art → file:../../../assets；com.lhl.buyu.ui-designs → file:../../../designs/ui。保留整个buyu-image目录即可迁移，不复制整套源PNG。uGUI2.6.0和所需内置模块随Unity解析，不依赖收费插件。

工程有六个入口：动作/特效（89clip）、31张界面设计、924项独立素材、6炮台轴心、8类22UI状态、离线捕鱼演示。方向键切换，空格播放/暂停或发射，鼠标点击鱼触发射击；捕鱼覆盖36鱼种。可暂停、逐帧、重播、切换明暗底和原生1:1显示。根点十字、炮口红点与顶部导航为验收叠层。

PNG导入保持原生尺寸、RGBA32、sRGB、输入Alpha、无压缩/无mipmap/NPOT不缩放；Unity可扩展全透明像素下的RGB供双线性采样，源PNG不变。顶左归一化root只转换一次Y，帧播放器累积真实durationMs，单次片段结束停末帧并回调一次。炮口由config/cannon-registration.json登记，旋转后随炮管子节点变换。

UI逻辑画布/热区/文字区/状态drawOffset共用注册，未独立绘制的hover/focus按配置回退。Tooltip和list-row使用已验收九宫格边距；文字由两款Noto CJK字体实时排版。31张截图是设计参考，运行验收不把它们冒充31个生产交互窗口。

## 复验

技术入口：`-batchmode -projectPath <本目录> -executeMethod Buyu.Editor.BuyuArtValidation.ValidateAll -logFile <日志路径>`，结果为Logs/BuyuArtValidation.json。实际画面入口：`-executeMethod Buyu.Editor.BuyuRuntimeAcceptanceEntry.Run`，主报告覆盖89clip；`-buyuSupplement`补充16帧FX与完整Boss视窗；`-buyuUiOnly`仅复验UI、炮口/拉伸和捕鱼。后三项使用实际GPU渲染，不加-nographics，也不加-quit抢先退出。

原始技术报告保留自身“视觉审阅待外部确认”字段，技术脚本不自动授予美术批准；最终agent视觉审阅另封存。变更后先检查影响项，再用根目录tools/Accept-GameArt.py重新封存实际证据，不能仅靠修改布尔值。

Library/Temp/Logs/UserSettings为本地忽略产物；交付保留Assets/Packages/ProjectSettings及.meta。当前范围为Editor美术验收，未构建Standalone。Standalone如需沿用原图需正确打包StreamingAssets及导入Font资产，说明见源码加载器；这不是已交付的生产发行包。
''')
    put('docs/acceptance/README.md','''# 首发美术验收证据

最终状态和输入SHA256在[UNITY_FINAL_ACCEPTANCE.json](../UNITY_FINAL_ACCEPTANCE.json)。[AGENT_VISUAL_REVIEW.json](AGENT_VISUAL_REVIEW.json)记录root agent实际查看范围、修正和限制，没有声称人类手动验收。

- unity-import.json：实际Unity导入/编译后的1087项技术检查，955贴图、924Sprite、89clip、31设计图、8类22状态与2字体。
- runtime-all-89.json：实际PlayMode覆盖全部89clip所有帧，检查loop回绕/单次完成与回调。
- runtime-fx-boss-supplement.json：完整16帧FX联系图和固定整只Boss视窗。
- runtime-ui-cannon-final.json：最终按钮状态、18个炮口角度、9次九宫格拉伸、实际指针与捕获事件。
- motion/：89张实际Unity逐帧渲染联系图，FX为16格；同clip固定视窗、根点和源显示比例。
- screens/：31项实际Unity设计图显示；ui/：8类状态；cannons/：6炮台与多角度；stretch/：3组件各3宽度。

![实际捕鱼演示](fishing-before.png)

![发射捕获后](fishing-after.png)

以上图片为确定性Unity画面导出，不是新增AI生图。报告自己的manualVisualApproval/gameArtComplete=false保留原始技术范围，最终视觉审阅与完成结论单独在上层封存，未篡改历史报告。原生像素、来源、时长和显示比例证据仍在assets清单和逐图记录中。
''')
    # Update the active integration guide while retaining the detailed coordinate contracts.
    path=ROOT/'docs/GAME_ART_INTEGRATION.md';text=path.read_text('utf-8')
    paragraphs=text.split('\n\n')
    replacements={
      '[Unity美术验收工程]':'[Unity美术验收工程](../unity/BuyuClient/README.md)已完成实际导入、编译、PlayMode与美术验收。全部81动作releaseReady；最终证据和范围见[UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。',
      '单图可直接加载。':'单图可直接加载。当前146页atlas覆盖917项，所有入图集区域与原生RGBA逐像素一致；5场景及2插画独立加载。全924源PNG与146atlas的最终SHA256已复核，九宫格元数据更新不改变像素。正式打包不旋转、不缩放、不裁紧共享画布。',
      'UI状态按 ':'UI状态按 [ui-state-registration.json](../config/ui-state-registration.json) 的family共用逻辑画布、logicalRoot、drawOffset、sharedDisplayScale；文本用contentRect，热区用hitRect。8类22状态已经实际渲染和切换，原画形状差异警告保留。未独立绘制hover/focus按配置回退，不能按单状态光晕bbox缩放。',
      '`nineSlice`':'`nineSlice`顺序为左、上、右、下原生像素。通用窗体、列表、提示框已按640/960/1200宽度实际拉伸审阅；tooltip为64四边，list-row为[112,56,112,56]。中央徽章、标题牌、圆形头像和图标等比显示，文字独立布局；完整值以catalog为准。',
      '炮台每套':'炮台每套底座与炮管各一张PNG。朝上，底座30/炮管31；root为顶左归一化[0.5,0.70]。各炮口按[原生登记](../config/cannon-registration.json)设置旋转子节点，18角度实际检查通过；不要用共享长度估计炮口。弹丸icons/bullet头锚[0.31,0.61]，美术原前向顶左坐标[-0.7071,0.7071]，旋转对准速度。',
      '当前不宣称':'首发2D美术合同已完成，gameArtComplete=true；不包含联网、经济、声音、商店发布素材或Standalone构建。当前冻结批次、远端SHA与独立下载结果分别见发布清单和本机PUBLIC_UPLOAD_RECEIPT_CURRENT.json。旧225项回执继续仅作历史证据。'}
    for i,p in enumerate(paragraphs):
        for start,replacement in replacements.items():
            if p.startswith(start):paragraphs[i]=replacement;break
    text='\n\n'.join(paragraphs).replace('实际Alpha、鳍尾/肢体形变、身份、循环接缝、捕获恢复和跨动作尺度仍未验收；文件数量或不同hash不等于动作通过。','实际播放、逐帧姿态、共享尺度、循环/单次恢复与Alpha已经结合技术报告和agent画面审阅验收，见最终证据；文件计数本身不作为通过依据。')
    put('docs/GAME_ART_INTEGRATION.md',text)
    # These files are dated records, so append the new result instead of rewriting old evidence.
    for file in ['docs/GAME_LOGO_DELIVERY.md','docs/UI_SUITE_DELIVERY.md','docs/ANIMATION_FRAME_CONTRACT.md','docs/UNITY_ART_ACCEPTANCE_HANDOFF_20261028.md']:
        path=ROOT/file
        if not path.exists():continue
        text=path.read_text('utf-8')
        note='> 当前接续：本机资源限制已由用户明确解除，本批首发美术已完成Unity导入、编译、实际播放和agent逐项画面验收。结论、精确范围及输入哈希见 [UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。下方保留原日期的制作过程记录；历史“未启动/待验收/未上传”不代表当前状态。\n\n'
        if not text.startswith('> 当前接续：'):put(file,note+text)
    print(json.dumps({'written':'current accepted delivery, Unity instructions and dated-record continuation notes'},ensure_ascii=False))

if __name__=='__main__':main()
