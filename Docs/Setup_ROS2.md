# Ubuntu 24.04 (Noble) + ROS 2 Jazzy + Zsh 配置手册

> 适用环境：Ubuntu 24.04 LTS (Noble)，Shell 为 Zsh（含 Oh My Zsh 及 Powerlevel10k），并已安装
> Miniforge3 (Conda)。
>
> 核心难点解决：解决系统安全更新库（如 `liblz4-dev` 等带 `.1` 后缀的版本）与 ROS 固定依赖的冲突。

---

## 1. 环境概览

- **操作系统**：Ubuntu 24.04.1 LTS (Noble)
- **ROS 发行版**：ROS 2 Jazzy Jalisco (LTS)
- **Shell**：Zsh (5.9)
- **其他环境**：Miniforge3 (Conda)、CUDA 12.9、Java 25

---

## 2. 添加 ROS 2 软件源

首先，启用 Ubuntu 的 `universe` 仓库并添加 ROS 官方源。

```bash
# 启用 universe 仓库
sudo add-apt-repository universe

# 安装依赖工具
sudo apt update && sudo apt install -y curl gnupg lsb-release

# 添加 ROS 2 GPG 密钥
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key
-o /usr/share/keyrings/ros-archive-keyring.gpg

# 添加软件源（注意代号为 noble）
echo "deb [arch=$(dpkg --print-architecture)
signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.
org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.
d/ros2.list > /dev/null
```

---

## 3. 解决依赖冲突并安装 ROS 2

### 3.1 问题背景

直接使用 `sudo apt install ros-jazdy-desktop` 会报错，
原因是系统安全更新将 `liblz4-dev`、`libzstd-dev`、`zlib1g-dev` 等库升级到了带有 `.1` 后缀的版本，而 ROS
依赖固定的旧版本。

### 3.2 解决方案：使用 `aptitude` 智能降级

使用 `aptitude` 工具，它会在安装时自动识别冲突并提出“降级冲突包”的解决方案。

```bash
# 安装 aptitude
sudo apt install -y aptitude

# 先安装核心基础包（减少依赖范围，更容易成功）
sudo aptitude install ros-jazzy-ros-base
```

**关键交互操作**：
当 `aptitude` 提示解决依赖关系时，它会给出类似以下方案：

- `降级 liblz4-dev`、`降级 libzstd-dev`、`降级 zlib1g-dev`。
- **输入 `Y` 并回车**，接受降级方案。

### 3.3 安装桌面组件及演示工具

基础包安装成功后，再单独安装桌面工具（避免一次性安装 `desktop` 元包可能带来的冗余依赖问题）。

```bash
# 安装核心可视化工具和小海龟演示包
sudo apt install ros-jazzy-turtlesim ros-jazzy-rviz2
```

---

## 4. 配置 Zsh 环境（最关键步骤）

> **警告**：请勿在 `~/.zshrc` 中手动写入 `export ROS_DISTRO=jazzy` 等零散的变量。
> 必须使用官方提供的 `setup.zsh` 脚本，否则会导致 ROS 2 的命令行自动补全（Tab 补全）失效，且缺少动态环境变量。

### 4.1 编辑 `~/.zshrc`

在 `~/.zshrc` 的**末尾**（建议放在 `source ~/.p10k.zsh` 之后）添加以下内容：

```bash
# ===== ROS 2 Jazzy =====
# 使用官方 setup.zsh 以支持自动补全和完整环境变量
source /opt/ros/jazzy/setup.zsh
```

### 4.2 应用配置

执行以下命令或重新打开终端：

```bash
source ~/.zshrc
```

---

## 5. 验证安装

### 5.1 检查环境变量

```bash
echo $ROS_DISTRO
# 应输出: jazzy
```

### 5.2 测试自动补全（检查 `setup.zsh` 是否生效）

输入 `ros2 topic` 然后按两次 `Tab` 键，应能列出 `list`、`echo` 等子命令。

### 5.3 运行小海龟示例（终极验证）

```bash
# 终端 1
ros2 run turtlesim turtlesim_node

# 终端 2（新开一个，无需额外配置）
ros2 run turtlesim turtle_teleop_key
```

在终端 2 中按方向键，小海龟移动即表示通信完全正常。

---

## 6. 安装开发工具（可选但推荐）

```bash
# 构建工具 colcon
sudo apt install python3-colcon-common-extensions

# 依赖管理工具 rosdep
sudo apt install python3-rosdep

# 初始化 rosdep（注意：国内网络可能需要代理或更换源）
sudo rosdep init
rosdep update
```

---

## 7. 故障排查速记

| 问题现象                                 | 可能原因                             | 解决方法                                                             |
| :--------------------------------------- | :----------------------------------- | :------------------------------------------------------------------- |
| `ros2: command not found`                | 新终端未加载环境                     | 检查 `~/.zshrc` 中的 `source /opt/ros/jazzy/setup.zsh` 是否存在      |
| `ModuleNotFoundError` 运行 Python 节点时 | Conda 环境干扰了系统 Python          | 执行 `conda deactivate` 后再运行 ROS 命令，或参考 4.2 节关闭自动激活 |
| Tab 补全 `ros2` 无反应                   | 使用了手动 `export` 而非 `setup.zsh` | 删除 `~/.zshrc` 中的手动 export，改用 `source setup.zsh`             |
| `liblz4-dev` 等依赖报错                  | 系统更新导致版本不匹配               | 使用 `sudo aptitude install ros-jazzy-ros-base` 进行降级安装         |

