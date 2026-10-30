> 当前接续：本机资源限制已由用户明确解除，本批首发美术已完成Unity导入、编译、实际播放和agent逐项画面验收。结论、精确范围及输入哈希见 [UNITY_FINAL_ACCEPTANCE.json](UNITY_FINAL_ACCEPTANCE.json)。下方保留原日期的制作过程记录；历史“未启动/待验收/未上传”不代表当前状态。

# 捕鱼美术与Unity接续点

当前工作目录为项目根。已有31张UI整屏设计、276项静态/FX PNG、81套648张动作PNG候选，运行catalog共924项/89 clips。视频不是本批前置条件，没有启用另行计费视频路线。所有动作仍未实际播放验收，releaseReady为0。

Unity工程位于 `unity/BuyuClient`，本机已安装6000.6.0f1：`D:/luyuan/tools/Unity/6000.6.0f1/Editor/Unity.exe`。不是缺少Unity。已有数据库、Loader、固定画布Player、状态控件、六模式审片/捕鱼演示、原生纹理导入策略、技术验证入口和首次场景引导。Source仅静态回读；尚未启动Editor、导入、编译、播放或构建。两个UPM包直接引用根assets及designs/ui，无整包复制。

## 当前阻断

服务器验收协调窗口 `01a17d44-68c6-7510-88f9-268bdbec8728` 持有本机单重型任务时段。当前禁止Unity/导入/编译/测试、图集重建、批量编码及Git重型打包。允许纯文件编辑、元数据和少量现有图片查看。已在本聊天请求用户交接资源，尚无回复；时间流逝、另一个窗口暂时idle或Docker等待都不算资源已交回。不得结束或关闭别人的进程，不向其他聊天发消息，除非用户明确授权。

本地file://浏览器访问和localhost服务之前被自动审批拒绝，不能换浏览器/CDP/无头工具绕过。无需浏览器也可在获准后用Unity进行独立运行验收。旧 `tmp/public-release` 递归清理被自动审批拒绝，禁止换命令重试删除该目录。

## 资源交回后

1. 先启动对应版本Unity导入并收集编译/导入结果。`Buyu.Editor.BuyuArtValidation.ValidateAll()` 可作独立技术检查，结果写工程 `Logs/BuyuArtValidation.json`；batch模式按0/1退出。此入口不批准动作或游戏美术。
2. 第一次交互导入成功会创建缺少的 `Assets/Scenes/BuyuArtReview.unity`；也可用Buyu菜单创建/打开。不要覆盖既有场景。实际Play六模式，核对924项路径、中文字体、31整屏尺寸、8类22状态、炮管轴心/炮口/弹丸方向、8FX及全部81动作。
3. 优先播放09蝴蝶鱼swim的03→04/07→00和13云纹龟swim的03→04/07→00，检查脸部与划鳍接点。06capture07眼神、31capture03/04闭眼、33capture03/04缩头是候选审片项，不能用暗瞳CC变化自动判定头尺度错误。详见FRAME_STATIC_REVIEW_20261028.json。
4. 对真正不合格动作按既定原生生成路线返修；每次AI生图前重读AGENTS、配置、模型策略，实际附邮件/组队主参考和当前角色/采用稿，保存实际request/receipt/来源。不要以逐帧bboxfit或放大掩盖身份/尺度问题。
5. 当前元数据桥接已统一C组比例和道童idle，不能重跑旧Prepare/Switch计划把状态重置。工具Export-UnityArtDatabase.py仅JSON/PNG头导出，Build-GameArtPack.py含真正图集/编码任务，二者不可混淆。旧225项/13atlas/218回环仅历史证据；当前924需实际后续核验。
6. 完成实际运行与必要技术验证后，更新当前状态/图像清单/接入说明。Unity生成的.meta需正常保留；Library/Temp/Logs/构建输出忽略。

## 发布与素材保留

公开仓库lhl-java/luhailong-python仍是旧225项批次，无父提交e3fcb061a5672cfc967605befb98bcdd32e4cce8，回执保留。新924项候选和Unity源代码尚未发布。新批发布前读取PUBLICATION_POLICY.md及源项目GIT_LATEST_STATE_POLICY.md；固定新批、私有Git、一个无父提交、核实际远端后lease推送及独立下载验真，不改共享Git，不热换旧固定批。

道童庆祝已采用A+`celebrate-b-a-only-v3.png`；旧B1/B2因头身密度差已核实删除PNG，文字记录保留，8张成品与最终两源仍在。静态鱼主图Alpha角点为0，旧“实色矩形底”判断已纠正；不能因查看器显示透明像素RGB而重新误删/重做合格主图。
