# PlatformIO 终端命令速查笔记

> 整理日期：2026-07-30；最近更新：2026-08-06（网络配置分层方案 + src/ 子目录多固件隔离）  
> 适用环境：Ubuntu 24.04 + VS Code + PlatformIO Core  
> 核心原则：**终端命令与 VS Code 扩展调用的是同一套 PIO Core**，但终端可显式控制环境变量（如代理）。

---

## 1. 项目创建与管理

### 1.1 创建新项目

```bash
# 基本格式
pio project init --board <board-id> --project-dir <项目名>

# 示例：创建 ESP32-S3 项目
pio project init --board esp32-s3-devkitc-1 --project-dir my_s3_project

# 指定框架（Arduino / esp-idf）
pio project init --board esp32-s3-devkitc-1 --project-dir my_s3_project
--framework arduino
```

### 1.2 已有项目初始化（添加 platformio.ini）

```bash
cd 已有代码文件夹
pio project init --board esp32-s3-devkitc-1
```

### 1.3 查看/修改项目配置

```bash
# 查看当前项目配置
cat platformio.ini

# 重新初始化（更新依赖）
pio project init
```

---

## 2. 编译、上传与监控

### 2.1 编译

```bash
# 完整编译
pio run

# 只编译，不链接（检查语法）
pio run --target compiledb

# 强制重新编译（清除缓存后编译）
pio run --target clean
pio run
```

### 2.2 上传（烧录）

```bash
# 编译并上传
pio run --target upload

# 只上传（假设已编译）
pio run --target upload --upload-port /dev/ttyUSB0
```

### 2.3 串口监视器

```bash
# 打开串口监视器（默认 9600）
pio device monitor

# 指定波特率
pio device monitor --baud 115200

# 指定端口
pio device monitor --port /dev/ttyUSB0

# 常用组合：编译+上传+监视
pio run --target upload && pio device monitor --baud 115200
```

### 2.4 指定环境编译（多 env 时）

```ini
; platformio.ini
[env:esp32-s3]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino

[env:esp32]
platform = espressif32
board = esp32dev
framework = arduino
```

```bash
# 只编译 esp32-s3 环境
pio run -e esp32-s3

# 只上传 esp32-s3 环境
pio run -e esp32-s3 --target upload
```

### 2.5 src/ 子目录多固件隔离（build_src_filter + -e）

> 参考项目：`~/Documents/PlatformIO_project/fishbot_motion_control`（鱼香ROS 书配套，
> 尚未上传为 repo）

**场景**：在 `src/` 下新建子目录写 demo（如 `src/wifi_test/main.cpp`），不动主程序 `src/main.cpp`。
**坑**：`src/` 下同时存在两个 `setup()`/`loop()` 会符号重复定义，链接失败。
**解法**：`build_src_filter` 环境隔离 + 独立 env + `-e` 指定环境。以 fishbot 项目实际配置为例：

```ini
; 主固件: 排除 wifi_test 目录, 保证只编译 src/main.cpp
[env:esp32-s3-devkitc-1]
build_src_filter = +<*>-<wifi_test>

; 网络测试固件: 只编译 src/wifi_test/main.cpp, 与主固件互不干扰
[env:esp32-s3-devkitc-1-wifi-test]
build_src_filter = +<wifi_test>
```

```bash
# 只编译/烧录测试固件（重点: -e 指定 env 名）
pio run -e esp32-s3-devkitc-1-wifi-test -t upload

# 编译/烧录主固件
pio run -e esp32-s3-devkitc-1 -t upload
```

> ⚠️ 注意：PlatformIO 6.x 已将 `src_filter` 更名为 **`build_src_filter`**，
> 语法不变（`+<目录>` 仅包含 / `-<目录>` 排除）。
> 多 env 共享的选项（如 `lib_deps`、`board_microros_transport`）需在两个 env 里各自声明，
> 或用 `[platformio]` + `default_envs` 等进阶写法。

---

## 3. 板子查询

```bash
# 列出所有 ESP32 相关板子
pio boards esp32

# 搜索特定板子
pio boards esp32-s3

# 搜索 Freenove
pio boards | grep -i freenove

# 查看某块板子的详细信息
pio boards esp32-s3-devkitc-1
```

> 常用 ESP32-S3 通用板 ID：`esp32-s3-devkitc-1`（即使实际板子是 Freenove N8R8，也用这个）

