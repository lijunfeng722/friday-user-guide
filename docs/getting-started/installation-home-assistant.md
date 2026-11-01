# 安装 HA 并接入自己的小米设备

**本章目的：**把自己在米家中使用的设备接入 Friday，让 Friday 能显示真实房间、设备和状态。你将新建或复用 Home Assistant，在其中接入小米设备，再授权 Friday 读取这份家庭清单。

## 为什么需要 HA 和 Xiaomi Home

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

这条设备接入路线无需先安装 Miloco。Miloco 是独立项目，选择其摄像头或智能功能时，再按[可选摄像头章节](installation-camera.md)准备。

**适用与跳过：**

- 还没有 HA：从第 1 步开始。
- 已有 HA，但尚未接入小米设备：按第 3 步说明在原实例安装集成，再完成第 5 步。
- HA 已能看到目标设备：直接进入第 6 步。其他品牌设备通过各自的 HA 集成接入后，也从这里继续。
- 只体验示例：可跳过本章。

**开始前：**已经完成 [macOS](installation-macos.md)或 [Linux](installation-linux.md)基础安装。新建 HA 时，Docker 服务端及 Compose 检查成功。

**完成标志：**HA 和 Friday 都能找到自己的目标设备，且 Friday 显示真实家庭来源。需要发送设备动作时，再按第 7 步配置控制范围并现场验证。

## 1. 准备持久化配置

在 Friday 安装电脑的终端执行：

```sh
cd "$HOME/friday-home/Friday"
.venv/bin/python scripts/setup-dependencies.py plan
.venv/bin/python scripts/setup-dependencies.py prepare
```

**应看到：**plan 列出当前工具，prepare 返回 `prepared: true`、`services_started: false`。它创建 `data/deployment/compose.yaml`、`.env` 和所需私有目录，还没有启动 HA。

已有这些文件时不要重复 prepare；先检查是否属于已有部署。HA 数据以后保存在 `data/deployment/homeassistant`，容器里对应 `/config`，重建容器不会替你重新创建账号。

## 2. 设置自己的时区

```sh
nano data/deployment/.env
```

将 `TZ=UTC` 改为自己的 IANA 时区，例如 `TZ=Asia/Shanghai`、`TZ=Europe/Berlin`。保存按 Control+O、回车，退出按 Control+X。

**应看到：**文件只保留所选时区配置。错误时区会影响时间显示和自动化时间判断。

## 3. 把 Xiaomi Home 安装到 HA 内

本教程现在使用 **Xiaomi Home v0.5.0**。当前 Friday 安装基线已包含更新的安装器；下方同时提供同内容的独立下载工具，便于沿用较早 Friday 版本的用户升级集成。工具只安装集成；小米登录仍在 HA 官方页面完成。

### 下载安装工具

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

**应看到：**安装工具和许可证均显示 `OK`。也可分别下载[安装工具](../assets/scripts/setup-dependencies.py)、[许可证](../assets/scripts/FRIDAY-SCRIPT-LICENSE.txt)和[校验清单](../assets/scripts/SETUP-SHA256SUMS)。

### 首次安装集成

```sh
cd "$HOME/friday-home/Friday"
.venv/bin/python "$HOME/friday-home/service-tools/setup-dependencies.py" xiaomi-home --project "$PWD"
```

**应看到：**`installed: true`、`version: v0.5.0`，并提示需要 HA 重启和账号登录。工具校验官方固定提交 `75b3acb6325a3a8d295688b13904737d6738a6a5`；集成位于 `data/deployment/homeassistant/custom_components/xiaomi_home`。它是 HA 内部集成，不是另一个独立 Web 服务。

