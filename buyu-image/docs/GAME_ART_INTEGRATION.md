# 捕鱼美术资源接入

统一入口为 [runtime-catalog.json](../assets/runtime-catalog.json)，离线素材审阅台读取同内容的 [runtime-catalog.js](../assets/runtime-catalog.js)。当前924项资源由276项静态/FX和648张原生角色动作帧组成；89组clips包括8组FX和81组角色动作。31项UI整屏设计继续在 [gallery](../gallery/index.html) 展示，用于美术、层级与功能参考；整屏图不是可点击窗口实现。

[Unity美术验收工程](../unity/BuyuClient/README.md)已完成实际导入、编译、PlayMode与美术验收。全部81动作releaseReady；最终证据和范围见[UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。

## 文件与显示尺寸

`file`、`generationRecord`、`manifest`和atlas路径均相对项目根。`id`是带分类命名空间的唯一键，`localId`是各组内名称。PNG保留实际原生像素，默认禁止放大。

静态资源的`displayBox`是建议显示上限，`displaySize`是在该范围内等比缩小后的完整源图尺寸。**角色动作使用不同合同**：`uniformDisplayScale`是该clip全帧共用的原生像素到显示像素比例；`displaySize=canvas×uniformDisplayScale`表示完整透明画布的显示尺寸，`bodyDisplayBox`另记可见身体目标。不得把整张透明画布再次fit到120×80或128×128，也不得逐帧按Alpha包围框fit。

C组动作的校准值来自源manifest的`animation.displayCalibration.uniformDisplayScale`，catalog已继承。道童idle用入口帧实测原生身高501px对齐显示身高280px，全8帧共用`280/501`；其800方画布显示为约447.106方。point与celebrate分别使用各自已记录的统一clip密度校准，不能逐帧修改比例。

单图可直接加载。当前146页atlas覆盖917项，所有入图集区域与原生RGBA逐像素一致；5场景及2插画独立加载。全924源PNG与146atlas的最终SHA256已复核，九宫格元数据更新不改变像素。正式打包不旋转、不缩放、不裁紧共享画布。

## 透明、根点与UI状态

PNG按普通straight-alpha读取。若引擎要求预乘Alpha，统一在导入阶段处理，避免重复预乘。`anchor`与clip的`root`采用**左上原点归一化源画布坐标**；Unity左下原点pivot为`[x,1-y]`，catalog已提供`unityPivot`，不可再次翻转。道童脚根为`anchor=[0.5,0.85]`，对应Unity pivot约`[0.5,0.15]`。保留每组共享root，不随每帧可见边界重置位置。

UI状态按 [ui-state-registration.json](../config/ui-state-registration.json) 的family共用逻辑画布、logicalRoot、drawOffset、sharedDisplayScale；文本用contentRect，热区用hitRect。8类22状态已经实际渲染和切换，原画形状差异警告保留。未独立绘制hover/focus按配置回退，不能按单状态光晕bbox缩放。

`nineSlice`顺序为左、上、右、下原生像素。通用窗体、列表、提示框已按640/960/1200宽度实际拉伸审阅；tooltip为64四边，list-row为[112,56,112,56]。中央徽章、标题牌、圆形头像和图标等比显示，文字独立布局；完整值以catalog为准。

## FX、角色动作与炮台

八组FX为渔网、冰封、雷网、捕获、命中、聚鱼、护持、激流，各16帧，16FPS、总长1秒，正式播放为单次。各clip的`canvas`以catalog为准：前五组314方，新增三组394方；后者在原生314方提取图四边各加40px透明边，像素未缩放，不能宣称新增原生394细节。源图边距警告与运行时补边门禁分开保留。已有WebP只作审片预览，循环预览不改变正式one-shot设置。

六技能的图标、释放FX和持续状态绑定读取 [skill-art-bindings.json](../config/skill-art-bindings.json)。追踪使用空心锁鱼环；护持释放片段单次播放，持续护罩采用另记的峰值帧叠层与透明度反馈，不循环整套出现/消散帧。聚鱼轨迹、冷却、持续时间和命中判断由游戏逻辑驱动。

角色动作按用户指定的原生AI动作表制作，648张PNG组成81个8帧clip（鱼/Boss78、道童3），无需视频前置。`clips.frames`是catalog资产ID，按数组顺序播放；`fps`、`loop`、`durationsMs`、`durationMs`和根点来自实际manifest，不从旧计划硬编码。当前40组loop、41组单次；12FPS动作的整数帧长为83/84ms组合，应累积逐帧时长，避免把每帧统一截为83ms。实际播放、逐帧姿态、共享尺度、循环/单次恢复与Alpha已经结合技术报告和agent画面审阅验收，见最终证据；文件计数本身不作为通过依据。

炮台每套底座与炮管各一张PNG。朝上，底座30/炮管31；root为顶左归一化[0.5,0.70]。各炮口按[原生登记](../config/cannon-registration.json)设置旋转子节点，18角度实际检查通过；不要用共享长度估计炮口。弹丸icons/bullet头锚[0.31,0.61]，美术原前向顶左坐标[-0.7071,0.7071]，旋转对准速度。

## 客户端绘制与验收范围

文字、数值、红点、数量、冷却扇形、禁用灰化、锁定剪影、模态遮罩、滚动裁切和交互反馈由客户端渲染。背包入口与两态太极滑块已各有独立资源；滑块的位置、拖动、热区和数值仍属于客户端行为。三甲数字叠在空白奖章中心，寻宝连线和状态叠在无字岛图上。

首发2D美术合同已完成，gameArtComplete=true；不包含联网、经济、声音、商店发布素材或Standalone构建。当前冻结批次、远端SHA与独立下载结果分别见发布清单和本机PUBLIC_UPLOAD_RECEIPT_CURRENT.json。旧225项回执继续仅作历史证据。