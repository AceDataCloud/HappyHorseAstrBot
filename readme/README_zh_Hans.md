# AstrBot Happy Horse 视频插件

通过您自己的 Ace Data Cloud 账号，在 AstrBot 对话中生成一条 Happy Horse 视频。`happyhorse_generate_video` 提交一次文生或首帧图生视频任务，`happyhorse_get_task` 用同一个任务 ID 查询最终结果。

**本 PR 的目标版本为 0.1.1**：新增原生帮助及管理员查询指令、双语配置和图文说明。合并和市场发布前，当前 0.1.0 安装不会自动获得这些入口。

这是 **Ace Data Cloud 提供的 Happy Horse 独立集成**，不是 Happy Horse 厂商或 AstrBot 团队的官方插件。使用自己的 Ace 账号和 API Key；不要填写其他平台的密钥。

[English guide](../README.md) · [视频接口](https://platform.acedata.cloud/documents/happyhorse-videos?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorseastrbot_readme_documents_happyhorse_videos) · [任务接口](https://platform.acedata.cloud/documents/happyhorse-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorseastrbot_readme_documents_happyhorse_tasks) · [当前价格](https://platform.acedata.cloud/services/happyhorse?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorseastrbot_readme_services_happyhorse)

## 查找与安装

当前上游文档（2026-10-18）：侧栏 **插件 → 顶部插件 → 插件市场 / 已安装**；旧 4.28.2 英文界面可能显示 Extensions。插件参数在已安装卡片齿轮里设置，**不要把服务插件 Key 填进模型提供商**。

**发布状态（2026-10-18）：尚未在官方市场上架。** 正式发布后，先打开 [AstrBot Cloud 插件市场](https://cloud.astrbot.app/market)，搜索 **Happy Horse**，再核对 **Happy Horse by Ace Data Cloud / acedatacloud**。当前请用下面的 Git 仓地址手动安装；不要把仓库安装说成官方市场收录。

官方 AstrBot Cloud 上架仍待完成。源码合并后，可通过**已安装 → 安装 (+) → 从 URL 安装**并填写 `https://github.com/AceDataCloud/HappyHorseAstrBot` 预览。通过 URL 安装不代表已在官方市场上架。

## 配置密钥

先[注册或登录 Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorseastrbot_readme_signup)；首次没有通用应用时，先初始化 **General application**。下图取自同一 Ace 应用管理页面，不是 AstrBot 界面。

在 [Ace Data Cloud 应用管理](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorseastrbot_readme_api_key)复制生成 API Key，或创建同时允许 `/happyhorse/videos` 与 `/happyhorse/tasks` 的 Key。提交前核对当前每秒价格、时长、分辨率和余额。将 Key 填入插件的 **Ace Data Cloud generation API key with Happy Horse access** 配置项，不要添加 `Bearer `，也不要使用 `platform-...` 管理令牌。AstrBot WebUI 会遮蔽显示此字段，但原值保存在数据目录中，请保护该目录。

选择支持工具调用的对话模型，并在当前对话的 profile 与 persona 中允许两个 Happy Horse 工具。

1. 打开 **General application**，用图中 **1** 复制现有 Key，或点 **2 Manage Keys → Create** 创建专用 Key。

![复制 Ace Key 或管理专用 Key（已脱敏）](../_assets/tutorial/get-api-key-en.png)

2. 可把名称设为 `AstrBot Happy Horse`，按需要设置到期/限额；Allowed APIs 同时包含 `/happyhorse/videos` 和 `/happyhorse/tasks`。截图的 Dify tutorial 只是旧示例名称。

![创建专用 Key（共享 Ace 页面，非 AstrBot）](../_assets/tutorial/create-api-key-en.png)

图片于 2026-10-18 复用核验，原始拍摄日期未提供；凭据与余额已脱敏。 [来源和版本边界](../_assets/tutorial/sources.json)。

### 在 AstrBot 粘贴的位置

打开 **插件 → 插件 → 已安装**，点击 **Happy Horse by Ace Data Cloud** 卡片齿轮，把 Key 填入 **Ace Data Cloud generation API key with Happy Horse access**（保存字段为 `api_key`）并保存。不要填 `Bearer `；也不要在聊天里输入 Key。

![AstrBot 官方历史插件配置参考，非本插件运行截图](../_assets/tutorial/astrbot-plugin-config-reference.png)

此图是 AstrBot 官方 `helloworld` 配置示例，界面标签 v3.4.14（构建 v3.4.9），不是 Ace 配置或运行证明。上方说明给出了本插件的准确字段和当前菜单；新版本布局可能不同。

## 无需聊天模型的原生指令

| 输入 | 作用 |
| --- | --- |
| `/happyhorse_ace` | 显示本服务、Token 配置和查询用法，不请求外部 API。 |
| `/happyhorse_ace_task <task_id>` | 仅 AstrBot 管理员：查询一个已有任务，返回状态与最终媒体，不调用 LLM 或生成。 |

指令采用默认 `/` 前缀；自定义唤醒前缀时相应替换。管理员身份由 AstrBot 判断；同一实例的插件 Key 是共享配置，因此查询指令默认限管理员。其他用户继续使用受当前人格/配置允许的 Agent 工具。`pending` 时稍后只查同一编号，`failed` 时按原 task/trace 排查。

## 生成一次，然后查询

可以对机器人说：

> 用 `happyhorse_generate_video` 生成一条黄色纸风筝从绿色草地升起的视频。模型 `happyhorse-1.1-t2v`，3 秒、720P、16:9。只提交一次并告诉我任务 ID。

工具会异步提交一次 `POST /happyhorse/videos` 请求，返回 `status: submitted` 和任务 ID。这时还不能认为视频已完成。保存 ID，随后说：

> 用 `happyhorse_get_task` 查询准确的任务 ID `<task_id>`，告诉我状态与最终视频链接，不要重新生成。

如果仍是 pending，稍后继续查询同一个 ID。只有 `status: succeeded`、`success: true` 和最终 HTTPS 视频链接同时出现才算完成。插件不会自动重试付费提交。

文生视频可用 `happyhorse-1.0-t2v` 或 `happyhorse-1.1-t2v`。要让您有权处理的图片动起来，传入公开的 HTTPS `image_url` 并明确选择 `happyhorse-1.0-i2v` 或 `happyhorse-1.1-i2v`；插件不会自行切换模型。支持 3–15 秒，分辨率为 `720P` 或 `1080P`。首版固定 `watermark=false`，只支持一张首帧图片；多图参考生成与视频编辑暂未覆盖。

## 核验与排查

在 Ace Data Cloud 用量记录中优先按返回的 trace ID 核对。任务结果可能包含以 Credits 计的公开 `cost` 字段；以实时用量记录为扣费依据。任务查询只读取已有任务，不会再次生成。

| 现象 | 检查 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**加载失败的插件**和**数据与日志 → 日志**。 |
| 看不到工具 | 插件启用、当前 profile 与 persona 允许两个工具、对话模型支持工具调用。 |
| HTTP 401/403 | Key 类型、两个 API 路径的权限和账号访问权限。 |
| 提交后网络报错 | 再次生成前先看请求历史；超时也可能已创建付费任务。 |
| 任务仍在进行 | 稍后查询同一个任务 ID。 |
| 任务失败 | 用任务 ID 或 trace ID 查请求历史。 |

Key 只会发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件只把最终视频链接和公开费用字段交给对话模型，不返回内部原始数据。运行时仅用 Python 标准库。

## 验收与品牌图标

在官方 AstrBot `v4.28.2` 的隔离实例中，editable 安装成功注册两个工具。ChatUI 用 `happyhorse-1.1-t2v`、3 秒、720P 提交了一次视频任务，并查询同一个 ID 一次，没有重复生成。最终 MP4 返回 HTTP 200、`video/mp4`，H.264 视频和 AAC 音频，1280×720、3.163 秒。准确 trace ID 对应一条成功的 `/happyhorse/videos` 用量记录，实扣 2.97 Credits；任务返回原价 3.3 Credits。见[脱敏实测证据](../tests/e2e-results.json)。图生视频及其他模型和设置仅做结构校验，未实际生成。这只是本地 editable 安装；Cloud 审核、市场安装以及市场包的首次调用仍待完成。

`logo.png` 是[当前 Happy Horse 服务图标](https://cdn.acedata.cloud/e58fce2811.jpg)不改变画面的 PNG 编码，447×447。源 JPEG 的 SHA-256 为 `58c5821d63219093ca86d5780231612218c472d66f8a66a59131a873fc736d0f`；打包 PNG 的 SHA-256 为 `28d49c107808fe2a5779b56338f53df947ad6c2335755aaae5c483540ee3a4d1`。
