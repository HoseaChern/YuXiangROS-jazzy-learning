# Gazebo Classic vs Harmonic 写法差异笔记

> **环境信息**：Ubuntu 24.04 | Shell: Zsh | ROS 2 发行版: Jazzy | 仿真器: Gazebo Harmonic
>
> **参考功能包**：`YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description`

---

## 一、两个版本是什么关系？

- **Gazebo Classic**：早期版本（如 Gazebo 11），基于 OGRE 1.x，ROS 1/ROS 2 早期教程大量使用。ROS 2
  Jazzy 不再默认支持。
- **Gazebo Sim / Harmonic**：Gazebo 的新一代版本（Gazebo Sim 8 对应 Harmonic），基于 OGRE 2.
  x，内部通信从 ROS 话题切换到 `gz-transport`，与 ROS 2 通过 `ros_gz` 桥接包交互。

> **关键结论**：Jazzy 官方推荐搭配 **Gazebo Harmonic**，Classic 的写法不能直接复制粘贴。

### 1.1 为什么必须迁移：Gazebo Classic 已停止维护

- **时间线**：Gazebo Classic（Gazebo 9/11）已于 **2025 年 1 月正式停止维护（EOL）**，官方不再提供新版本、
  安全更新与 bug 修复。
- **Ubuntu 24.04 的现实**：`apt` 官方源中**只有 Harmonic**，Classic 已无法直接安装。若坚持使用
  Classic，需走旧版 PPA 或源码编译，依赖冲突多、风险大，对初学者极不友好。
- **教程生态断层**：市面绝大多数教程、书籍、视频（包括本仓库参考的《ROS2 机器人开发》）都基于 humble + Classic，
  新手照抄必然踩坑——这正是本笔记与 `YuXiangROS` 各章适配代码存在的意义。

> 本仓库在 Ubuntu 24.04 + Jazzy + Harmonic 下已验证可用，代码中保留了 `[旧版: xxx]` 对照注释，供迁移时对照。

---

## 二、ROS 包名与依赖

| 项目              | Gazebo Classic                                       | Gazebo Harmonic                                 |
| :---------------- | :--------------------------------------------------- | :---------------------------------------------- |
| 启动 Gazebo 的包  | `gazebo_ros`                                         | `ros_gz_sim`                                    |
| 生成实体的包      | `gazebo_ros`                                         | `ros_gz_sim`                                    |
| ROS-Gazebo 桥接   | `gazebo_ros_pkgs`                                    | `ros_gz_bridge`                                 |
| ros2_control 插件 | `gazebo_ros2_control`                                | `gz_ros2_control`                               |
| 安装命令          | `sudo apt install ros-${ROS_DISTRO}-gazebo-ros-pkgs` | `sudo apt install ros-${ROS_DISTRO}-ros-gz-sim` |

---

## 三、启动 Gazebo

### 3.1 launch 文件路径

| 版本     | 启动文件                             |
| :------- | :----------------------------------- |
| Classic  | `gazebo_ros/launch/gazebo.launch.py` |
| Harmonic | `ros_gz_sim/launch/gz_sim.launch.py` |

### 3.2 世界文件参数

**Classic**：

```python
IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        [get_package_share_directory("gazebo_ros"), "/launch/gazebo.launch.
py"]
    ),
    launch_arguments=[
        ("world", "<world_path>"),
        ("verbose", "true"),
    ],
)
```

**Harmonic**：

```python
IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        [get_package_share_directory("ros_gz_sim"), "/launch/gz_sim.launch.
py"]
    ),
    launch_arguments=[
        # -r: 启动即运行仿真; -v 4: verbose 级别
        ("gz_args", "-r -v 4 <world_path>"),
    ],
)
```

> **注意**：Harmonic 的 `gz_args` 是字符串，Classic 是键值对。

---

## 四、生成机器人实体

### 4.1 节点定义

| 版本     | package      | executable        |
| :------- | :----------- | :---------------- |
| Classic  | `gazebo_ros` | `spawn_entity.py` |
| Harmonic | `ros_gz_sim` | `create`          |

### 4.2 参数差异

**Classic**：

