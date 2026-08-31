# ROS 2 四大通信机制详解

> **环境信息**：Ubuntu 24.04 | Shell: Zsh | ROS 2 发行版: Jazzy | 仿真器: Gazebo Harmonic
>
> **关联工作空间**：`Chap7/Navigation_ws`（原书，Nav2 导航）、`Chap7/Action_ws`（补充工作空间，原书无）。

---

## 一、为什么需要四种通信机制？

ROS 2 的四种通信方式并非冗余，而是针对不同**时间尺度**与**交互模式**的精确分层。
一个机器人系统里，传感器持续产生数据、控制器需要临时请求、导航是分钟级长任务、运行参数需要随时调整——
没有单一机制能高效覆盖所有这些场景。

| 机制               | 解决的问题                       | 时间尺度        |
| :----------------- | :------------------------------- | :-------------- |
| **话题 Topic**     | 持续产生的数据如何被多方无声消费 | 毫秒级 ~ 持续流 |
| **服务 Service**   | 如何快速完成一次请求-响应事务    | 毫秒级 ~ 单次   |
| **动作 Action**    | 长任务如何报告进度并允许取消     | 秒级 ~ 分钟级   |
| **参数 Parameter** | 节点运行时的配置如何管理         | 初始化 / 调试时 |

---

## 二、四种机制详解

### 2.1 话题（Topic）— 发布 / 订阅模型

**通信模型**：单向、异步、多对多、无状态。

```text
Publisher A ──┐
Publisher B ──┼──→ /scan ──├──→ Subscriber X
Publisher C ──┘            ├──→ Subscriber Y
                           └──→ Subscriber Z
```

**关键特征**：

- **解耦**：发布者与订阅者互不知晓对方存在，仅通过话题名称松耦合连接
- **异步非阻塞**：`publish()` 立即返回，不等待订阅者处理
- **无反馈**：发布者不知道消息是否被成功接收和处理
- **QoS 策略**：支持 `Reliable` / `Best Effort`、`Keep Last` / `Keep All` 等策略，适配不同网络环境

**典型场景**：激光雷达点云 `/scan`、IMU 数据 `/imu`、摄像头图像 `/camera/image_raw`、速度指令 `/cmd_vel`。

**代码示例（Python）**：

```python
from std_msgs.msg import String

# 创建发布者，队列深度 10
pub = node.create_publisher(String, "chatter", 10)
pub.publish(String(data="hello"))

# 创建订阅者
sub = node.create_subscription(
    String, "chatter",
    lambda msg: node.get_logger().info(f"Received: {msg.data}"),
    10,
)
```

> **注意**：话题是"单向广播"，没有请求-响应语义。若需要"把结果告诉我"，请用服务或动作。

---

### 2.2 服务（Service）— 请求 / 响应模型

**通信模型**：双向、同步（语义上）、一对一、有状态。

```text
Client ──Request──→ Server
       ←─Response──
```

**关键特征**：

- **同步语义**：客户端调用后阻塞等待结果（底层基于异步 Future，但使用体验是同步的）
- **一对一**：每个请求对应唯一的服务端处理
- **短事务**：适合在毫秒级完成的操作，不适合长时间任务
- **无中间反馈**：客户端只能拿到最终结果，无法得知执行过程中的进度

**典型场景**：获取当前机器人位姿、计算逆运动学、触发一次拍照、查询地图某点占用状态。

**代码示例（Python）**：

```python
from example_interfaces.srv import AddTwoInts

# 服务端
node.create_service(AddTwoInts, "add_two_ints", lambda req, res: AddTwoInts.Response(sum=req.a + req.b))

# 客户端（异步调用 + 阻塞等待结果）
client = node.create_client(AddTwoInts, "add_two_ints")
future = client.call_async(AddTwoInts.Request(a=1, b=2))
rclpy.spin_until_future_complete(node, future)
result = future.result()
```

> **注意**：若服务端未启动，客户端调用会失败。**服务不适合服务端可能离线的场景。**

---

### 2.3 动作（Action）— 目标 / 反馈 / 结果模型

**通信模型**：双向、异步、可取消、支持进度反馈。

```text
Client ──Goal────→ Server
       ←─Feedback─  (周期性)
       ←─Result────  (最终)
       ──Cancel──→  (可随时发送)
```

**关键特征**：

- **异步非阻塞**：发送 Goal 后立即返回 GoalHandle，不阻塞主线程
- **周期性反馈**：服务端在执行过程中可多次发送 Feedback，客户端实时掌握进度
- **可取消**：客户端可随时调用 `cancel_goal()` 终止任务
- **抢占支持**：新的 Goal 可以覆盖（或排队）旧的 Goal，由服务端策略决定
- **复合实现**：底层由 **3 个 Topic**（goal、feedback、result）+ **2 个 Service**（cancel、status）组合实现

