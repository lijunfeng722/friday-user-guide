# 维护 Friday 用户手册

先读 README.md 和[公共开发规范](https://github.com/lijunfeng722/friday-project-index/blob/main/docs/development.md)。用户操作文档面向非技术家庭使用者，开发约定放在本文件和仓库维护入口，不混入产品操作流程。

按变化更新任务页、FAQ 和对应示例截图；有架构或流程说明时使用必要的 Mermaid 图。公开图片来自可重复的示例，不包含真实家庭、凭据、设备清单、私有路径或原始日志。生成证据放在忽略的 .artifacts/。

内容改动后运行 `python3 scripts/export_manual.py` 同步 USER_MANUAL.md，再运行 `.venv/bin/python scripts/check_docs.py`、`.venv/bin/mkdocs build --strict`、`.venv/bin/python scripts/check_docs.py --built site` 和 `python3 scripts/check_dev_policy.py check`。这些检查不需要启动真实家庭服务。

启停工具源码及测试在元仓库根目录和 scripts/ 中维护；本站的 docs/assets/scripts/ 及 scripts/test_services.py 是同步副本。先修改元仓库，再用其 scripts/sync_service_tools.py 更新本站，执行 `python3 scripts/test_services.py`、三个 Shell 入口的语法与 SHA256 清单检查。普通文档变更不重复执行硬件测试。

提交只包含当前任务文件，按已有任务范围推送和发布。发布时确认 Pages 状态与实际页面；服务启动和使用者实物确认分别记录。公共约定通过元仓库同步，保留以上专用要求。

<!-- friday-dev-policy:start -->
## Friday 公共开发约定

规范版本：2026-11-09.1

- 所有变更开始前，先获取目标仓库远端主干的最新代码，并从该最新提交新建本次任务分支；代码、文档、配置、脚本、Skill、AGENTS.md 与生成副本同步均适用。禁止直接在 `main`、`master` 或其他主干上开发，不得从未更新的本地主干或旧任务分支开始新任务；跨仓库变更时各仓库分别执行。
- 新增人工提交使用中文说明目的，推荐“功能：……”“修复：……”“文档：……”。保留英文技术名称；不为格式要求重写上游或已有历史。
- 新增、修改的解释性注释和文档字符串使用中文。保留工具指令、协议字段、标准术语、第三方原文及用于反例的测试数据；不要求批量翻译旧注释。
- 协作规范正文统一使用中文；合并历史规则时整合同义要求，保留原有约束及必要的命令、文件名和技术术语。
- 用户可见的新特性或使用方式变化，同步用户手册的步骤、限制与相关 FAQ；界面变化时更新对应产品截图。内部重构可说明无用户文档影响及理由。
- 架构、接口、数据流或部署方式变化，同步对应技术说明和必要的 Mermaid 图；涉及仓库职责、依赖和维护入口时同步顶级索引。
- 按变更选择相关验证，记录实际结果与未验证范围。代码提交、服务就绪、设备回报与使用者实物确认分别报告；普通测试使用隔离、合成输入。
- 保留原仓库的隐私与权限约束。凭据、真实家庭画面、私有配置、备份和未审阅的私有历史不进入公共仓库；只提交当前任务的文件。
- 提交、推送、发布、部署和真实设备动作按本次任务已有授权执行。只分析、只给方案、只读审查时遵守该边界；本规范和 Skill 不额外授予操作权限。
- 完整规则和跨仓库同步方式见 [Friday 开发规范](https://github.com/lijunfeng722/friday-project-index/blob/main/docs/development.md)。
<!-- friday-dev-policy:end -->