```python
Node(
    package="gazebo_ros",
    executable="spawn_entity.py",
    arguments=["-topic", "/robot_description", "-entity", "fishbot"],
)
```

**Harmonic**：

```python
Node(
    package="ros_gz_sim",
    executable="create",
    arguments=["-topic", "/robot_description", "-name", "fishbot"],
)
```

> **注意**：Classic 用 `-entity` 指定实体名，Harmonic 用 `-name`。

---

## 五、世界文件迁移（.world → .sdf）

世界文件是"Harmonic 与 Classic 不兼容"的重灾区，网上能直接复用的 Classic 世界文件几乎都无法在 Harmonic 加载。

### 5.1 扩展名与 SDF 版本

| 版本     | 扩展名   | SDF 版本              | 根结构                        |
| :------- | :------- | :-------------------- | :---------------------------- |
| Classic  | `.world` | 1.6 / 1.7             | `<sdf version="1.6"><world>`  |
| Harmonic | `.sdf`   | 1.9+（本仓库用 1.11） | `<sdf version="1.11"><world>` |

> Classic 的 `.world` 本质也是 SDF，但版本低、默认行为不同；Harmonic 只认 `.sdf`，且许多老写法（如不写系统插件）
> 会导致加载异常。

### 5.2 资源引用方式差异（最容易踩的坑）

**Classic**：通过 `<include><uri>model://xxx</uri></include>` 引用模型数据库，
或直接引用 `model://cafe_table/meshes/cafe_table.dae` 网格（原书 `custom_room.world`
即此写法）：

```xml
<sdf version="1.6">
  <world name="custom_room">
    <include><uri>model://ground_plane</uri></include>
    <include><uri>model://sun</uri></include>
    <model name="cafe_table_1">
      <include><uri>model://cafe_table</uri></include>
    </model>
  </world>
</sdf>
```

**Harmonic**：不再自动附带模型数据库，`model://` 引用常因资源缺失而失败。本仓库的 `custom_room.sdf`
采用**全内联**写法——每个模型（地面、墙、家具）都用 `<model>` + `<link>` + `<geometry><box>` 显式定义，
并把系统插件、场景、光照写全：

```xml
<sdf version="1.11">
  <world name="apartment_three_bedroom">
    <!-- 物理与系统插件：Harmonic 必须显式声明，Classic 会自动加载 -->
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
    </physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"
/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems:
:SceneBroadcaster" />
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <!-- 场景与光照 -->
    <scene>
      <ambient>0.45 0.45 0.45 1.0</ambient>
      <shadows>true</shadows>
      <grid>false</grid>
    </scene>

    <!-- 全部模型内联定义 -->
    <model name="room_structure">
      <static>true</static>
      <link name="wall_north">
        <pose>0.0 7.6 1.5 0 0 0</pose>
        <visual name="visual"><geometry><box><size>20.4 0.2 3.
0</size></box></geometry></visual>
        <collision name="collision"><geometry><box><size>20.4 0.2 3.
0</size></box></geometry></collision>
      </link>
      <!-- ... 其余墙、家具同理 ... -->
    </model>
  </world>
</sdf>
```

### 5.3 迁移 checklist

- [ ] 扩展名改为 `.sdf`，`<sdf version>` 升级到 1.9+（本仓库用 1.11）
- [ ] 检查所有 `model://` 引用：确认资源本地存在，否则改为全内联定义
- [ ]
  显式声明系统插件：`gz-sim-physics-system`、`gz-sim-scene-broadcaster-system`、`gz-sim-s
  ensors-system` 等
- [ ] 用 `gz sim -s <world.sdf>`（无 GUI 模式）验证世界能否正常加载
- [ ] 注意 `<physics>` 标签在 SDF 1.11 的取值变化（`type="ignored"` 等）

> 完整可运行的迁移实例：`YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/world/cu
> stom_room.sdf`（三室一厅室内世界，带家具碰撞体，可直接用于导航/避障仿真）。

---

## 六、ROS-Gazebo 话题桥接

Harmonic 内部使用 `gz-transport` 话题，ROS 2 侧通过 `ros_gz_bridge` 桥接。

### 5.1 桥接格式

