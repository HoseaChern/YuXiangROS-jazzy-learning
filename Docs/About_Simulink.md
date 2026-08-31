# MATLAB / Simulink 使用笔记

> **环境信息**：Ubuntu 24.04 | Shell: Zsh | ROS 2 发行版: Jazzy | 仿真器: Gazebo Harmonic + CoppeliaSim
>
> **版本配对**：MATLAB R2025a 官方推荐的 ROS 2 发行版为 **Jazzy Jalisco**（R2025a–R2026a 均推荐 Jazzy），与当前环境完全匹配。

---

## 一、MATLAB / Simulink 在工作流中的定位

MATLAB 与 Simulink 在机器人开发工作流中扮演的是 **"算法设计层"** 角色，与 ROS 的 **"通信与调度层"**、仿真器的 **"物理世界层"** 互补，构成完整的三层开发链路：

```text
┌─────────────────────────────────────────────┐
│  算法设计层    MATLAB / Simulink              │  建模、仿真、验证、代码生成
├─────────────────────────────────────────────┤
│  通信与调度层  ROS 2 (Jazzy)                   │  Topic/Service/参数/生命周期
├─────────────────────────────────────────────┤
│  物理世界层    Gazebo Harmonic / CoppeliaSim   │  物理引擎、传感器、渲染
└─────────────────────────────────────────────┘
```

### 具体作用

| 作用                  | 说明                                                                           |
| --------------------- | ------------------------------------------------------------------------------ |
| **控制系统设计**      | 状态空间、传递函数、频域分析、LQR/MPC 等控制算法的建模与仿真                   |
| **Simulink 模型仿真** | 可视化搭建机器人动力学模型与控制器，拖拽式建模，无需手写微分方程求解           |
| **代码生成**          | Simulink Coder / MATLAB Coder 可从模型直接生成 C/C++ 代码，甚至生成 ROS 2 节点 |
| **数据分析**          | 处理 `ros2 bag` 录制的数据：回放、滤波、FFT、绘图，验证算法效果                |
| **算法预研**          | 在纯数学环境中快速验证算法逻辑，确认后再迁移到 ROS 节点                        |

---

## 二、与 Ubuntu 24.04 + ROS 2 Jazzy 的配合

### 2.1 官方支持情况

MATLAB 的 **ROS Toolbox** 提供 ROS/ROS 2 接口，支持创建节点、发布/订阅 Topic、调用 Service、读写参数、录制/回放 rosbag，并可连接外部仿真器（Gazebo 等）。

官方版本矩阵（ROS Toolbox System Requirements）：

| MATLAB 版本     | 推荐的 ROS 发行版 | 推荐的 ROS 2 发行版 |
| --------------- | ----------------- | ------------------- |
| R2025a – R2026a | Noetic Ninjemys   | **Jazzy Jalisco**   |
| R2023b – R2024b | Noetic Ninjemys   | Humble Hawksbill 等 |

关键结论：**R2025a 与 ROS 2 Jazzy 是官方配对**，且你的 Ubuntu 24.04 正是 Jazzy 的官方适配系统，无需为版本兼容性担忧。

### 2.2 两种部署形态

| 部署形态             | 做法                                                        | 优劣                                                        |
| -------------------- | ----------------------------------------------------------- | ----------------------------------------------------------- |
| **同机部署（推荐）** | MATLAB 直接装在 Ubuntu 24.04 上，与 ROS 2 共享本机 DDS 通信 | 零网络配置，`ros2 node list` 直接看到 MATLAB 节点，最稳妥   |
| **跨机部署**         | MATLAB 在 Windows/macOS，通过 DDS 与 Ubuntu 上的 ROS 2 通信 | 需统一 RMW 实现、配置 `ROS_DOMAIN_ID`、放行防火墙，复杂度高 |

同机部署是 MathWorks 官方推荐形态：ROS Toolbox 在 Linux 上是原生支持，DDS 发现机制在同一主机的环回接口上开箱即用。

### 2.3 同机部署的基本用法

```matlab
% 在 MATLAB 中连接到 ROS 2 网络（默认 DDS，同机无需额外配置）
ros2init

% 查看当前网络中的节点
ros2 node list

% 发布 / 订阅 Topic 示例
pub = ros2publisher('/chatter', 'std_msgs/String');
msg = ros2message(pub);
msg.data = 'Hello from MATLAB';
send(pub, msg);

sub = ros2subscriber('/chatter', 'std_msgs/String');
msg = receive(sub, 10);
```

