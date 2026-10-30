# 可随包中文字体

已从官方 [notofonts/noto-cjk](https://github.com/notofonts/noto-cjk) 取得两份未修改的简体中文Regular OTF与对应的OFL1.1许可文本。源固定到实际核对的提交 [f8d157532fbfaeda587e826d4cd5b21a49186f7c](https://github.com/notofonts/noto-cjk/commit/f8d157532fbfaeda587e826d4cd5b21a49186f7c)，不是不固定版本的下载链接。没有克隆整个仓库，没有复制Windows字体，没有做子集化、格式转换、字形渲染、测试或重型构建。

具体来源、版本、文件大小、SHA256、官方Git blob SHA1、原字体内的版权/许可元数据与下载核验时间见 [fonts.json](../assets/fonts/fonts.json)。该文件特意不命名为manifest.json，避免PNG素材汇编把字体当作图像items处理。

| 角色 | 实际字体族与版本 | 文件 | 字节数 |
|---|---|---|---:|
| 正文/数字 | Noto Sans CJK SC Regular，2.004 | [NotoSansCJKsc-Regular.otf](../assets/fonts/NotoSansCJKsc-Regular.otf) | 16,437,364 |
| 标题 | Noto Serif CJK SC Regular，2.003 | [NotoSerifCJKsc-Regular.otf](../assets/fonts/NotoSerifCJKsc-Regular.otf) | 24,543,080 |

字体族名、Regular子族、版本与400字重已从OTF的name/OS2元数据实际读取。两文件以OTTO开头；实际字节数与按原字节计算的Git blob SHA1均与官方目录元数据一致，没有使用HTML下载页或LFS指针代替字体。

SHA256：

- Sans：`2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b`
- Serif：`2a2eae2628df83556c54018c41e20fa532c1b862c5256ae8b3f23feb918d12ca`
- 两份原始许可文本各4,301字节，SHA256均为 `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2`

## 许可随包

保留 [Sans许可](../assets/fonts/LICENSE-NotoSansCJK.txt)、[Serif许可](../assets/fonts/LICENSE-NotoSerifCJK.txt)与[原字体版权通知](../assets/fonts/NOTICE-NotoCJK.txt)。它们与字体一同交付，不能只在说明中口头表示有授权。

两个官方文本实际为SIL Open Font License 1.1。按其实际条款，字体可与软件打包分发，同时保留许可及原版权通知；不可将字体本身单独出售。若将来改字或子集化，应重新遵守实际OFL中修改版、保留字体名称及许可要求；本次没有修改。字体作者/版权所有者不应被表示为游戏代言或认可者。实际条款以随包完整LICENSE为准。

官方文件页：

- [Sans Regular](https://github.com/notofonts/noto-cjk/blob/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf)，[Sans LICENSE](https://github.com/notofonts/noto-cjk/blob/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/LICENSE)。
- [Serif Regular](https://github.com/notofonts/noto-cjk/blob/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Serif/OTF/SimplifiedChinese/NotoSerifCJKsc-Regular.otf)，[Serif LICENSE](https://github.com/notofonts/noto-cjk/blob/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Serif/LICENSE)。

## 接入与未完成验收

[ui-typography.json](../config/ui-typography.json)已优先指向实际随包字体：display用Noto Serif CJK SC，body/numeric用Noto Sans CJK SC。Windows既有字体仅保留为系统候选信息，未复制入项目，也不把其存在当作分发许可。当前只有两份Regular400，因此排版token的500/600候选改为实际400，禁止自动宣称已带medium/bold字重；额外字重若需要，应另有真实源文件与许可记录。

字体文件和许可已齐，不代表字体在目标运行端已加载，也不代表31页全部中文、数字对齐、长文案、缺字/fallback和换行已经验收。本次没有枚举字形或进行字体渲染。字体清单状态为 `bundled_with_official_license_pending_target_glyph_and_render_review`，排版规格继续为 `candidate_pending_visual_runtime_review`。

Noto的印刷字形不能自动等同于主参考的手绘/书写标题。它解决合法、可随包、跨环境不依赖Windows字体的资源门禁；字号、行高、字形风格及其与玉金面板的实际搭配还需运行终审。
