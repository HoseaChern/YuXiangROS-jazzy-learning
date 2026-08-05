# Python venv 速查笔记

> 适用于 ROS 2 Jazzy + Ubuntu 24.04 + zsh 环境

---

## 一、前置安装

Ubuntu 24.04 默认 Python 3.12 已内置 `venv` 模块，但**创建虚拟环境所需的工具包需单独安装**：

```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

> ⚠️ 不装 `python3-venv` 会报错：`The virtual environment was not created successfully because ensurepip is not available`

---

## 二、创建虚拟环境

### 基础用法

```bash
# 进入目标目录
cd ~/your_project

# 创建虚拟环境（目录名自定义，惯例用 .venv 或 venv）
python3 -m venv .venv
```

### ROS 2 专用：继承系统包

```bash
python3 -m venv .venv --system-site-packages
```

| 参数                     | 作用                                                      |
| ------------------------ | --------------------------------------------------------- |
| `--system-site-packages` | 虚拟环境继承系统 Python 的已安装包（如 `rclpy`、`numpy`） |

> 不加此参数，虚拟环境是**完全隔离**的，ROS 2 的包无法直接 import。

---

## 三、激活与退出

### 激活（当前终端生效）

```bash
source .venv/bin/activate
```

激活后提示符前缀会出现 `(.venv)`：

```
(.venv) user@host:~/your_project$
```

### 退出

```bash
deactivate
```

### 删除虚拟环境

直接删目录即可，无残留：

```bash
rm -rf .venv
```

---

## 四、在虚拟环境中安装包

```bash
# 激活后，pip 指向虚拟环境内的 pip
source .venv/bin/activate
pip install <package_name>
```

> 无需 `sudo`，也不会触发 Ubuntu 24.04 的 "externally managed" 警告。

---

## 五、zsh 自动激活配置

在 `~/.zshrc` 中添加（按需调整路径）：

```bash
# ROS 2 Jazzy 基础环境
source /opt/ros/jazzy/setup.zsh

# 自动激活项目虚拟环境（进入目录时）
function auto_venv() {
    if [[ -d "$PWD/.venv" ]]; then
        source "$PWD/.venv/bin/activate" 2>/dev/null
    fi
}
# 每次切换目录后检查
chpwd_functions+=(auto_venv)
```

---

## 六、venv vs conda/mamba 对比

| 维度                | `venv`                                       | `conda` / `mamba`                                               |
| ------------------- | -------------------------------------------- | --------------------------------------------------------------- |
| **来源**            | Python 标准库内置                            | Anaconda/Miniconda 独立发行版                                   |
| **安装方式**        | `apt install python3-venv`                   | 下载安装包或 `apt install miniconda`                            |
| **Python 版本管理** | ❌ 只能使用系统已安装的 Python 版本           | ✅ 可安装任意 Python 版本（`conda create -n py311 python=3.11`） |
| **非 Python 依赖**  | ❌ 不支持（需手动 `apt install`）             | ✅ 支持（`conda install numpy` 会自动处理 C 库依赖）             |
| **包管理**          | `pip`                                        | `conda` + `pip` 混合                                            |
| **环境存储位置**    | 项目目录内（`.venv/`）                       | `~/miniconda3/envs/` 集中管理                                   |
| **启动速度**        | ⚡ 快（纯 Python，无额外开销）                | 稍慢（需加载 conda 基础环境）                                   |
| **与 ROS 2 配合**   | ✅ 直接用 `--system-site-packages` 继承系统包 | ⚠️ 需额外配置 `PYTHONPATH`，容易冲突                             |
| **离线/内网环境**   | 需手动准备 wheel 包                          | ✅ `conda` 可自建 channel，离线部署更方便                        |
| **典型场景**        | 轻量项目、系统 Python 已满足需求             | 多版本 Python、复杂 C 依赖、数据科学栈                          |

### 一句话总结

- **`venv`**：轻量、标准、与系统 Python 配合好，适合 ROS 2 等依赖系统 Python 的场景。
- **`conda/mamba`**：功能强大、管理多版本和非 Python 依赖方便，但和 ROS 2 的系统 Python 容易打架，**不推荐在 ROS 2 开发中使用**。

---

## 七、常见问题

### Q1: 为什么 Ubuntu 24.04 直接 `pip install` 会报错？

系统 Python 被标记为 "externally managed"（PEP 668），防止用户误装包破坏系统工具。解决方案：
- 用 `venv` 创建隔离环境 ✅
- 或加 `--break-system-packages` 强行安装 ❌（不推荐）

### Q2: `face_recognition` 的 `dlib` 编译失败？

先装系统编译依赖：

```bash
sudo apt install cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
```

### Q3: 虚拟环境里 import 不到 `rclpy`？

创建时忘了加 `--system-site-packages`，删除重建：

```bash
rm -rf .venv
python3 -m venv .venv --system-site-packages
```

---

## 八、速查命令卡

```bash
# 安装
sudo apt install python3-venv python3-pip

