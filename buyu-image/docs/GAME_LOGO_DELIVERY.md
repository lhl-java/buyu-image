> 当前接续：本机资源限制已由用户明确解除，本批首发美术已完成Unity导入、编译、实际播放和agent逐项画面验收。结论、精确范围及输入哈希见 [UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。下方保留原日期的制作过程记录；历史“未启动/待验收/未上传”不代表当前状态。

# 灵海仙渔 · 主Logo

游戏正式名称为 **《灵海仙渔》**，用户在定名后要求制作Logo。本版采用四字横排，玉绿衬底、象牙米金字面、暖金细边，以及葫芦太极、玉珠、灵鱼云浪和少量红穗。实际附上邮件、组队两张指定成图，使用宿主内置image_gen生成。

| 文件 | 用途 |
|---|---|
| [透明PNG](../assets/branding/linghai-xianyu-logo-v1.png) | 游戏运行主Logo，1774×887原生像素，RGBA |
| [设计源图](../designs/branding/linghai-xianyu-logo-v1/linghai-xianyu-logo.png) | 当前采用的Logo成图，与运行PNG字节相同 |
| [逐图记录](../designs/branding/linghai-xianyu-logo-v1/linghai-xianyu-logo.png.generation.json) | 实际调用、配置快照、参考哈希、时间与尺寸 |
| [实际提示词](../designs/branding/linghai-xianyu-logo-v1/linghai-xianyu-logo.prompt.txt) | 真实提交的四字、风格及透明要求 |
| [Alpha检查](../designs/branding/linghai-xianyu-logo-v1/linghai-xianyu-logo.alpha-qa.json) | 原生透明及叠底复核 |
| [品牌设置](../config/game-brand.json) | 正式名称、Logo ID、路径及显示框 |

源图和运行PNG SHA256均为 `def85ed9e51d2c9c6525980bf815af01480e1b3359a7b7d430412780c0e6ef38`。没有放大、重采样、裁断、程序描字或改色；1774×887是实际返回尺寸。Alpha范围0—255，783270个像素完全透明；画布左缘只含alpha1的不可见级残留，其他三边为0，未发现主体截断。源像素保持不变。

根制作和独立复核均已实际查看四字和米白/深青叠底：字形为“灵海仙渔”，葫芦、鱼尾、云浪和流苏完整，未见实色背景矩形或明显色边。当前为静态视觉检查完成、待用户审阅；没有把720px联系图复核写成220px实际页眉运行通过。

主标题保留canonical ID `branding/brand-title`，清单指向新版本PNG，不增加重复主标题条目。目录总数仍为924项。素材验收台与31界面图集页眉已引用新Logo；Unity源代码使用同一ID，读取品牌名称并留出Logo高度。31张旧设计图的烘焙文字未批量AI重画。旧“捕鱼”标题与旧发布回执属于先前制作批次，不冒充本次新Logo。

配置目标仍为GPT Image2.5 Sunburst/max；本次内置工具没有model/quality选择器，也未返回可靠实际版本/质量字段，所以逐图actualModel/actualQuality记为null，未确认。配置与官方公告不能替代真实调用证据。

本轮仅新图、单图检查、源代码及元数据接入；未启动Unity、浏览器、重导入、图集编码或Git发布。当前新批仍未上传，整款美术最终验收状态继续见GAME_ART_STATUS.json。