**典型场景**：导航到目标点（Nav2）、机械臂轨迹执行、长时间扫描建图、机器人自主充电。

**代码示例（Python，对应本仓库 `Action_ws`）**：

```python
from chap7_interfaces.action import NavigateToPose
from rclpy.action import ActionClient

# 创建动作客户端（动作名带 / 前缀）
action_client = ActionClient(node, NavigateToPose, "/navigate_to_pose")

# 发送目标（异步）
goal_msg = NavigateToPose.Goal()
goal_msg.target_x = 2.0
goal_msg.target_y = 2.0
send_goal_future = action_client.send_goal_async(
    goal_msg,
    feedback_callback=lambda fb: node.get_logger().info(
        f"Progress: {fb.feedback.current_x:.2f}, {fb.feedback.current_y:.2f}"
    ),
)
goal_handle = send_goal_future.result()

# 取消目标
goal_handle.cancel_goal_async()

# 获取最终结果
result_future = goal_handle.get_result_async()
```

> **动作的本质**：它是 Topic + Service 的"高级封装"。若用原始 Topic / Service 实现一个带进度反馈的长任务，
> 代码会非常冗长且容易出错。动作替你封装了状态机：
> $\text{PENDING} \to \text{ACTIVE} \to \text{PREEMPTED} / \text{SUCCEEDED} / \text{ABORTED} / \text{CANCELED}$。

> **关联本仓库**：`Action_ws` 为**补充工作空间（原书无）**，用 C++ 与 Python 各实现一套动作服务端与客户端，
> 配套自定义接口 `chap7_interfaces/action/NavigateToPose`（字段 `target_x/target_y`），完整演示
> goal 接受、feedback 反馈、result 返回与可取消全流程。

---

### 2.4 参数（Parameter）— 节点配置模型

**通信模型**：节点内部存储，外部通过服务接口查询 / 修改。

**关键特征**：

- **节点级作用域**：每个参数归属于特定节点，全局命名空间为 `/node_name/parameter_name`
- **类型安全**：声明时必须指定类型（int、float、bool、string、byte array、string array），支持范围约束
- **动态重配置**：运行时可通过 `ros2 param set` 修改，无需重启节点
- **持久化**：支持从 YAML 文件加载 / 导出

**典型场景**：PID 控制器增益、传感器采样率、算法阈值、机器人物理参数（轮距、减速比、质量）。

**代码示例（Python）**：

```python
from rcl_interfaces.msg import ParameterDescriptor

# 声明参数（带默认值和描述）
node.declare_parameter(
    "kp", 1.0,
    descriptor=ParameterDescriptor(description="Proportional gain"),
)

# 读取参数
kp = node.get_parameter("kp").value

# 参数变更回调
node.add_on_set_parameters_callback(validate_params)
```

> **注意**：参数适合少量配置项，**不适合高频读写或大数据存储**。

---

## 三、底层实现对比

| 机制               | 底层 DDS 原语                | 是否基于 DDS | 通信方向    | 是否持久化 |
| :----------------- | :--------------------------- | :----------- | :---------- | :--------- |
| **话题 Topic**     | DDS Topic（Reader / Writer） | 原生         | 单向        | 否（默认） |
| **服务 Service**   | DDS Request / Reply 模式     | 封装         | 双向        | 否         |
| **动作 Action**    | 3 × Topic + 2 × Service      | 组合封装     | 双向 + 持续 | 否         |
| **参数 Parameter** | DDS Service（参数服务）      | 封装         | 双向        | 是（YAML） |

---

## 四、选型指南

### 4.1 决策树

```text
需要配置节点行为？
  ├─ 是 → Parameter
  └─ 否 → 任务执行时间？
           ├─ 持续流数据（传感器 / 控制）→ Topic
           └─ 离散任务 → 需要进度反馈或可能取消？
                          ├─ 是 → Action
                          └─ 否 → Service
```

### 4.2 快速判断口诀

| 你的需求                                                 | 选择          |
| :------------------------------------------------------- | :------------ |
| 传感器一直在发数据                                       | **Topic**     |
| 帮我算一下，立刻给我结果                                 | **Service**   |
| 去那边，到了告诉我，中途告诉我走到哪了，不想走了可以叫停 | **Action**    |
| 这个值我要能随时改                                       | **Parameter** |

---

## 五、常见误区

1. **用 Service 做长任务**：Service 调用会阻塞客户端，若服务端卡住，客户端会挂死。超过 1 秒的操作请用 Action。
2. **用 Topic 做请求-响应**：Topic 无反馈机制，你无法确认请求是否被处理、处理结果如何。
3. **Action 过度使用**：如果任务在 100ms 内完成且无需反馈，用 Service 更轻量。Action 的状态机开销更大。
4. **Parameter 当数据库用**：Parameter 适合少量配置项，不适合高频读写或大数据存储。

---

笔记整理日期：2026年8月
