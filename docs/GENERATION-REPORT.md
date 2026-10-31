# 用户手册生成记录

- 使用技能：user-manual-generator 2.0.0。
- 面向非技术家庭使用者；按入门、操作指南、参考、解释和问题排查组织。
- 25 个专题页面，33 项使用问答，15 个温度质量场景。
- 36 个独立截图文件：35 张 Friday 新版图和 1 张已标日期的 ARL 原生开发演示图。
- 同时提供完整单文件 Markdown、按主题 Markdown 与 MkDocs Material 站点。
- 基础安装入口来自上游；真实设备效果、声音、NAS 与可选模型按家庭另行验证，详见 [验证范围](TODO.md)。

## 已准备的检查

`python scripts/check_docs.py` 检查链接、图片与发布输入；`mkdocs build --strict` 检查构建；`python scripts/check_docs.py --built site` 检查生成页面、语言与锚点。浏览器核对中文检索、产品图、关系图与桌面可读性；手机实机效果另行确认。

## 发布方式

推送 main 后运行 `.github/workflows/pages.yml`。工作流使用锁定依赖及固定摘要的官方 GitHub Actions，将构建产物部署到 GitHub Pages。仓库需先在 Settings → Pages 选择 GitHub Actions。

## 文档维护

入口、按钮或功能改变时，修改对应任务页并更新示例截图；执行 `python scripts/export_manual.py` 同步完整 Markdown，然后运行检查与构建。不能将真实家庭画面、授权文件、本机备份或运行日志复制进文档仓库。
