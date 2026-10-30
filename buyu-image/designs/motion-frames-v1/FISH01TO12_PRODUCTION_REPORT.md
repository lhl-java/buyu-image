# 01—12 鱼种动作候选交付

已落盘24张原生动作表、192张独立RGBA帧。每动作8帧12FPS，游动循环、捕获单次；实际查看原表、眼ROI、固定根浅/深底和游戏显示尺寸对照。当前是制作候选，待root复核与Unity播放，不能称全部验收完成。

| 鱼种 | 共享画布 | 最小运行留白 | 帧数 |
|---|---:|---:|---:|
| 01-qingqi | 576² | 13.89% | 16 |
| 02-jinwei | 672² | 13.10% | 16 |
| 03-chiyu | 800² | 13.38% | 16 |
| 04-shenxian | 672² | 12.20% | 16 |
| 05-hetun | 640² | 12.66% | 16 |
| 06-haima | 608² | 13.65% | 16 |
| 07-zihai | 704² | 13.07% | 16 |
| 08-lanbian | 640² | 12.50% | 16 |
| 09-caidie | 672² | 13.24% | 16 |
| 10-qingya | 736² | 13.45% | 16 |
| 11-yinlin | 640² | 12.97% | 16 |
| 12-yuewei | 768² | 13.41% | 16 |

生成表均原生1774×887；帧仅完整ownership裁切、alpha≤3清零、整数瞳孔注册与透明补边，没有原生PNG缩放/放大/变形。源名义网格越界/12%留白警告完整保留；实际ownership无邻鱼像素，运行帧边距均≥12%。

每clip统一显示scale，displaySize代表完整画布；目标可见rest身体框为120×80以内并保长宽比。02捕获按入口原生密度、12捕获按实际8眼虹膜宽中位38/34补偿一次scale，眼-root偏移同步补偿；不按每帧bbox缩放。

所有生图/AI编辑均有request、prompt、receipt及逐图记录。配置目标GPT Image2.5 Sunburst/max；内置工具未披露实际型号与质量，实际值null。

复核入口：tmp/art-qa/{id}-pair-review.png，左游动右捕获、上浅下深；{id}-display-rest-qa.png是按实际clip显示scale的入口对照。完整来源、sourceRects、root、时长、像素保留与警告见同名JSON和各assets/animations/{id}/{swim,capture}/manifest.json。09后半行头身细微差异、06捕获末帧眼神变化保留在待播放审查项。

未改static master/global/Git；未做重型构建、测试、atlas或Unity；未新上传。本目录旧样片SAMPLE_REVIEW为历史首次送审，当前注册以运行manifest及本汇总为准。
