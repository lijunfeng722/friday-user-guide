# 安装前先准备什么

先运行示例，确认本机服务可打开，再逐项接入自己的家庭。已经完成部署的电脑可直接从[第一次打开](quick-start.md)开始。

## 基础示例

需要受支持的 Python 3.11 以上版本和 [uv](https://docs.astral.sh/uv/getting-started/installation/)。维护人员可从 [Friday 源码仓库](https://github.com/Geeprox/Friday)取得代码，在仓库根目录执行上游提供的入口：

```sh
./scripts/install-home.sh
./bin/home doctor
./bin/home serve
```

打开终端显示的本机地址，默认是 `http://127.0.0.1:8740`。**预期结果：**顶部显示“示例家庭”，可以阅读模拟状态；这一步不要求小米账号、模型或真实硬件。

这些命令来自上游安装说明。本次手册核对使用已经部署的环境，并未把每种操作系统的全新安装都计作通过。新电脑仍需逐步确认依赖与服务状态。

## 接真实家庭前

准备一个可正常打开的 Home Assistant。优先复用已有服务；macOS 的 HA Container 使用 Linux 虚拟机或独立 HA 主机，具体安装按 [HA 官方指南](https://www.home-assistant.io/installation/)进行。

让维护人员在 HA 内安装 [Xiaomi Home 集成](https://github.com/XiaoMi/ha_xiaomi_home)，再由你在 HA 的官方页面完成小米账号、家庭和设备选择。它不是另一套需要独立启动的服务。

## 摄像头与可选能力

本地摄像头和识别环境需要另外安装依赖、原生组件、模型和自己的配置，按 [Friday 部署指南](https://github.com/Geeprox/Friday/blob/main/docs/deployment.md)准备。Miloco 若采用插件方案，按其固定版本的官方平台说明部署。

只接入家庭设备时可以暂不配置摄像头。音频、语音回复、云台、电视、NAS、ARL 与云端模型各自按需求准备，不由基础安装自动开启。

**完成标准：**示例服务可打开；若使用真实家庭，HA 本身可打开且已出现自己的目标设备。接下来做[家庭连接](connect-home.md)。