---

## 4. 包与平台管理

### 4.1 安装平台/框架

```bash
# 安装 ESP32 平台（最新版）
pio pkg install --global --platform "platformio/espressif32"

# 安装指定版本
pio pkg install --global --platform "platformio/espressif32@^6.10.0"

# 安装 Arduino 框架
pio pkg install --global --tool "platformio/framework-arduinoespressif32"

# 安装烧录工具
pio pkg install --global --tool "platformio/tool-esptoolpy"

# 安装文件系统工具
pio pkg install --global --tool "platformio/tool-mkfatfs"
pio pkg install --global --tool "platformio/tool-mklittlefs"
pio pkg install --global --tool "platformio/tool-mkspiffs"
```

### 4.2 查看已安装的包

```bash
pio pkg list

# 只查看全局包
pio pkg list --global
```

### 4.3 更新包

```bash
# 更新所有包
pio pkg update

# 更新指定平台
pio pkg update --platform "platformio/espressif32"
```

### 4.4 卸载包

```bash
pio pkg uninstall --global --platform "platformio/espressif32"
```

---

## 5. 代理与网络配置

> **本机现状**：Clash Verge（混合端口 7897）。**5.1 git 定向代理、5.2 zshrc 代理函数、5.3 pip
> 镜像均已配置，5.4 VSCode inheritEnv 已解决**；仅 TUN 模式未启用（可选）。

PIO 的网络需求分三类，各有对应解法：

- `lib_deps` 的 GitHub git 依赖 → 5.1 git 定向代理
- platform/toolchain 下载（`dl.platformio.org`）→ 5.2 环境变量
- `pio upgrade` / pip 装包 → 5.2 + 5.3 的 pip 镜像

### 5.1 git 定向代理（已配置 ✅，解决 `lib_deps` 的 GitHub 依赖）

git 只认环境变量或 `git config`，不读"系统代理"。只对 github.com 走代理，不依赖环境变量：

```bash
git config --global http.https://github.com.proxy http://127.0.0.1:7897
git config --global https.https://github.com.proxy http://127.0.0.1:7897

git ls-remote https://github.com/fishros/micro_ros_platformio.git HEAD  # 验证,
应秒回
git config --global --get-regexp 'proxy'                      # 查看
git config --global --unset-all http.https://github.com.proxy  # 移除
```

### 5.2 `~/.zshrc` 代理管理函数（已配置 ✅，解决工具链下载 + pip）

PIO 从 `dl.platformio.org` 下载 platform/toolchain 走 HTTPS，需要环境变量。
函数带**存活检测**（代理开着才 export，关了自动 unset，避免"变量指向死端口 → 连接被拒"），且静默执行避免 p10k instant
prompt 警告：

```bash
proxy_port=7897
proxy_on() {
  local addr="http://127.0.0.1:${proxy_port}"
  if curl -x "$addr" -m 2 -s -o /dev/null https://www.gstatic.
com/generate_204; then
    export http_proxy="$addr" https_proxy="$addr" all_proxy="$addr"
    export no_proxy="127.0.0.1,localhost,192.168.0.0/16,10.0.0.0/8,172.16.0.
0/12,.local"
    export NO_PROXY="$no_proxy"; return 0
  else proxy_off; return 1; fi
}
proxy_off() { unset http_proxy https_proxy all_proxy no_proxy NO_PROXY; }
proxy_status() { proxy_on && echo "[proxy] ON  http://127.0.0.1:
${proxy_port}" || echo "[proxy] OFF"; }
proxy_on   # 开终端自动执行
```

- `NO_PROXY` 兜住本地/局域网（micro-ROS Agent 的 UDP 不受影响）
- 手动命令：`proxy_on` / `proxy_off` / `proxy_status`

### 5.3 pip 国内镜像（已配置 ✅，`pio upgrade` 本质是 pip）

`~/.config/pip/pip.conf` 已配置（清华源 + trusted-host，与代理解耦）：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

### 5.4 VSCode 内置终端（已解决 ✅，inheritEnv）

`settings.json` 的 `"terminal.integrated.inheritEnv": false`
会使内置终端**不继承环境变量**，`git clone` 龟速。本机已改为 `true`（继承主进程环境，VSCode 自带终端即正常）：

```json
"terminal.integrated.inheritEnv": true,
```

