# 启动、备份与安装排障

**本章目的：**让首次安装好的环境能够持续使用：你会知道怎样启动、正常停止、重新检查、备份，并在出错时找到对应环节。

## 为什么安装后还需要维护步骤

Friday、HA、Miloco 等组件分别运行，也分别保存账号连接、家庭配置和规则。关闭终端、电脑重启或升级软件后，需要逐项确认服务和状态；提前保存配置与版本信息，才能恢复自己的设置。

本章把日常操作和安装排障放在一起，帮助你判断当前应启动哪个服务、保留哪些数据，以及应向维护者提供什么信息。

**适用与跳过：**所有已完成安装的读者都应了解启动与备份。没有安装 Miloco、OpenClaw、摄像头或回看功能时，跳过对应小节。Friday 尚未安装成功时，先返回自己的 [macOS](installation-macos.md)或 [Linux](installation-linux.md)章节。

**完成标志：**你能重新打开正确的服务、确认真实家庭来源和暂停状态，知道备份位置，并能按症状定位下一步。操作前先确认正在管理自己的哪台电脑、哪套服务。

## 1. 日常启动与停止

基础 Web 在自己的安装目录启动：

```sh
cd "$HOME/friday-home/Friday"
./bin/home serve
```

终端持续运行时打开 [Friday](http://127.0.0.1:8740/)，Control+C 停止。电脑睡眠、关闭终端和停止前台进程都会影响访问；安装依赖不等于配置了开机自启动。

Mac 新建 HA 时先启动其虚拟机：

```sh
colima start --profile friday-home
```

然后按 [HA 章节](installation-home-assistant.md#4-启动-ha-并检查页面)启动 / 查看 Compose。需要停止 HA 时，使用同一组 project-name、file、env-file 参数，把末尾 `up -d` 换为 `stop`；Linux 的 Docker 命令仍带 sudo。停止保留数据，不使用删除卷的参数。

Miloco / OpenClaw 可能使用各自的后台服务。检查：

```sh
miloco-cli service status
openclaw gateway status
```

它们启动成功不代表 Friday 也已经启动。完整识别部署另使用自己的正式启动入口，保留已配置的环境与暂停策略。

## 2. 记住几个入口

| 地址 / 位置 | 含义 |
| --- | --- |
| `http://127.0.0.1:8740/` | 当前电脑上的 Friday，或已建立转发的 Linux 服务 |
| `http://127.0.0.1:8123/` | 当前电脑可访问的 HA 入口 |
| `http://127.0.0.1:1810/` | Miloco 默认本机页面，以实际安装输出为准 |
| Friday 的“查看识别” | 通过已配置入口查看视觉预览，不需要公开查看密钥 |

手机、浏览器电脑、Linux 服务器和虚拟机各自有自己的 127.0.0.1。更换电脑访问时先配置相应入口或转发，不把同一地址当成自动共享。

## 3. 重启后检查什么

1. 依次确认容器主机、HA、需要的 Miloco 和 Friday 是否运行。
2. 看 Friday 顶部是“示例家庭”还是自己的真实来源。
3. 基础源码入口可能从示例启动，已有授权时重新读取家庭；不要因为来源未激活就删除账号。
4. 核对目标设备状态、控制范围、摄像头感知与手势总开关。
5. 验证部署版本提供的恢复机制后，再安排自启动。

用户手册里的截图或一次历史动作成功，不代表当前重启后的全部设备已经验收。

## 4. 备份自己的配置与数据

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

## 5. 更新时保留哪些环境

| 环境 | 日常确认方式 | 更新时注意 |
| --- | --- | --- |
| Web `.venv` | `.venv/bin/python --version` | 使用对应 `uv.lock` 和原先选择的 extras |
| 视觉 `data/embodied/runtime` | 使用该目录自己的 Python | SDK、模型和原生程序单独核对 |
| Miloco 安装环境 | 安装器及 `miloco-cli service status` | 不用 Friday 的 uv sync 替它升级 |
| 可选 ARL | 按自己的 ARL 部署说明检查 | 本地额外安装的 SDK 不一定在 Friday 锁文件中 |

更新前运行 `git status --short` 和 `git rev-parse HEAD`，备份后选择目标版本再切换。不要用清理源码目录的命令清掉私有数据。`uv sync` 会按选择的依赖集合同步环境；重新安装时保留所需 extras，并重新核对另外安装的 SDK。

## 6. 可选：准备保护回看的媒体工具

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

上面的命令展示回看所需集合；若同一 Web 环境还需要其他 extras，一并写在这次同步命令中。之后配置自己的 NAS 或录像来源，按[保护录像回看](../guides/recordings.md)验证。模型权重和真实录像来源不由此命令自动生成。

## 7. 按症状排查安装

| 现象 | 先检查 |
| --- | --- |
| 命令找不到 | 当前终端 PATH、工具是否安装、是否进入正确目录 |
| Python 版本不符 | 使用 `.venv/bin/python` 或指定的 uv Python，不看另一个环境的版本 |
| 下载 / 镜像拉取失败 | 包源、证书、系统时间；Mac 还需检查虚拟机内的 DNS 和代理 |
| HA 容器运行但网页打不开 | 8123、端口转发、容器日志及正确 Docker context |
| 小米确认授权后出错 | 浏览器电脑能否通过回调主机名访问正确 HA，见[回调处理](installation-home-assistant.md#小米确认授权后返回失败) |
| HA 有设备，Friday 仍是示例 | Friday 当前来源是否已连接并读取；HA 登录与来源激活分别检查 |
| 设备可见但无可选动作 | 首次控制范围、目标实体能力和已有范围是否暂停 |
| Miloco 有视频，Friday 尚未配置 | 独立视觉 Python、SDK、原生程序、模型、私有注册和后台入口 |
| 查看识别点不开 | 查看地址、服务监听、私有查看配置与部署版本是否匹配 |
| 画面或骨架可见但规则不触发 | 保存卡片、目标、使用范围、总开关、操作者与识别条件 |
| 重启后又未配置 | 运行目录是否一致，是否用了不同的 Python 或启动入口 |
| ffprobe 在终端可用但回看报错 | Friday 实际进程的工具定位和文件权限 |

## 8. 给维护者提供什么

提供系统与芯片、源码提交、工具版本、出错阶段、错误码，以及不含私人信息的界面状态。诊断导出使用产品提供的脱敏入口，并先在本机检查内容。

密码、Token、授权码、完整查看链接、家庭导出和原始视频不放进聊天或公开 issue。可继续查[常见问题](../troubleshooting/faq.md)或[按现象排查](../troubleshooting/common-errors.md)。
