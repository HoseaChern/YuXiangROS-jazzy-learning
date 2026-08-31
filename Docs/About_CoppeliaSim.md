# CoppeliaSim 使用笔记

> **环境信息**：Ubuntu 24.04 | Shell: Zsh | ROS 2 发行版: Jazzy | 仿真器: Gazebo Harmonic（对比参照）

**CoppeliaSim**（原名 **V-REP**，Virtual Robot Experimentation Platform）是一款功能全面的 **机器人仿真软件** ，与 ROS、Matlab 可以无缝配合。简单来说，它就是一个 **"虚拟试验场"** ——可以在电脑里搭建机器人、传感器、环境，先跑通算法、验证控制逻辑，再放到真实硬件上。

---

## 一、它是什么

| 项目   | 说明                                                                                    |
| :----- | :-------------------------------------------------------------------------------------- |
| 出身   | 由 Coppelia Robotics 开发，2019 年底从 V-REP 更名而来，完全兼容旧版                     |
| 定位   | 通用机器人仿真平台，号称机器人仿真器里的"瑞士军刀"                                      |
| 许可   | 教育版（EDU）功能完整、免费非商用；专业版（Pro）收费可商用；Player 版仅运行仿真不可编辑 |
| 跨平台 | Windows / Linux / macOS 通用，场景文件单文件跨系统直接打开                              |

---

## 二、核心能力

### 2.1 多物理引擎支持

内置 **5 种物理引擎**：MuJoCo、ODE、Bullet、Vortex、Newton。不同引擎在摩擦力、软体、碰撞精度上各有侧重，可按需切换。

### 2.2 分布式控制架构

场景里的**每个物体/模型**都可以独立挂控制脚本，支持：

- **内置脚本**：Lua（原生）、Python
- **外部程序**：C/C++、Java、Matlab/Octave
- **ROS/ROS2 节点**：直接作为 ROS 网络中的一个节点运行

### 2.3 丰富的 API 与传感器仿真

- **400+ API 函数**，可精细控制仿真步进、关节、力、碰撞检测等
- 内置视觉传感器、激光雷达、力传感器、接近传感器等
- 支持路径规划（OMPL 库）、图像处理（OpenCV）

### 2.4 模型导入方便

支持 URDF、SDF、STL、OBJ、Collada 等格式，可从 SolidWorks 等 CAD 软件导出机器人模型直接导入仿真。

---

## 三、与现有工具的关系

既然已经在用 **ROS** 和 **Matlab**，CoppeliaSim 可以非常自然地嵌入工作流：

| 组合方式               | 作用                                                                                                                                                     |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CoppeliaSim + ROS/ROS2 | 内置 ROS/ROS2 接口插件，可直接发布/订阅 Topic、调用 Service、广播 TF2。仿真里的机器人就是 ROS 网络中的一个真实节点。                                     |
| CoppeliaSim + Matlab   | 通过 **Remote API** 或 **ROS 中间件**实现联合仿真。Matlab 写控制算法，CoppeliaSim 做物理仿真和可视化。典型场景：四足机器人步态规划、机械臂逆运动学验证。 |
| 三者一起用             | Matlab 做高层决策/算法 → ROS 做通信中间件 → CoppeliaSim 做底层物理仿真与可视化，形成完整的数字孪生链路。                                                 |

---

## 四、与 Gazebo Harmonic 的对比

从已经熟悉的 **Gazebo Harmonic** 出发，CoppeliaSim 和它的关系可以概括为一句话：**同赛道、不同设计哲学的直接竞品**——两者都是通用机器人物理仿真平台，但 Gazebo 是 ROS 生态的"官方仿真器"，CoppeliaSim 是独立通用的"瑞士军刀"。

### 4.1 核心关系定位

| 维度        | Gazebo Harmonic                              | CoppeliaSim                                  |
| :---------- | :------------------------------------------- | :------------------------------------------- |
| 出身        | Open Robotics 基金会开源项目，ROS 生态"嫡系" | Coppelia Robotics 公司商业产品（教育版免费） |
| 设计哲学    | 模块化、可深度定制、研究导向的"仿真引擎"     | 集成化、开箱即用、教育与应用并重的"仿真软件" |
| 与 ROS 关系 | **原生深度绑定**，ROS 工具链无缝集成         | 通过官方插件桥接 ROS1/ROS2，功能完整但非原生 |
| 开源性      | 完全开源（Apache 2.0）                       | 闭源，教育版（EDU）免费且功能无阉割          |

### 4.2 关键差异（从 Gazebo 用户视角）

#### 易用性与学习曲线

- **Gazebo Harmonic**：场景搭建依赖 SDF/URDF 文件手写或导入，GUI 编辑器相对"原始"，配置环境（尤其是非 Linux）容易踩坑。
- **CoppeliaSim**：提供**可视化场景编辑器**，内置大量机器人、传感器、环境模型，鼠标拖拽即可搭建场景。Lua 脚本直接内嵌在对象上，调试直观。

> 一句话感受：Gazebo 像"用代码搭乐高"，CoppeliaSim 像"用 GUI 搭乐高"。

#### 跨平台体验