备用方案 B：保持 `false` 时，内置终端以 login shell 启动会执行 `~/.zshrc`，5.2 的代理函数自动生效（此路未用）。

> 仅 **TUN 模式**（Clash Verge 全系统透明代理，零配置、占用略高）未启用，需要时再开。

### 5.5 排查命令速查

```bash
env | grep -i proxy                      # 当前环境变量的代理
git config --global --get-regexp 'proxy' # git 代理配置
ss -tlnp | grep 127.0.0.1                # 找本机代理真实端口
curl -x http://127.0.0.1:7897 -I https://github.com   # 验证端口可用(HTTP/200)
ps -p $PPID -o args=                     # 内置终端是否 login shell
```

- 常见端口：Clash for Windows / ClashX `7890`；**Clash Verge Rev `7897`（本机）**；
  v2rayN `10809`；Shadowsocks `1080`
- git 的 `https_proxy` 填 **HTTP** 代理地址；只有 SOCKS5 端口时填 `socks5://127.0.0.1:端口`
- 报错 `Failed to connect to 127.0.0.1 port XXXX after 0 ms` =
  该端口没有代理进程在监听（不是变量问题）

---

## 6. 清理与维护

```bash
# 清理当前项目的编译缓存
pio run --target clean

# 清理所有无用缓存（全局）
pio system prune

# 查看 PIO 系统信息
pio system info

# 升级 PIO Core
pio upgrade

# 检查 PIO Core 版本
pio --version
```

---

## 7. VS Code 扩展 vs 终端的关系

| 维度            | VS Code 扩展 (GUI)                  | 终端命令                            |
| --------------- | ----------------------------------- | ----------------------------------- |
| **调用的 Core** | 同一个 `~/.platformio/penv/bin/pio` | 同一个 `~/.platformio/penv/bin/pio` |
| **环境变量**    | 继承桌面 Session（无代理）          | 继承当前 Shell（可设代理）          |
| **输出可见性**  | 有限，卡死时无反馈                  | 实时进度条，问题一目了然            |
| **适用场景**    | 日常开发、代码补全                  | 首次创建、网络不佳、排查问题        |

### 最佳实践

1. **首次创建项目/安装平台** → 用终端（可控制代理，有实时输出）
2. **日常编译上传** → 用 VS Code 底部工具栏按钮（方便）
3. **网络卡住排查** → 终端执行相同命令，看具体停在哪一步

---

## 8. 常见问题速查

### Q: `UnknownPackageError: Could not find the package`

A: 包名写错了。用 `pio pkg list` 查看可用包，或去
[PlatformIO Registry](https://registry.platformio.org/) 搜索正确名称。

### Q: 创建项目时一直等待/卡住

A: 网络问题。在终端设代理后执行 `pio project init`，或配置系统级代理后重启。

### Q: 每次编译都很慢

A: 开启 `build_type = release`，关闭调试日志，确保项目不在同步盘（OneDrive/iCloud）上。

### Q: 上传后串口监视器看不到输出

A: 检查 `monitor_speed` 是否匹配代码中的 `Serial.begin()` 波特率。

### Q: 找不到板子定义

A: 先用 `pio boards | grep -i 关键词` 搜索，用通用板 ID（如 `esp32-s3-devkitc-1`）即可。

### Q: `lib_deps` 的 GitHub 依赖下载龟速/失败

A: git 不读系统代理，只认环境变量或 `git config`。设置 git 定向代理（见 5.1），或检查 VSCode
内置终端是否被 `inheritEnv: false` 截断环境变量（见 5.4）。

### Q: 下载 platform / toolchain 卡住（`dl.platformio.org`）

A: 走 HTTPS 需要 `http_proxy`/`https_proxy` 环境变量。用 5.2 的 zshrc 代理函数（带存活检测）
；`pio upgrade` 慢则走 5.3 的 pip 镜像。

### Q: `Failed to connect to 127.0.0.1 port XXXX after 0 ms`

A: 端口写错或代理未开启 —— 该端口没有代理进程在监听，与变量传递无关。用 `ss -tlnp | grep 127.0.0.1`
找真实端口，`curl -x` 验证（见 5.5）。

---

> **记住**：PlatformIO 的所有 GUI 操作都有对应的终端命令。当 GUI 行为异常时，终端是最高效的诊断和绕过手段。
