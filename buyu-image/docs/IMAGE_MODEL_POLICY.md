# 模型与逐图记录

默认设置唯一入口为 [config/image-generation.json](../config/image-generation.json)。用户本次指定 GPT Image 2.5；配置中的型号和最高质量是创作目标，不是宿主实际返回值。

2026-10-26 已读取官方 [Sunburst 模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)和 [Images API 参数页](https://developers.openai.com/api/reference/resources/images/methods/generate)，确认该型号及 max 档位。后续新批次核对官方资料，同一批次保持一致，用户明确选择优先。

2026-10-28 本批补项已重新读取同一官方型号页及实际参数说明：继续使用用户选定的GPT Image2.5 Sunburst目标，最高档仍为max。配置核对日期更新，新调用保留本次快照；旧图历史记录不改写。内置工具仍没有model/quality参数或实际返回版本，逐图实际值继续为未确认。

优先内置 `image_gen`。当前工具开放提示词、参考图和透明背景参数，没有 model／quality 选择器；继续使用宿主管理入口，不要求额外 API Key。实际参数为 null，返回证据未披露的实际型号和质量也为 null，并注明未确认。官方产品公告、提示词或本地配置不能证明本次实际锁定 API 分支与质量。

API/CLI 仅在用户明确选择该单独计费路径后使用；真实参数读取本项目 JSON，凭证保留在本机安全配置中。不要更改全局配置来影响其他制作窗口。

## 每张图片的记录

新生成、重试、AI 编辑都在图片旁保存 `<图片名>.generation.json`，至少包含：

- `file`、`sha256`、含时区的 `generatedAt`、实际 `width`／`height`／`format`。
- `tool`、`route` 和工具实际返回的调用／结果 ID。
- `configSnapshot`：当次配置快照，保留 model、quality、builtin_product、verified_on 和 sources。
- `submittedParameters.model`、`submittedParameters.quality`：只记录真实提交参数，无选择器时为 null。
- `actualModel`、`actualQuality`：只取本次可靠返回证据，未知为 null。
- `evidence`、`unverifiedReason`、实际提示词文件 `prompt`、参考图路径及用途 `references`。

派生图使用 `derivedFrom` 和 `operation` 追溯源图路径、哈希及记录。复制、裁切、缩放、拼接不能记录为新模型生成。保留每个旧图的历史证据，不按新配置补写版本。

交付时列出图片与记录索引、原生与导出尺寸及验收状态。只保留当前设计和正式交付需要的图片，处理旧版本遵守根 AGENTS.md；来源文字记录继续保留。
