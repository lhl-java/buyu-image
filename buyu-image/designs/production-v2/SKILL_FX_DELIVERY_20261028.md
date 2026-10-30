# 六技能缺项补齐：聚鱼、护持、激流

本组新增3张采用源表、48个真实RGBA特效帧。每张源表为内置image_gen生成的原生1254×1254；聚鱼、护持各做一次定点AI containment修正，激流采用首张。实际附上邮件/组队主参考与08技能成图，实际型号与质量未由工具披露，均保留null。完整清单见 `SKILL_FX_DELIVERY_20261028.json`。

| 特效 | 当前源图 | 运行帧 | 最小运行透明留白 |
|---|---|---|---:|
| 聚鱼金鱼旋流 | fx-gather/fx-gather-contained.png | assets/fx/fx-gather/frame-00.png至frame-15.png | 12.94% |
| 护持太极葫芦护罩释放 | fx-guard/fx-guard-contained.png | assets/fx/fx-guard/frame-00.png至frame-15.png | 16.75% |
| 激流蓝白浪 | fx-surge/fx-surge.png | assets/fx/fx-surge/frame-00.png至frame-15.png | 12.18% |

每组16帧、16FPS、1秒、单次播放，根点为(0.5,0.5)。原1254方图按固定4×4网格产生313/314格，先只在右/下补透明到314，再统一四边各补40像素得到394方画布；没有缩放、重绘或裁掉光尾。运行394表示透明画布尺寸，不是原生394细节。每帧operation记有原生切格PNG/像素hash、统一补边、源图hash与逐图记录，补边前后源像素逐字节相等。

全部当前源表切片边界检查 `cell_border_alpha` 警告为0；实际看过浅米白、深青两套Alpha合成，主形、光尾和消散阶段完整，无跨格截断。源表alpha>3的12%留白要求仍未全部满足：聚鱼9帧、护持3帧、激流11帧告警在各组 `*.visual-qa.json` 的sourceWarnings原样保留，最小值分别3.50%、7.99%、2.24%，阈值12%。它们没有被写成源门禁通过；通过的是单独的runtimePaddingMargin门禁。最终runtimeWarnings为空。

护持是完整释放one-shot，不是持续循环。客户端需要显示持续护罩时，可暂时保持 `assets/fx/fx-guard/frame-06.png` 为静态active姿势，再继续消散；这不表示已生成持续loop，正式持续流动需求须另制独立闭环片段。

重建本组先运行既有 `tools/Build-ArtAssets.py` 对每个slice.json切格，再运行 `designs/production-v2/Finish-SkillFx.py <fx-id> --pad 40`，最后轻量 `Validate-SkillFx.py <fx-id>`。后处理拒绝有边界警告的图，不能用padding掩盖截断。重建后仍需实际目视。每个slice.json已写postprocess约定，避免只重切而丢失padding。

被替代的聚鱼/护持首稿PNG已在当前源及16帧hash核对后移除，历史真实请求、提示词、逐图记录与原始QA文字保留。没有修改catalog、全局状态、Git或上传；没有执行全工程构建、批量atlas、编译或重型测试。目标客户端接入与最终播放验收仍待根任务执行。