```python
"/ros_topic@ros_msg_type<方向符号>gz_msg_type"
```

- `[`：Gazebo → ROS
- `]`：ROS → Gazebo

### 5.2 常用话题

**Classic**：由 Gazebo 原生插件直接发布/订阅 ROS 话题，无需桥接。

**Harmonic**：

```python
arguments=[
    # GZ → ROS: 仿真时钟
    "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
    # ROS → GZ: 速度指令（Gazebo 原生差速插件方式）
    "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
    # GZ → ROS: 里程计
    "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
    # GZ → ROS: TF
    "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
    # GZ → ROS: 关节状态
    "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
    # GZ → ROS: 传感器数据
    "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
    "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
    "/camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
]
```

> **重要冲突**：若使用 `ros2_control`，`/cmd_vel`、`/odom`、`/tf`、`/joint_states`
> 由控制器直接接管，**不能再桥接**，否则会出现话题冲突。

### 5.3 别忘了 use_sim_time

Harmonic 通过桥接发布仿真时钟 `/clock`，但**只有开启 `use_sim_time` 的节点才会使用它**。若未开启，TF
时间戳与真实时钟漂移，会出现 TF 报错、传感器数据乱序等诡异问题。

```python
# 为节点（或节点组）设置
Node(..., parameters=[{"use_sim_time": True}])
```

```yaml
# 或 yaml 全局配置
/**: ros__parameters: use_sim_time: true
```

> 本仓库所有仿真 launch（Chap6/7/9 的 `gazebo_sim.launch.py`、导航参数）均开启 `use_sim_time`；
> 真机运行时才关闭。

---

## 七、差速驱动插件

### 6.1 Classic

```xml
<gazebo>
  <plugin name="differential_drive_controller"
filename="libgazebo_ros_diff_drive.so">
    <ros>
      <namespace>/</namespace>
      <remapping>cmd_vel:=cmd_vel</remapping>
      <remapping>odom:=odom</remapping>
    </ros>
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint>
    <wheel_separation>0.2</wheel_separation>
    <wheel_diameter>0.064</wheel_diameter>
    <publish_odom_tf>true</publish_odom_tf>
  </plugin>
</gazebo>
```

### 6.2 Harmonic

```xml
<gazebo>
  <plugin filename="gz-sim-diff-drive-system" name="gz::sim::systems::
DiffDrive">
    <topic>/cmd_vel</topic>
    <odom_topic>/odom</odom_topic>
    <tf_topic>/tf</tf_topic>
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.2</wheel_separation>
    <wheel_radius>0.032</wheel_radius>
    <frame_id>odom</frame_id>
    <child_frame_id>base_footprint</child_frame_id>
    <odom_publish_frequency>30</odom_publish_frequency>
  </plugin>

  <!-- Harmonic 需要显式添加关节状态发布插件 -->
  <plugin filename="gz-sim-joint-state-publisher-system"
    name="gz::sim::systems::JointStatePublisher">
    <topic>/joint_states</topic>
    <joint_name>left_wheel_joint</joint_name>
    <joint_name>right_wheel_joint</joint_name>
  </plugin>
</gazebo>
```

> **差异点**：
>
> - Classic 用 `wheel_diameter`（直径），Harmonic 用 `wheel_radius`（半径）；
> - - Classic 的 diff_drive 自带关节状态发布，Harmonic
>   需要额外添加 `gz-sim-joint-state-publisher-system`。

---

## 八、传感器插件

### 7.1 激光雷达

**Classic**：

```xml
<gazebo reference="laser_link">
  <sensor type="ray" name="laserscan">
    <plugin name="gazebo_ros_laser_controller" filename="libgazebo_ros_laser.
so">
      <topic_name>/scan</topic_name>
      <frame_name>laser_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

**Harmonic**：

```xml
<gazebo reference="laser_link">
  <sensor name="laserscan" type="gpu_lidar">
    <always_on>true</always_on>
    <visualize>true</visualize>
    <update_rate>5</update_rate>
    <topic>scan</topic>
    <frame_id>laser_link</frame_id>
    <gz_frame_id>laser_link</gz_frame_id>
    <lidar>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>0</min_angle>
          <max_angle>6.28</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.12</min>
        <max>8.0</max>
        <resolution>0.015</resolution>
      </range>
    </lidar>
  </sensor>
