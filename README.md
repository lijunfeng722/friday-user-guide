# Friday 用户手册

面向非技术家庭使用者的独立图文手册，包含入门、操作指南、页面参考、功能说明与常见问题。

- [在线阅读](https://lijunfeng722.github.io/friday-user-guide/)
- [完整单文件 Markdown 手册](USER_MANUAL.md)
- [按专题阅读 Markdown](docs/index.md)
- [文档生成记录](docs/GENERATION-REPORT.md)
- [相关仓库索引](https://github.com/lijunfeng722/project-index)

截图来自明确标记的隔离示例服务；不包含家庭录像、账号凭据或本机部署目录。产品源码和各依赖遵循原仓库的许可证。本站与产品源码分开维护。

## 本地预览

需要 Python 3.12。

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/mkdocs serve
```

打开命令显示的本机地址。修改后运行 `.venv/bin/mkdocs build --strict` 和 `.venv/bin/python scripts/check_docs.py`，推送 main 后由 GitHub Actions 发布 Pages。