- **Gazebo Harmonic**：原生为 Linux 设计，Windows/macOS 支持较弱或体验打折。
- **CoppeliaSim**：Windows / Linux / macOS **三平台原生支持**，场景文件单文件跨系统直接打开，体验一致。

#### 物理引擎选择

- **Gazebo Harmonic**：ODE、Bullet、DART、Simbody
- **CoppeliaSim**：**MuJoCo、Bullet、ODE、Vortex、Newton**（5 种，可按任务切换）

CoppeliaSim 额外集成了 MuJoCo 和 Vortex，在接触动力学、软体仿真等场景下精度更高。有定量实验显示，CoppeliaSim 的 IMU 数据准确性（0.98）略高于 Gazebo（0.95），实时因子也略优（0.95 vs 0.92）。

#### 编程与控制方式

- **Gazebo Harmonic**：主要通过 C++ 插件 / Python 脚本 / ROS 节点控制，控制器通常作为外部进程运行。
- **CoppeliaSim**：支持 **Lua（原生内嵌）、Python、C/C++、Matlab、Java、Octave**。最独特的是**分布式控制架构**——场景里每个物体/模型都可以独立挂脚本，互不干扰，多机器人协同仿真非常方便。

#### ROS 生态深度

这是 Gazebo 最硬的护城河：

- **Gazebo Harmonic**：与 ROS2 Jazzy/Humble 原生配套，SLAM、Navigation、MoveIt 等工具链开箱即用，社区模型库（TurtleBot、Fetch 等）极其丰富。
- **CoppeliaSim**：通过 `simROS` / `simROS2` 插件实现 Topic 订阅/发布、Service、TF2 等，功能完整，但生态丰富度和社区教程量明显不如 Gazebo+ROS 组合。

### 4.3 选型建议

| 场景                                    | 推荐选择        | 理由                                         |
| :-------------------------------------- | :-------------- | :------------------------------------------- |
| 重度 ROS2 开发（SLAM、Nav2、MoveIt）    | Gazebo Harmonic | 原生生态，社区资源最多，迁移真机最顺滑       |
| 快速原型验证 / 教学演示                 | CoppeliaSim     | 搭建场景快，可视化好，学生上手门槛低         |
| 跨平台协作（团队有 Windows/macOS 用户） | CoppeliaSim     | 三平台体验一致，无需折腾 WSL/Docker          |
| Matlab/Simulink 联合仿真                | CoppeliaSim     | 官方支持 Matlab Remote API，联动更成熟       |
| 多机器人分布式控制                      | CoppeliaSim     | 每个模型独立脚本，天然支持多智能体           |
| 需要完全掌控底层 / 二次开发             | Gazebo Harmonic | 开源，可改物理引擎、传感器插件源码           |
| 强化学习训练（需 MuJoCo 精度）          | CoppeliaSim     | 内置 MuJoCo 引擎，且支持无界面 headless 模式 |

---

## 五、典型应用场景

- **算法验证**：先在仿真里跑通路径规划、避障、抓取，再上真机
- **多机器人协作**：利用分布式架构同时仿真多个机器人
- **传感器融合测试**：模拟摄像头、IMU、激光雷达数据，验证 SLAM/感知算法
- **数字孪生**：与真实机器人同步运行，用于监控和调试
- **教学演示**：软件自带大量示例场景（机械臂、移动机器人、人形机器人等），开箱即用

---

## 六、上手建议

1. **下载**：官网 [coppeliarobotics.com](https://www.coppeliarobotics.com/) 下载 **EDU 版本**（免费、功能无阉割）
2. **入门路径**：先跑自带示例场景 → 学 Lua 内置脚本控制关节 → 尝试用 Python Remote API 外部控制 → 最后接入 ROS/Matlab 工作流
3. **版本注意**：V4 版本后 API 命名有变化（旧版 `vrep.*` → 新版 `sim.*`），看教程时注意版本对应

---

## 七、总结

> **Gazebo Harmonic 是 ROS 生态里的"专业赛道"，CoppeliaSim 是跨平台的"通用瑞士军刀"。** 前者胜在生态深度，后者胜在易用广度和跨平台一致性。两者不是替代关系，而是根据项目阶段和需求互相补充。

对 ROS + Matlab 用户的实用建议：**两者可以互补，不必二选一**。

- **继续用 Gazebo Harmonic**：当项目深度依赖 ROS2 导航、SLAM、MoveIt 等工具链时，Gazebo 仍是首选。
- **引入 CoppeliaSim**：当需要**快速验证一个控制算法**、**给团队做演示**、**与 Matlab 做联合仿真**、或者**在 Windows 上临时跑仿真**时，CoppeliaSim 的效率会高很多。

实际很多研究者会**双持**：用 CoppeliaSim 做前期快速原型和算法验证，确认逻辑无误后再迁移到 Gazebo+ROS 的完整系统里做集成测试。学习曲线也会很平缓——它的价值在于**把 ROS 的通信框架和 Matlab 的算法能力，落地到一个高保真的物理仿真环境里**，可以先从"用 Matlab 控制 CoppeliaSim 里的机械臂"这种联合仿真小项目入手。