</gazebo>
```

> **差异点**：
>
> - Classic 传感器类型为 `ray`，Harmonic 为 `gpu_lidar`；
> - - Classic 需要单独 `<plugin>` 把数据转 ROS，Harmonic 通过 `<topic>` 直接发布
>   gz-transport 话题，再由 `ros_gz_bridge` 桥接；
> - Harmonic 需要 `<frame_id>` 和 `<gz_frame_id>`。

### 7.2 IMU

**Classic**：

```xml
<gazebo reference="imu_link">
  <sensor type="imu" name="imu_sensor">
    <plugin filename="libgazebo_ros_imu_sensor.so" name="imu_plugin">
      <topic>imu</topic>
    </plugin>
  </sensor>
</gazebo>
```

**Harmonic**：

```xml
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <topic>imu</topic>
    <frame_id>imu_link</frame_id>
    <gz_frame_id>imu_link</gz_frame_id>
    <update_rate>100</update_rate>
    <always_on>true</always_on>
    <imu>
      <angular_velocity>
        <x><noise type="gaussian"><mean>0.
0</mean><stddev>2e-4</stddev></noise></x>
        <!-- y, z 同理 -->
      </angular_velocity>
    </imu>
  </sensor>
</gazebo>
```

### 7.3 深度/RGBD 相机

**Classic**：

```xml
<gazebo reference="camera_link">
  <sensor type="depth" name="camera_sensor">
    <plugin name="camera_plugin" filename="libgazebo_ros_depth_camera.so">
      <topic>camera</topic>
    </plugin>
  </sensor>
</gazebo>
```

**Harmonic**：

```xml
<gazebo reference="camera_link">
  <sensor name="camera_sensor" type="rgbd_camera">
    <topic>camera</topic>
    <frame_id>camera_optical_link</frame_id>
    <gz_frame_id>camera_optical_link</gz_frame_id>
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <camera name="camera">
      <horizontal_fov>1.5009831567</horizontal_fov>
      <image>
        <width>800</width>
        <height>600</height>
        <format>R8G8B8</format>
      </image>
    </camera>
  </sensor>
</gazebo>
```

> **差异点**：Classic 用 `depth` 类型 + ROS 插件，Harmonic 用 `rgbd_camera` 类型，直接输出彩色图、
> 深度图、点云。

---

## 九、ros2_control

### 8.1 硬件插件

| 版本     | hardware plugin                    | Gazebo 插件                 |
| :------- | :--------------------------------- | :-------------------------- |
| Classic  | `gazebo_ros2_control/GazeboSystem` | `libgazebo_ros2_control.so` |
| Harmonic | `gz_ros2_control/GazeboSimSystem`  | `gz_ros2_control-system`    |

### 8.2 Harmonic 配置示例

```xml
<ros2_control name="FishBotGazeboSystem" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>
  <joint name="left_wheel_joint">
    <command_interface name="velocity">
      <param name="min">-1</param>
      <param name="max">1</param>
    </command_interface>
    <state_interface name="position" />
    <state_interface name="velocity" />
  </joint>
</ros2_control>

<gazebo>
  <plugin filename="gz_ros2_control-system"
    name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <parameters>$(find
fishbot_description)/config/ros2_controller/controllers.yaml</parameters>
  </plugin>
</gazebo>
```

### 8.3 Jazzy 特别提醒

Jazzy 的 `diff_drive_controller` 已移除 `use_stamped_vel` 参数，
**强制订阅 `geometry_msgs/msg/TwistStamped`**。如果键盘节点发布的是 `Twist`，
需要通过 `twist_stamper` 转换：

```bash
ros2 run twist_stamper twist_stamper \
  --ros-args \
  -r cmd_vel_in:=/cmd_vel \
  -r cmd_vel_out:=/cmd_vel_stamped
