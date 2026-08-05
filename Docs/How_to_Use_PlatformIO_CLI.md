# PlatformIO 终端命令速查笔记

> 整理日期：2026-07-30  
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
pio project init --board esp32-s3-devkitc-1 --project-dir my_s3_project --framework arduino
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

### 5.1 临时代理（当前终端会话）

```bash
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
# 端口根据你的代理软件修改：Clash 默认 7890，V2RayA 默认 20171

# 然后执行 PIO 命令
pio project init --board esp32-s3-devkitc-1 --project-dir test
```

### 5.2 永久代理（系统级，推荐）

```bash
# Ubuntu 24.04 使用 systemd 用户环境
mkdir -p ~/.config/environment.d
cat > ~/.config/environment.d/90-proxy.conf << 'EOF'
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
http_proxy=http://127.0.0.1:7890
https_proxy=http://127.0.0.1:7890
EOF

# 注销并重新登录（或重启）后生效
```

### 5.3 pip 国内镜像（PIO 底层依赖 pip）

```bash
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

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

A: 包名写错了。用 `pio pkg list` 查看可用包，或去 [PlatformIO Registry](https://registry.platformio.org/) 搜索正确名称。

### Q: 创建项目时一直等待/卡住

A: 网络问题。在终端设代理后执行 `pio project init`，或配置系统级代理后重启。

### Q: 每次编译都很慢

A: 开启 `build_type = release`，关闭调试日志，确保项目不在同步盘（OneDrive/iCloud）上。

### Q: 上传后串口监视器看不到输出

A: 检查 `monitor_speed` 是否匹配代码中的 `Serial.begin()` 波特率。

### Q: 找不到板子定义

A: 先用 `pio boards | grep -i 关键词` 搜索，用通用板 ID（如 `esp32-s3-devkitc-1`）即可。

---

> **记住**：PlatformIO 的所有 GUI 操作都有对应的终端命令。当 GUI 行为异常时，终端是最高效的诊断和绕过手段。