若本机同时运行多个 ROS 2 应用，保持 `ROS_DOMAIN_ID` 一致即可（Ubuntu 端 `.bashrc` 与 MATLAB 端 Preferences → ROS Toolbox 中同步设置）。

### 2.4 与仿真器的联合

| 仿真器              | 联合方式                           | 说明                                                                                         |
| ------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------- |
| **Gazebo Harmonic** | Simulink Co-Simulation（官方支持） | MathWorks 提供 Simulink 与 Gazebo 的同步联合仿真示例，Simulink 发指令、Gazebo 回传传感器数据 |
| **CoppeliaSim**     | Remote API 或 ROS 桥接             | MATLAB 通过 Remote API 直接控制场景，或经 ROS 2 中间层联动                                   |

---

## 三、MATLAB 能否被替代

### 3.1 可被 Python 栈替代的部分

| 场景               | Python 替代   | 评估                                    |
| ------------------ | ------------- | --------------------------------------- |
| 矩阵运算、数值计算 | NumPy + SciPy | 完全可替代                              |
| 绘图               | Matplotlib    | 功能足够，美观度略逊                    |
| ROS 2 节点开发     | rclpy         | 原生 Python API，比 MATLAB 工具箱更直接 |
| 数据处理           | Pandas        | 更强                                    |

### 3.2 难以替代的部分（MATLAB 的护城河）

| 场景                        | 说明                                                   |
| --------------------------- | ------------------------------------------------------ |
| **Simulink 图形化建模**     | 拖拽式搭建动力学模型与控制器，Python 无直接对标物      |
| **代码生成**                | 从模型直接生成 C/C++ 或 ROS 2 节点，省去手写嵌入式代码 |
| **Control System Toolbox**  | 频域分析、状态空间设计、LQR/MPC 的工具链成熟度高       |
| **Robotics System Toolbox** | 运动学、轨迹规划、传感器融合的开箱即用算法             |

> 结论：**纯数值计算 + ROS 2 节点开发，Python 完全可以替代；但涉及 Simulink 建模、代码生成、控制工具箱深度使用时，MATLAB 没有成熟的开源替代。**

---

## 四、其他值得介绍的内容

### 4.1 Simulink External Mode（在线调参）

Simulink 支持 **External Mode**：模型在 Ubuntu 上运行，可以在 Simulink 界面中在线修改参数、实时观察 ROS 2 数据流，适合 PID 调参、控制器在线整定。

### 4.2 自动生成 ROS 2 节点

Simulink Coder 支持将模型编译为 ROS 2 节点（C++），直接部署到 ROS 2 网络中，实现"模型到节点"的一站式流程——这在需要把控制算法下放到嵌入式硬件时价值很大。

### 4.3 rosbag 数据工作流

```text
Ubuntu: ros2 bag record → MATLAB: 导入/回放/分析 → 验证算法 → 回到 ROS 2 部署
```

MATLAB 可直接读取 rosbag 文件（`ros2bagReader`），用于离线分析仿真或实机数据。

### 4.4 许可与安装注意

| 事项       | 说明                                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------------- |
| 许可       | 需要 MATLAB + Simulink + ROS Toolbox 三个组件的许可                                                     |
| Linux 安装 | 官方提供 Linux 安装器，R2025a 在 Ubuntu 24.04 有成功案例，后续版本官方支持列表明确包含 Ubuntu 24.04 LTS |
| 体积       | 完整安装占用数十 GB，建议按需选择组件                                                                   |

---

## 五、总结

| 维度             | 结论                                                                    |
| ---------------- | ----------------------------------------------------------------------- |
| **版本兼容性**   | R2025a 官方配对 ROS 2 Jazzy，与 Ubuntu 24.04 环境完全匹配，无兼容性顾虑 |
| **推荐形态**     | MATLAB 装在 Ubuntu 24.04 同机部署，走本机 DDS，免去跨机网络配置         |
| **工作流定位**   | 算法设计层：Simulink 建模仿真 + 代码生成 + rosbag 数据分析              |
| **可替代性**     | 数值计算/节点开发可被 Python 替代；Simulink/代码生成/控制工具箱不可替代 |
| **与仿真器协同** | 官方支持 Gazebo Co-Simulation；CoppeliaSim 走 Remote API 或 ROS 桥接    |

**一句话**：MATLAB/Simulink 的价值不在"与 ROS 竞争"，而在 **"算法设计与验证的上游环节"**——先用 Simulink 把控制算法建模、仿真、调参验证，确认后或生成 ROS 2 节点部署，或迁移到 Python/rclpy 实现，与现有 Ubuntu 24.04 + Jazzy + Gazebo/CoppeliaSim 的体系互补使用。
