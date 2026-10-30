# 捕鱼首批美术首稿 · 2026-10-26

用户在主协调聊天要求“那你开始做吧”后，先制作捕鱼主界面与同身份的捕鱼道童，均延续 image 已确认的邮件／组队成图风格。当前状态为待用户审阅的美术首稿。

| 图片 | 实际原生尺寸 | 提示词 | 来源记录 |
|---|---|---|---|
| [捕鱼主界面 v1](../designs/ui/fishing-main-v1/fishing-main-v1.png) | 1672×941，RGB PNG | [初稿](../designs/ui/fishing-main-v1/fishing-main-v1.prompt.txt)、[文案修正](../designs/ui/fishing-main-v1/fishing-main-v1-text-fix.prompt.txt) | [逐图记录](../designs/ui/fishing-main-v1/fishing-main-v1.png.generation.json) |
| [捕鱼道童 v1](../designs/characters/fishing-dao-child-v1/fishing-dao-child-v1.png) | 1254×1254，RGBA PNG | [提示词](../designs/characters/fishing-dao-child-v1/fishing-dao-child-v1.prompt.txt) | [逐图记录](../designs/characters/fishing-dao-child-v1/fishing-dao-child-v1.png.generation.json) |

主界面采用浅海场景、玉绿金边标题与控件、米白信息栏和底部葫芦炮台，包含自动、锁定、技能与图鉴的首稿入口。旧参考示例姓名和等级经一次 AI 定点修正，改为“见习渔师／角色首稿”。初稿来源文字与哈希保留。

角色保留主界面头像的金发带、棕色短发与圆润表情，玉绿米白衣装配同系葫芦捕鱼法器。真实 Alpha 已检查；米白和深玉绿背景的不缩放合成检查未见明显红绿彩边、黑底或人物裁切。外框有 21 个 alpha=1 的低透明像素，原生 RGBA 未清洗、未重采样。内部合成检查图是临时验证产物。

内置 image_gen 完成两次生成与一次 AI 文案修正。每次保存当次目标配置快照、真实提交参数、工具来源与提示词。目标为 GPT Image 2.5 Sunburst／max，工具未披露实际型号与质量，实际字段按未确认记录。提示词所期望的更大画布与实际返回尺寸分开保存，没有放大冒充原生高清。

横屏比例、单炮台布局、资源数字、按钮功能和角色设定是首稿假设。两张图用于确认画风和布局；正式尺寸合同、控件拆分、动作方向与客户端接入后续按具体任务执行。assets 目录尚无正式导出。

机器可读清单见 [first-batch-20261026.json](first-batch-20261026.json)。参考截图与需求仍可放入 [references/incoming](../references/incoming/)。
