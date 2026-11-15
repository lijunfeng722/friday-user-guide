# Linux 从零准备

**本章目的：**在 Linux 桌面或服务器上安装并启动 Friday。需要在这台 Linux 新建 HA 时，再安装 Docker Engine 和 Compose，为下一章提供容器主机。

## 为什么需要这些工具

| 组件 | 本章用它做什么 | 你为什么需要 |
| --- | --- | --- |
| Git、下载工具 | 获取源码、安装器和依赖 | 从空环境取得需要的软件 |
| uv、Python | 创建 Friday 的独立运行环境 | 按项目要求运行 Web，不依赖系统 Python 恰好符合版本 |
| Docker Engine、Compose | 直接在 Linux 运行 HA 容器 | 仅在这台主机新建 HA 时使用 |
| SSH 转发 | 在另一台电脑的浏览器访问本机监听的服务 | 无桌面或远程部署时，打开 Friday 和 HA 的页面 |

Linux 可以直接运行 Docker Engine，无需再为 HA 额外创建一层 Mac 式虚拟机。**完成标志：**本机浏览器或 SSH 转发后的浏览器能打开 Friday 示例；选择新建 HA 时，Docker 服务端也可用。

**适用范围：**命令示例针对 Ubuntu 22.04 / 24.04 / 26.04、Debian 12 / 13 的 64 位系统。其他发行版按其包管理器和 Docker 官方平台说明准备同等工具。Apple Vision 仍只适用于 macOS；配套开发预览提供 ONNX CPU 替代，但尚未完成全功能实机验收，详见[摄像头平台范围](installation-camera.md#先确认平台与目标)。

**可以跳过什么：**已有可用 HA 时，跳过 Docker 安装；已有 Friday 时直接进入[家庭接入](installation-home-assistant.md)或[日常使用](quick-start.md)。

## 1. 打开终端，确认系统

桌面 Linux 打开“终端”；无桌面的服务器使用已经配置好的 SSH 或主机控制台。输入：

```sh
cat /etc/os-release
uname -m
```

**应看到：**发行版名称、版本和架构。`x86_64` 对应 amd64，`aarch64` 对应 ARM64。需要能使用 sudo 的个人账号。

## 2. 安装下载和编辑工具

```sh
sudo apt-get update
sudo apt-get install -y git curl ca-certificates nano unzip xz-utils
```

**应看到：**安装完成，没有软件源或证书错误。后续从自己的账号运行 Friday，不用 root 运行项目或安装 Python 包。

## 3. 安装 uv 和 Python

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

## 4. 下载 Friday 并安装

```sh
mkdir -p "$HOME/friday-home"
git clone https://github.com/Geeprox/Friday.git "$HOME/friday-home/Friday"
cd "$HOME/friday-home/Friday"
git switch --detach b069e20584e4d68f4a7fb9b3731a2f35fc87d29e
UV_PYTHON=3.12 ./scripts/install-home.sh
./bin/home doctor
```

**应看到：**基础依赖安装成功，doctor 的基础模式为 `simulator`。选定提交产生的 `detached HEAD` 是版本定位提示。已有目录时先看[安装人员维护参考](../maintenance/installation-maintenance.md)，不覆盖原数据。

启动：

```sh
./bin/home serve
```

保持终端运行，在这台 Linux 的浏览器打开 [Friday](http://127.0.0.1:8740/)。看到“示例家庭”即完成基础安装，Control+C 用于停止前台服务。

## 5. 在另一台电脑查看 Linux 服务

Friday 默认只监听 Linux 主机自己的 `127.0.0.1`。已有 SSH 连接时，可在你的浏览器电脑另开终端建立转发：

```sh
ssh -N -L 8740:127.0.0.1:8740 -L 8123:127.0.0.1:8123 user@192.0.2.10
```

将 `user@192.0.2.10` 换成自己的 SSH 用户和 Linux 主机地址；这是文档示例地址。保持转发终端运行，再在浏览器电脑打开 `http://127.0.0.1:8740/`。8123 的转发供稍后的 HA 使用。

**应看到：**与 Linux 本机相同的 Friday 页面。正式账号连接使用默认端口，以便和当前版本的本机回调一致。直接把 Linux 的内网 IP 拼到 8740 后面，不能替代这个转发。

## 6. 需要新 HA 时，安装 Docker Engine

已有可用 HA 可跳过本节，直接进入[HA 与小米接入](installation-home-assistant.md)。已有 Docker 时先运行 `sudo docker info` 和 `sudo docker compose version`，两项成功即可复用。

全新 Ubuntu / Debian 按下面步骤添加 Docker 官方软件源。先准备保存签名密钥的目录：

```sh
sudo install -d -m 0755 /etc/apt/keyrings
```

### Ubuntu：执行这一组

```sh
curl -fLsS https://download.docker.com/linux/ubuntu/gpg -o /tmp/friday-docker.asc
sudo install -m 0644 /tmp/friday-docker.asc /etc/apt/keyrings/docker.asc
friday_codename="$(. /etc/os-release; printf '%s' "$VERSION_CODENAME")"
friday_arch="$(dpkg --print-architecture)"
printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' "$friday_arch" "$friday_codename" | sudo tee /etc/apt/sources.list.d/friday-docker.list >/dev/null
```

### Debian：执行这一组

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

## 7. 常见安装问题

| 现象 | 检查位置 |
| --- | --- |
| apt 找不到 Docker 包 | 发行版和代号是否匹配官方源，`apt-get update` 是否成功 |
| Docker socket 权限不足 | 使用本章带 sudo 的 Docker 命令；不改 socket 为任意用户可写 |
| Docker 服务没启动 | `sudo systemctl status docker`，再看服务日志 |
| 服务器运行但自己浏览器打不开 | 先核对 SSH 转发，区分浏览器电脑和 Linux 主机的 127.0.0.1 |
| 依赖下载失败 | 检查网络、时间、证书与包源；保留报错，不把软件源错误当成账号错误 |
| 想在 Linux 执行原生手势编译 | 不运行 Apple Vision 编译；候选版本使用 ONNX CPU，见[摄像头平台范围](installation-camera.md#先确认平台与目标) |

**完成标准：**示例页面可打开；需要新 HA 时 Docker Engine、Compose 也已就绪。继续[安装 HA 与小米接入](installation-home-assistant.md)。

## CPU 识别与 ARL 开发预览

包含本次适配的候选代码可在普通 Intel/AMD Linux 上使用独立的 CPU 识别环境。基础路线是 ONNX 人体/手势、SenseVoice 语音识别、espeak-ng 中文回复和 ARL Linux 宿主。没有独立显卡也能准备这些组件，但实际摄像头帧率、识别准确性和音箱效果需要在自己的设备逐项确认。

此预览尚未包含在上文固定发布提交中，不能只执行基础安装就认为所有能力已迁移。安装人员请参考配套 Friday 源码的 `docs/linux-runtime.md` 和 ARL 源码的 `docs/linux-host.md`，核对代码版本后再配置；不要复制 Mac 的 Python 环境或动态库。

- Apple 提醒事项、日历、信息、备忘录和钥匙串明确不支持。
- 方向云台与人体/宠物跟踪已接入固定版本 Linux SDK；KTV 分离改用 ONNX CPU。真实云台动作、分离效果和耗时仍需在目标机器验收。
- ARL 提供本机浏览器服务设置与命令行，可管理通用服务、AI 任务和应用授权；音乐、出行等账号不会自动获得授权。操作见 [Linux ARL 设置](../explanation/arl.md#linux-宿主)。
- 可选的重型画面复核另需至少 24 GiB 内存及独立模型环境；CPU 性能尚未实测，超时会跳过。它不能替代家庭安全防护。
- AI 任务仍可能使用联网模型；“Linux 本地运行”不等于所有模型完全离线。

先检查前置条件，再逐步确认画面、识别和经授权的设备动作。检查显示依赖齐全、模拟测试通过，都不代表真实设备已经执行。

### 云台、自动跟踪与 KTV

安装人员应按 Friday `docs/linux-runtime.md` 准备精确匹配的摄像头 SDK、独立 CPU 分离环境与固定模型。云台仅开放四个方向短步进；启用自动跟踪前，先确认选中相机、画面正常及控制授权。识别丢失或指令过期时不会补发旧转动；停用后沿用原有摄像头设置恢复流程。通信回执不能代替观察云台是否转动。

KTV 中仍按原流程选择本地音频、准备伴奏再播放。Linux 自动使用 CPU 分离；首次准备需要等待，取消后不会把不完整音轨当作可播放伴奏。CPU 分离不承诺实时完成，输入最长 30 分钟；安装人员应先用自己允许处理的短片段检查人声残留、失真和时间开销。


### Docker 容器启动检查

配套候选代码提供 CPU 镜像构建入口。在三个仓库并列、Docker 已运行的情况下，进入项目索引仓库执行：

```sh
python3 scripts/build_linux_container.py
docker compose -f docker/compose.yaml up -d --wait --wait-timeout 660
```

打开 `http://127.0.0.1:8740` 查看明确标注的模拟页面。ARL 本机设置链接用下列命令取得，它含有临时令牌，不要分享：

```sh
docker compose -f docker/compose.yaml exec runtime python /opt/container/entrypoint.py settings-url
```

这套镜像使用独立数据卷，不会自动导入原来 Mac 的家庭账号、规则或启动摄像头。首次启动会自动下载并校验固定版本摄像头 SDK，不需要手动处理 SDK 文件；模型仍需按组件准备；页面能打开不能代表真实设备已连接。Apple Silicon Mac 上的 amd64 镜像需要模拟运行，速度不能代表目标 Intel/AMD 电脑。

停止测试容器使用 `docker compose -f docker/compose.yaml stop`，保留数据卷。原部署仍由原停止、启动脚本管理；恢复原部署前先停止测试容器，避免端口冲突。完整说明见 [CPU 容器部署入口](https://github.com/lijunfeng722/friday-project-index/blob/main/docs/linux-container.md)。此入口尚属未发布的候选代码。

已有家庭配置可另行导入私有数据卷，并叠加 `docker/compose.household.yaml` 启动真实家庭模式。此操作需要先停止原 Friday、保留备份，再核对同一个 HA 实例、授权、摄像头暂停状态和设备范围；不是直接复制整个 Mac 安装目录。真实来源连接失败时，家庭模式会报错，不会偷偷显示模拟家庭。摄像头 SDK 由首次启动自动安装，模型仍需按固定来源准备。

当前实测已通过真实 HA 接入、浏览器麦克风到 Docker CPU 的中文识别，以及公开音乐片段的人声分离，使用者确认识别正确、分离效果可用。摄像头视频已通过宿主的受限网络转发进入 Linux 容器并完成解码；转发器只使用普通网络接口，不运行 Mac 视觉或摄像头 SDK。实际云台转动已通过画面位移验证，使用者确认人体左右跟随正常、停下后稳定。随后摄像头麦克风的实际语音也在 Docker CPU 完成识别，使用者确认正确；家庭屏文本播报经试听确认内容清楚。宠物跟踪尚未验收。不要因网页健康或模型已安装就认为这些功能已经可用。

当前人体和手部识别已改为不要求 AVX 的 ONNX CPU 路径，并在当前 Mac 的 Docker 中实际运行。可选环境声音分类仍需要 AVX；它与已验证的中文语音识别不同。新视觉路径暂不提供实验性虹膜注视判断，会明确显示能力不支持。


#### 家庭屏的文本播报例外

Xiaomi 智能家庭屏 Mini 可以采用“播放文本”：Friday 在 Docker 中发送文字，由 Mini 生成并播放声音。它不依赖 Apple 服务，也不要求独立显卡，但声音不是 Docker 内的 CPU 模型生成的；设备是否需要厂商云端尚未验证，不能视为完全离线。

接入时明确选定家庭屏，并从 HA 中选择该设备的“播放文本”能力；“执行文本指令”不是同一个接口。当前接入接口没有本地音频文件播放入口，因此不能直接播放 Docker 合成的音频。目标与授权保存在私有配置中，不随公共镜像分发。

首次验证先检查设备是否正在播放、是否静音，以较低音量播放一句短话，再由本人确认声音清楚。完成后恢复原音量与静音设置。本次实测已完成这些步骤，原来的语音暂停状态也已恢复；保存播报目标不会自动开启持续监听、语音控制或持续播报。摄像头输入识别与音箱输出分别通过，不代表完整语音问答或所有家电命令已经验收。


#### 迁移后手势设置没有可选设备

如果家庭设备已显示，但“设置设备控制”的设备列表为空，请让安装人员核对 Docker 的家庭连接与原设备控制授权是否指向同一个 HA 地址、同一个实例。迁移时连接地址改变而授权仍保留旧地址，会导致候选设备全部被拒绝。修复时保留原授权范围，不需要扩大权限；也无需先开启手势执行。列表恢复后可选择设备和查看支持的动作，实际使用时再按需启用手势控制。


### 候选镜像检查与自动更新

安装人员可以先在独立模拟容器中检查候选镜像；检查使用临时端口和数据，结束后自动清理，不会重启你正在使用的家庭服务。GitHub 上的构建与发布也不会自动更新家中的 Docker。升级时仍需按维护步骤备份并明确选择版本。

公开 CPU 镜像与当前本地家庭镜像的配套文件可能不同：条件性的小米摄像头 SDK 不随公开构建自动附带，接入这类摄像头需要另行确认许可和准备组件。CPU 模型、家庭账号及私有配置也不放入公开镜像。当前发布仍在集成验证阶段，不能把构建成功当作已经可以从 GHCR 下载。


### 首次启动自动准备摄像头组件

启动新容器后，先等待固定版本摄像头组件下载、校验和安装完成，再打开页面。首次需要联网，预留约十分钟；后续启动检查已保存的组件并直接复用，不需要重新下载。安装组件不会自动登录小米账号或开启摄像头，家庭配置和设备授权仍需单独完成。

如果下载中断，容器会报告失败；网络恢复后重启该容器即可重试。如果提示文件校验失败，请交给安装人员核对，不要跳过校验，也不要删除家庭数据卷。原许可证和非商业用途说明会随安装保留；自动安装不扩大原许可证的使用范围。GitHub 构建或本地生成候选镜像不会自动替换你正在运行的家庭服务。
