# 灵海仙渔 Unity 美术验收工程

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
