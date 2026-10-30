# 青鳍鱼 8 帧游动样片 · 2026-10-28

> 这是历史首次送审记录。后续已完成整数瞳孔注册并为游动/捕获统一576×576画布，眼(368,276)、根(288,288)；当前结果见运行manifest与 [本批汇总](../../FISH01TO12_PRODUCTION_REPORT.md)。本文的444画布与未注册项只描述首次样片，源名义网格边距告警仍保留；播放验收仍待Unity。

当前候选为 `01-qingqi-swim-contained-v2.png`，原生 1774×887，真 Alpha；4×2 等格切出 8 张 444×444 固定画布，只有源格右/下 0—1px 透明补齐，没有缩放、重绘、旋转或程序变形。目标可见鱼体框 120×80，最终统一显示比例留给 root；原生可见框约 304—323×188—235，满足后续缩小使用而无须上采样。

## 实际目视

已查看原生表和 `tmp/art-qa/01-qingqi-swim-light.png`、`01-qingqi-swim-dark.png`。鱼脸、蓝青鳞片、金边鳍、金色卷纹和朝右身份一致，浅深背景下轮廓完整。尾扇形状从中位向上弯（01）、上峰（02）、回落（03），再向下弯（05/06）和恢复（07）；近侧鳍在前四帧下展，后半帧上收，并有膜片形状变化。这是原生 AI 逐帧形变，而非平移/旋缩整图。文件哈希不同仅作追溯，不作为动作通过依据。

## 尚未通过项

- `warnings=[]` 仅指切格边缘没有 Alpha；不等同全部 QA 通过。
- 源边距 7/8 帧仍低于合同 12%：最小为 frame-02 的 9.459%。逐帧具体值保留于 `01-qingqi-swim.visual-qa.json` 与运行 manifest 的 `sourceMarginWarnings`。没有补边掩盖源门禁，也没有宣称源边距通过。
- 生成的头/躯干尚未登记：上排头部局部 y 约 283，第二排约 197，约 86px 行间漂移；各帧眼睛 x 另有小量漂移。固定画布与 root [.5,.5] 只是数据合同，不能称实际注册完成。需 root 选定前躯干/眼睛共同基准后用整数平移统一注册，不能按每帧 bbox 拉伸。
- 8→0 循环接缝、真实双鳍交替和整体节奏尚未经播放验收。身份、motion 与 loop 仍 `pending_root_visual` / `pending_root_playback`。
- 两次 AI 留白返修后主体已完整且有明显改善；本样片停在 root 目视评审，尚未扩批。前两张 PNG 暂属当前选择比较材料，待 root 确认采用稿后按素材保留规则清理，来源文字记录保留。

## 交付

- 源：`designs/motion-frames-v1/01-qingqi/swim/01-qingqi-swim-contained-v2.png`（SHA256 `8062b4d48c58d7d0d64f776e24a670ae3b100fe0898208d12132c1d0ba856bfd`）
- 帧与 manifest：`assets/animations/01-qingqi/swim/`
- 帧顺序 00—07；12FPS；loop=true；时长 [83,84,83,83,84,83,83,84] ms（12FPS 为权威，整数毫秒按累计边界四舍五入）。
- 所有调用均为内置 image_gen。每张源保留 request、prompt、实际 tool receipt 与 generation 记录；配置目标 GPT Image 2.5 Sunburst/max，工具没有 model/quality 参数且返回未披露，实际值 null/未确认。
- 未调用 API、未上传、未改 global catalog/status/Git、未运行重型构建/测试/atlas/Unity。