已有集成时，脚本会拒绝覆盖；按[已有集成升级步骤](installation-maintenance.md#已有-xiaomi-home-怎样升级)维护。对其他方式安装的 HA，要将集成安装到该实例实际使用的 `/config/custom_components`，不能把本教程新目录当作原实例配置。[Xiaomi Home 官方安装说明](https://github.com/XiaoMi/ha_xiaomi_home/tree/v0.5.0)

## 4. 启动 HA 并检查页面

### macOS

确认 Colima 的专用实例运行后执行：

```sh
docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env up -d
docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env ps
```

### Linux

```sh
sudo docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env up -d
sudo docker compose --project-name friday-home --file data/deployment/compose.yaml --env-file data/deployment/.env ps
```

**应看到：**homeassistant 服务运行。首次拉取镜像和初始化需要等待。该 Compose 使用固定 HA 镜像和 Linux host network；没有自动配置 USB、蓝牙或 Zigbee 适配器。[HA Container 官方说明](https://www.home-assistant.io/installation/linux/)

在 HA 所在主机，或已经建立对应端口转发的浏览器电脑，打开 [HA 本机入口](http://127.0.0.1:8123/)。按页面创建自己的管理员、设置家庭位置与时区，直到进入 HA 主界面。密码和验证码只填在页面。

### Mac 的 8123 打不开时

先检查容器仍在运行。Colima 自动转发没有生效、而虚拟机内 HA 可用时，可以在 Mac 新开终端建立仅本机转发：

```sh
umask 077
colima ssh-config --profile friday-home > "$HOME/friday-home/ha-ssh.config"
friday_ssh_host="$(awk '$1 == "Host" {print $2; exit}' "$HOME/friday-home/ha-ssh.config")"
ssh -F "$HOME/friday-home/ha-ssh.config" -o ExitOnForwardFailure=yes -N -L 127.0.0.1:8123:127.0.0.1:8123 "$friday_ssh_host"
```

保持这个终端运行，再打开 8123。端口已经被占用时先核对现有转发，不反复启动。此配置文件由你自己的 Colima 生成，不需要填写作者电脑的 SSH 路径。

Linux 远程主机使用 [Linux 章节的 SSH 转发](installation-linux.md#5-在另一台电脑查看-linux-服务)。HA 地址需同时能被 Friday 所在主机访问；不在同一主机时，使用该 HA 的实际可达地址。

## 5. 在 HA 完成小米登录与设备选择

1. 在 HA 打开“设置 → 设备与服务 → 添加集成”。
2. 搜索 Xiaomi Home，阅读集成提示，选择自己的区域。
3. 打开其小米官方授权页，登录自己的账号并确认授权。
4. 回到 HA，选择需要接入的家庭和设备，完成后续页面。
5. 在 HA 集成页查找目标设备，查看房间和状态。

新增集成文件后搜索不到 Xiaomi Home，先重启本教程的 homeassistant 服务，再刷新浏览器。不要把 Miloco 登录当作这一步已经完成。

### 小米确认授权后返回失败

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

## 6. 让 Friday 读取自己的家庭

保持 HA 运行，重新打开 Friday 的“连接”：

1. 点击“查找并连接”；多个结果时选自己的 HA。
2. 没发现时点击“填写地址”，输入完整可达地址。
3. 在 HA 官方登录页面完成 Friday 的授权。
4. 返回 Friday，点击“连接并读取设备”。

![Friday 家庭连接向导，摄像头被单独列为可选项](../assets/screenshots/friday-settings.jpg)

**应看到：**“家庭已连接”，设备页出现自己的设备。设备数量按当前家庭决定，不以示例截图的数量为标准。一个设备的多个实体也不是多台设备。详细操作见[连接自己的家](connect-home.md)。

基础源码入口重启后可能仍从示例模式启动；已有授权与当前来源分别判断。重新进入连接页读取家庭，或使用部署版本提供的已配置来源启动器，再确认顶部状态；不需要因此反复删除账号授权。

## 7. 首次开放设备控制范围

读取设备完成后，可以先只查看状态。首次控制需要本机操作员根据自己的 HA 实例、实体标识和设备能力配置允许范围；这是一项部署设置，不是每次使用都要逐台重新登录。

当前界面可以暂停 / 恢复已有范围，但没有替代首次范围文件配置。源码 Web 默认使用 `data/homeplane/action-authority.json`；桌面部署的私有目录不同，应按其构建说明确认。

配置时核对：HA 地址与实例标识、允许的操作、明确的实体列表、是否启用及有效期。只开放准备使用的设备，不复制其他家庭的标识。文件格式以所选版本的 [HomeDeviceAuthority 契约](https://github.com/Geeprox/Friday/blob/5961567d3ed897eed20fb161be6dfa49d522df3d/homeplane/action_contracts.py)及[控制授权说明](https://github.com/Geeprox/Friday/blob/5961567d3ed897eed20fb161be6dfa49d522df3d/docs/deployment.md#6-设备控制权限)为准；配置完成后重新连接并核对候选目标。

先用一个选定设备验证：检查目标和动作 → 明确执行 → 看页面回执 → 观察设备实际变化。有记录并不替代现场确认。之后可继续[设备操作](../guides/devices.md)或[摄像头与识别准备](installation-camera.md)。

**完成标准：**HA、Friday 都能找到自己的目标，来源明确；需要控制时，相应动作范围已配置并由你确认实际效果。