```

---

## 十、控制方式切换与冲突

`fishbot_description` 功能包提供两种控制方式，**不能同时启用**：

| 方式                   | 控制源                     | 是否需要桥接 `/cmd_vel` `/odom` `/tf` `/joint_states` |
| :--------------------- | :------------------------- | :---------------------------------------------------- |
| A. Gazebo 原生差速插件 | `gz-sim-diff-drive-system` | 需要                                                  |
| B. ros2_control        | `diff_drive_controller`    | 不需要                                                |

切换步骤：

1. 在 `urdf/fishbot/fishbot.urdf.xacro` 中切换 include 的插件文件；
2. 在 `launch/gazebo_sim.launch.py` 中切换桥接话题和是否启动控制器 spawner；
3. 重新 `colcon build` 后启动。

> 若两种方式同时启用，Gazebo 会报关节被多个控制器争夺的错误，小车行为异常。

---

## 十一、速查表

| 功能                     | Classic                            | Harmonic                          |
| :----------------------- | :--------------------------------- | :-------------------------------- |
| 启动包                   | `gazebo_ros`                       | `ros_gz_sim`                      |
| 启动文件                 | `gazebo.launch.py`                 | `gz_sim.launch.py`                |
| 世界参数                 | `("world", path)`                  | `("gz_args", "-r -v 4 path")`     |
| spawn 包/可执行          | `gazebo_ros/spawn_entity.py`       | `ros_gz_sim/create`               |
| spawn 实体名参数         | `-entity`                          | `-name`                           |
| 差速插件                 | `libgazebo_ros_diff_drive.so`      | `gz-sim-diff-drive-system`        |
| 差速直径/半径            | `wheel_diameter`                   | `wheel_radius`                    |
| 激光雷达类型             | `ray`                              | `gpu_lidar`                       |
| 深度相机类型             | `depth`                            | `rgbd_camera`                     |
| ros2_control 硬件        | `gazebo_ros2_control/GazeboSystem` | `gz_ros2_control/GazeboSimSystem` |
| ros2_control Gazebo 插件 | `libgazebo_ros2_control.so`        | `gz_ros2_control-system`          |

---

## 十二、常见报错速查（初学者高频）

| 报错现象                                                      | 原因                                                   | 解法                                                                            |
| :------------------------------------------------------------ | :----------------------------------------------------- | :------------------------------------------------------------------------------ |
| `spawn_entity.py: command not found`                          | 用了 Classic 的 `spawn_entity.py` 可执行文件           | 改用 `ros_gz_sim` 的 `create`，`-entity` 改 `-name`                             |
| `package 'gazebo_ros' not found`                              | Jazzy 没有 `gazebo_ros` 包                             | 安装 `ros-jazzy-ros-gz-sim`，launch 改用 `ros_gz_sim`                           |
| `libgazebo_ros2_control.so: cannot open shared object file`   | 用了 Classic 的 ros2_control 插件                      | 改用 `gz_ros2_control-system` + `gz_ros2_control/GazeboSimSystem`               |
| `[Err] [ModelDatabase] model://xxx not found`                 | Classic 世界的 `model://` 资源在 Harmonic 中不存在     | 改为全内联模型定义（见"世界文件迁移"）                                          |
| 无 `/clock` 话题 / TF 时间戳跳跃                              | 未桥接 `/clock` 或未开 `use_sim_time`                  | 桥接 `/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock` 并设置 `use_sim_time: True` |
| 关节被多个控制器争夺，小车不动                                | 同时启用了原生差速插件与 ros2_control                  | 二选一（见"控制方式切换"）                                                      |
| 发布 `cmd_vel` 但小车不动                                     | Jazzy 的 `diff_drive_controller` 默认收 `TwistStamped` | 加 `twist_stamper` 转换（见"ros2_control"章）                                   |
| `Failed to load plugin [gz-sim-sensors-system]`，传感器无数据 | Harmonic 世界/URDF 缺系统插件                          | 显式声明 `gz-sim-physics-system`、`gz-sim-sensors-system` 等                    |

---

笔记整理日期：2026年7月；2026年8月补充 EOL 背景、世界文件迁移、use_sim_time 与报错速查

参考：ROS 2 Jazzy 官方安装文档、Gazebo Harmonic 官方文档、原书《ROS2 机器人开发》配套仓库
fishros/ros2bookcode
