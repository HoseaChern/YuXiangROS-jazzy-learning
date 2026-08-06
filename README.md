# YuXiangROS-jazzy-learning

> ROS 2 学习工作区：参考《ROS2机器人开发 从入门到实践》（桑欣 著）的代码，适配 **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic** 环境，并附带原创的 JSON/Python 字典转 URDF/Xacro 工具（`Dict_To_URDF`）。

[English Version](README_EN.md)

---

## 目录

- [项目简介](#项目简介)
- [环境说明与原书差异](#环境说明与原书差异)
- [Python 虚拟环境（.venv）说明](#python-虚拟环境venv说明)
- [Gazebo Classic → Harmonic 迁移要点](#gazebo-classic--harmonic-迁移要点)
- [各章导读](#各章导读)
- [原创工具：Dict_To_URDF](#原创工具dict_to_urdf)
- [Chap9 第三方依赖包获取](#chap9-第三方依赖包获取)
- [许可证与致谢](#许可证与致谢)

---

## 项目简介

本仓库是笔者学习《ROS2机器人开发 从入门到实践》（[桑欣 / fishros](https://github.com/fishros)，配套仓库 [fishros/ros2bookcode](https://github.com/fishros/ros2bookcode)）过程中的代码与笔记整理。

**本仓库是衍生学习项目，非官方版本。** 原书代码基于 **Ubuntu 22.04 + ROS 2 Humble + Gazebo Classic** 编写，本仓库在保留原书结构与思路的前提下，将其迁移适配至 **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic**，具体包括：

- 处理 Jazzy 对 Humble 的破坏性更新（`use_stamped_vel` 移除、`spawner` 参数变化等）
- 将 Gazebo Classic 生态（`gazebo_ros`、`spawn_entity.py`、`gazebo_ros2_control`、`.world` 世界文件）迁移至 Gazebo Harmonic 生态（`ros_gz_sim`、`create`、`gz_ros2_control`、`.sdf` 世界文件）
- 全部迁移改动以 `[旧版: xxx]` 代码注释形式保留对照说明，方便初学者理解差异

仓库内还包含 11 篇个人学习笔记（`Docs/` 目录），其中 [About Gazebo Classic vs Harmonic.md](Docs/About%20Gazebo%20Classic%20vs%20Harmonic.md) 深入讲解了本次环境迁移的全部痛点与解决过程。

## 环境说明与原书差异

| 项目 | 原书环境 | 本仓库环境 |
|---|---|---|
| 操作系统 | Ubuntu 22.04 | **Ubuntu 24.04** |
| ROS 2 | Humble | **Jazzy** |
| Gazebo | Gazebo Classic 11 | **Gazebo Harmonic** |
| 仿真启动 | `gazebo_ros/gazebo.launch.py` | `ros_gz_sim/gz_sim.launch.py` |
| 实体生成 | `spawn_entity.py -entity` | `ros_gz_sim create -name` |
| ros2_control 硬件接口 | `gazebo_ros2_control` | `gz_ros2_control`（`GazeboSimSystem`） |
| 世界文件 | `.world`（SDF 1.6） | `.sdf`（SDF 1.9+/1.11） |
| 话题/服务桥接 | 自动桥接 | `parameter_bridge` 显式桥接 |
| 仿真时钟 | 部分节点自动 | 需显式 `use_sim_time: True` |
| Python 环境管理 | 系统 Python 直接 `pip install` | **`.venv` 虚拟环境**（Ubuntu 23.10+ 遵循 PEP 668，详见下方说明） |

> 环境背景：Gazebo Classic 已于 **2025 年 1 月停止维护**，Ubuntu 24.04 软件源中无法直接安装 Classic，因此升级到 Jazzy 后必须迁移到 Gazebo Harmonic（详见下方迁移笔记）。

## Python 虚拟环境（.venv）说明

**为什么需要 .venv？** Ubuntu 从 23.10 起遵循 [PEP 668](https://peps.python.org/pep-0668/)，系统 Python 默认被标记为 "externally managed"，直接 `pip install` 会被拒绝（强行 `--break-system-packages` 不推荐）；而 ROS 2 又绑定系统 Python，无法用 conda 替代（conda 自带的 Python 与系统 Python 并存容易冲突）。因此，**书中第 4 / 7 / 8 章需要安装第三方 Python 库时，本仓库统一使用 `.venv` 虚拟环境**：

| 章节 | 需要的第三方库 | 现成启动脚本 |
|---|---|---|
| `Chap4`（人脸检测服务） | `face_recognition`、`dlib`、OpenCV 等 | `YuXiangROS/Chap4/4.2_4.3_Service_ws/start_venv.zsh` |
| `Chap7`（Nav2 巡逻 + 语音播报） | 语音播报等 | `YuXiangROS/Chap7/Navigation_ws/start_venv.zsh` |
| `Chap8`（Nav2 自定义插件） | 同上 | `YuXiangROS/Chap8/Nav2_Custom_ws/start_venv.zsh` |

**核心命令**（ROS 2 专用姿势，`--system-site-packages` 必须加，否则 venv 里 import 不到 `rclpy`）：

```bash
python3 -m venv .venv --system-site-packages   # 创建（继承系统已装的 ROS 2 包）
source .venv/bin/activate                        # 激活
pip install <package_name>                       # 安装包（无需 sudo）
```

> ⚠️ **两个高频踩坑**：
> 1. `ros2 run` 走系统 Python，找不到 venv 里装的包 —— 必须在 venv 里安装自己的 `colcon`（`pip install --ignore-installed colcon-common-extensions`），并让 `which colcon` 指向 `.venv/bin/colcon`；
> 2. 工作空间路径**不要含空格**，否则 setuptools 生成的 shebang 会被空格截断，导致 `ros2 run` 失败（`4.2 Service_ws` → `4.2_4.3_Service_ws` 即为踩坑后改名重建）。

完整笔记（前置安装、zsh 自动激活、venv vs conda 对比、4 个踩坑详解、一键启动脚本模板）见 **`Docs/About pyvenv.md`**。

## Gazebo Classic → Harmonic 迁移要点

初学者从 Humble + Classic 转向 Jazzy + Harmonic 时，最容易卡住的是 **仿真相关的命令与文件格式全部变了**。以下是本仓库实践中总结的核心差异：

| 关注点 | Gazebo Classic（原书） | Gazebo Harmonic（本仓库） |
|---|---|---|
| 启动仿真 | `gazebo_ros` 包、`gazebo.launch.py`，参数 `world`、`verbose` | `ros_gz_sim` 包、`gz_sim.launch.py`，参数 `gz_args: "-r -v 4 <world>"` |
| 生成机器人 | `spawn_entity.py -entity fishbot -topic /robot_description` | `ros_gz_sim create -name fishbot -topic /robot_description` |
| ros2_control | `gazebo_ros2_control` 插件 | `gz_ros2_control/GazeboSimSystem` 硬件接口 + `gz_ros2_control-system` 插件 |
| 话题桥接 | 默认自动桥接 | 必须显式 `parameter_bridge "<ros话题>@<ROS类型>[<GZ类型>"` |
| 世界文件 | `.world`（SDF 1.6，可引用 `model://` 外部资源） | `.sdf`（SDF 1.9+/1.11，`<sdf><world>` 根结构，模型全内联，插件显式声明如 `gz-sim-physics-system`） |
| 仿真时钟 | 部分节点默认对齐 | 必须为 `robot_state_publisher`、`controller_manager` 等设置 `use_sim_time: True`，否则 TF 时间戳错乱 |
| 速度指令 | `diff_drive_controller` 支持 `use_stamped_vel` | Jazzy 移除该参数，需用 `twist_stamper` 将 `Twist` 转为 `TwistStamped` |
| 控制器启动 | `spawner` 旧参数 | `spawner --param-file <file> --controller-manager-timeout 30` + `OnProcessExit` 事件链 |

**详细教程见**：[About Gazebo Classic vs Harmonic.md](Docs/About%20Gazebo%20Classic%20vs%20Harmonic.md) —— 该笔记约 500 行，涵盖 Classic EOL 背景、启动/桥接/控制逐项对比、世界文件（`.world` → `.sdf`）迁移完整流程与 checklist、以及 8 条常见报错速查表（如 `spawn_entity.py: command not found`、`libgazebo_ros2_control.so: cannot open shared object file` 等）。

典型的迁移示例代码：`YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/launch/gazebo_sim.launch.py`，其中每一处 Harmonic 改动旁均有 `# 旧版: xxx` 注释。

## 各章导读

代码按原书章节组织在 `YuXiangROS/` 下（Chap2 ~ Chap10），每章包含对应主题的独立工作区（workspace）。

| 章节 | 主题 | 主要内容 |
|---|---|---|
| `Chap2` | ROS 2 基础 | 最小 C++/Python 节点、创建 Python/C++ 包（`demo_python_pkg`、`demo_cpp_pkg`）、colcon 工作区（自定义话题发布/订阅、多线程） |
| `Chap3` | 话题 Topic | 小乌龟话题控制（`demo_cpp_topic`）、小说文本话题发布（`demo_python_topic`）、系统状态监控实践（自定义 `SystemStatus.msg` + 发布器 + 订阅显示） |
| `Chap4` | 服务 Service | 自定义 `srv`（`FaceDetector.srv`、`Patrol.srv`）、基于 OpenCV 的人脸检测服务端/客户端（Python）、C++ 服务端与客户端 |
| `Chap5` | TF 坐标变换 | 静态/动态 TF 广播器与监听器（C++ 与 Python），附 rosbag2 回放数据 |
| `Chap6` | URDF 建模 + RViz + Gazebo | 鱼车（fishbot）完整建模：URDF/Xacro、关节、传感器（相机/IMU/激光）、ros2_control 配置、RViz 显示、Gazebo Harmonic 仿真（含 `custom_room.sdf` 三室一厅世界）；**含原创工具 `Dict_To_URDF`** |
| `Chap7` | Nav2 导航 | 基于 `nav2_simple_commander` 的巡逻应用（`patrol_node.py`、`waypoint_follower.py`）、语音播报服务、Nav2 参数配置与地图 |
| `Chap8` | Nav2 自定义插件 + pluginlib | Nav2 自定义控制器插件、自定义全局规划器插件（C++，pluginlib 导出）、pluginlib 插件机制教学示例（`motion_control_system`） |
| `Chap9` | 实体机器人（micro-ROS/雷达） | 实车启动整合（`robot_bringup`）、简化鱼车模型（`robot_description`）、实车 Nav2 导航（`robot_navigation2`）；依赖 4 个第三方包，需自行 clone（见下文） |
| `Chap10` | ROS 2 进阶 | QoS 可靠性测试、Executor 模型、进程内通信（`compose`）、DDS 零拷贝租借消息（`shm_pub`）、时间同步（`message_filter`）、生命周期节点（`lifecyclenode`），附 FastDDS profile 示例 |

## 原创工具：Dict_To_URDF

位于 `YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/Dict_To_URDF/`，是笔者自研的 **JSON / Python 字典转 URDF / Xacro** 工具：

- **`json_to_urdf.py`**：JSON → URDF XML 转换器，完整支持 URDF 1.0 规范元素。基于 dataclass 数据模型（`Origin/Geometry/Material/Inertial/Visual/Collision/Joint/Transmission`），顶层支持 `materials/links/joints/transmissions/gazebo/ros2_control` 标签；内置结构校验（root link 单根树、关节引用、`ros2_control` 硬件/关节引用检查）。
  ```bash
  # 用法: python json_to_urdf.py <input.json> [-o output.urdf] [--no-validate] [--no-pretty]
  python json_to_urdf.py JSON_URDF_demo.json -o JSON_URDF_demo.urdf
  ```
  > 注：默认开启结构校验，`--no-validate` 可跳过；`--no-pretty` 输出紧凑 XML。
- **`Python_Xacro_demo.py`**：用 Python 模拟 xacro 宏机制，调用 `convert()` 生成 URDF。
- **`pyacro_demo/`**：完整的 fishbot "Python acro" 实现，用纯 Python 构建出与 `xacro` 等价的 URDF（含 base/actuator/sensor/plugins 各模块）。

配套 demo：`JSON_URDF_demo.json/.urdf`（简单 demo）、`Python_Xacro_demo.py/.urdf`。

**设计思路**：URDF 本质上是一种"树形结构化数据"，用 JSON/Python dict 表达比 XML 更直观、更易复用。该工具让模型定义与生成逻辑分离——把模型当作数据管理，再用脚本生成标准 URDF/Xacro，适合需要批量生成或程序化管理机器人模型的场景。

## Chap9 第三方依赖包获取

`Chap9/Robot_ws/src/` 下有 4 个第三方包，属于 **git clone 的上游代码**，为避免在仓库中产生嵌套 git 仓库（gitlink）与重复快照，本仓库已通过 `.gitignore` 将其排除，**读者需自行 clone**：

| 包 | 作用 | 来源 |
|---|---|---|
| `micro-ROS-Agent` | micro-ROS 通信代理 | https://github.com/micro-ROS/micro-ROS-Agent |
| `micro_ros_msgs` | micro-ROS 消息定义 | https://github.com/micro-ROS/micro_ros_msgs |
| `ros_serial2wifi` | 串口 ↔ WiFi(UDP/TCP) 透传（fishros 社区示例） | https://github.com/fishros/ros_serial2wifi |
| `ydlidar_ros2` | YDLidar 激光雷达 ROS 2 驱动 | https://github.com/fishros/ydlidar_ros2 |

```bash
cd YuXiangROS/Chap9/Robot_ws/src
git clone https://github.com/micro-ROS/micro-ROS-Agent.git
git clone https://github.com/micro-ROS/micro_ros_msgs.git
git clone https://github.com/fishros/ros_serial2wifi.git
git clone https://github.com/fishros/ydlidar_ros2.git
```

> 建议与上游保持同步：`git pull` 上游更新即可，本仓库不会对这些包做任何改动。其余自写包（`robot_bringup`、`robot_description`、`robot_navigation2`）已正常纳入版本管理。

## 许可证与致谢

- 本仓库的**原创代码、笔记与工具**采用 [Apache License 2.0](LICENSE)，版权归 `HoseaChern`（2026）所有。
- **原书与参考代码**：本仓库代码改编自《ROS2机器人开发 从入门到实践》及其配套仓库 [fishros/ros2bookcode](https://github.com/fishros/ros2bookcode)。**感谢原作者桑欣（fishros）** 的精彩教材与开源精神。本仓库为衍生学习项目，非官方版本，已尽量保留原代码的结构与注释风格，迁移改动均以 `[旧版: xxx]` 标注。
- **第三方包**（micro-ROS-Agent、micro_ros_msgs、ros_serial2wifi、ydlidar_ros2）版权归其各自作者所有，使用请遵循其各自的许可证。
- 若原作者认为本衍生仓库不妥，欢迎通过 issue 联系，笔者将配合修改或下架。

---

*本仓库由 `HoseaChern` 维护，用于个人 ROS 2 学习记录与交流。*