# 创建（ROS 2 用）
python3 -m venv .venv --system-site-packages

# 激活 / 退出
source .venv/bin/activate
deactivate

# 安装包
pip install <pkg>

# 查看已装包
pip list

# 导出依赖清单
pip freeze > requirements.txt

# 从清单恢复
pip install -r requirements.txt

# 删除环境
rm -rf .venv
```

---

## 九、ROS 2 + venv 实战踩坑记录

### 坑 1：`ros2 run` 用系统 Python，找不到 venv 里的包

**现象**：`python3 -c "import face_recognition"` 成功，但 `ros2 run` 报 `ModuleNotFoundError`。

**原因**：`ros2 run` 通过 launcher 脚本启动节点，脚本的 shebang 指向 `/usr/bin/python3`（系统 Python），而非 venv 的 Python。

**解决**：venv 里必须安装自己的 `colcon`，确保 `which colcon` 指向 `.venv/bin/colcon`，这样编译时 setuptools 会用 venv Python 生成 shebang。

```bash
source .venv/bin/activate
pip install --ignore-installed colcon-common-extensions  # 强制装到 venv
export PATH="/your/workspace/.venv/bin:$PATH"            # 优先用 venv 的 colcon
which colcon  # 确认指向 venv
```

> ⚠️ 不加 `--ignore-installed`，pip 检测到系统已有 colcon 会直接跳过。

---

### 坑 2：工作空间路径带空格，shebang 断裂

**现象**：编译成功，launcher 脚本存在，但 `ros2 run` 报 `FileNotFoundError` 或 `Exec format error`。

**原因**：setuptools 生成的 shebang 是绝对路径，如 `#!/home/user/4.2 Service_ws/.venv/bin/python3`。Linux 内核解析 shebang 时以空格分隔，把 `Service_ws/.venv/bin/python3` 当成参数，导致解释器路径断裂。

**解决**：
- **彻底**：工作空间目录名不要用空格，如 `4.2_Service_ws`。
- **重建 venv**：改名后必须重建 venv，因为 venv 内部硬编码了旧路径。

```bash
# 改名后彻底重建
deactivate
rm -rf .venv
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install face_recognition colcon-common-extensions
```

> 用 `sed` 批量替换 venv 内路径容易遗漏，重建最干净。

---

### 坑 3：`colcon build --cmake-args -DPYTHON_EXECUTABLE=$(which python3)` 对 Python 包无效

**现象**：加了 `PYTHON_EXECUTABLE` 参数，重新编译后 launcher shebang 还是 `/usr/bin/python3`。

**原因**：`PYTHON_EXECUTABLE` 只影响 CMake 编译的 C++ 包，不影响 `ament_python` 类型包的 setuptools 入口脚本生成。

**解决**：根本办法是让 `colcon` 本身运行在 venv Python 上（见坑 1），而不是传 CMake 参数。

---

### 坑 4：`pip install --ignore-installed` 后 setuptools 版本冲突

**现象**：安装 colcon 时，依赖解析提示 `colcon-core 0.21.0 requires setuptools<80`，但 venv 里装的是 79.0.1。

**处理**：79.0.1 已满足 `<80`，属于警告级别，不影响使用。若后续遇到兼容问题，可显式降级：

```bash
pip install 'setuptools<80,>=30.3.0'
```

---

### 一句话总结 ROS 2 + venv 的正确姿势

1. 工作空间路径**不要有空格**
2. venv 里**必须装自己的 colcon**
3. 编译前 `which colcon` 确认指向 `.venv/bin/colcon`
4. 每次新开终端，**激活 venv + 调整 PATH + source ROS 2 + source 工作空间**

---

## 十、ROS 2 工作空间一键启动脚本模板

```bash
#!/bin/zsh
# 保存为 ~/your_workspace/start_ws.zsh

WS_DIR="/home/changli/Documents/ROS/YuXiangROS/Chap4/4.2_Service_ws"

cd "$WS_DIR"
source .venv/bin/activate

# 关键：确保用 venv 的 colcon
export PATH="$WS_DIR/.venv/bin:$PATH"

source /opt/ros/jazzy/setup.zsh
source ./install/setup.zsh

echo "[OK] ROS 2 workspace ready: $WS_DIR"
echo "Python: $(which python3)"
echo "colcon: $(which colcon)"
```

使用：

```bash
source ~/your_workspace/start_ws.zsh
ros2 run demo_python_service learn_face_detect
```

---

> **附**：若需在 `.zshrc` 中配置别名，注意 `export PATH` 要放在 `source /opt/ros/jazzy/setup.zsh` **之后**，否则 ROS 2 的 setup 可能重置 PATH 顺序。