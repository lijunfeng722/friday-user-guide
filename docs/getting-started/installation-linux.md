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

**适用范围：**命令示例针对 Ubuntu 22.04 / 24.04 / 26.04、Debian 12 / 13 的 64 位系统。其他发行版按其包管理器和 Docker 官方平台说明准备同等工具。当前 Apple Vision 原生识别不属于 Linux 安装路线，详见[摄像头平台范围](installation-camera.md#先确认平台与目标)。

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
git switch --detach 9a45a82cbfac0c1820c8fa100ad6cb77b9c904c1
UV_PYTHON=3.12 ./scripts/install-home.sh
./bin/home doctor
```

**应看到：**基础依赖安装成功，doctor 的基础模式为 `simulator`。选定提交产生的 `detached HEAD` 是版本定位提示。已有目录时先看[维护章节](installation-maintenance.md)，不覆盖原数据。

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
| 想在 Linux 执行原生手势编译 | 当前 Apple Vision 入口不适用，见[摄像头平台范围](installation-camera.md#先确认平台与目标) |

**完成标准：**示例页面可打开；需要新 HA 时 Docker Engine、Compose 也已就绪。继续[安装 HA 与小米接入](installation-home-assistant.md)。
