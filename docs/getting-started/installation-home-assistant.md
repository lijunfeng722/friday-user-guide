# 安装 HA 并接入自己的小米设备

完成后，你能在 HA 和 Friday 分别找到自己的设备。已有 HA 的读者复用原实例，从第 5 步检查 Xiaomi Home；不要再创建一套空 HA。

**开始前：**已经完成 [macOS](installation-macos.md)或 [Linux](installation-linux.md)基础安装。新建 HA 时，Docker 服务端及 Compose 检查成功。

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

```sh
.venv/bin/python scripts/setup-dependencies.py xiaomi-home
```

**应看到：**集成安装成功，并提示需要 HA 重启和账号登录。固定版本集成位于 `data/deployment/homeassistant/custom_components/xiaomi_home`。它是 HA 内部集成，不是另一个独立 Web 服务。

已有该集成或上游下载目录时，脚本会拒绝覆盖；先核对原安装。对已有 HA，要将集成安装到该实例实际使用的 `/config/custom_components`，不能把本教程新目录当作原实例配置。[Xiaomi Home 官方安装说明](https://github.com/XiaoMi/ha_xiaomi_home/tree/v0.4.3)

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

配置时核对：HA 地址与实例标识、允许的操作、明确的实体列表、是否启用及有效期。只开放准备使用的设备，不复制其他家庭的标识。文件格式以所选版本的 [HomeDeviceAuthority 契约](https://github.com/Geeprox/Friday/blob/e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3/homeplane/action_contracts.py)及[控制授权说明](https://github.com/Geeprox/Friday/blob/e1e9c9997d0ad45ec75d1c81f3ffa602eac8f5b3/docs/deployment.md#6-设备控制权限)为准；配置完成后重新连接并核对候选目标。

先用一个选定设备验证：检查目标和动作 → 明确执行 → 看页面回执 → 观察设备实际变化。有记录并不替代现场确认。之后可继续[设备操作](../guides/devices.md)或[摄像头与识别准备](installation-camera.md)。

**完成标准：**HA、Friday 都能找到自己的目标，来源明确；需要控制时，相应动作范围已配置并由你确认实际效果。
