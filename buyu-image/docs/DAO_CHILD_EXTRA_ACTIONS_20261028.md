# 道童指向与庆祝动作候选

两动作各8帧、10FPS、单次800ms。来源原画由root生成，本窗口只做完整alpha ownership、脚底整数注册、透明补边和导出，未调用生图；未改idle或源PNG。

| 动作 | 当前源 | 入口原生身高 | 单一显示scale | 完整画布显示尺寸 |
|---|---|---:|---:|---:|
| point | point-a-v1 + point-b-v1 | 599px | 280/599 = 0.467446 | 467.446² |
| celebrate | celebrate-a-v1 + celebrate-b-a-only-v3 | 533px | 280/533 = 0.525328 | 525.328² |

正式独立PNG在 `assets/animations/dao-child/{point,celebrate}/frame-00..07.png`；两manifest记录sourceRects、来源SHA、每帧sole/root、注册offset和真实显示比例。共享画布1000²只是原生像素加透明边，不能称模型原生1000px人物。脚根(500,850)，图像顶部归一化anchor(.5,.85)，Unity底部归一化pivot(.5,.15)。每个clip所有帧复用同一显示scale，PNG没有缩放、上采样或变形。

已实际查看原生图、无缩放脚底对齐密度比较、浅/深底注册帧和idle可见身高280的显示对照。最小运行透明留白14.6%，全部源RGBA裁切像素roundtrip通过；名义数学格线告警保留，实际ownership没有邻图混入或源总画布截断，指尖/拳头完整。

庆祝仅采用A-only-v3恢复表：相对A，身体高中位+0.65%、棕发宽+1.01%、入口眼距-0.53%、鞋跨度-1.37%。早先B约8%的头身偏大记录留在JSON历史；没有用同clip分sheet/分帧scale掩盖。

复核图在 `tmp/dao-child-export/{action}-registered-review.png`（上浅下深）及 `{action}-idle-display-qa.png`。当前仍为制作候选，待root目视与Unity播放；没有把静态QA当作节奏、接缝、实际客户端或全游戏验收通过。

重建时先运行 `tools/Inspect-DaoPointCelebrate.py`；celebrate须用 `--b-file`明确指向当前 `celebrate-b-a-only-v3.png`，然后实际查看密度QA，再运行 `tools/Export-DaoPointCelebrate.py action --source-visual-reviewed`。脚本拒绝源密度不一致或ownership未解决的输入。所有处理仅限单动作8帧的轻量文件操作，没有重型构建、测试、atlas或Unity。

