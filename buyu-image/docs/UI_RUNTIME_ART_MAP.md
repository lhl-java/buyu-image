# 31个界面的首发运行美术映射

本批首发美术已经实际Unity导入、编译、播放和agent画面验收；924项PNG、89组clip、81套角色动作均有最终证据，见[UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。下表为设计参考与独立资源的对应，不把31张截图当作31个生产交互窗口。

动态文案、正式标题Logo、数据、奖励、冷却、红点、滚动、锁定、交互和状态由客户端叠加；原设计截图的测试文字不作为业务数据。4海域/港口及两张无字活动插画有独立文件，活动路径使用实际岛心坐标。

| 界面与设计稿 | 组件分组 | 独立美术与用途 |
|---|---|---|
| [01-start 开始界面](../designs/ui/full-suite-v1/01-start/01-start.png) | `actions` | 整幅背景：`scenes/scene-harbor`；正式Logo：`branding/brand-title`；右侧道童独立静态主图：`characters/dao-child/dao-child`；公告入口符号复用：`icons/mail`；设置入口：`icons/settings` |
| [02-loading 加载界面](../designs/ui/full-suite-v1/02-loading/02-loading.png) | `progress` | 加载背景：`scenes/scene-shallow`；葫芦炮底座：`cannons/batch-1/hulu-base`；葫芦炮炮管：`cannons/batch-1/hulu-barrel`；点景鱼静态图：`fish/batch-1/01-qingqi` |
| [03-lobby 游戏大厅](../designs/ui/full-suite-v1/03-lobby/03-lobby.png) | `window`, `actions`, `resource`, `portrait`, `scenes4`, `backpack` | 港口背景：`scenes/scene-harbor`；玩家头像：`characters/portraits/fisher`；炮台：`icons/cannon`；图鉴：`icons/book`；任务：`icons/task`；商城：`icons/shop`；好友：`icons/friend`；邮件：`icons/mail`；设置：`icons/settings` |
| [04-rooms 渔场选择](../designs/ui/full-suite-v1/04-rooms/04-rooms.png) | `window`, `actions`, `tabs`, `list`, `scenes4` | 锁定图标：`icons/lock`；返回图标：`icons/back` |
| [05-gameplay 捕鱼主界面](../designs/ui/fishing-main-v1/fishing-main-v1.png) | `resource`, `skills6`, `fish36`, `cannon6`, `fx8` | 首海域背景：`scenes/scene-shallow`；底部操作承载条：`ui/hud/bottom-rail`；自动入口：`icons/auto`；锁定功能入口：`icons/target`；弹丸：`icons/bullet`；透明中心准星：`ornaments/aim-jade`；透明中心锁鱼环：`ornaments/aim-gold`；增加倍率：`icons/plus`；减少倍率：`icons/minus` |
| [06-cannons 炮台选择](../designs/ui/full-suite-v1/06-cannons/06-cannons.png) | `window`, `actions`, `slots`, `cannon6` | 锁定符号：`icons/lock` |
| [07-upgrade 炮台升级](../designs/ui/full-suite-v1/07-upgrade/07-upgrade.png) | `window`, `actions`, `slots`, `progress` | 当前炮底座：`cannons/batch-1/hulu-base`；当前炮管：`cannons/batch-1/hulu-barrel`；升级材料：`icons/jade-shard`；金币成本：`icons/coin`；数值增长辅助符号：`icons/plus` |
| [08-skills 技能面板](../designs/ui/full-suite-v1/08-skills/08-skills.png) | `window`, `actions`, `slots`, `skills6` | 描述/冷却信息承载：`ui/panels/tooltip-panel` |
| [09-encyclopedia 鱼类图鉴](../designs/ui/full-suite-v1/09-encyclopedia/09-encyclopedia.png) | `window`, `actions`, `tabs`, `slots`, `fish36` | 品质星：`ornaments/rarity-star`；未发现符号：`icons/lock` |
| [10-fish-detail 鱼类详情](../designs/ui/full-suite-v1/10-fish-detail/10-fish-detail.png) | `window`, `actions`, `progress` | 灵锦鲤详情主图：`fish/batch-4/19-lingjinli`；品质星：`ornaments/rarity-star`；栖息地示意：`scenes/scene-coral` |
| [11-bag 背包](../designs/ui/full-suite-v1/11-bag/11-bag.png) | `window`, `actions`, `tabs`, `slots` | 背包物品图标：`icons/ice`；背包物品图标：`icons/thunder`；背包物品图标：`icons/jade-shard`；背包物品图标：`icons/net`；背包物品图标：`icons/key`；背包物品图标：`icons/shell`；背包物品图标：`icons/chest`；背包物品图标：`icons/coin-pouch`；背包物品图标：`icons/cannon-skin`；背包物品图标：`icons/pearl` |
| [12-item-use 道具使用](../designs/ui/full-suite-v1/12-item-use/12-item-use.png) | `window`, `actions` | 当前道具：`icons/ice`；减量：`icons/minus`；加量：`icons/plus` |
| [13-tasks 每日任务](../designs/ui/full-suite-v1/13-tasks/13-tasks-v2.png) | `window`, `actions`, `tabs`, `list`, `progress`, `slots` | 任务/奖励/状态符号：`icons/task`；任务/奖励/状态符号：`icons/coin`；任务/奖励/状态符号：`icons/jade-shard`；任务/奖励/状态符号：`icons/chest`；任务/奖励/状态符号：`icons/check` |
| [14-achievements 成就](../designs/ui/full-suite-v1/14-achievements/14-achievements.png) | `window`, `actions`, `tabs`, `list`, `progress` | 成就符号：`icons/achievement`；成就奖章：`ornaments/medal-gold`；金币奖励：`icons/coin`；灵玉奖励：`icons/jade`；完成状态：`icons/check` |
| [15-signin 每日签到](../designs/ui/full-suite-v1/15-signin/15-signin-v2.png) | `window`, `actions`, `slots` | 七日奖励图标：`icons/coin`；七日奖励图标：`icons/jade-shard`；七日奖励图标：`icons/ice`；七日奖励图标：`icons/net`；七日奖励图标：`icons/key`；七日奖励图标：`icons/pearl`；七日奖励图标：`icons/chest`；已签到勾记：`icons/check`；侧边道童：`characters/dao-child/dao-child` |
| [16-events 活动中心](../designs/ui/full-suite-v1/16-events/16-events.png) | `window`, `actions`, `tabs`, `slots` | 独立无字活动横幅：`illustrations/event-banner`；活动页签鱼图：`fish/batch-4/19-lingjinli`；礼包页签：`icons/gift`；灵贝页签：`icons/shell`；金币奖励：`icons/coin-pouch`；灵玉奖励：`icons/jade-shard` |
| [17-event-detail 活动详情](../designs/ui/full-suite-v1/17-event-detail/17-event-detail.png) | `window`, `actions`, `progress`, `slots` | 无字寻宝岛图：`illustrations/event-route`；当前节点空心标记：`ornaments/stage-marker`；灵贝节点/任务图标：`icons/shell`；已完成节点：`icons/check`；未解锁节点：`icons/lock`；终点奖励：`icons/chest`；奖励：`icons/coin`；奖励：`icons/jade-shard` |
| [18-shop 商城](../designs/ui/full-suite-v1/18-shop/18-shop.png) | `window`, `actions`, `tabs`, `slots`, `resource` | 商品图标：`icons/ice`；商品图标：`icons/thunder`；商品图标：`icons/jade-shard`；商品图标：`icons/key`；商品图标：`icons/cannon-skin`；商品图标：`icons/shell` |
| [19-purchase 购买确认](../designs/ui/full-suite-v1/19-purchase/19-purchase.png) | `window`, `actions` | 购买物品：`icons/ice`；游戏货币：`icons/coin`；减少数量：`icons/minus`；增加数量：`icons/plus` |
| [20-mail 邮件](../designs/ui/full-suite-v1/20-mail/20-mail.png) | `window`, `actions`, `tabs`, `list`, `slots` | 邮件/附件图标：`icons/mail`；邮件/附件图标：`icons/coin`；邮件/附件图标：`icons/jade-shard`；邮件/附件图标：`icons/ice`；邮件/附件图标：`icons/gift`；邮件/附件图标：`icons/check` |
| [21-friends 好友](../designs/ui/full-suite-v1/21-friends/21-friends-v2.png) | `window`, `actions`, `tabs`, `list`, `portrait`, `portraits6` | 好友符号：`icons/friend`；添加入口：`icons/plus`；所在渔场缩略图：`scenes/scene-shallow` |
| [22-ranking 排行榜](../designs/ui/full-suite-v1/22-ranking/22-ranking.png) | `window`, `actions`, `tabs`, `list`, `portrait`, `portraits6` | 三甲奖章：`ornaments/medal-gold`；三甲奖章：`ornaments/medal-silver`；三甲奖章：`ornaments/medal-bronze`；排行入口符号：`icons/rank` |
| [23-profile 个人资料](../designs/ui/full-suite-v1/23-profile/23-profile.png) | `window`, `actions`, `progress`, `portrait`, `portraits6` | 全身人物静态图：`characters/dao-child/dao-child`；当前炮台底座：`cannons/batch-1/hulu-base`；当前炮管：`cannons/batch-1/hulu-barrel`；徽章：`icons/achievement`；品质徽记：`ornaments/rarity-star`；图鉴统计：`icons/book`；炮台统计：`icons/cannon` |
| [24-settings 设置](../designs/ui/full-suite-v1/24-settings/24-settings.png) | `window`, `actions`, `tabs`, `settings`, `progress`, `slider-thumb` | 设置项符号：`icons/music`；设置项符号：`icons/sound`；设置项符号：`icons/vibration`；设置项符号：`icons/quality`；设置项符号：`icons/target`；设置项符号：`icons/settings` |
| [25-help 玩法说明](../designs/ui/full-suite-v1/25-help/25-help.png) | `window`, `actions`, `tabs`, `slots` | 发射说明炮台底座：`cannons/batch-1/hulu-base`；发射说明炮管：`cannons/batch-1/hulu-barrel`；目标说明准星：`ornaments/aim-jade`；技能说明图标：`skills/skill-ice` |
| [26-settlement 渔获结算](../designs/ui/full-suite-v1/26-settlement/26-settlement.png) | `window`, `actions`, `slots`, `fish36` | 结算背景：`scenes/scene-shallow`；金币奖励：`icons/coin-pouch`；材料奖励：`icons/jade-shard` |
| [27-rewards 奖励领取](../designs/ui/full-suite-v1/27-rewards/27-rewards.png) | `window`, `actions`, `slots` | 铜钱奖励：`icons/coin`；碎片奖励：`icons/jade-shard`；冰封符奖励：`icons/ice` |
| [28-hud-overlays 捕鱼操作状态](../designs/ui/full-suite-v1/28-hud-overlays/28-hud-overlays.png) | `resource`, `skills6`, `window`, `actions` | 自动入口：`icons/auto`；锁定入口：`icons/target`；锁鱼环：`ornaments/aim-gold`；目标鱼示例：`fish/batch-4/19-lingjinli`；场景背景：`scenes/scene-shallow` |
| [29-dialogs 确认与网络弹窗](../designs/ui/full-suite-v1/29-dialogs/29-dialogs.png) | `window`, `actions`, `tooltip` | 金币不足提示符号：`icons/coin`；道具确认符号：`icons/ice` |
| [30-empty-states 空白加载异常状态](../designs/ui/full-suite-v1/30-empty-states/30-empty-states.png) | `window`, `actions`, `tooltip` | 暂无邮件示意：`icons/mail`；暂无好友示意：`icons/friend`；加载状态可选符号：`icons/bubble`；获取失败可选卷轴符号：`icons/task` |
| [31-components 通用控件规范图](../designs/ui/full-suite-v1/31-components/31-components.png) | `window`, `actions`, `tabs`, `slots`, `progress`, `settings`, `resource`, `tooltip`, `portrait`, `slider-thumb` |  |

## 共用控件

| Family | 独立状态资源 | 逻辑画布 | 全家族统一比例 |
|---|---|---|---|
| `primary` | `normal` → `ui/buttons/primary-normal`, `pressed` → `ui/buttons/primary-pressed`, `disabled` → `ui/buttons/primary-disabled`, `selected` → `ui/buttons/primary-selected` | `[382, 180]` | `0.8474576` |
| `secondary` | `normal` → `ui/buttons/secondary-normal`, `pressed` → `ui/buttons/secondary-pressed`, `disabled` → `ui/buttons/secondary-disabled`, `selected` → `ui/buttons/secondary-selected` | `[382, 180]` | `0.7457627` |
| `tab` | `normal` → `ui/buttons/tab-normal`, `selected` → `ui/buttons/tab-selected` | `[352, 154]` | `0.6949153` |
| `close` | `normal` → `ui/buttons/close-normal`, `pressed` → `ui/buttons/close-pressed` | `[248, 246]` | `0.2616822` |
| `slot` | `normal` → `ui/hud/slot-normal`, `selected` → `ui/hud/slot-selected`, `locked` → `ui/hud/slot-locked`, `empty` → `ui/hud/slot-empty` | `[310, 308]` | `0.4552846` |
| `toggle` | `off` → `ui/hud/toggle-off`, `on` → `ui/hud/toggle-on` | `[302, 166]` | `0.3271375` |
| `checkbox` | `off` → `ui/hud/checkbox-off`, `on` → `ui/hud/checkbox-on` | `[230, 224]` | `0.1919192` |
| `slider-thumb` | `normal` → `ui/additions/slider-thumb-normal`, `pressed` → `ui/additions/slider-thumb-pressed` | `[406, 402]` | `0.1072386` |

数据读取[状态注册](../config/ui-state-registration.json)，按logicalRoot/drawOffset/sharedDisplayScale放置，文字使用contentRect，热区使用hitRect。8类22状态、实际指针事件和文字安全区已验收。primary/secondary选中态源形状差异记录保留，未逐状态按bbox缩放；hover/focus按明示回退规则。

通用窗体、列表行、提示面板已在640/960/1200宽度实际拉伸。nineSlice为源像素L/T/R/B，tooltip为64四边，list-row为[112,56,112,56]，其余值从当前catalog读取。标题、圆形徽章和图标等比显示，文字另行排版。

## 动作、技能与炮台

36鱼种各游动/捕获，3Boss额外攻击/怒态，道童idle/point/celebrate，共81动作648帧；40循环、41单次，按manifest逐帧时长播放。8组FX共128帧、16FPS、单次，护持持续层用另记峰值帧。六技能绑定见[配置](../config/skill-art-bindings.json)，客户端负责目标、轨迹、命中、持续时间和冷却。

6套炮管root与原生炮口见[cannon-registration.json](../config/cannon-registration.json)，已实际检查18个角度样本；弹丸头锚/原始朝向见catalog.projectile，运行演示按炮管子节点发射并完成捕获。帧使用全clip统一显示比例，不能按逐帧透明包围框fit。

字体包含Noto Sans/Serif CJK SC及OFL；两字体各57样例字符可用。最终实际渲染、所有动作帧和原始技术报告随[acceptance](acceptance/README.md)交付。原始技术报告保持自身技术范围字段，完成结论由上层视觉审阅封存。
