# 本批公开发布约定

2026-10-27 用户授权创建公开仓库 `luhailong-python`，并明确选择 `lhl-java` 账号。本批只发布本项目当前文件到仓库 `buyu-image/`。公开目标为 https://github.com/lhl-java/luhailong-python 。创建凭据通过本机既有Git Credential Manager使用，不能把令牌、Cookie或私钥写入文件/命令输出。

发布前读取 GAME_ART_STATUS.json、GAME_ART_PACK_VALIDATION.json、PUBLIC_CONTENT_AUDIT.json；固定采用文件与SHA256，复制到项目忽略目录 `tmp/public-release/` 后只用固定副本。包含当前设计、运行候选资源、主参考、必要提示词/来源证据、索引、接入资料与制作工具。排除tmp、缓存、私有Git目录、__pycache__、pyc、日志、环境凭据与密钥容器。复核副本每个SHA256和实际文件数量，无LFS指针或超限文件。

本项目采用相邻image的“最新状态”原则：用本窗口独立Git目录准备一个无父提交，不改相邻项目或共享Git的HEAD/index/refs。新建空仓首次发布到main；若远端已出现提交，停止覆盖并核对，不盲目强推。本批截止后新文件不混入在途上传。

发布成功后核对远端main SHA、提交数1、完整文件清单；独立下载zip并逐项比较实际字节SHA256与固定清单，确认真实PNG而非LFS指针。成功回执放本地 `docs/PUBLIC_UPLOAD_RECEIPT.json`，其自身不递归收入本次固定清单。Git提交树可读或push成功不能替代下载验收。不宣称托管端物理空间已释放。

完整游戏美术未完成时必须保留 `gameArtComplete=false`、81项待制动作和目标客户端验收门禁，不把本次公开上传写成游戏美术全部验收。
