# UI状态注册与文字规格

当前状态为 `candidate_pending_visual_runtime_review`。本次只读取22张小PNG的Alpha及已有manifest/QA，写入注册数据和字体规格；没有改写、缩放或重画任何PNG，没有渲染联系表、批量构建、测试或重打atlas。原按钮/HUD切片的静态QA仍可追溯，但它不证明运行中的状态切换已通过。

入口为 [ui-state-registration.json](../config/ui-state-registration.json)，生成工具为 [Register-UiStates.py](../tools/Register-UiStates.py)。八组22状态包括主/次按钮各四态、页签二态、关闭二态、槽位四态、开关二态、复选框二态和新增太极滑块拇指二态。它们都是已存在的原生切片；未存在的按下、禁用等状态只给出明确客户端复用/着色策略，不伪造额外PNG。

## 共享几何

所有坐标为原生源像素，矩形格式为`[x,y,width,height]`，左上为原点。每组有共享`logicalCanvas`、`logicalRoot`、`contentRect`与`hitRect`；每张图只有自己的`drawOffset`，按原始宽高以1:1放进这张逻辑画布。选中辉光仍保留完整，不参与逐状态的单独缩放。

客户端先从参考状态本体和目标显示范围算出一次统一组缩放，再把相同缩放用于全部状态、文字锚点和点击区域。JSON的`sharedDisplayScale`只是参考viewport的候选值，不是已冻结的客户端布局。不要继续拿每张独立PNG的外框各自适配128×128，否则带辉光状态的按钮本体会缩小。

```text
scale = family.sharedDisplayScale
imageLeft = controlRootX + (state.drawOffset.x - family.logicalRoot.x) * scale
imageTop  = controlRootY + (state.drawOffset.y - family.logicalRoot.y) * scale
draw source PNG at originalWidth * scale, originalHeight * scale
text and hitRect use the same family scale and logicalRoot; never per-state bbox fit
```

`drawOffset`均为整数，不重采样源图；本体中心因奇偶尺寸的舍入偏差记录在`rootResidualPx`，最多0.5个原生像素。此偏差不能拿来证明实际光学中心已确认。需要在目标运行界面实看。

本体候选用Alpha≥224的包围框测量，同时记录192与240阈值作依据。不能用Alpha254/255直接找“实心本体”：原画许多近不透明纹理并不是255，例如选中槽位最大Alpha为254，但Alpha254只有稀疏区域。阈值框只是避免外围淡辉光参与适配的启发式，不会识别所有装饰、笔触或内框。

未来若需要同canvas PNG，可按`futurePaddingExport`把原PNG放到逻辑画布的整数偏移处，只增加透明边；本次没有导出这种派生PNG，也没有将它称为新模型生成。

## 原画形变风险

共享位置和缩放能避免辉光引起的整体缩小，却不能消除不同状态原画已经存在的本体形变。当前阈值测量中两条超过3%的告警如下，均保留在JSON的`warnings`：

| 告警 | 原文件 | 本体宽度变化 | 本体高度变化 | 阈值 |
|---|---|---:|---:|---:|
| source_state_core_shape_drift | assets/ui/buttons/primary-selected.png | +0.912% | +5.085% | 3% |
| source_state_core_shape_drift | assets/ui/buttons/secondary-selected.png | +1.846% | +4.237% | 3% |

页签选中本体宽度约+2.572%，槽位选中约+2.439%宽/+1.230%高；都未触发3%告警，但仍需实看切换。开关/复选框本来有语义图形变化，不以像素完全相同作为验收条件。新增拇指已实际查看，太极朝向一致，按下态更暗，仍只是候选注册而非运行验收。

当前不自动要求全部重画。先在固定位置和统一组缩放下做原生/游戏显示尺寸的实际切换终审；若按钮本体仍明显变厚、扩张或角装饰跳动，再只对有问题的选中态作定点AI编辑，以正常态为结构参考，保留原native细节和完整辉光。不能偷偷按单张图缩放、非等比压扁或裁掉辉光，把告警伪装成消除。

## 文字

[ui-typography.json](../config/ui-typography.json)提供38px窗口标题、28px分区标题、22px正文、18px辅助文字、28/26px主次按钮、24px页签/数字及36px大数字的候选规格，参考当前1672×941原生设计族。行高、颜色、溢出、数字对齐和跨状态锚点均有明确字段，仍待目标客户端测量。

Windows原有Microsoft YaHei/KaiTi/Arial只记录本机存在，未复制这些字体，也不把其存在当作分发许可。现已另行补齐官方Noto Serif CJK SC与Noto Sans CJK SC两份Regular400及实际OFL1.1许可，见[字体交付](FONT_DELIVERY.md)；排版配置优先加载这两个随包文件，系统font fallback仍只是后备次序。由于只带Regular，token改用实际400，不宣称medium/bold已随包。标题/按钮不横向压缩；长正文换行/滚动，名单可省略但详情提供全名，关键数量和操作不能被不明缩写截掉。Noto字形与主参考实际搭配仍待终审，不是选择字体就自动风格通过。

整套31页的最长中文、较大金额、按钮标签、字体fallback与缺字、实际最小横屏尺寸都还没有运行验收。没有把本次metadata或JSON可读取称为交互和排版已通过。
