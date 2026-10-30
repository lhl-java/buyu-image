# 本制作窗口动作候选交接（2026-10-28）

当前已落盘19动作、152帧：25–30号各swim/capture的12动作96帧；31–33号由root生成、此窗口只导出其6动作48帧；道童idle8帧。全部仍为 `candidate_pending_root_visual_and_playback_review`，`releaseReady:false`。目录与逐动作校准见 `FRAME_WORKER_25_36_PROGRESS.json`。未改全局catalog/status/Git，未创建Unity或运行重型测试/批量渲染。

## 产物与来源

- 25–30号动作图：`designs/motion-frames-v1/{id}/{swim|capture}/`，实际调用request/prompt/tool-result/generation记录齐全。每次调用均读取现行AGENTS、图像配置与策略，实际查看并附身份图及两张主风格图。
- 31–33号：只读取root既有 `*-v1.png`、`extract-v1.json`、owned pose PNG与 `source-v1-qa.json`；不生成、不修改这些源。源哈希符合既有ownership报告。
- 最终候选帧：`assets/animations/{id}/{action}/frame-00.png` 至 `frame-07.png`、逐帧来源JSON和manifest。
- 25–30共享640²透明canvas；31–33共享800²；道童idle800²。鱼动作8帧12fps，swim循环、capture单次；道童idle8fps循环。时长由累计帧边界四舍五入，不编造额外相位或重复帧。
- 新图实际型号/质量工具未返回，均保持null；配置目标GPT Image2.5/max不是实际锁定证明。切片/注册均为派生，不记成新模型生成。

## 原像素、所有权和透明

所有动作本身来自AI手绘局部姿态；鳍、尾、腕足、腿螯或人物衣褶确有局部变化。加工只做原生格/ownership提取、整数根点注册及透明padding，不用整图平移/缩放充当动作，不resize/upscale/pose-warp，也不逐帧bbox归一化。

最终alpha>16可见身体四侧边距均≥12%。这只证明最终画布padding，部分原生sheet没有12%留白，记录如实保留。格线越界不等于总画布截断；26号和30号按真实透明空隙分配ownership，30号强alpha253/140越过数学线的右螯经x890空隙切开保全。31–33直接继承root的连通域ownership，33swim原bbox中的邻鱼像素保持排除，没有混入输出。

28swim有alpha4–10的弱灯光/鳍缘到名义格边，整图外边max4；32swim03整图边max5。可见alpha>16轮廓完整，这些弱边限制未被抹掉或说成完全通过。

25–30旧静态master经实际Alpha核验，六张角Alpha全0。查看器显示的棕/蓝底是alpha0的RGB残留，不能作为实色背景缺口。未新增重复静态候选或覆盖master。

## 固定根点与跨动作密度

manifest顶层 `animation.displayCalibration.uniformDisplayScale` 是每clip一个固定候选显示比例，全部≤1且最大显示包络≤240×180；每帧 `anchor` 必须一起使用，不能把不同clipScale仍锚到画布中心，否则头会偏移。PNG本身未缩放。

| 鱼种 | swim scale | capture scale |
|---|---:|---:|
| 25夜星鱼 | .55556 | .65574 |
| 26墨玉章鱼 | .50303 | .48779 |
| 27荧光乌贼 | .57143 | .48780 |
| 28深海鮟鱇 | .55556 | .55556 |
| 29海龙 | .49314 | .47670 |
| 30金甲蟹 | .52173 | .51477 |
| 31冰晶鲨 | .65752 | .59177 |
| 32红莲鳐 | .48913 | .45150 |
| 33玄武灵龟 | .53449 | .54563 |

黑瞳高光可能切断深色连通域。27capture原黑瞳宽28–39并不等于头随帧放大；实际浅底00/04查看与更完整暗虹膜区域复核后，27swim虹膜宽35–36、capture39–41，动作内稳定。27和31采用有界71px眼部ROI、RGBmax<170/alpha>220的完整暗虹膜连通域做轻量整数精修，并按首个rest虹膜宽校准跨clip密度。其余保持已选眼部代理与中值。代理仍不是完整头骨/眼外圈的严格测量，所有密度值待root实际播放审查。

31capture03/04、32capture04、33capture04为闭眼，根点明确记录为眼睑centroid代理，不称真实黑瞳；闭眼帧不参与跨clip密度估计。33capture03/04缩头/遮挡与代理稳定单列待审，未逐帧缩放掩盖。

## 实际看过的与尚未通过的

已实际看原始动作源、31–33全部ownership深底contact，以及31–33各clip首帧或捕获峰值的浅米白/深玉绿真实Alpha合成；25swim00、26capture04、27capture00/04也做了本机小量合成查看。31swim0与27capture4在虹膜注册后刷新了合成图与源帧hash记录。未声称所有152帧均已逐帧双底或实际播放。

仍需root实际播放每一动作：身份、鳍肢/尾/腿螯/腕足拓扑、局部动作自然度、眼脸稳定、循环首尾、capture节奏/恢复和跨clip密度；之后做真正目标Unity接入验收。静态PNG计数、所有权断言、HTML或程序整体运动不能替代这些步骤。

本窗口不再有在途imagegen调用。31–36生图、道童point/celebrate和Boss attack/enrage均由root独占，此窗口没有重复调用或写入其源。