---

## 8. 配置总结

本配置的核心思想是：

1. **不急于求成**：先装 `ros-base`，再装 GUI 工具，避开元包的复杂依赖。
2. **信赖官方脚本**：永远使用 `source /opt/ros/jazzy/setup.zsh` 管理环境，而非手动写死路径。
3. **隔离 Python 环境**：处理好 Conda 与系统 Python 的关系，避免运行时诡异报错。

---

## 9. Python & C++ 运行环境调整

### 📘 要点一：Python —— 彻底“隔离” Conda 对 ROS 2 的干扰

**背景问题**：Miniforge/Conda 会在终端启动时自动激活 `base` 环境，并将其 Python 路径置于 `PATH` 最前面，导致
ROS 2 的 Python 节点错用 Conda 的库而报错。

**解决方案（二选一，推荐方案1）**：

- **方案一（一劳永逸，推荐）**：禁止 Conda 自动激活 `base` 环境。在终端执行以下命令：

  ```bash
  conda config --set auto_activate_base false
  ```

  之后，每次打开新终端，前缀将不再显示 `(base)`。此时 ROS 2 将默认使用系统 Python (`/usr/bin/python3`)，
冲突解除。如需使用 Conda，手动执行 `conda activate <环境名>` 即可。

- **方案二（临时补救）**：在需要运行 ROS 2 Python 节点的终端中，手动执行 `conda deactivate` 退出当前 Conda
  环境。

**⚠️ VSCode 操作重要提示**：
务必在**终端没有 `(base)` 前缀**的状态下，输入 `code .` 来启动 VSCode。否则，VSCode 的 Python 插件会继承
Conda 的解释器路径，导致 ROS 2 的 Python 库无法被识别。

---

### 📘 要点二：C++ —— 双管齐下配置 `rclcpp` 头文件环境

针对 `<rclcpp/rclcpp.hpp>` 的 `#include` 错误，你的思路完全正确：**VSCode 的“语法解析”** 和
**CMake 的“实际编译”** 必须分别配置。

#### 1. VSCode 配置 (`c_cpp_properties.json`) —— 解决编辑器红色波浪线

此文件负责告诉 VSCode 在哪里查找头文件以提供代码高亮和跳转。

在你的工作区根目录下创建 `.vscode/c_cpp_properties.json`，填入以下内容（针对 ROS 2 Jazzy 已配置好）：

```json
{
    "configurations": [
        {
            "name": "ROS2 Jazzy",
            "includePath": [
                "${workspaceFolder}/**",
                "/opt/ros/jazzy/include/**",  // ROS 2 核心头文件
                "/usr/include/**"             // 系统标准库
            ],
            "defines": [],
            "compilerPath": "/usr/bin/g++",
            "cStandard": "c17",
            "cppStandard": "gnu++20",        // ROS 2 Jazzy 默认使用 C++20
            "intelliSenseMode": "linux-gcc-x64"
        }
    ],
    "version": 4
}
```

#### 2. CMake 配置 (`CMakeLists.txt`) —— 解决实际编译链接

你的 CMake 写法逻辑是正确的。为了让它更贴合 ROS 2 的现代规范，建议在保留你思路的基础上做如下强化：

**你的原始写法（保留你的逻辑）**：

```cmake
cmake_minimum_required(VERSION 3.8)
project(ros2_cpp)

# 1. 寻找 rclcpp 库（核心步骤）
find_package(rclcpp REQUIRED)

# 2. 声明可执行文件
add_executable(ros2_cpp_node ros2_cpp_node.cpp)

# 3. 添加头文件目录（你的思路：让编译器找得到 .hpp）
target_include_directories(ros2_cpp_node PUBLIC ${rclcpp_INCLUDE_DIRS})

# 4. 链接库文件（你的思路：让链接器找得到 .so）
target_link_libraries(ros2_cpp_node ${rclcpp_LIBRARIES})
```

*(注：虽然现代 `rclcpp::rclcpp` 目标会自动传递包含路径，但在初学者阶段显式写出 `INCLUDE_DIRS`
和 `LIBRARIES` 有助于加深对编译链接过程的理解。)*

---

### 💎 最终总结

| 任务 | 配置文件 | 核心动作 | 你的理解正确性 |
| --- | --- | --- | --- |
| **Python 冲突** | `~/.bashrc` / 终端 | 禁止 Conda 自启动 (`auto_activate_base false`) | ✅ 完全正确 |
| **C++ 头文件报错** | `.vscode/c_cpp_properties.json` | 将 `/opt/ros/jazzy/include/**` 加入 `includePath` | ✅ 完全正确 |
| **C++ 编译链接** | `CMakeLists.txt` | 使用 `find_package` + `target_link_libraries` | ✅ 完全正确 |

现在你可以安心在 VSCode 中继续编码实践了。如果后续遇到 `ament_cmake` 未找到的报错，记得在 CMake
中补充 `find_package(ament_cmake REQUIRED)` 和最后的 `ament_package()`。
