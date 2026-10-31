# Friday 用户使用文档

> 面向家庭使用者；按新版界面编写。Friday 示例截图采集于 2026-10-31；ARL 原生开发版演示图保留 2026-10-30 的阶段含义。真实家庭验收资料保存在本机私有版。

[在线手册](https://lijunfeng722.github.io/friday-user-guide/) · [项目索引](https://github.com/lijunfeng722/project-index)

## 阅读目录

1. [从零开始安装 Friday](#guide-getting-started-installation)

2. [macOS 从零准备](#guide-getting-started-installation-macos)

3. [Linux 从零准备](#guide-getting-started-installation-linux)

4. [安装 HA 并接入自己的小米设备](#guide-getting-started-installation-home-assistant)

5. [准备摄像头与本地识别（可选）](#guide-getting-started-installation-camera)

6. [启动、备份与安装排障](#guide-getting-started-installation-maintenance)

7. [第一次打开 Friday](#guide-getting-started-quick-start)

8. [连接自己的家](#guide-getting-started-connect-home)

9. [查看与操作设备](#guide-guides-devices)

10. [查看摄像头与识别](#guide-guides-cameras)

11. [完成第一条手势控制](#guide-tutorials-first-gesture)

12. [管理互动控制规则](#guide-guides-interactions)

13. [管理场景与自动化](#guide-guides-automations)

14. [连接录像并保护回看](#guide-guides-recordings)

15. [查看家庭事件的来源](#guide-guides-events)

16. [核对人物与待确认分组](#guide-guides-people)

17. [查看智能预警与本机画面复核](#guide-guides-safety)

18. [使用游戏库](#guide-guides-games)

19. [找到家庭资料预览](#guide-guides-files)

20. [用文字预览模拟规则变更](#guide-guides-dialogue)

21. [新版入口速查](#guide-reference-navigation)

22. [读懂页面状态](#guide-reference-status)

23. [十五个温度质量场景](#guide-reference-temperature-scenarios)

24. [这些程序分别做什么](#guide-explanation-components)

25. [怎样看待 ARL 管理界面](#guide-explanation-arl)

26. [2026-10-31 新版使用变化](#guide-releases-2026-10-31)

27. [按现象排查](#guide-troubleshooting-common-errors)

28. [常见问题](#guide-troubleshooting-faq)

29. [后续现场验证范围](#guide-)

<a id="guide-getting-started-installation"></a>

## 1. 从零开始安装 Friday

**本章目的：**帮你选好安装路线，知道接下来要准备哪些软件，以及每一步完成后能做什么。即使电脑还没有 Python、uv、Docker 或 Home Assistant，也可以从这里开始。

**为什么先看安装路线：**Friday 提供日常使用的家庭界面，真实设备由接入服务提供，摄像头与识别还需要另一组组件。先按自己的目标选择，才能分阶段得到可用结果：先打开示例，再连接设备，最后按需要增加摄像头和互动。

**读完后：**你应能选定 macOS 或 Linux 路线，分清基础安装、真实家庭接入和可选功能，并知道各阶段的验收标准。

已经能打开 Friday 的读者，可直接进入[第一次打开](#guide-getting-started-quick-start)；已有运行环境且准备接设备的读者，可进入[连接自己的家](#guide-getting-started-connect-home)。

### 1. 选择你要完成的目标

| 你的目标 | 需要完成的章节 | 完成标志 |
| --- | --- | --- |
| 先体验页面 | 选择 macOS 或 Linux 章节，完成基础安装 | 8740 页面显示“示例家庭” |
| 查看自己的设备 | 基础安装 → HA 与小米接入 → Friday 连接 | 显示自己的房间、设备和实际状态 |
| 操作灯、窗帘等 | 设备接入 → 首次配置控制范围 | 目标控件可用，现场确认动作 |
| 使用摄像头手势 | 上述步骤 → 摄像头与识别准备 → 手势教程 | 画面与关键点可见，规则有响应且设备实际执行 |

**安装路线：**[macOS 从零准备](#guide-getting-started-installation-macos) · [Linux 从零准备](#guide-getting-started-installation-linux) → [HA 与小米接入](#guide-getting-started-installation-home-assistant) → [可选摄像头与识别](#guide-getting-started-installation-camera) → [启动、备份与排障](#guide-getting-started-installation-maintenance)。

```mermaid
flowchart TB
  S[选择安装电脑] --> M[macOS：终端、Git、uv、Python]
  S --> L[Linux：终端、Git、uv、Python]
  M --> F[下载 Friday 并打开示例]
  L --> F
  F --> H[已有 HA 直接复用；没有则安装]
  H --> X[在 HA 内安装 Xiaomi Home 并登录]
  X --> C[Friday 连接 HA 并读取自己的设备]
  C --> D[配置控制范围并验证目标设备]
  D -. 按需继续 .-> V[macOS 本地视觉、摄像头与手势]
```

### 2. 先看平台差异

| 能力 | macOS | Linux |
| --- | --- | --- |
| Friday Web、示例、HA 设备接入 | 本机 Python 环境 | 本机 Python；本文详述 Ubuntu / Debian |
| 同机运行 HA Container | 先建立 Linux 虚拟机；本文使用 Colima | 直接使用 Linux Docker Engine |
| 连接其他主机的 HA | 填写 Friday 主机可访问的地址 | 填写 Friday 主机可访问的地址 |
| Miloco | 按发行包支持的系统与芯片选择 | 按发行包支持的系统与芯片选择 |
| 当前原生人体、手部识别 | 需要 Apple Vision、兼容 SDK 与编译工具 | 当前这套原生入口不能直接运行，没有等价的 Linux 安装命令 |
| 保护录像回看 | 另装媒体工具并配置录像来源 | 另装媒体工具并配置录像来源 |

不要把 Miloco 的平台支持范围理解为 Friday 的 Apple Vision 程序也支持这些平台。Intel Mac、Apple Silicon、Linux x86_64 和 Linux ARM64 的二进制包不能混用。

### 3. 安装前准备

准备可下载 GitHub 源码、Python 软件包和容器镜像的网络，以及保存项目和数据的磁盘空间。安装系统软件时可能需要自己的管理员密码，它只填写在系统提示中。

接真实设备需要已正常使用的小米账号和设备；接摄像头前，先确认米家或对应官方应用能正常查看它。只体验示例时可暂不准备账号和硬件。

本文把项目放在 `$HOME/friday-home/Friday`。`$HOME` 会展开为你自己的主目录，不需要替换成作者电脑的路径。`cd` 用来进入目录；以 `#` 开头的行是说明，不用输入命令提示符 `$`。

先完成一组命令，核对“应看到什么”，再进入下一步。报错时保留错误文字，按对应章节处理，再继续。

### 4. 各工具分别负责什么

| 名称 | 用途 | 何时需要 |
| --- | --- | --- |
| Git | 下载、记录源码版本 | 基础安装 |
| uv、Python | 准备项目独立运行环境 | 基础安装 |
| Docker Engine、Compose | 运行 HA 容器和读取容器配置 | 新建 HA |
| Colima、Lima | 在 Mac 提供 Linux 容器主机 | Mac 单机运行 HA |
| Home Assistant（HA） | 独立的家庭设备接入平台，管理房间、设备、状态和服务，供 Friday 连接 | 接入自己的家庭；已有 HA 可以复用 |
| [Xiaomi Home 集成（ha_xiaomi_home）](https://github.com/XiaoMi/ha_xiaomi_home) | 安装在 HA 内，让 HA 登录小米账号并接入受支持的小米设备 | 通过 HA 接入小米设备 |
| [Miloco（xiaomi-miloco）](https://github.com/XiaoMi/xiaomi-miloco) | 独立的小米智能家庭项目；本安装方案使用其账号绑定、摄像头与相关智能服务 | 选择 Miloco 摄像头或智能功能方案时 |
| Node.js | OpenClaw 使用的 JavaScript 运行环境 | 选择 OpenClaw 宿主方案时 |
| OpenClaw 或 Hermes | Miloco 插件的宿主平台，按官方指南选择其中一种 | 选择对应 Miloco 插件方案时 |
| 摄像头 SDK、Apple Vision、本地模型 | 视频连接、关键点与本地场景处理 | 兼容的本地识别方案 |
| FFmpeg、ffprobe | 媒体处理与录像信息检查 | 保护回看等媒体能力 |
| ARL、云端模型 | 可选智能任务 | 对应功能单独配置 |

**本手册中的 Xiaomi Home 指 HA 内的 `ha_xiaomi_home` 集成，和 Miloco 是两个不同项目。** 查看家庭设备的接入链路是 **Friday → Home Assistant → Xiaomi Home 集成 → 小米设备**；这条链路无需先安装 Miloco。选择 Miloco 方案时，需要另外安装并在其页面完成账号绑定。HA 中的小米授权与 Miloco 的账号绑定分别保存，一边完成不代表另一边也已完成。

更多分工见[这些程序分别做什么](#guide-explanation-components)。

### 5. 版本与下载来源

基础命令按以下公开入口核对，方便安装后定位差异。系统软件采用各厂商支持当前系统的发行方式，安装时记录实际版本。

| 对象 | 本教程基线 / 来源 |
| --- | --- |
| Friday | [公开提交 e1e9c999](https://github.com/Geeprox/Friday/tree/e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3)及该提交的 `uv.lock` |
| Python / uv | Python 3.12；示例使用 uv 0.13.6 的[官方安装器](https://docs.astral.sh/uv/getting-started/installation/) |
| HA / Xiaomi Home | HA `2026.10.4`；[HA 章节的更新安装工具](#guide-getting-started-installation-home-assistant)固定 Xiaomi Home `v0.5.0` 及官方提交；旧公开源码自带工具仍固定旧版 |
| Miloco | [固定发行版 v2026.10.16](https://github.com/XiaoMi/xiaomi-miloco/releases/tag/v2026.10.16)，按平台完整指南安装 |

基础安装不会自动下载摄像头 SDK、模型、ARL，或替你配置设备控制范围。摄像头章节分别说明可执行的准备步骤和仍需匹配部署组件的部分；不会把某台电脑的私有启动器当作通用安装包。

### 6. 每一阶段怎样算完成

1. **示例可用**：明确显示“示例家庭”，能够查看模拟设备。
2. **家庭接入**：HA 和 Friday 都能找到自己的目标设备，按各自统计口径核对数量。
3. **控制可用**：目标动作已开放，页面有回执，并由你观察设备实际执行。
4. **识别可用**：真实画面持续更新、关键点可见；仍要单独验证手势触发。
5. **可以日常使用**：知道如何停止、启动和备份，重启后核对真实来源与暂停状态。

![基础安装后查看明确标记为示例家庭的设备](docs/assets/screenshots/friday-devices.jpg)

产品截图来自隔离示例，用于说明应核对的界面，不是操作系统安装过程的实机证明。各平台的新机安装、摄像头型号和真实动作按阶段分别验证，详见[验证范围](#guide-)。

<a id="guide-getting-started-installation-macos"></a>

## 2. macOS 从零准备

**本章目的：**在自己的 Mac 准备 Friday 的运行环境，下载程序并打开第一个示例页面。需要在同一台 Mac 新建 HA 时，再准备后半章的 Linux 容器环境。

### 为什么需要这些工具

Friday 的源码需要 Python 和依赖包才能运行。HA Container 则需要 Linux 容器主机，所以 Mac 的基础 Web 与 HA 容器环境分两段准备。

| 组件 | 本章用它做什么 | 你为什么需要 |
| --- | --- | --- |
| Command Line Tools、Git | 提供源码下载工具；后续原生构建也会使用编译工具 | 取得指定版本的 Friday |
| uv、Python | 为 Friday 创建独立运行环境并安装依赖 | 让 Web 服务能在自己的 Mac 启动 |
| Colima、Lima | 在 Mac 运行 Linux 虚拟机 | 仅在这台 Mac 新建 HA Container 时使用 |
| Docker 客户端、Compose | 管理虚拟机中的 HA 容器及其配置 | 创建并维护这套 HA 服务 |

**完成标志：**浏览器可打开 Friday，并看到明确标记的“示例家庭”；选择本机新建 HA 时，Docker 服务端也应可用。

**可以跳过什么：**已有可用 HA 的读者只需完成基础 Web，跳过本章的容器安装，转到[HA 与小米接入](#guide-getting-started-installation-home-assistant)。已有 Friday 服务可直接看[第一次打开](#guide-getting-started-quick-start)。

### 1. 查看电脑并打开终端

点击苹果菜单 →“关于本机”，记录系统版本和芯片。在“应用程序 → 实用工具”打开“终端”，输入：

```sh
sw_vers -productVersion
uname -m
```

**应看到：**系统版本及 `arm64`（Apple 芯片）或 `x86_64`（Intel）。下载软件时选择对应架构。

### 2. 准备 Git 和命令行工具

```sh
xcode-select --install
```

在 Apple 的窗口完成安装。提示已经安装时，继续检查：

```sh
xcode-select -p
git --version
```

**应看到：**开发工具目录和 Git 版本。工具还在下载时，等安装完成再继续。[Apple 开发工具说明](https://developer.apple.com/xcode/resources/)

### 3. 安装 uv，再准备 Python

uv 负责下载 Python 和管理项目环境。先下载官方安装器，再运行：

```sh
curl -fLsS https://astral.sh/uv/0.13.6/install.sh -o /tmp/friday-install-uv.sh
sh /tmp/friday-install-uv.sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
uv python install 3.12
uv python find 3.12
```

**应看到：**uv 版本和 Python 3.12 的路径。无需先升级系统自带 Python，也不使用 `sudo pip install`。[uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)

若重开终端后找不到 uv，用 `nano ~/.zshrc` 将下一行加入自己的配置；保存按 Control+O、回车，退出按 Control+X，再打开新终端：

```sh
export PATH="$HOME/.local/bin:$PATH"
```

使用其他 shell 时按安装器显示的对应提示处理。

### 4. 下载 Friday 并安装基础环境

```sh
mkdir -p "$HOME/friday-home"
git clone https://github.com/Geeprox/Friday.git "$HOME/friday-home/Friday"
cd "$HOME/friday-home/Friday"
git switch --detach e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3
UV_PYTHON=3.12 ./scripts/install-home.sh
./bin/home doctor
```

**应看到：**依赖安装完成，doctor 返回状态信息，基础模式为 `simulator`。ARL、摄像头等可选能力未就绪，不阻止运行示例。`detached HEAD` 表示使用选定提交，不是安装失败。

已有同名目录时不要重复 clone 或删除 `data/`，先看[维护章节](#guide-getting-started-installation-maintenance)。

### 5. 打开示例

```sh
cd "$HOME/friday-home/Friday"
./bin/home serve
```

保持终端运行，在同一台 Mac 打开 [Friday](http://127.0.0.1:8740/)。**应看到：**“示例家庭”和产品菜单。按 Control+C 停止前台服务；停止后网页暂时打不开属于正常现象。

![示例设备页用于核对基础服务已启动](docs/assets/screenshots/friday-devices.jpg)

只体验页面可到这里结束，继续[第一次打开](#guide-getting-started-quick-start)。已有 HA 可直接进入[家庭接入](#guide-getting-started-installation-home-assistant)。

### 6. 没有 HA 时，准备 Linux 容器环境

HA Container 使用 Linux Docker Engine。Mac 通过 Colima / Lima 提供 Linux 虚拟机，Docker 客户端负责向里面发送命令。[Colima 官方说明](https://github.com/abiosoft/colima/tree/v0.10.3)

先执行 `command -v brew`。没有结果时，按 [Homebrew 官网](https://brew.sh/)安装，也可下载官方脚本后运行：

```sh
curl -fLsS https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o /tmp/friday-install-brew.sh
/bin/bash /tmp/friday-install-brew.sh
```

按安装器末尾的 **Next steps** 设置环境，再打开新终端执行 `brew --version`。官网当前支持 macOS 15 及更新版本；较旧系统可按 [Colima 的其他安装方式](https://github.com/abiosoft/colima/blob/v0.10.3/docs/INSTALL.md)选择匹配发行包，或复用已有 / [Linux HA 主机](#guide-getting-started-installation-linux)。基础 Friday 不依赖 Homebrew。

在 Homebrew 支持的系统上执行：

```sh
brew install colima docker docker-compose
colima version
docker --version
docker-compose version
```

**应看到：**三个工具的版本。这一步尚未安装 HA 或完成账号接入。

### 7. 让 Docker 找到 Compose

若 `docker compose version` 已有结果，跳过本步；否则注册已安装的插件：

```sh
mkdir -p "$HOME/.docker/cli-plugins"
if [ ! -e "$HOME/.docker/cli-plugins/docker-compose" ]; then
  ln -s "$(command -v docker-compose)" "$HOME/.docker/cli-plugins/docker-compose"
fi
docker compose version
```

**应看到：**Compose 版本。若设置过 `DOCKER_CONFIG`，插件应放到该目录下的 `cli-plugins`，保留已有插件。[Homebrew Compose 说明](https://formulae.brew.sh/formula/docker-compose)

### 8. 创建专用虚拟机并检查 Docker

```sh
colima start --profile friday-home --runtime docker --cpus 2 --memory 4 --disk 32 --mount "$HOME/friday-home:w"
colima status --profile friday-home
docker context show
docker info
```

**应看到：**虚拟机运行，Docker 返回服务端信息。2 核、4 GiB 内存、32 GiB 虚拟磁盘是示例分配，可按负载调整，不是整机最低配置。可写挂载用于保存 HA 数据。

有其他 Docker / Colima 实例时，核对当前 context 对应本教程的 `friday-home` 再操作。保持虚拟机运行，继续[安装 HA 与小米接入](#guide-getting-started-installation-home-assistant)。

### 9. 常见安装问题

| 现象 | 下一步 |
| --- | --- |
| 找不到 uv | 核对安装器输出、`$HOME/.local/bin` 和当前终端的 PATH |
| 下载中断或证书错误 | 检查系统时间、网络和代理，重试官方源或固定发行包；保留证书校验 |
| Homebrew 不支持当前系统 | 采用 Colima 官方发行方式或已有 / Linux HA；基础 Friday 不依赖 Homebrew |
| `docker info` 失败 | 先启动 Colima，检查 context，再看虚拟机日志和网络 |
| HA 容器已启动，Mac 的 8123 仍打不开 | 按 [Mac 端口转发](#guide-getting-started-installation-home-assistant)处理 |
| 8740 已占用 | 先确认是否已有 Friday；并行示例可用 `./bin/home serve --port 8741`，正式连接另核对回调地址 |

**完成标准：**Friday 示例可打开；新建 HA 时，Colima 与 Docker 服务端也可用。摄像头另按[可选章节](#guide-getting-started-installation-camera)准备。

<a id="guide-getting-started-installation-linux"></a>

## 3. Linux 从零准备

**本章目的：**在 Linux 桌面或服务器上安装并启动 Friday。需要在这台 Linux 新建 HA 时，再安装 Docker Engine 和 Compose，为下一章提供容器主机。

### 为什么需要这些工具

| 组件 | 本章用它做什么 | 你为什么需要 |
| --- | --- | --- |
| Git、下载工具 | 获取源码、安装器和依赖 | 从空环境取得需要的软件 |
| uv、Python | 创建 Friday 的独立运行环境 | 按项目要求运行 Web，不依赖系统 Python 恰好符合版本 |
| Docker Engine、Compose | 直接在 Linux 运行 HA 容器 | 仅在这台主机新建 HA 时使用 |
| SSH 转发 | 在另一台电脑的浏览器访问本机监听的服务 | 无桌面或远程部署时，打开 Friday 和 HA 的页面 |

Linux 可以直接运行 Docker Engine，无需再为 HA 额外创建一层 Mac 式虚拟机。**完成标志：**本机浏览器或 SSH 转发后的浏览器能打开 Friday 示例；选择新建 HA 时，Docker 服务端也可用。

**适用范围：**命令示例针对 Ubuntu 22.04 / 24.04 / 26.04、Debian 12 / 13 的 64 位系统。其他发行版按其包管理器和 Docker 官方平台说明准备同等工具。当前 Apple Vision 原生识别不属于 Linux 安装路线，详见[摄像头平台范围](#guide-getting-started-installation-camera)。

**可以跳过什么：**已有可用 HA 时，跳过 Docker 安装；已有 Friday 时直接进入[家庭接入](#guide-getting-started-installation-home-assistant)或[日常使用](#guide-getting-started-quick-start)。

### 1. 打开终端，确认系统

桌面 Linux 打开“终端”；无桌面的服务器使用已经配置好的 SSH 或主机控制台。输入：

```sh
cat /etc/os-release
uname -m
```

**应看到：**发行版名称、版本和架构。`x86_64` 对应 amd64，`aarch64` 对应 ARM64。需要能使用 sudo 的个人账号。

### 2. 安装下载和编辑工具

```sh
sudo apt-get update
sudo apt-get install -y git curl ca-certificates nano unzip xz-utils
```

**应看到：**安装完成，没有软件源或证书错误。后续从自己的账号运行 Friday，不用 root 运行项目或安装 Python 包。

### 3. 安装 uv 和 Python

```sh
curl -fLsS https://astral.sh/uv/0.13.6/install.sh -o /tmp/friday-install-uv.sh
sh /tmp/friday-install-uv.sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
uv python install 3.12
uv python find 3.12
```

**应看到：**uv 版本与 Python 3.12 的路径。无需依赖发行版自带 Python 的版本。[uv 安装](https://docs.astral.sh/uv/getting-started/installation/)与[管理 Python](https://docs.astral.sh/uv/guides/install-python/)

若新终端找不到 uv，使用 `nano ~/.bashrc` 加入下面一行并重新打开终端；zsh 用户改用自己的 `~/.zshrc`：

```sh
export PATH="$HOME/.local/bin:$PATH"
```

nano 保存按 Control+O、回车，退出按 Control+X。

### 4. 下载 Friday 并安装

```sh
mkdir -p "$HOME/friday-home"
git clone https://github.com/Geeprox/Friday.git "$HOME/friday-home/Friday"
cd "$HOME/friday-home/Friday"
git switch --detach e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3
UV_PYTHON=3.12 ./scripts/install-home.sh
./bin/home doctor
```

**应看到：**基础依赖安装成功，doctor 的基础模式为 `simulator`。选定提交产生的 `detached HEAD` 是版本定位提示。已有目录时先看[维护章节](#guide-getting-started-installation-maintenance)，不覆盖原数据。

启动：

```sh
./bin/home serve
```

保持终端运行，在这台 Linux 的浏览器打开 [Friday](http://127.0.0.1:8740/)。看到“示例家庭”即完成基础安装，Control+C 用于停止前台服务。

### 5. 在另一台电脑查看 Linux 服务

Friday 默认只监听 Linux 主机自己的 `127.0.0.1`。已有 SSH 连接时，可在你的浏览器电脑另开终端建立转发：

```sh
ssh -N -L 8740:127.0.0.1:8740 -L 8123:127.0.0.1:8123 user@192.0.2.10
```

将 `user@192.0.2.10` 换成自己的 SSH 用户和 Linux 主机地址；这是文档示例地址。保持转发终端运行，再在浏览器电脑打开 `http://127.0.0.1:8740/`。8123 的转发供稍后的 HA 使用。

**应看到：**与 Linux 本机相同的 Friday 页面。正式账号连接使用默认端口，以便和当前版本的本机回调一致。直接把 Linux 的内网 IP 拼到 8740 后面，不能替代这个转发。

### 6. 需要新 HA 时，安装 Docker Engine

已有可用 HA 可跳过本节，直接进入[HA 与小米接入](#guide-getting-started-installation-home-assistant)。已有 Docker 时先运行 `sudo docker info` 和 `sudo docker compose version`，两项成功即可复用。

全新 Ubuntu / Debian 按下面步骤添加 Docker 官方软件源。先准备保存签名密钥的目录：

```sh
sudo install -d -m 0755 /etc/apt/keyrings
```

#### Ubuntu：执行这一组

```sh
curl -fLsS https://download.docker.com/linux/ubuntu/gpg -o /tmp/friday-docker.asc
sudo install -m 0644 /tmp/friday-docker.asc /etc/apt/keyrings/docker.asc
friday_codename="$(. /etc/os-release; printf '%s' "$VERSION_CODENAME")"
friday_arch="$(dpkg --print-architecture)"
printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' "$friday_arch" "$friday_codename" | sudo tee /etc/apt/sources.list.d/friday-docker.list >/dev/null
```

#### Debian：执行这一组

```sh
curl -fLsS https://download.docker.com/linux/debian/gpg -o /tmp/friday-docker.asc
sudo install -m 0644 /tmp/friday-docker.asc /etc/apt/keyrings/docker.asc
friday_codename="$(. /etc/os-release; printf '%s' "$VERSION_CODENAME")"
friday_arch="$(dpkg --print-architecture)"
printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian %s stable\n' "$friday_arch" "$friday_codename" | sudo tee /etc/apt/sources.list.d/friday-docker.list >/dev/null
```

两组只选匹配发行版的一组。接着安装并检查：

```sh
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker info
sudo docker compose version
```

**应看到：**Docker 服务端信息及 Compose 版本。`enable` 同时让 Docker 随系统启动；Friday Web 仍按自己的启动方式管理。本教程给需要 Docker 权限的 Linux 命令显式加 sudo，无需先修改用户组。

若机器已有其他容器软件、软件源或 Docker 数据，按 [Docker Ubuntu 官方安装](https://docs.docker.com/engine/install/ubuntu/)或 [Debian 官方安装](https://docs.docker.com/engine/install/debian/)处理兼容问题，不套用清空数据命令。其他发行版从 [Docker Engine 平台列表](https://docs.docker.com/engine/install/)选择。

### 7. 常见安装问题

| 现象 | 检查位置 |
| --- | --- |
| apt 找不到 Docker 包 | 发行版和代号是否匹配官方源，`apt-get update` 是否成功 |
| Docker socket 权限不足 | 使用本章带 sudo 的 Docker 命令；不改 socket 为任意用户可写 |
| Docker 服务没启动 | `sudo systemctl status docker`，再看服务日志 |
| 服务器运行但自己浏览器打不开 | 先核对 SSH 转发，区分浏览器电脑和 Linux 主机的 127.0.0.1 |
| 依赖下载失败 | 检查网络、时间、证书与包源；保留报错，不把软件源错误当成账号错误 |
| 想在 Linux 执行原生手势编译 | 当前 Apple Vision 入口不适用，见[摄像头平台范围](#guide-getting-started-installation-camera) |

**完成标准：**示例页面可打开；需要新 HA 时 Docker Engine、Compose 也已就绪。继续[安装 HA 与小米接入](#guide-getting-started-installation-home-assistant)。

<a id="guide-getting-started-installation-home-assistant"></a>

## 4. 安装 HA 并接入自己的小米设备

**本章目的：**把自己在米家中使用的设备接入 Friday，让 Friday 能显示真实房间、设备和状态。你将新建或复用 Home Assistant，在其中接入小米设备，再授权 Friday 读取这份家庭清单。

### 为什么需要 HA 和 Xiaomi Home

本教程使用 HA 作为 Friday 的设备接入平台。米家手机应用已经能控制设备，并不表示 Friday 已经获得这些设备和状态；需要先建立下面这条接入链路。

| 组件 | 它是什么 | 本章为什么需要 |
| --- | --- | --- |
| Friday | 你日常打开的家庭界面 | 从 HA 读取房间、设备和状态，并提供使用入口 |
| Home Assistant（HA） | 独立运行的家庭设备平台 | 汇集设备和房间，向 Friday 提供统一的状态与服务 |
| Xiaomi Home（ha_xiaomi_home） | 安装在 HA 内的小米设备集成 | 让 HA 登录你的小米账号，接入所选家庭中受支持的设备 |

```mermaid
flowchart LR
  F[Friday 家庭界面] --> H[Home Assistant 设备平台]
  H --> X[Xiaomi Home 小米集成]
  X --> D[自己的小米设备]
```

你会分别完成两项授权：**Xiaomi Home 登录小米账号，把设备接入 HA；Friday 登录 HA，读取已接入的家庭。** 它们有各自的页面和保存记录。

这条设备接入路线无需先安装 Miloco。Miloco 是独立项目，选择其摄像头或智能功能时，再按[可选摄像头章节](#guide-getting-started-installation-camera)准备。

**适用与跳过：**

- 还没有 HA：从第 1 步开始。
- 已有 HA，但尚未接入小米设备：按第 3 步说明在原实例安装集成，再完成第 5 步。
- HA 已能看到目标设备：直接进入第 6 步。其他品牌设备通过各自的 HA 集成接入后，也从这里继续。
- 只体验示例：可跳过本章。

**开始前：**已经完成 [macOS](#guide-getting-started-installation-macos)或 [Linux](#guide-getting-started-installation-linux)基础安装。新建 HA 时，Docker 服务端及 Compose 检查成功。

**完成标志：**HA 和 Friday 都能找到自己的目标设备，且 Friday 显示真实家庭来源。需要发送设备动作时，再按第 7 步配置控制范围并现场验证。

### 1. 准备持久化配置

在 Friday 安装电脑的终端执行：

```sh
cd "$HOME/friday-home/Friday"
.venv/bin/python scripts/setup-dependencies.py plan
.venv/bin/python scripts/setup-dependencies.py prepare
```

**应看到：**plan 列出当前工具，prepare 返回 `prepared: true`、`services_started: false`。它创建 `data/deployment/compose.yaml`、`.env` 和所需私有目录，还没有启动 HA。

已有这些文件时不要重复 prepare；先检查是否属于已有部署。HA 数据以后保存在 `data/deployment/homeassistant`，容器里对应 `/config`，重建容器不会替你重新创建账号。

### 2. 设置自己的时区

```sh
nano data/deployment/.env
```

将 `TZ=UTC` 改为自己的 IANA 时区，例如 `TZ=Asia/Shanghai`、`TZ=Europe/Berlin`。保存按 Control+O、回车，退出按 Control+X。

**应看到：**文件只保留所选时区配置。错误时区会影响时间显示和自动化时间判断。

### 3. 把 Xiaomi Home 安装到 HA 内

本教程现在使用 **Xiaomi Home v0.5.0**。早期公开 Friday 源码中的准备脚本仍固定旧版，因此这里单独下载已更新的安装工具，不依赖旧脚本的版本选择。工具只安装集成；小米登录仍在 HA 官方页面完成。

#### 下载安装工具

```sh
mkdir -p "$HOME/friday-home/service-tools"
cd "$HOME/friday-home/service-tools"
friday_setup_url="https://lijunfeng722.github.io/friday-user-guide/assets/scripts"
for friday_setup_file in setup-dependencies.py FRIDAY-SCRIPT-LICENSE.txt SETUP-SHA256SUMS; do
  curl -fL "$friday_setup_url/$friday_setup_file" -o "$friday_setup_file"
done
```

macOS 校验下载内容：

```sh
shasum -a 256 -c SETUP-SHA256SUMS
```

Linux 校验下载内容：

```sh
sha256sum -c SETUP-SHA256SUMS
```

**应看到：**安装工具和许可证均显示 `OK`。也可分别下载[安装工具](docs/assets/scripts/setup-dependencies.py)、[许可证](docs/assets/scripts/FRIDAY-SCRIPT-LICENSE.txt)和[校验清单](docs/assets/scripts/SETUP-SHA256SUMS)。

#### 首次安装集成

```sh
cd "$HOME/friday-home/Friday"
.venv/bin/python "$HOME/friday-home/service-tools/setup-dependencies.py" xiaomi-home --project "$PWD"
```

**应看到：**`installed: true`、`version: v0.5.0`，并提示需要 HA 重启和账号登录。工具校验官方固定提交 `75b3acb6325a3a8d295688b13904737d6738a6a5`；集成位于 `data/deployment/homeassistant/custom_components/xiaomi_home`。它是 HA 内部集成，不是另一个独立 Web 服务。

已有集成时，脚本会拒绝覆盖；按[已有集成升级步骤](#guide-getting-started-installation-maintenance)维护。对其他方式安装的 HA，要将集成安装到该实例实际使用的 `/config/custom_components`，不能把本教程新目录当作原实例配置。[Xiaomi Home 官方安装说明](https://github.com/XiaoMi/ha_xiaomi_home/tree/v0.5.0)

### 4. 启动 HA 并检查页面

#### macOS

确认 Colima 的专用实例运行后执行：

```sh
docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env up -d
docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env ps
```

#### Linux

```sh
sudo docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env up -d
sudo docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env ps
```

**应看到：**homeassistant 服务运行。首次拉取镜像和初始化需要等待。该 Compose 使用固定 HA 镜像和 Linux host network；没有自动配置 USB、蓝牙或 Zigbee 适配器。[HA Container 官方说明](https://www.home-assistant.io/installation/linux/)

在 HA 所在主机，或已经建立对应端口转发的浏览器电脑，打开 [HA 本机入口](http://127.0.0.1:8123/)。按页面创建自己的管理员、设置家庭位置与时区，直到进入 HA 主界面。密码和验证码只填在页面。

#### Mac 的 8123 打不开时

先检查容器仍在运行。Colima 自动转发没有生效、而虚拟机内 HA 可用时，可以在 Mac 新开终端建立仅本机转发：

```sh
umask 077
colima ssh-config --profile friday-home > "$HOME/friday-home/ha-ssh.config"
friday_ssh_host="$(awk '$1 == "Host" {print $2; exit}' "$HOME/friday-home/ha-ssh.config")"
ssh -F "$HOME/friday-home/ha-ssh.config" -o ExitOnForwardFailure=yes -N -L 127.0.0.1:8123:127.0.0.1:8123 "$friday_ssh_host"
```

保持这个终端运行，再打开 8123。端口已经被占用时先核对现有转发，不反复启动。此配置文件由你自己的 Colima 生成，不需要填写作者电脑的 SSH 路径。

Linux 远程主机使用 [Linux 章节的 SSH 转发](#guide-getting-started-installation-linux)。HA 地址需同时能被 Friday 所在主机访问；不在同一主机时，使用该 HA 的实际可达地址。

### 5. 在 HA 完成小米登录与设备选择

1. 在 HA 打开“设置 → 设备与服务 → 添加集成”。
2. 搜索 Xiaomi Home，阅读集成提示，选择自己的区域。
3. 打开其小米官方授权页，登录自己的账号并确认授权。
4. 回到 HA，选择需要接入的家庭和设备，完成后续页面。
5. 在 HA 集成页查找目标设备，查看房间和状态。

新增集成文件后搜索不到 Xiaomi Home，先重启本教程的 homeassistant 服务，再刷新浏览器。不要把 Miloco 登录当作这一步已经完成。

#### 小米确认授权后返回失败

检查授权回调使用的主机名，当前固定集成通常使用 `homeassistant.local:8123`。先在**进行登录的浏览器电脑**打开 `http://homeassistant.local:8123/`；它也应能打开同一台 HA。

如果这个名字不能解析或指向另一台机器，先修复本地域名 / mDNS，再重新发起授权。不要修改授权链接里的 state 或把含授权码的完整回调地址发给别人。

对于 HA 就在本机 8123、或通过上述 SSH 转发访问本机 8123 的情况，可由这台浏览器电脑的管理员在 hosts 文件中将该名称指向本机：

```sh
sudo nano /etc/hosts
```

在确认没有另一台同名 HA 后，添加单独一行并保存：

```text
127.0.0.1 homeassistant.local
```

再次访问该名称，能打开正确 HA 后才重试授权。若 HA 通过其他主机地址访问，应由自己的网络配置将这个名字指向那台 HA 的可达地址；不要照抄 loopback 映射。以后撤销本机映射时，只移除自己新增的这一行。

### 6. 让 Friday 读取自己的家庭

保持 HA 运行，重新打开 Friday 的“连接”：

1. 点击“查找并连接”；多个结果时选自己的 HA。
2. 没发现时点击“填写地址”，输入完整可达地址。
3. 在 HA 官方登录页面完成 Friday 的授权。
4. 返回 Friday，点击“连接并读取设备”。

![Friday 家庭连接向导，摄像头被单独列为可选项](docs/assets/screenshots/friday-settings.jpg)

**应看到：**“家庭已连接”，设备页出现自己的设备。设备数量按当前家庭决定，不以示例截图的数量为标准。一个设备的多个实体也不是多台设备。详细操作见[连接自己的家](#guide-getting-started-connect-home)。

基础源码入口重启后可能仍从示例模式启动；已有授权与当前来源分别判断。重新进入连接页读取家庭，或使用部署版本提供的已配置来源启动器，再确认顶部状态；不需要因此反复删除账号授权。

### 7. 首次开放设备控制范围

读取设备完成后，可以先只查看状态。首次控制需要本机操作员根据自己的 HA 实例、实体标识和设备能力配置允许范围；这是一项部署设置，不是每次使用都要逐台重新登录。

当前界面可以暂停 / 恢复已有范围，但没有替代首次范围文件配置。源码 Web 默认使用 `data/homeplane/action-authority.json`；桌面部署的私有目录不同，应按其构建说明确认。

配置时核对：HA 地址与实例标识、允许的操作、明确的实体列表、是否启用及有效期。只开放准备使用的设备，不复制其他家庭的标识。文件格式以所选版本的 [HomeDeviceAuthority 契约](https://github.com/Geeprox/Friday/blob/e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3/homeplane/action_contracts.py)及[控制授权说明](https://github.com/Geeprox/Friday/blob/e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3/docs/deployment.md#6-设备控制权限)为准；配置完成后重新连接并核对候选目标。

先用一个选定设备验证：检查目标和动作 → 明确执行 → 看页面回执 → 观察设备实际变化。有记录并不替代现场确认。之后可继续[设备操作](#guide-guides-devices)或[摄像头与识别准备](#guide-getting-started-installation-camera)。

**完成标准：**HA、Friday 都能找到自己的目标，来源明确；需要控制时，相应动作范围已配置并由你确认实际效果。

<a id="guide-getting-started-installation-camera"></a>

## 5. 准备摄像头与本地识别（可选）

**本章目的：**准备摄像头连接和 Friday 本地识别所需的组件，逐步验证画面、人体与手部识别，再为手势控制提供输入。

### 为什么要分开准备视频、识别和控制

| 部分 | 负责什么 | 你为什么需要 |
| --- | --- | --- |
| Miloco 及所选插件宿主 | 本方案中的小米账号绑定、摄像头与相关服务 | 建立所选摄像头方案的账号和服务条件 |
| Friday 视觉环境 | SDK、视频解码、Apple Vision 与本地模型等组件 | 连接画面，得到人体、手部关键点及场景信息 |
| 手势规则与设备控制范围 | 把识别到的动作关联到允许控制的目标 | 让你选定的动作能触发正确设备 |

三部分分别配置和验收：先确认画面，再看识别结果，最后验证规则和真实设备效果。Miloco 能播放视频后，仍需准备 Friday 的识别环境；看到骨架后，也要核对规则和控制范围。

**适用与跳过：**需要摄像头或手势的读者继续；只查看或操作 HA 设备时可跳过。已经接通的用户直接看[摄像头使用指南](#guide-guides-cameras)。

**开始前与完成标志：**先让摄像头在官方应用中正常工作；本章按阶段核对安装、登录、画面、识别和动作效果。完整识别还需要所选部署版本提供摄像头注册与后台启动组件，具体见第 7 步。

### 先确认平台与目标

| 目标 | macOS | Linux |
| --- | --- | --- |
| 安装 Miloco、绑定账号、查看支持的摄像头 | 选择官方支持的系统与芯片包 | 选择官方支持的架构包 |
| Friday 原生人体、手部识别 | 需要 Apple Vision、匹配 SDK、模型与后台装配 | 当前原生程序依赖 Apple Vision，不能照搬 macOS 编译步骤 |
| 普通 HA 设备控制 | 完成家庭接入和控制范围配置即可 | 完成家庭接入和控制范围配置即可 |

摄像头画面正常，不表示 Friday 已具备识别环境；识别可见，也不表示规则已允许执行。Intel Mac 如没有匹配的 SDK 发行包，同样不能使用 arm64 包替代。

### 1. 先检查摄像头与账号

在米家或摄像头官方应用确认：目标属于自己的账号、设备在线、镜头已由你主动打开、画面能播放。记下目标名称供本机选择，不将设备标识或家庭画面放进公开仓库。

HA 的 Xiaomi Home 登录与 Miloco 的小米绑定各自保存授权，一边完成不能代替另一边。普通本地手势不要求先购买云端模型服务。

### 2. 准备 Miloco 的插件宿主

Miloco v2026.10.16 的安装入口提供 OpenClaw、Hermes 平台指南。这里以 OpenClaw 为例；已有兼容宿主可以复用，先确认原配置，不新建覆盖原账号。

从 [Node.js 官方发行目录](https://nodejs.org/dist/v24.22.1/)选择 Node 24.22.1 对应系统、架构的安装包，并按同目录的校验清单核对。Mac 可下载 `.pkg` 安装器，按系统窗口完成安装后重开终端。

Linux 先按 `uname -m` 的结果二选一：

```sh
# x86_64 使用这一行
friday_node_archive=node-v24.22.1-linux-x64.tar.xz
```

```sh
# aarch64 / arm64 使用这一行
friday_node_archive=node-v24.22.1-linux-arm64.tar.xz
```

接着在同一个终端下载、校验和解压：

```sh
mkdir -p "$HOME/friday-home/downloads" "$HOME/friday-home/tools"
cd "$HOME/friday-home/downloads"
curl -fLO "https://nodejs.org/dist/v24.22.1/$friday_node_archive"
curl -fLsS https://nodejs.org/dist/v24.22.1/SHASUMS256.txt -o node-SHASUMS256.txt
sha256sum --check --ignore-missing node-SHASUMS256.txt
tar -xf "$friday_node_archive" -C "$HOME/friday-home/tools"
friday_node_folder="${friday_node_archive%.tar.xz}"
export PATH="$HOME/friday-home/tools/$friday_node_folder/bin:$PATH"
```

**应看到：**下载文件的校验结果为 `OK`。需要新终端继续使用时，把实际解压目录的 `bin` 路径加入自己的 shell 配置，例如 x64 对应 `$HOME/friday-home/tools/node-v24.22.1-linux-x64/bin`。随后确认：

```sh
node --version
npm --version
```

**应看到：**Node `v24.22.1` 和 npm 版本。需要详细平台操作时见 [Node 官方下载入口](https://nodejs.org/en/download)。不要用系统里一个过旧的 Node 继续安装。

在个人目录安装选定宿主版本：

```sh
mkdir -p "$HOME/friday-home/tools/openclaw"
npm install --prefix "$HOME/friday-home/tools/openclaw" openclaw@2026.10.9
export PATH="$HOME/friday-home/tools/openclaw/node_modules/.bin:$PATH"
openclaw --version
openclaw configure --section gateway
```

按本机向导配置本地网关及其认证，再安装、检查服务：

```sh
openclaw gateway install
openclaw gateway status
```

**应看到：**网关可用。需要后续终端继续找到 openclaw 时，把同一条 PATH 配置加入自己的 shell 配置。网关认证信息保存在自己的本机配置；本阶段不必配置 IM，也不把网关启动当作模型任务已经可用。[OpenClaw 官方入门](https://docs.openclaw.ai/start/getting-started)

### 3. 安装固定版本 Miloco

先阅读[固定版本平台选择入口](https://github.com/XiaoMi/xiaomi-miloco/blob/v2026.10.16/scripts/install-guide.md)，确认选择 OpenClaw 路线。下载该版本官方安装器：

```sh
curl -fLsS https://github.com/XiaoMi/xiaomi-miloco/releases/download/v2026.10.16/install.sh -o /tmp/friday-install-miloco.sh
bash /tmp/friday-install-miloco.sh --agent-prepare
```

**应看到：**环境准备、核心包和服务状态结果，或明确的失败步骤。安装器可能准备自己的 Python 和依赖，这不需要把 Friday 的 Python 3.12 替换掉。系统出现本地网络权限提示时，按自己要使用的本地设备功能选择。

按输出打开本机 Miloco 页面，默认入口为 `http://127.0.0.1:1810/`。自己完成小米登录与绑定；授权结果只填回对应页面，不放进聊天、命令历史或文档。

账号绑定后，按同版本平台指南完成剩余安装：

```sh
bash /tmp/friday-install-miloco.sh --agent-finish
openclaw gateway restart
miloco-cli service status
miloco-cli device list
```

**应看到：**服务运行，设备清单中能找到自己的摄像头。若终端找不到 miloco-cli，核对安装器输出及 `$HOME/.local/bin`。没有模型 Key 时，服务与账号、摄像头接入分别验收；不把未配置的多模态智能功能计为完成。

### 4. 在 Friday 记录摄像头连接

在“连接 → 摄像头与互动”按页面选择安装或已有服务入口。兼容服务地址必须是本机入口；填写自己的摄像头并检查服务和绑定状态。

![连接页把摄像头与互动列为可选阶段](docs/assets/screenshots/friday-settings.jpg)

服务检查成功只说明连接和账号条件，接下来还需 Friday 自己的视觉环境。

### 5. macOS：准备独立视觉环境

以下是源码部署的进阶准备。使用统一的默认目录 `data/embodied`，不要把另一台机器的私有目录、会话或绝对路径复制进来。

```sh
cd "$HOME/friday-home/Friday"
mkdir -p data/embodied
uv venv --python 3.12 data/embodied/runtime
uv export --locked --no-dev --extra vision --extra camera-media --no-emit-project --format requirements.txt --output-file data/embodied/requirements-vision.txt
uv pip install --python data/embodied/runtime/bin/python --require-hashes -r data/embodied/requirements-vision.txt
```

**应看到：**锁定依赖安装到独立的 `runtime`，与 Web 的 `.venv` 分开。不要对已有且正在使用的视觉环境重复创建。

SDK 不随 Friday 分发。从 [Miloco 固定发行版](https://github.com/XiaoMi/xiaomi-miloco/releases/tag/v2026.10.16)及其官方说明取得与系统、芯片、Python 匹配的 SDK wheel，在本机指定实际下载路径：

```sh
printf '请输入匹配 SDK wheel 的完整本机路径：'
read -r friday_sdk_wheel
uv pip install --python data/embodied/runtime/bin/python "$friday_sdk_wheel"
data/embodied/runtime/bin/python -c 'import av, cv2, onnxruntime, miot.camera; print("视觉依赖与摄像头 SDK 可导入")'
```

**应看到：**依赖和 SDK 可导入。下载了 Miloco 服务或在 Web 环境装了 PyAV，不能替代这个检查。

### 6. macOS：编译原生程序并准备模型

先检查编译器，再编译当前源码：

```sh
xcrun --find swiftc
xcrun --find clang
.venv/bin/python scripts/embodied/runtime.py --build-native
```

**应看到：**`data/embodied/bin` 下生成 `friday-vision` 与 `camera-sockets.dylib`，命令返回文件摘要。它不会下载模型、注册账号或启动摄像头。

另外准备 `data/embodied/models/yolov8n.onnx`。可使用对应部署版本提供、来源和摘要明确的模型；自行导出时，使用 [Ultralytics 官方权重](https://github.com/ultralytics/assets/releases/tag/v8.3.0)和[官方 ONNX 导出方式](https://docs.ultralytics.com/integrations/onnx/)，在独立导出环境生成，不在生产视觉环境临时升级依赖。

交给部署者核对的参数包括：所用权重及许可、导出器版本、ONNX opset、输入尺寸、是否动态尺寸和实际 SHA-256。一个采用 opset 17、640×640、静态输入的导出产物，也必须核对当前程序兼容性；不能直接把它标成参考清单中另一个文件的摘要。

### 7. 初始化自己的摄像头与后台入口

这一阶段仍需要对应版本的部署组件或部署维护者完成注册。当前公开基础命令 `./bin/home serve` 默认不启动识别后台；安装上面的包并不自动补齐这一阶段。

| 必须准备 | 要核对的内容 |
| --- | --- |
| 摄像头私有配置 | 来自自己账号的设备、匹配设备描述、稳定 camera ID、默认镜头 |
| 当前登录会话 | 有效的访问会话和过期时间；由原登录服务持有刷新职责 |
| 本机查看和控制配置 | 私有密钥、页面 origin、查看地址和端口，文件权限受限 |
| 一致的运行目录 | 安装、构建、模型、私有配置、主进程与 worker 读取同一目录 |
| 后台启动 | 所选入口启用 supervisor、真实家庭来源和识别策略，并恢复已保存的暂停状态 |
| 设备控制范围 | 与自己的 HA 实例和选定设备绑定；不因打开摄像头自动扩大 |

使用部署版本提供的正式注册、启动入口。没有这些入口或匹配组件时，先停在准备阶段，把缺项交给部署维护者；不要复制别人的私有 JSON 或猜测设备属性。基础 CLI 没有一个“安装全部识别环境”的通用开关，手册也不会把某台电脑的私有修复脚本当作公开安装器。

可先运行不会打开硬件的缺项检查：

```sh
.venv/bin/python scripts/embodied/runtime.py --check
```

本文公开基线的检查包含额外语音 / 决策资源，只检查预期文件，不等于实际连接、推理或物理动作成功。它没有 `--profile gestures` 参数；不要照抄其他本机修复版本才有的参数。普通手势的准备范围应按所用部署版本说明逐项核对。

### 8. 分层验收

1. 先保持手势触发暂停，确认自己的摄像头画面持续更新。
2. 在 Friday“摄像头 → 人物与手势检查 → 查看识别”查看骨架或手部提示。
3. 核对镜头、房间、设备控制范围，再保存规则。
4. 明确这条规则的实际效果后恢复手势控制。
5. 同时查看“最近响应”和目标设备的实际变化。

![识别入口与镜头状态需要分别核对，截图为隔离示例](docs/assets/screenshots/friday-cameras.jpg)

按[第一条手势控制](#guide-tutorials-first-gesture)完成现场验证。“电视未连接”不妨碍电脑预览；语音、云台、电视、人脸登记和房间标定按自己的需求分别准备。

**完成标准：**安装、登录、画面、识别、规则响应与物理效果分别有依据。Linux 完成 Miloco 接入后仍不因此具备当前 Apple Vision 手势链路。

<a id="guide-getting-started-installation-maintenance"></a>

## 6. 启动、备份与安装排障

**本章目的：**让首次安装好的环境能够持续使用：你会知道怎样启动、正常停止、重新检查、备份，并在出错时找到对应环节。

### 为什么安装后还需要维护步骤

Friday、HA、Miloco 等组件分别运行，也分别保存账号连接、家庭配置和规则。关闭终端、电脑重启或升级软件后，需要逐项确认服务和状态；提前保存配置与版本信息，才能恢复自己的设置。

本章把日常操作和安装排障放在一起，帮助你判断当前应启动哪个服务、保留哪些数据，以及应向维护者提供什么信息。

**适用与跳过：**所有已完成安装的读者都应了解启动与备份。没有安装 Miloco、OpenClaw、摄像头或回看功能时，跳过对应小节。Friday 尚未安装成功时，先返回自己的 [macOS](#guide-getting-started-installation-macos)或 [Linux](#guide-getting-started-installation-linux)章节。

**完成标志：**你能重新打开正确的服务、确认真实家庭来源和暂停状态，知道备份位置，并能按症状定位下一步。操作前先确认正在管理自己的哪台电脑、哪套服务。

### 1. 日常启动与停止

你可以选择部署时已经配好的整套入口，或为基础源码安装准备通用脚本。**先确认脚本管理哪些服务，再执行。** 停止服务会让网页暂时不可用，但会保留账号连接、规则、模型和家庭数据。

重启会恢复原部署中已启用的后台和规则。暂时不希望手势触发设备时，先在 Friday“互动控制”暂停互动，再停止服务；脚本会保留这个暂停设置。

#### 已有整套部署脚本：直接使用

如果部署人员已经为你的电脑准备了脚本及 `services.local.json`，在这份交付目录中操作。需要停止时执行：

```sh
./stop-friday.sh
```

需要重新启动时执行：

```sh
./restart-friday.sh
```

macOS 交付包也可提供“优雅停止.command”“重新启动.command”：在 Finder 双击对应文件即可。保留同目录的管理程序、辅助程序和配置文件；这些入口使用的是同一份配置。

**不需要重新初始化、重新安装依赖或逐台设备登录。** 已配置的视觉、ARL、Miloco、插件宿主等组件，只有被登记在这份部署配置里，才会由脚本管理。换电脑、移动运行环境或重建 HA 容器后，先核对配置中的路径和服务归属。

#### 基础源码安装：先准备通用脚本

适用于已按本手册安装好 Friday 的 macOS / Linux 用户。下载版默认管理基础 Web；初始化时可以加上**本教程创建的 HA 容器**。它不自动装配摄像头、ARL 或 Miloco；完整部署应使用上一节对应的专属配置。

下载文件：[管理程序](docs/assets/scripts/friday-services.py)、[停止脚本](docs/assets/scripts/stop-friday.sh)、[重启脚本](docs/assets/scripts/restart-friday.sh)、[文件校验清单](docs/assets/scripts/SHA256SUMS)。也可在终端下载到自己的目录：

```sh
mkdir -p "$HOME/friday-home/service-tools"
cd "$HOME/friday-home/service-tools"
friday_script_url="https://lijunfeng722.github.io/friday-user-guide/assets/scripts"
for friday_script_file in friday-services.py stop-friday.sh restart-friday.sh SHA256SUMS; do
  curl -fL "$friday_script_url/$friday_script_file" -o "$friday_script_file"
done
```

核对下载是否完整。macOS 执行：

```sh
shasum -a 256 -c SHA256SUMS
```

Linux 执行：

```sh
sha256sum -c SHA256SUMS
```

**应看到：**三个脚本均为 `OK`。校验失败时先重新下载，不继续执行。然后赋予执行权限：

```sh
chmod +x stop-friday.sh restart-friday.sh
```

接下来**选择一种**初始化方式。此步只保存本机服务清单，不启动或停止服务；已有 `services.local.json` 时拒绝覆盖。

只管理 Friday Web：

```sh
"$HOME/friday-home/Friday/.venv/bin/python" friday-services.py init \
  --project "$HOME/friday-home/Friday" --config "$PWD/services.local.json"
```

同时管理本教程创建且已经运行过的 HA 容器，macOS 或不需要 sudo 的 Docker 用户执行：

```sh
"$HOME/friday-home/Friday/.venv/bin/python" friday-services.py init \
  --project "$HOME/friday-home/Friday" --with-ha --config "$PWD/services.local.json"
```

Linux 按本手册使用 sudo 管理 Docker 时，改用：

```sh
sudo -v
"$HOME/friday-home/Friday/.venv/bin/python" friday-services.py init \
  --project "$HOME/friday-home/Friday" --with-ha --docker-sudo --config "$PWD/services.local.json"
```

`--with-ha` 通过本教程的 Compose 配置查找唯一的既有 HA 容器，记录其标识；不会新建 HA，也不管理其他家庭的 HA。使用其他安装方式或远程 HA 时，选只管理 Web，并按原服务的维护方式管理 HA。

**应看到：**`configuration / created_no_service_started`，本目录生成仅自己可读的 `services.local.json`。这份配置属于你的电脑，不上传公开仓库。初始化失败时，先确认 Friday 的 `.venv` 存在、Docker 服务端可用，以及自己的 HA 已经按前章启动。

#### 每天怎样停止和重新启动

在脚本目录执行。若使用 `--docker-sudo`，先运行 `sudo -v`；macOS 的 HA 位于 Colima 时，先确认专用实例运行、当前 Docker 连接仍指向该实例，必要时执行 `colima start --profile friday-home`。

先预览将管理的服务，不实际停止：

```sh
FRIDAY_PYTHON="$HOME/friday-home/Friday/.venv/bin/python" ./restart-friday.sh --dry-run
```

需要停止时：

```sh
FRIDAY_PYTHON="$HOME/friday-home/Friday/.venv/bin/python" ./stop-friday.sh
```

需要重新启动时：

```sh
FRIDAY_PYTHON="$HOME/friday-home/Friday/.venv/bin/python" ./restart-friday.sh
```

完整部署的专属入口也遵循同样的顺序：按配置顺序启动，倒序停止。例如：

```mermaid
flowchart TD
  A[停止 Friday] --> B[等待视觉与后台子进程收尾]
  B --> C[停止已登记的 ARL、插件宿主、Miloco]
  C --> D[停止这套 HA，保留数据与容器主机]
  D --> E[重新启动时先准备 HA 和所需依赖]
  E --> F[启动 Friday 并核对启用规则的设备状态]
  F --> G[打开页面核对来源与开关]
```

| 输出 | 你应怎样理解 |
| --- | --- |
| `would_stop` / `would_start` | 预览计划，没有改变服务 |
| `would_prepare` | 重新启动前会先确认已登记的容器主机可用 |
| `stopping` / `waiting` | 正在等待正常退出或启动，保持终端运行 |
| `stopped` | 这一项已完成停止检查 |
| `ready` / `already_running` | 这一项的进程或服务及配置的就绪检查已通过 |
| `kept_running` | 明确保留的容器主机等依赖继续运行 |
| `deployment / stop_complete` | 本次配置中需要停止的服务均已完成检查 |
| `deployment / restart_complete` | 本次配置中的启动顺序与就绪检查已完成 |
| `deployment / failed:…` | 没有完成；按后面的错误说明处理 |

管理程序向归属核对通过的 Friday 进程请求正常退出，等待已记录的子进程收尾；HA 使用不自动升级为强制结束的停止请求。退出超时或摄像头恢复检查未通过时，脚本报错，保留尚未关闭的依赖，也不会继续启动下一轮。Miloco 等外部服务仍由对应官方维护命令执行停止，遵循其自身的退出策略。[Docker 停止行为说明](https://docs.docker.com/reference/cli/docker/container/stop/)

**完成标志：**先看最终的 `stop_complete` 或 `restart_complete`。重启后再打开 [Friday](http://127.0.0.1:8740/)，按第 3 节检查自己的家庭来源、开关和画面。`ready` 表示配置的服务检查通过，不等于手势准确率、设备实际动作或摄像头画面已经完成现场验收。

新版初始化生成的配置会额外检查：当前启用的手势规则所绑定的设备，是否仍在允许控制范围内，且有正常、未过期的设备状态。设备仅出现在列表里不能通过这项检查；HA 返回“不可用”时，会继续等待，超时后报告未就绪。已经暂停的互动会保留暂停状态。完整部署维护者也应在 Friday 的 `ready` 配置中启用 `verify_saved_gestures: true`。

基础源码默认入口仍可能打开“示例家庭”。这时到“连接”读取已授权家庭；脚本保留数据，但不会把基础示例入口替换为完整视觉部署入口。

![重启后可进入连接页核对家庭来源及可选摄像头接入；示例截图不代表自己的账号状态](docs/assets/screenshots/friday-settings.jpg)

#### 脚本报错时怎么办

| 错误片段 | 处理方法 |
| --- | --- |
| `config_already_exists` | 已有配置不会被覆盖；直接使用原配置，不反复初始化 |
| `pid_identity_mismatch` / `service_pid_identity_mismatch` | PID 记录与预期服务不符；先查看状态，请维护者核对，不随意结束进程 |
| `port_in_use` / `port_still_in_use` | 同一端口还有服务；若原来在另一个终端前台启动，回到原终端按 Control+C，再使用本套入口 |
| `descendants_still_running` / `cleanup_pending` | 收尾或恢复尚未完成；保留依赖，等待后重试停止；不要跳到重新启动 |
| `status_unavailable` / `command_timeout` | 检查 Docker 连接、sudo 有效期、对应服务和本机私有日志，不把状态未知当作已停止 |
| `start_not_ready` / `not_ready` | 查看绑定设备在 HA 中是否为“不可用”，按第 3 节恢复集成连接后再核对；服务进程存在并不代表设备可用 |
| `executable_missing` / `cwd_missing` | 原运行环境被移动或缺失；核对路径和所用 Python，不重建一套空环境替代 |
| `another_lifecycle_command_is_running` | 另一条启停命令仍在执行；等待结束，不同时双击多份脚本 |

查看当前服务状态：

```sh
"$HOME/friday-home/Friday/.venv/bin/python" friday-services.py status --config "$PWD/services.local.json"
```

完整部署的 macOS 交付包可直接使用“查看服务状态.command”。状态页可能显示某些项目已停、某些仍运行；失败后的实际状态以逐项输出为准。

#### 尚未使用管理脚本时

基础 Web 仍可在安装目录前台启动 `./bin/home serve`，回到该终端按 Control+C 停止。第一次改用管理脚本前，先停止原前台服务；脚本不会凭端口接管已有进程。

HA 仍可使用原 Compose 参数执行 `stop`，并保留数据。Docker / Colima 宿主默认不由通用停止脚本关闭；若它还承载其他容器，按那些服务自己的维护要求处理。安装依赖不等于配置了开机自启动。

Miloco / OpenClaw 可能使用各自的后台服务。检查：

```sh
miloco-cli service status
openclaw gateway status
```

它们启动成功不代表 Friday 也已经启动。未登记到服务清单的组件继续使用自己的正式维护入口。

### 2. 记住几个入口

| 地址 / 位置 | 含义 |
| --- | --- |
| `http://127.0.0.1:8740/` | 当前电脑上的 Friday，或已建立转发的 Linux 服务 |
| `http://127.0.0.1:8123/` | 当前电脑可访问的 HA 入口 |
| `http://127.0.0.1:1810/` | Miloco 默认本机页面，以实际安装输出为准 |
| Friday 的“查看识别” | 通过已配置入口查看视觉预览，不需要公开查看密钥 |

手机、浏览器电脑、Linux 服务器和虚拟机各自有自己的 127.0.0.1。更换电脑访问时先配置相应入口或转发，不把同一地址当成自动共享。

### 3. 重启后检查什么

1. 依次确认容器主机、HA、需要的 Miloco 和 Friday 是否运行。
2. 看 Friday 顶部是“示例家庭”还是自己的真实来源。
3. 基础源码入口可能从示例启动，已有授权时重新读取家庭；不要因为来源未激活就删除账号。
4. 核对目标设备状态、控制范围、摄像头感知与手势总开关。
5. 验证部署版本提供的恢复机制后，再安排自启动。

用户手册里的截图或一次历史动作成功，不代表当前重启后的全部设备已经验收。

#### 重启后有手势记录，设备却没动

如果“最近的手势响应”已有记录，却显示“操作未完成”，先检查该设备在 HA 中是否为“不可用”。这时规则可能已经识别到动作，但设备状态不满足执行条件，Friday 会拒绝发送指令；重新添加规则不能恢复上游设备连接。

1. 打开 HA，在目标设备页确认当前状态。
2. 小米设备集中变为“不可用”时，检查 HA 的 Xiaomi Home 集成连接与系统日志。
3. 网络恢复后，可在 HA“设置 → 设备与服务 → Xiaomi Home”的菜单中重新加载原集成。这会重新连接现有集成，账号和设备选择仍沿用原配置。[HA 官方重新加载说明](https://www.home-assistant.io/actions/homeassistant.reload_config_entry/)
4. 等绑定设备恢复正常状态，再回到 Friday 刷新，做一次已配置的动作，同时核对页面回执和设备实际效果。

重新加载后仍不可用，继续检查 HA 所在主机访问小米服务的网络，以及集成是否明确提示重新认证。保留现有规则和授权，不把反复重建家庭当作排障方法。

#### 已有 Xiaomi Home 怎样升级

这是一次依赖维护，日常重启不用重复执行。旧版 v0.4.3 在云设备刷新遇到网络异常后，可能停止重试；官方在 [v0.4.6](https://github.com/XiaoMi/ha_xiaomi_home/releases/tag/v0.4.6)修复了这条异常路径，本手册现在固定的 [v0.5.0](https://github.com/XiaoMi/ha_xiaomi_home/releases/tag/v0.5.0)包含该修复。升级能补上恢复逻辑，仍需确认自己的网络及目标设备可用。

下面适用于**本教程目录中的 HA Container**；其他 HA 安装方式使用各自的更新与备份入口。先在 Friday 暂停互动，按 [HA 章节下载安装工具](#guide-getting-started-installation-home-assistant)下载并校验更新工具，已有集成不要执行“首次安装集成”命令。

**第 1 步：在 HA 仍运行时记录原容器，并提前下载集成。** 在同一个终端继续操作，保留变量。macOS / 无需 sudo 的 Docker 执行：

```sh
cd "$HOME/friday-home/Friday"
friday_ha_container="$(docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env ps --quiet homeassistant)"
test -n "$friday_ha_container"
```

Linux 按本手册使用 sudo 时，改用：

```sh
cd "$HOME/friday-home/Friday"
sudo -v
friday_ha_container="$(sudo docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env ps --quiet homeassistant)"
test -n "$friday_ha_container"
```

两种方式接着执行：

```sh
.venv/bin/python "$HOME/friday-home/service-tools/setup-dependencies.py" xiaomi-home-source --project "$PWD"
```

**应看到：**`downloaded: true`、`version: v0.5.0`、`installed: false`。此步没有替换运行中的集成。变量为空或出现错误时，先核对自己的 Docker 连接和原容器，不新建另一台 HA。

**第 2 步：正常停止同一套服务。** 使用本章已经配置的停止入口；完整部署使用自己交付包中的入口，基础部署可执行：

```sh
FRIDAY_PYTHON="$HOME/friday-home/Friday/.venv/bin/python" "$HOME/friday-home/service-tools/stop-friday.sh"
```

**应看到：**最终 `stop_complete`，包括这台 HA 已停止。只停 Friday 没有停 HA 时，升级工具会拒绝继续。

如果服务清单只登记了 Friday，仍需停止第 1 步记录的原 HA 容器。macOS / 无需 sudo 的 Docker 执行：

```sh
docker stop --timeout -1 "$friday_ha_container"
```

Linux 需要 sudo 时执行：

```sh
sudo docker stop --timeout -1 "$friday_ha_container"
```

等待命令正常返回；这里不删除容器或数据。稍后也需用原启动入口先启动这台 HA，再启动 Friday。

**第 3 步：保存完整 HA 备份。** 回到 Friday 目录，先创建只有自己可访问的备份目录：

```sh
cd "$HOME/friday-home/Friday"
umask 077
friday_backup_dir="$HOME/friday-home/backups/xiaomi-home-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 -p "$friday_backup_dir"
```

macOS / 当前账号可读取配置的用户执行：

```sh
tar -czf "$friday_backup_dir/ha-config.tgz" -C data/deployment homeassistant
```

Linux 配置由容器 root 持有时执行：

```sh
sudo tar -czf "$friday_backup_dir/ha-config.tgz" -C data/deployment homeassistant
sudo chmod 600 "$friday_backup_dir/ha-config.tgz"
```

**应看到：**命令成功退出，目录中生成 `ha-config.tgz`；任何读取失败都先解决再继续。备份包含 `.storage` 中的账号及注册表，也包含凭据，只保存在自己的私有存储。另按原部署备份 Friday 私有配置目录中的规则、控制范围及来源记录，保留当前暂停设置。

**第 4 步：替换已停止实例的集成。** macOS / 无需 sudo 的 Docker 执行：

```sh
.venv/bin/python "$HOME/friday-home/service-tools/setup-dependencies.py" xiaomi-home-upgrade \
  --project "$PWD" --ha-container "$friday_ha_container"
```

Linux 需要 sudo 管理 Docker 时执行：

```sh
sudo -v
.venv/bin/python "$HOME/friday-home/service-tools/setup-dependencies.py" xiaomi-home-upgrade \
  --project "$PWD" --ha-container "$friday_ha_container" --docker-sudo
```

**应看到：**`installed: true`、`version: v0.5.0`、`configuration_retained: true`、`services_started: false`。工具核对固定提交、原容器停止状态及其 `/config` 目录，仅替换集成文件，旧组件保存在 `data/deployment/integration-backups/`，沿用原账号连接和设备选择。检查不通过会拒绝更新；不要跳过检查强行覆盖。

**第 5 步：上线并核对，再恢复互动。** 使用自己的重新启动入口。基础部署可执行：

```sh
FRIDAY_PYTHON="$HOME/friday-home/Friday/.venv/bin/python" "$HOME/friday-home/service-tools/restart-friday.sh"
```

确认 HA 中 Xiaomi Home 已加载、原目标设备状态正常，Friday 的家庭来源、原规则和允许控制范围一致；需要摄像头的部署还要确认实时识别恢复。保持暂停的规则不会被脚本自动打开，完成检查后自行恢复互动，并观察一次页面回执与实物动作。无需重新给每台设备登录授权。

升级后若需回滚，由维护者先停同一套服务，再恢复第 3 步的**完整 HA 备份**和相应 Friday 配置。新版可能迁移注册表，仅换回旧集成文件不能代替完整恢复。安装工具能撤回文件替换失败，不能替你判断上线后的全部设备效果。

#### 脚本已验证的范围

2026-10-31 已核对：macOS 实际完整部署的正常停止、重复停止、重新启动和配置保留；通用基础源码入口的初始化、运行中重启及停止；macOS 与隔离 Linux 环境各 15 项进程和错误路径检查。隔离检查包括端口冲突、PID 不符、退出超时、子进程收尾、并发执行、容器主机准备顺序，以及绑定设备不可用、状态过期或控制范围缺失时不能被判为就绪。

现场曾出现“HA 页面可访问、设备列表存在，但小米设备状态不可用”的情况；重新加载原 Xiaomi Home 集成后恢复，由使用者再次完成手势与窗帘实体验收。因此新增了绑定设备状态检查，进程检查与配置保留不再作为互动可用的全部依据。

2026-10-31 又完成 v0.4.3 → v0.5.0 的隔离迁移预演及 macOS 实际停机、备份、升级和上线。原实体标识与设备关联、手势规则、控制范围和摄像头配置保持一致，升级前正常的目标状态已恢复；新版上线后的实物动作由使用者另行确认。安装器的离线替换、运行中拒绝升级、来源核对和失败恢复测试，以及相关发布输入测试共 28 项通过。

Linux 检查使用临时容器与合成服务，不代表全新 Linux 系统、所有 HA 安装方式或 Linux 本地视觉已经验收。通用脚本也不替你创建、迁移或重新授权外部服务。

### 4. 备份自己的配置与数据

备份前先停止对应写入服务：Friday 正常退出，HA 使用 Compose `stop`；Miloco、OpenClaw 按各自官方维护方式停止或做一致性备份。不要把运行中的数据库直接当作可靠备份。

在个人备份目录保存 Friday 的 `data/`：

```sh
mkdir -p "$HOME/friday-home/backups"
friday_backup="$HOME/friday-home/backups/friday-data-$(date +%Y%m%d-%H%M%S).tgz"
umask 077
```

macOS：

```sh
tar -czf "$friday_backup" -C "$HOME/friday-home/Friday" data
chmod 600 "$friday_backup"
```

Linux：HA 配置可能由容器账号拥有，需要权限读取时使用：

```sh
sudo tar -czf "$friday_backup" -C "$HOME/friday-home/Friday" data
sudo chown "$(id -u):$(id -g)" "$friday_backup"
chmod 600 "$friday_backup"
```

**应看到：**备份文件成功生成，没有读取失败。`data/` 可能包含账号授权、HA 配置、规则、模型和视觉运行环境，文件可能较大，保存在自己的私有备份位置，不上传到文档仓库。Miloco / OpenClaw 安装器使用的外部状态目录另按其官方说明备份。

还需记录源码提交、依赖锁文件、所用 extras、模型来源与摘要、启动入口及路径。恢复时先保留当前数据，在停止状态下核对备份和版本，再恢复；不把覆盖正在运行的目录当作恢复步骤。

### 5. 更新时保留哪些环境

| 环境 | 日常确认方式 | 更新时注意 |
| --- | --- | --- |
| Web `.venv` | `.venv/bin/python --version` | 使用对应 `uv.lock` 和原先选择的 extras |
| 视觉 `data/embodied/runtime` | 使用该目录自己的 Python | SDK、模型和原生程序单独核对 |
| Miloco 安装环境 | 安装器及 `miloco-cli service status` | 不用 Friday 的 uv sync 替它升级 |
| 可选 ARL | 按自己的 ARL 部署说明检查 | 本地额外安装的 SDK 不一定在 Friday 锁文件中 |

更新前运行 `git status --short` 和 `git rev-parse HEAD`，备份后选择目标版本再切换。不要用清理源码目录的命令清掉私有数据。`uv sync` 会按选择的依赖集合同步环境；重新安装时保留所需 extras，并重新核对另外安装的 SDK。

### 6. 可选：准备保护回看的媒体工具

macOS 在 Homebrew 支持的系统上执行 `brew install ffmpeg`；Ubuntu / Debian 执行 `sudo apt-get install ffmpeg`。然后检查：

```sh
ffmpeg -version
ffprobe -version
```

**应看到：**两项都有版本输出。只有 PyAV 不代表所有录像检查工具都已齐全。后台或桌面进程需要能定位受信的媒体程序；终端的 PATH 与桌面启动环境可能不同，应在所用部署入口配置工具路径。

再安装所需依赖，并保留此前已经使用的 extras：

```sh
cd "$HOME/friday-home/Friday"
uv sync --locked --python 3.12 --no-dev --extra nas-connection --extra privacy-playback --extra privacy-model
```

上面的命令展示回看所需集合；若同一 Web 环境还需要其他 extras，一并写在这次同步命令中。之后配置自己的 NAS 或录像来源，按[保护录像回看](#guide-guides-recordings)验证。模型权重和真实录像来源不由此命令自动生成。

### 7. 按症状排查安装

| 现象 | 先检查 |
| --- | --- |
| 命令找不到 | 当前终端 PATH、工具是否安装、是否进入正确目录 |
| Python 版本不符 | 使用 `.venv/bin/python` 或指定的 uv Python，不看另一个环境的版本 |
| 下载 / 镜像拉取失败 | 包源、证书、系统时间；Mac 还需检查虚拟机内的 DNS 和代理 |
| HA 容器运行但网页打不开 | 8123、端口转发、容器日志及正确 Docker context |
| 小米确认授权后出错 | 浏览器电脑能否通过回调主机名访问正确 HA，见[回调处理](#guide-getting-started-installation-home-assistant) |
| HA 有设备，Friday 仍是示例 | Friday 当前来源是否已连接并读取；HA 登录与来源激活分别检查 |
| 设备可见但无可选动作 | 首次控制范围、目标实体能力和已有范围是否暂停 |
| Miloco 有视频，Friday 尚未配置 | 独立视觉 Python、SDK、原生程序、模型、私有注册和后台入口 |
| 查看识别点不开 | 查看地址、服务监听、私有查看配置与部署版本是否匹配 |
| 画面或骨架可见但规则不触发 | 保存卡片、目标、使用范围、总开关、操作者与识别条件 |
| 重启后又未配置 | 运行目录是否一致，是否用了不同的 Python 或启动入口 |
| ffprobe 在终端可用但回看报错 | Friday 实际进程的工具定位和文件权限 |

### 8. 给维护者提供什么

提供系统与芯片、源码提交、工具版本、出错阶段、错误码，以及不含私人信息的界面状态。诊断导出使用产品提供的脱敏入口，并先在本机检查内容。

密码、Token、授权码、完整查看链接、家庭导出和原始视频不放进聊天或公开 issue。可继续查[常见问题](#guide-troubleshooting-faq)或[按现象排查](#guide-troubleshooting-common-errors)。

<a id="guide-getting-started-quick-start"></a>

## 7. 第一次打开 Friday

完成后，你能确认自己打开了正确的服务、看懂设备来源，并找到日常操作入口。

**开始前：**Friday 已经安装并启动。全新电脑先按[从零安装](#guide-getting-started-installation)选择 macOS 或 Linux 路线，再回到本节。

### 1. 打开本机页面

在部署 Friday 的电脑上打开 [Friday 本地控制台](http://127.0.0.1:8740/)。网页打不开时，先按[启动与维护](#guide-getting-started-installation-maintenance)运行服务，再刷新页面。Linux 远程部署先建立对应的 SSH 转发。

`127.0.0.1` 表示“当前这台电脑”。把它复制到手机上，不会自动访问电脑上的 Friday。

### 2. 看顶部家庭来源

顶部显示“示例家庭”时，先阅读演示，不要把卡片数量当作你家实际设备数量。“家庭已连接 · 只读”可以查看信息；能够操作哪些设备仍由已配置的控制范围决定。

![新版首页，未导入户型时保留空状态](docs/assets/screenshots/friday-home.jpg)

### 3. 打开设备页

点击“设备”，按房间或设备类型筛选。卡片的读数与按钮分别表达状态和可用操作；“暂时不可用”不是“已经关闭”。详见[查看与操作设备](#guide-guides-devices)。

### 4. 需要自己的家庭时再连接

打开“连接”，按“连接 Home Assistant → 让 Friday 读取你的家”完成必要步骤。摄像头与互动是可选项，可以稍后配置。

### 5. 确认你已完成

你能够重新打开页面、分清示例与真实来源，并找到设备页，就完成了本节。接下来按[连接自己的家](#guide-getting-started-connect-home)或[第一条手势控制](#guide-tutorials-first-gesture)继续。

**如果卡住：**网页打不开，先查[启动与连接问题](#guide-troubleshooting-common-errors)，不用先删除账号或重装。

<a id="guide-getting-started-connect-home"></a>

## 8. 连接自己的家

把已经接入 Home Assistant 的家庭设备显示到 Friday。连接过程先读取房间和设备，不会替你执行开关动作。

**开始前：**你已有可打开的 Home Assistant，并已在里面添加所需设备。没有服务时，先按[安装 HA 与小米接入](#guide-getting-started-installation-home-assistant)准备；Mac 和 Linux 的容器环境分别在安装章节说明。

### 先分清三个位置

| 在哪里操作 | 负责什么 |
| --- | --- |
| Home Assistant | 接入设备和集成，管理真实家庭清单 |
| HA 里的 Xiaomi Home 集成 | 登录小米账号，选择家庭与设备 |
| Friday 的连接页 | 授权 Friday 读取 HA，并查看当前连接情况 |

**XiaoMi/ha_xiaomi_home 装在 HA 内部，是集成，不是另一套需要独立启动的服务。** Miloco 可用于其摄像头与智能功能，但不是 HA 小米登录的前置条件。详见[各程序的分工](#guide-explanation-components)。

### 1. 先在 HA 接入小米设备

在 HA 的“设置 → 设备与服务 → 添加集成”进入 Xiaomi Home，按官方页面完成区域、登录、家庭和设备选择。密码、验证码和授权结果只填在对应页面。

完成后，在 HA 集成页核对是否已经出现目标设备。一个物理设备可能对应多个状态项目，设备数与实体数不必相同。

### 2. 在 Friday 查找并连接

打开“连接”，点击“查找并连接”。找到多个地址时选自己的 HA；未找到时点击“填写地址”，填写浏览器可以打开的完整 HA 地址。

![新版家庭连接向导，摄像头明确标为可选](docs/assets/screenshots/friday-settings.jpg)

### 3. 完成登录，再读取家庭

在 HA 官方登录页完成授权，返回 Friday 后点击“连接并读取设备”。看到“家庭已连接”及自己的房间、设备后，读取接入完成。

服务离线时，先检查地址和服务状态再重试。不要反复删除已有授权，也不要把授权结果复制到聊天或文档仓库。

### 4. 分别检查控制和摄像头

“只读”时仍可查看设备。首次开放设备操作范围需要本机配置；这不等于每次都要逐台登录。现有范围可以暂停或恢复，新设备不会因被发现就自动获得控制权。

摄像头接入、画面识别与设备控制需要分别准备。完成读取后，可继续[设备操作](#guide-guides-devices)或[摄像头与识别](#guide-guides-cameras)。

**完成标准：**Friday 显示家庭已连接，能在设备页找到自己的目标。**有设备但按钮不可用：**查[只读与权限](#guide-troubleshooting-faq)。

<a id="guide-guides-devices"></a>

## 9. 查看与操作设备

按房间找到设备，分清当前状态与可用操作，再使用设备专属控件。

### 先找设备，再看状态

点击“设备”，选择房间、类型，或在“搜索设备”输入名称。新版会保留只读及暂时不可用的设备，不再因为没有控制按钮就隐藏整台设备。

![新版设备列表保留示例中的四台设备](docs/assets/screenshots/friday-devices.jpg)

“我的家”侧重家庭空间与房间入口；需要完整卡片列表时点“打开设备”或左侧“设备”。没有导入自己的户型时，空间区域留空，未定位设备仍可在列表中使用。

### 使用对应控件

| 设备类型 | 常见控件 | 操作前看什么 |
| --- | --- | --- |
| 灯 | 开关、亮度，受支持时可调色温 | 是目标房间的目标灯；哪些调节项已开放 |
| 窗帘 | 打开、关闭、停止、开合位置 | 当前开合程度与电机支持范围 |
| 空调 | 工作模式、设定温度，受支持时有风速 | 当前室温与设定温度不是同一个数 |
| 风扇 | 开关及受支持的风速 | 设备在线，当前动作可用 |
| 摄像头 | 镜头状态与查看画面 | 查看画面和主动打开镜头的含义不同 |

点击卡片名称可展开设备详情。具体出现哪些控件，由设备能力与本机控制范围共同决定；不能因为新版增加了某种控件，就认为所有设备已获得新权限。

### 核对操作结果

选择模式、点击开关或调节按钮可能直接执行已授权操作。先确认目标，再操作一次，观察页面提示和设备实际变化。

“暂时不可用”时先检查设备连接，不要把它当成“关闭”。传感器读数是设备报告；插座内部温度和空调回风温度不自动等于房间室温。

**完成标准：**找到正确设备，页面报告与实际效果一致。设备列表为空或按钮灰色，见[常见问题](#guide-troubleshooting-faq)。

<a id="guide-guides-cameras"></a>

## 10. 查看摄像头与识别

先确认镜头状态，再按需要查看普通画面或人体、手部识别结果。

### 看画面

1. 打开“摄像头”，查看目标镜头的状态。
2. 镜头已经打开时，点击“查看画面”。
3. 不再观看时关闭预览；这与暂停后台感知是两件事。

![摄像头页的镜头列表与后台感知开关，隔离示例未连接摄像头](docs/assets/screenshots/friday-cameras.jpg)

镜头在米家里关闭后，Friday 的自动重连不会替你强行打开它。需要画面时，由你在米家或摄像头的明确开关入口主动打开。

### 看人体与手部识别

展开“人物与手势检查”，在“识别调试”点击“查看识别”。时间应持续更新；骨架或手部提示只表示检测结果，设备有没有执行要去互动页核对。

“电视未连接”只说明没有电视端，不妨碍电脑上的实时查看。位置尚未标定主要影响空间指向和座位，不要求为了普通手势先填一套猜测户型。

### 分清三个开关

| 你想暂停什么 | 应在哪里操作 | 仍会发生什么 |
| --- | --- | --- |
| 只停止手势触发设备 | 互动控制 → 暂停手势控制 | 后台识别可以继续 |
| 停止 Friday 后台感知 | 摄像头或连接页 → 暂停摄像头感知 | 暂停状态重启后保留；按需手动查看选定镜头不代表恢复全部后台识别 |
| 让摄像头设备本身关闭镜头 | 米家镜头开关或明确的设备开关 | 以设备自己的录像和镜头设置为准 |

麦克风、语音回复和云台接管有独立配置。接通视频不表示这些功能也已开启。

**如果 Miloco 有画面而 Friday 未配置：**按[摄像头与本地识别准备](#guide-getting-started-installation-camera)分别核对 SDK、独立环境、原生程序、模型、私有注册和后台入口。当前原生识别依赖 macOS Apple Vision；Linux 的 Miloco 视频成功不表示同一套手势链路已可运行。

完成后可继续[第一条手势控制](#guide-tutorials-first-gesture)。

<a id="guide-tutorials-first-gesture"></a>

## 11. 完成第一条手势控制

把一个身体动作绑定到一台已授权设备，并分别核对识别、响应记录和设备实际效果。

**开始前：**Friday 摄像头和本地识别已准备好；目标设备在 Friday 中允许控制；你了解本次绑定会执行什么动作。

### 1. 先看到实时识别

打开“摄像头”，展开“人物与手势检查”，点击“查看识别”。确认时间持续变化，人体或手部提示能够跟随你。电视未连接不影响本机查看。

![摄像头页面示例；示例服务没有连接任何真实镜头](docs/assets/screenshots/friday-cameras.jpg)

如果这里只显示未配置，先完成[摄像头接入](#guide-guides-cameras)，反复做动作不能补齐识别环境。

### 2. 选手势控制，而不是语音页

打开“互动控制”，切换到 **手势控制**。默认的“对镜头说话”是语音功能，打开页面不代表语音已经开启。

### 3. 保存一条完整规则

依次选择“使用范围 → 控制设备 → 动作 → 执行动作”。例如：在目标房间，双臂合上时关闭指定窗帘。核对后点击“保存手势控制”，再到“已设置的控制”确认规则已出现。

![新版手势配置表单，示例环境没有真实控制目标](docs/assets/screenshots/friday-interaction.jpg)

上方表单的默认选项不会自动修改已经保存的规则。修改旧规则要点击那条规则的“编辑”，再“保存修改”。

### 4. 开启总开关并完成动作

确认该规则的开关已启用，再点击“启用手势控制”。按钮显示“暂停手势控制”表示总开关正在运行。

站在镜头能清楚识别身体的位置，先保持稳定，再按所选动作说明完成连续变化。例如双臂合上应先张开，再向胸前合拢并短暂停留；一直保持合拢不等于新的动作。多人入镜时，先比 OK 选定操作者，再放下手开始。

### 5. 看记录，再看设备

展开“最近的手势响应”。出现记录后，再观察目标设备是否实际执行。“指令已发送”不能代替现场确认；设备本来已在目标状态，也可能没有新的可见动作。

### 6. 暂时不用时暂停

点击“暂停手势控制”会保留规则，阻止后续手势触发。它不会撤回已经发出的动作；关闭网页也不会自动停掉后台。

**完成标准：**规则已保存、总开关运行、最近响应出现对应目标，并且你确认设备实际效果。任一步缺失，按[手势不触发排查](#guide-troubleshooting-common-errors)逐层检查。

<a id="guide-guides-interactions"></a>

## 12. 管理互动控制规则

在同一页选择语音、手势或指向方式，修改已有规则，而不必删除后重建。

### 三种方式分别做什么

| 页签 | 用途 | 另外需要的准备 |
| --- | --- | --- |
| 对镜头说话 | 用设备和房间名称表达操作 | 所选镜头的声音输入、识别与语音处理已配置 |
| 手势控制 | 把明确动作绑定到设备 | 画面、本地识别与目标控制已配置 |
| 指向设备 | 在镜头画面标记目标，再按指向控制 | 镜头位置、设备点位和相应识别已核对 |

![互动页默认打开语音说明，按钮仍显示开启，表示尚未启用](docs/assets/screenshots/friday-interaction-voice.jpg)

只想做手势时，直接切到“手势控制”。本地手势不要求你先开启语音。

### 新建、修改和暂停

1. 选择使用范围；有多房间镜头时核对自己选择的房间或全屋范围。
2. 选择设备、动作和执行动作，检查表单中的完整描述，再保存。
3. 修改旧规则时点它的“编辑”，检查回填内容，点击“保存修改”；不想改就“取消编辑”。
4. 单条规则的开关只影响这一条；页顶手势总开关暂停时，已启用的规则也不会触发。

![新版手势控制表单](docs/assets/screenshots/friday-interaction.jpg)

移除规则后，页面提供撤销入口时可立即撤销。编辑草稿、设备失效提示和修复入口用于减少误改；最终以已保存卡片为准。重新发现同名设备不等于自动替换原来的目标。

### 指向设备前先核对点位

在“指向设备”选择目标，按当前画面标记位置或填写百分比。镜头移动后需要重新核对，不能把画面坐标当作永久房间坐标。

![指向设备的配置入口，尚未保存点位](docs/assets/screenshots/friday-interaction-pointing.jpg)

**完成标准：**保存卡片中的范围、手势、目标和动作都正确，并按[第一条手势控制](#guide-tutorials-first-gesture)完成现场验证。设备列表为空见[权限问题](#guide-troubleshooting-faq)。

<a id="guide-guides-automations"></a>

## 13. 管理场景与自动化

先确认规则来源，再决定运行一次、修改 Friday 自有规则，还是回到原平台管理。

### 三个分类

| 分类 | 你能做什么 |
| --- | --- |
| 一键场景 | 读取米家已有手动场景，核对后运行一次 |
| 自动运行 | 查看、暂停、编辑 Friday 自有自动化 |
| 其他平台的规则 | 查看外部来源及配置范围；不等于直接编辑上游规则 |

![自动化页的三个分类；示例环境没有小米账号，因此场景无法读取](docs/assets/screenshots/friday-automations.jpg)

### 运行米家一键场景

选择场景后，先核对确认框中的名称和涉及设备数量，再决定是否运行。场景按米家保存的内容执行，可能同时操作多个设备。

**米家场景是独立执行入口，其范围与 Friday 设备页已开放的逐台控制范围不同。** 想只操作指定设备时，使用设备页或对应手势规则；不要把场景设备数当作已逐台验证的控制范围。“已发送”后仍要核对现场效果。

### 新建 Friday 自动化

1. 点击“新建自动化”，填写能说明用途的名称。
2. 选择触发设备与状态变化，再添加需要执行的设备动作。
3. 需要时设置附加条件。
4. 点击“核对并保存”，检查预览；确认无误后再“确认保存并启用”。

![自动化编辑表单，示例没有提交保存，也没有执行动作](docs/assets/screenshots/friday-automation-editor.jpg)

保存规则与立即操作设备不同，但启用后，后续条件满足就可能执行。已有规则可以“编辑”或暂停；“执行一次”是主动操作入口，不必等触发条件。

**完成标准：**自有规则出现在“自动运行”，来源与启用状态正确。外部规则需要重建或变更时，先处理原平台规则，避免保留两套相似联动。

<a id="guide-guides-recordings"></a>

## 14. 连接录像并保护回看

从你已配置的录像目录查找片段，播放本机生成的保护预览，并核对时间范围。

**开始前：**NAS 或录像来源已由你连接，目标目录允许读取。摄像头直播正常不代表已接入历史录像。

### 1. 先检查来源

打开“回看”。未能读取时，进入“登录与存储设置”检查网络、已保存登录和允许目录；原来已配置的连接会尝试恢复，不需要每次重复填写。

![没有配置真实 NAS 的示例页面](docs/assets/screenshots/friday-activity.jpg)

### 2. 选择镜头和日期

按录像来源、日期或“最新录像”找到片段，再点击播放。文件名时间、设备时钟和实际事件时间不一定完全相同，需要先核对录像来源。

### 3. 看懂保护预览

默认播放短时的整帧马赛克预览，保留原片。选择性遮挡需要另外安装和配置本机模型；未配置时不能承诺只遮住特定区域。生成保护预览失败时，不会自动改播未保护原片。

播放器默认静音。视觉遮挡并不清除原音轨中的个人信息，有声音的录像需要你按场景决定是否取消静音。

![保护预览演示：只有 FFmpeg 生成的合成测试图，无真实家庭录像](docs/assets/screenshots/friday-protected-playback.jpg)

本图使用独立示例服务中的 **45 秒纯合成测试片**，用于演示播放器、保护状态和时间线，不代表真实 NAS 已连接或任何家庭录像已经验收。

### 4. 定位、继续播放与结束

可用时间线定位到片段内的位置。播放器按短片段准备后续内容，因此看到一个预览成功，不代表所有录像都已读取。来源变化或预览过期时，重新读取；结束查看后停止播放。

**完成标准：**能核对正确镜头、日期、时间范围，看到明确的保护状态，并成功定位到所需内容。没有录像、时间不符或准备失败时，见[回看问题](#guide-troubleshooting-common-errors)。

<a id="guide-guides-events"></a>

## 15. 查看家庭事件的来源

从设备状态变化查看已有记录、相关操作和录像引用，并分清“时间接近”与“原因已知”。

### 选择事件

1. 打开“回看”，展开“查看家庭事件”。
2. 选择房间、设备和时间范围，点击“刷新事件”。
3. 选择一条事件，查看“记录来源”“记录归属”“时间依据”和“物理效果”。

![合成门状态事件的实际详情，原因和时间依据不足时保持未知](docs/assets/screenshots/friday-event-evidence.jpg)

本图由独立示例服务明确注入一次模拟开门状态，不来自真实门锁、家人活动或家庭录像。

### 怎样理解为什么发生

来源明确记录的操作链、同组记录和仅仅时间相近的记录含义不同。页面显示“现有记录不能确定触发原因”时，不能据前后顺序推断某个手势或自动化造成了变化。

这里只展示本机保留的记录。外部平台规则和手动操作可能不可见；没有记录也不代表没有发生事件。

### 怎样查附近录像

只有摄像头、目录和事件时间范围能够可靠对应时，录像入口才有依据。时间未知或未核对时，先检查录像连接，不随意拼一个相近视频当作证据。

**完成标准：**你能说明这条记录来自哪里、哪些关联有依据、哪些仍未知。打开详情不会自动操作设备；继续看[保护回看](#guide-guides-recordings)。

<a id="guide-guides-people"></a>

## 16. 核对人物与待确认分组

把相似的匿名观察整理成可核对的候选组，再由你确认是否同一人、是否登记名字。

### 先核对，再登记

打开“人物”，查看实时人物、已登记人物和待确认组。绿色骨架或一次手势成功不表示已经完成姓名登记。

![新版人物目录为空的示例，展示待确认分组入口](docs/assets/screenshots/friday-people.jpg)

有候选照片时，逐张核对是否同一个人，再合并到同组、拆分错误观察，或归入已有家人。界面提供撤销时，可回退最近的整理操作；不要仅凭自动相似度就认定身份。

姓名登记用于资料整理与连续识别，不授予开门、账号访问或设备控制权限。没有登记人脸，也可在满足条件时使用单人动作控制；多人时按镜头提示选择操作者。

**完成标准：**照片和成员对应关系由你确认，错误分组已纠正。示例中没有人物资料，因此不能据截图认定人脸功能已完成现场验收。

<a id="guide-guides-safety"></a>

## 17. 查看智能预警与本机画面复核

分别检查监测、提醒和记录，不把一个开关当成整套能力已经准备好。

### 监测与语音提醒分别设置

打开“智能预警”，看清监测是否运行、语音提醒是否开启，以及播报音箱有没有选择。没有音箱时，不能因为存在提醒按钮就认为已经播报。

![智能预警与可选本机画面复核，示例保持暂停](docs/assets/screenshots/friday-safety.jpg)

预警记录用于核对疑似异常。界面已说明可能漏报或误报，记录与现场情况仍需由你检查。

### 本机画面复核是额外能力

新版提供可选的本机短画面复核，例如补充查看可见变化。看到“模型尚未安装”时，该项不能开启；它不由基础部署自动下载，也不是普通手势识别的必要步骤。

按页面说明确认本机资源、模型和使用范围后，再由维护人员准备。摄像头隐私暂停时，后台待处理画面会停止或清空。没有实际验证过的提醒效果，不计作已经通过。

**完成标准：**监测、提醒、输出设备和记录的状态都能分别说明。只想停止手势，使用互动页开关；想停全部后台感知，见[摄像头开关](#guide-guides-cameras)。

<a id="guide-guides-games"></a>

## 18. 使用游戏库

先检查识别与显示条件，再选择游戏和玩家。

页面提供林间滑雪、双人网球、动作闯关、运动闯关、座位指认与全屋互动等入口。每项需要的玩家人数和动作不同。

![游戏库示例，识别服务未配置时开始按钮不可用](docs/assets/screenshots/friday-games.jpg)

1. 先在摄像头页确认可用画面与识别。
2. 在游戏库选择游戏与镜头，按提示绑定玩家。
3. 确认显示位置，再开始；需要结束时使用游戏自己的结束入口。

电视是单独的显示端。没有电视不妨碍电脑查看识别，但不能因此认定电视投放已经接通。

**完成标准：**游戏画面、玩家识别与实际动作响应都正确。普通手势控制成功一次，并不能替代每种游戏的验收。

<a id="guide-guides-files"></a>

## 19. 找到家庭资料预览

新版将家庭资料放到实验功能中，用于搜索已索引的 NAS 资料和核对整理建议。

打开“连接 → 实验功能与调试 → 打开资料索引预览”。旧版左侧的“文件”不再是当前默认导航入口。

![家庭资料预览的四类操作与来源未就绪状态](docs/assets/screenshots/friday-files.jpg)

| 入口 | 用途 |
| --- | --- |
| 已索引资料 | 查看已经建立索引的资料 |
| 待提取 | 查看待补充提取的内容 |
| 搜索内容 | 在已有可用内容中搜索 |
| 整理建议 | 核对建议后再决定如何处理 |

来源未就绪时，先“设置资料来源”或“核对连接”。这不表示电脑中没有文件，也不表示 Friday 扫描了你的个人目录。

**完成标准：**你明确选择了资料来源，页面显示的索引范围和资料状态可核对。没有 NAS 或没有扫描时，不把空页面当作文件数量证明。

<a id="guide-guides-dialogue"></a>

## 20. 用文字预览模拟规则变更

在独立示例环境练习“先看差异、再批准、必要时恢复”，理解文字操作的范围。

**仅用于示例：**下面截图来自独立的示例家庭。不要为了照图练习，把已经连接真实家庭的服务改成模拟来源。

### 找到入口

打开“连接 → 实验功能与调试 → 文字指令调试”。旧版“对话”菜单已移动到这里。

### 1. 生成差异

输入“以后回家不开空调”，点击“发送”。检查保留的灯动作与移除的空调动作，以及本次预览的范围和有效期。

![模拟规则变更预览](docs/assets/screenshots/friday-habit-preview.jpg)

### 2. 批准这一份预览

在有效期内点击“批准变更”。示例返回“自有模拟规则配置已读取验证”，只证明示例规则配置完成，不证明实际空调已经关闭。

![模拟规则配置读取验证](docs/assets/screenshots/friday-habit-applied.jpg)

### 3. 需要时恢复

点击“恢复配置”，核对原模拟规则已恢复。配置回滚不能撤回此前已发生的设备动作。

![模拟配置恢复](docs/assets/screenshots/friday-habit-rollback.jpg)

不能识别的文字会要求更明确的命令。不要把文字输入框当作可以任意删改所有规则的通用助手；结构化的“查看依据”适合核对已有家庭记录。

**完成标准：**你能够读懂预览、批准范围和恢复结果，并分清模拟配置与真实设备效果。理解不同读数时，可继续[温度场景图解](#guide-reference-temperature-scenarios)。

<a id="guide-reference-navigation"></a>

## 21. 新版入口速查

按你要完成的任务找页面，避免沿用旧截图中的菜单名称。

| 你要做什么 | 新版入口 |
| --- | --- |
| 看家庭空间和房间 | 我的家 |
| 找完整设备卡片、开关与设定 | 设备 |
| 看镜头、暂停后台感知 | 摄像头 |
| 看骨架或手部识别 | 摄像头 → 人物与手势检查 → 查看识别 |
| 配置身体动作 | 互动控制 → 手势控制 |
| 使用声音输入 | 互动控制 → 对镜头说话 |
| 给画面中的设备标点位 | 互动控制 → 指向设备 |
| 看手势结果 | 互动控制 → 最近的手势响应 |
| 手动场景或自有自动化 | 自动化的三个分类 |
| 查历史录像与家庭事件 | 回看 |
| 登记或核对人物 | 人物 |
| 配置服务、账号与静音 | 连接 |
| 家庭资料预览 | 连接 → 实验功能与调试 → 打开资料索引预览 |
| 文字操作与结构化查询 | 连接 → 实验功能与调试 → 文字指令调试 |
| 系统状态和调试场景 | 开发工具 → 勾选显示调试 |

![实验功能的新位置](docs/assets/screenshots/friday-experimental-entry.jpg)

“对镜头说话”是互动页默认页签，不表示语音已经开启。只想使用动作绑定，切换到“手势控制”即可。

<a id="guide-reference-status"></a>

## 22. 读懂页面状态

同一设备可能同时有“读取正常”和“控制不可用”。先看状态描述的是哪件事。

| 页面文字 | 表示什么 | 接下来怎么做 |
| --- | --- | --- |
| 示例家庭 | 使用模拟数据 | 学习界面；不要当作自己的家庭 |
| 家庭已连接 | 已切到家庭来源 | 核对设备和当前控制范围 |
| 只读 | 当前只能查看，不能执行真实控制 | 如需控制，检查已有范围或首次配置 |
| 暂时不可用 | 当前条件不足以操作或确认状态 | 检查在线状态和连接，避免反复点击 |
| 识别运行 | 本地识别进程在处理画面 | 看提示是否跟随你，再检查规则 |
| 已启用（规则旁） | 这一条规则允许参与运行 | 仍需手势总开关开启 |
| 指令已发送 | 已产生或发送请求 | 观察实际设备，不直接认定完成 |
| 状态已更新 | 读回的设备报告符合目标 | 仍区分现场效果和设备报告 |
| 读数已过期 | 不能当作当前有效测量 | 等新测量或检查来源 |
| 暂不可确认 | 当前依据不足 | 不把它当作零、关闭或损坏结论 |

### 几个常见词

- **设备**：一台实际产品；它可以提供多个状态和操作。
- **实体或状态项目**：同一设备的一项能力，例如当前温度、设定温度或工作模式。
- **房间**：你在家庭平台里分配的位置，不一定等于设备测量所在位置。
- **规则**：何时、在什么条件下，对哪个设备做什么。
- **后台感知**：Friday 在后台接收画面并识别，不等于你正打开预览窗口。
- **保护预览**：为观看临时生成的保护画面，不是覆盖原录像。

更多实际例子见[温度场景图解](#guide-reference-temperature-scenarios)。

<a id="guide-reference-temperature-scenarios"></a>

## 23. 十五个温度质量场景

这些图来自独立、明确标为“示例家庭”的运行环境，用于学习读数含义。日常真实家庭无需切换来源或加载模拟场景。

### 怎样阅读

在示例环境打开“连接 → 实验功能与调试 → 文字指令调试”，房间选“客厅”，点击“只读查询”。同时看设备自身温度、房间室温、测量时间和质量说明。

读数来源位置不同，空调内部或插座内部的温度不自动代表房间室温。

### 01. 正常状态

温度计与空调都有有效测量，房间室温选择已配置的主来源，不能简单平均两种设备读数。

![场景 01：正常状态，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-baseline.jpg)

### 02. 相对校准演示

成对模拟样本用于说明校准过程；示例样本不证明你家的设备已经校准。

![场景 02：相对校准演示，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-calibration-training.jpg)

### 03. 主源过期，备用未校准

主温度计只返回旧记录，空调虽有读数但未通过相对校准，因此室温暂不可确认。

![场景 03：主源过期，备用未校准，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-stale-temperature.jpg)

### 04. 使用相对校准备源

备用来源符合当前校准条件，室温显示推算区间；这个区间不是绝对真值保证。

![场景 04：使用相对校准备源，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-calibrated-fallback.jpg)

### 05. 读数冻结

一个来源不变，独立来源持续变化时，冻结来源会暂时退出室温判断。

![场景 05：读数冻结，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-frozen-temperature.jpg)

### 06. 读数不一致

不同来源互相矛盾，系统保留无法确认的结论，不随意选一个数。

![场景 06：读数不一致，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-peer-disagreement.jpg)

### 07. 所有来源异常

没有可用依据时保持暂不可确认，而不是把旧数当作当前室温。

![场景 07：所有来源异常，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-all-sources-bad.jpg)

### 08. 连接恢复，观察不足

恢复连接不等于测量已经可信，还要等待足够的新测量和观察时间。

![场景 08：连接恢复，观察不足，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-recovered.jpg)

### 09. 暂缓切回主源

恢复期间继续使用已经可信的备用来源，避免在主备之间反复切换。

![场景 09：暂缓切回主源，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-recovery-hold.jpg)

### 10. 恢复后仍返回缓存

刷新旧记录不等于产生了新测量，不能据更新时间认定已经恢复。

![场景 10：恢复后仍返回缓存，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-cache-recovery.jpg)

### 11. 样本够，时间还不够

短时间内多个样本不能代替跨过完整观察期。

![场景 11：样本够，时间还不够，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-watch-window.jpg)

### 12. 电量读数过期

旧电量记录不能证明当前设备健康；温度仍有效与电量过期可以同时出现。

![场景 12：电量读数过期，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-battery-stale.jpg)

### 13. 空调模式不符

工作模式未知或不符合原校准条件时，不继续套用旧的室温推算。

![场景 13：空调模式不符，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-wrong-ac-mode.jpg)

### 14. 校准过期

校准范围或有效期已经失效，备用温度存在也不能继续当作合格室温。

![场景 14：校准过期，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-calibration-expired.jpg)

### 15. 连接中断

连通性不足时，需要重新核对状态，不能把上次测量当作现在仍有效。

![场景 15：连接中断，独立示例服务的实际查询页面](docs/assets/screenshots/friday-case-transport-gap.jpg)

遇到自己家庭的异常时，先看[页面状态](#guide-reference-status)与[按现象排查](#guide-troubleshooting-common-errors)。

<a id="guide-explanation-components"></a>

## 24. 这些程序分别做什么

Friday 是你日常打开的家庭界面。其他程序提供设备接入、摄像头或智能服务，各自需要自己的准备。

```mermaid
flowchart TB
  U[家庭用户] --> F[Friday：设备、互动、回看]
  F --> H[Home Assistant：设备和房间]
  H --> X[Xiaomi Home：安装在 HA 内的集成]
  X --> D[小米家庭设备]
  F --> V[Friday 本地视觉：人体和手势]
  V --> C[摄像头媒体连接与原生 SDK]
  M[Miloco：小米授权和摄像头智能服务] -. 按需配合 .-> C
  F -. 可选智能任务 .-> A[ARL：共享智能运行服务]
  F -. 配置后回看 .-> N[NAS：家庭录像]
```

### 为什么 Miloco 有画面，Friday 还可能没有识别

视频播放与人体、手部识别是两套准备。Friday 的视觉代码就在 Friday 仓库里，但运行时还需要本地依赖、模型、原生组件和自己的摄像头配置。

本地确定性手势不需要先配置 ARL 模型服务，也不需要先启用语音。Miloco 的画面理解、语音和云端模型是其他能力，不能因摄像头能播放就视为全部可用。

### 为什么设备数不相同

Miloco、HA 和 Friday 读取或展示的范围可能不同；一个设备还有多个状态项目。新版 Friday 会保留只读和暂不可用的设备；仍需看清统计的是物理设备、状态项目还是可控制目标。

### 为什么要区分连接和控制

账号接通先让设备可读取；控制范围还需要明确配置。规则保存后，还需要对应总开关、识别条件和设备连接都满足。它们分别显示，方便你判断卡在哪一步。

进一步了解项目之间的仓库关系，可查看[项目索引元仓库](https://github.com/lijunfeng722/project-index)。

<a id="guide-explanation-arl"></a>

## 25. 怎样看待 ARL 管理界面

ARL 为应用提供共享智能运行服务。日常家庭操作仍从 Friday 开始，不需要把 ARL 的所有页面都配置好，才使用本地手势。

### 各页看什么

| 页面 | 主要用途 | 不能直接据此认定什么 |
| --- | --- | --- |
| 运行概览 | 看后台是否可读、运行情况与基础状态 | 不能因此认定模型任务可执行 |
| 模型 | 看模型来源、连接与加载情况 | 有模型选项不表示已安装、已授权或正在调用 |
| 服务连接 | 查看日历、提醒、NAS 等独立服务能力 | 不表示已授予所有个人资料权限 |
| 应用接入 | 查看应用身份与接入状态 | 没有应用会话不能认定正式应用已经接通 |
| 性能、运行记录、诊断 | 查服务状态与问题线索 | 不替代家庭设备现场验收 |

![ARL 原生源码开发版的模型页，演示数据与受限按钮](docs/assets/screenshots/arl-demo-models.png)

本图保留 **2026-10-30** 的原生开发版演示界面；本轮没有升级 ARL 源码，Friday 的界面图则于 10 月 31 日重新采集。图中“源码候选、待授权”和灰色按钮表达的是开发版边界，不是已经加载模型。

### 为什么服务可读，界面仍待核对

后台可被读取，与模型来源、任务决策、应用会话及外部工具都准备好不同。Friday 的“连接”卡与“系统状态”也可能分别表达这些层次，按具体功能核对即可。

**完成标准：**能分清服务状态、模型状态与可执行任务。不需要为了让本地手势工作，开放日历、消息、模型或其他不相关服务。仓库关系见[项目索引](https://github.com/lijunfeng722/project-index)。

<a id="guide-releases-2026-10-31"></a>

## 26. 2026-10-31 新版使用变化

本页说明这版用户手册覆盖的重要界面与使用方式。功能可用性仍取决于你的部署、设备能力和已配置权限。

| 更新 | 对日常使用的影响 | 阅读 |
| --- | --- | --- |
| 分步连接向导 | 查找、登录、读取分别显示；摄像头可稍后设置 | [连接自己的家](#guide-getting-started-connect-home) |
| 设备专属控件与完整列表 | 按类型操作；只读和暂不可用设备也保留 | [查看设备](#guide-guides-devices) |
| 新版互动配置 | 三种方式分开；规则可编辑、暂停、移除和撤销 | [互动控制](#guide-guides-interactions) |
| 场景和自有规则管理 | 分清米家一键场景、Friday 自动运行与外部规则 | [自动化](#guide-guides-automations) |
| 保护录像回看 | 默认整帧保护、静音、时间线与分段准备 | [回看](#guide-guides-recordings) |
| 事件来源说明 | 分清已知操作链、时间接近和未知原因 | [家庭事件](#guide-guides-events) |
| 人物候选分组 | 核对、归组、拆分和撤销，仍由你确认身份 | [人物](#guide-guides-people) |
| 摄像头隐私与恢复 | 尊重镜头开关；后台感知暂停重启后保留 | [摄像头](#guide-guides-cameras) |
| 可选本机画面复核 | 缺少模型时明确不可开启，不自动下载 | [智能预警](#guide-guides-safety) |
| 预览功能入口收纳 | 旧“文件”“对话”移入连接页实验功能 | [入口速查](#guide-reference-navigation) |

### 这版文档怎样验证

主要入口、规则编辑界面、模拟规则预览与恢复、15 个温度质量场景，以及合成视频保护预览都通过本地运行的产品界面核对。合成测试不是每台真实设备的现场验证。

升级前一次真实手势的成功，也不代表新版全部设备、游戏、语音和智能预警均已验收。自己开始使用时，按任务指南分别确认结果。

### 维护与反馈

本手册由独立文档仓库维护。产品行为参考 [Friday 源码](https://github.com/Geeprox/Friday)，相关依赖见[元仓库索引](https://github.com/lijunfeng722/project-index)。反馈时说明手册页、产品版本与实际可见行为。

<a id="guide-troubleshooting-common-errors"></a>

## 27. 按现象排查

先定位卡住的环节，再处理对应设置；不要一次重装所有服务。

### 网页打不开

确认在部署服务的电脑上，地址和端口正确。先启动交付的环境，再刷新。关闭网页与停止后台不同，刷新不能启动已经停止的服务。

### 家庭连接失败

先在浏览器确认 HA 能正常打开，再回 Friday 核对地址。小米授权后，回原 HA 设置页看看是否已经进入家庭和设备选择。若没有，记录报错页面和时间，不必先删除已有集成。

### 设备或操作选项为空

先在 HA 确认设备已导入，再到 Friday 设备页找目标。若仍是只读，检查是否首次控制范围未配置，或已有操作被暂停。点击手势总开关不能替设备新增授权。

### Miloco 有画面，但 Friday 没有

检查 Friday 摄像头接入和本地识别环境。再看米家的镜头是否打开、设备是否在线。视频服务、识别环境和查看入口是不同环节。

### 手势不触发

按顺序检查：

1. 识别画面和时间持续更新。
2. 所需身体部位无遮挡，动作提示能跟随你。
3. 多人时已选定操作者。
4. 目标规则确实出现在“已设置的控制”，目标与设备动作正确。
5. 单条规则和手势总开关都已开启。
6. 完成连续动作，再看“最近的手势响应”，最后核对实际设备。

有骨架但没有记录，先检查识别和规则条件；有记录但设备没动，再检查目标、读回状态及现场。不要连续做动作催动可能仍在执行的设备。

### 录像不能播放

先分清“未连接录像来源”“没有找到文件”和“保护预览准备失败”。检查网络、来源目录、日期和设备时间；来源变更或预览过期后重新读取。不要为播放失败直接回退到未保护原片。

### ARL 待核对或按钮灰色

服务可以被读取，与模型、应用会话和工具能力全部就绪不同。本地手势可以独立运行，不要把 ARL 的所有可选能力当作手势前提。

### 提供什么信息便于协助

记录时间、页面、你的操作、可见提示和设备实际有没有变化。保留必要截图；账号密码、验证码和模型密钥只在对应服务页面填写。真实家庭画面只在你认可的范围内分享。

完整问答见[常见问题](#guide-troubleshooting-faq)。

<a id="guide-troubleshooting-faq"></a>

## 28. 常见问题

从使用者角度回答日常问题。需要按步骤定位时，先看[按现象排查](#guide-troubleshooting-common-errors)。

### Q01. 我每天应该打开哪个页面？

主要打开 Friday。添加集成或核对家庭清单时进入 Home Assistant；检查小米摄像头相关服务时再进入 Miloco，不必每天在三个页面重复登录。

### Q02. 网页打不开，第一步做什么？

确认在部署服务的电脑上，使用交付的启动入口启动环境，再打开 Friday。把本机地址复制到手机并不能访问电脑上的服务。

### Q03. 怎样判断是真实设备还是演示数据？

看顶部：“示例家庭”是模拟数据，“家庭已连接”是家庭来源。本文示例图中的英文设备不是自动发现的真实设备。

### Q04. 为什么几个页面的设备数量不同？

它们支持和展示的范围不同；同一物理设备还有多个状态项目。新版 Friday 会保留只读和暂不可用设备。核对时先确认统计的是设备、状态项目还是可控制目标。

### Q05. Xiaomi Home 要单独启动吗？

不用作为独立服务启动。它安装在 Home Assistant 内部，在 HA 的设备与服务里完成设置。Miloco 不是 HA 小米登录的前置条件。

### Q06. 小米授权后报错，需要重新安装吗？

先回原 HA 页面看看是否已经进入家庭和设备选择。仍未完成时，记录错误页面与时间再排查；不要先删除已有家庭或把授权结果发到聊天。

### Q07. 显示只读时能做什么？

可以查看已接入信息，不能从 Friday 发出真实设备控制。已有控制范围可暂停或恢复；首次开放范围需要在本机配置。

### Q08. 每次使用都要逐台设备重新授权吗？

日常不需要。已配置的范围会保留，你在规则里选择目标即可。新增设备不会因为被发现就自动取得控制权限。当前连接页可暂停或恢复已有范围；首次扩展仍需部署人员在本机设置，日常选设备不需要改代码。

### Q09. 规则里的设备列表为空怎么办？

先在设备页确认目标存在，再检查是否只读、操作是否暂停，以及该设备有没有支持的控制。启用手势总开关不会替设备增加权限。

### Q10. 选择了设备和手势，为什么没有规则？

还要选择执行动作并点击“保存手势控制”。以“已设置的控制”中的卡片为准，上方表单的临时选择不会自动保存。

### Q11. 怎样修改已经保存的规则？

在目标规则上点击“编辑”，核对回填的范围、动作、设备和执行动作，再点“保存修改”。没有打算改就“取消编辑”。

### Q12. 双臂打开可以绑定关闭窗帘吗？

可以。身体动作与设备动作由你绑定，核对完整描述即可，不能只看动作名称猜测设备会做什么。

### Q13. 为什么互动页首先显示语音？

新版默认打开“对镜头说话”。只想使用动作绑定，切到“手势控制”；打开语音页本身不表示声音输入已开启。

### Q14. Miloco 有画面，Friday 为什么还未配置？

视频服务与 Friday 的本地识别是分开的。需要先完成 Friday 这一侧的摄像头、识别环境和查看入口准备。

### Q15. 查看识别在哪里？

打开“摄像头”，展开“人物与手势检查”，再点击“查看识别”。确认时间持续更新，再观察人体或手部提示。

### Q16. 电视未连接会影响电脑上的手势吗？

不会。它只说明没有电视显示端连接。本机查看画面和手势不需要先连接电视。

### Q17. 有绿色骨架，为什么还没有控制设备？

骨架只表示检测结果。还需满足动作变化、操作者选择、规则启用、总开关运行与设备可用等条件，按排查页逐层检查。

### Q18. 一直保持双臂合上为什么没有反应？

它判断连续变化，先张开再合拢并短暂停留。一直保持同一姿势，不一定会产生新的动作事件。

### Q19. 旁边有人时怎样选操作者？

按镜头提示先比 OK 选择自己，放下手后再做动作。离开画面或追踪丢失后，可能需要重新选择。

### Q20. 必须先登记人脸吗？

单人动作控制不要求先登记姓名或人脸。人物登记用于资料整理与连续识别，不授予设备操作权限。

### Q21. 规则已启用，为什么页面还说暂停？

单条规则开关只控制这一条。手势总开关暂停时，规则即使已启用也不会触发。按钮显示“暂停手势控制”时，总开关正在运行。

### Q22. 没有身体动作文字提示，就一定没识别到吗？

不一定。识别页主要显示人体、手部和指向信息，不一定给每个动作显示独立文字。设备规则是否触发要看最近的手势响应。

### Q23. 指令已发送就是成功了吗？

还不能认定。需要看设备报告与实际效果；设备如果本来已在目标状态，也可能没有新的可见动作。

### Q24. 状态已更新与现场效果有什么区别？

前者说明设备回报符合目标，后者需要你在现场确认。两者都核对，才知道这一次操作是否满足预期。

### Q25. 一个手势成功后，其他设备也算验收了吗？

不算。其他目标、动作、光线、多人情况以及游戏，需要分别验证，不能由一次成功推定全部可用。

### Q26. 暂时不想让动作触发设备，怎么停？

在“手势控制”点击“暂停手势控制”。规则会保留，需要时再启用；暂停不会撤回已经发出的动作。

### Q27. 关闭预览或浏览器后还会继续运行吗？

后台与总开关仍运行时会继续。只停手势用手势总开关，停全部后台识别用“暂停摄像头感知”，停整套环境用交付的停止入口。

### Q28. 重启后需要重新登录和配置规则吗？

通常已保存设置会保留。使用[停止与重启脚本](#guide-getting-started-installation-maintenance)正常退出和重新启动，再核对来源、画面和开关。脚本不会删除账号连接和规则，也不会主动取消已有暂停设置；明确提示登录失效时再重新登录，迁移或清理私有数据后则需另行接入。

如果手势已有响应记录却操作未完成，检查绑定设备在 HA 中是否为“不可用”。小米集成可能尚未恢复设备连接；按[重启后的设备连接排查](#guide-getting-started-installation-maintenance)处理，不需要重新添加同一条规则。

仍在使用 Xiaomi Home v0.4.3 的部署，可按[已有集成升级步骤](#guide-getting-started-installation-maintenance)补上断网后的刷新重试修复。日常重启不需要重新安装集成，也不需要逐台设备重新授权。

### Q29. 手势一定需要云端模型或语音吗？

已经准备好的本地身体和手部手势不要求先开启麦克风，也不要求先购买云端模型。语音、画面理解和智能任务是另外的能力。

### Q30. 一键场景和单设备控制是同一范围吗？

不是。米家场景按照米家保存的整组内容执行，可能涉及多台设备。运行前核对确认框的名称和数量；只操作指定设备时使用设备页或对应规则。

### Q31. 回看为什么全是马赛克，为什么没有声音？

默认是整帧保护预览并保持静音。选择性遮挡需要额外本机模型配置；视觉保护不去除原音轨里的个人信息。

### Q32. 摄像头直播正常，为什么没有历史录像？

历史回看需要单独连接 NAS 或录像来源，并核对目录、日期和时间。直播与历史录像接入是两件事。

### Q33. 需要别人协助时提供什么？

提供发生时间、页面、操作、提示和设备实际变化。不要发送密码、验证码或模型密钥；真实家庭画面只在你认可的范围内分享。

<a id="guide-"></a>

## 29. 后续现场验证范围

本文把已做的软件核对与需要各家庭自行完成的现场验证分开，便于维护手册。

### 已完成的手册核对

- [x] 新版主要页面与入口逐项核对。
- [x] 手势表单及既有规则编辑入口核对；未借此改动真实规则。
- [x] 模拟文字规则的预览、批准与恢复。
- [x] 15 个温度质量场景重新截图。
- [x] 45 秒纯合成视频的整帧保护、静音与分段时间线演示。
- [x] 合成状态事件的来源和未知原因展示。
- [x] 从公开 Friday 基线的隔离源码副本安装基础依赖，核对安装入口。
- [x] 生命周期脚本在 macOS 实际部署验证停止、重复停止、重新启动与规则、来源及暂停设置保留。
- [x] 通用基础入口验证初始化、运行中重启、停止；macOS / 隔离 Linux 各 15 项进程、绑定设备状态及错误路径检查通过。
- [x] HA 小米集成设备状态不可用的现场恢复，使用者重新确认手势触发及窗帘实际动作；不扩展为所有设备均完成实体验收。
- [x] Xiaomi Home v0.5.0 隔离迁移及 macOS 实际停机备份、升级上线；既有实体标识、规则和允许控制范围保持一致。升级后实物动作单独等待使用者验收。

### 安装教程的验证范围

macOS / Linux 章节按公开源码入口、固定版本参数和官方平台安装方式整理。软件命令、页面链接与图表分别检查，不把某台已准备好环境的电脑视为所有平台全新安装均已通过。

- [ ] 在全新 macOS 系统完成工具、容器和账号全流程复测。
- [ ] 在全新 Ubuntu / Debian 主机完成系统安装命令与 HA 全流程复测。
- [ ] 按 SDK 实际发行范围分别核对芯片、Python 与摄像头型号。
- [ ] 通用摄像头注册、会话更新与识别后台装配需要所选部署版本提供相应组件；基础 CLI 不自动完成。

当前 Apple Vision 原生识别入口不适用于 Linux；没有把 Linux 本地手势端到端验收列为已通过。

### 使用各家庭时继续确认

- [ ] 按目标设备分别确认新增控件的实际效果。
- [ ] 多房间镜头的规则范围与多人情况。
- [ ] 自有 NAS 的格式、时钟、录像连续性与实际音画。
- [ ] 人物候选分组的现场核对、修正与撤销。
- [ ] 选择使用时，再准备语音、电视、智能预警或本机画面复核并分别验证。

图文依据分为实际界面核对、代码与合成测试核对、各家庭现场确认三个层次。可选功能未配置时明确写出，不能把一次旧版本的设备动作成功扩展为新版所有功能通过。
