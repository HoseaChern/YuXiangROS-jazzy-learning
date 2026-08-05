# YuXiangROS-jazzy-learning

> A ROS 2 learning workspace: code adapted from the book *"ROS2 Robot Development: From Beginner to Practice"* (by 桑欣 / Sang Xin), migrated to **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic**, plus an original JSON/Python-dict-to-URDF/Xacro tool (`Dict_To_URDF`).

[中文版](README.md)

---

## Table of Contents

- [Introduction](#introduction)
- [Environment & Differences from the Book](#environment--differences-from-the-book)
- [Gazebo Classic → Harmonic Migration Essentials](#gazebo-classic--harmonic-migration-essentials)
- [Chapter Guide](#chapter-guide)
- [Original Tool: Dict_To_URDF](#original-tool-dict_to_urdf)
- [Chap9 Third-Party Dependencies](#chap9-third-party-dependencies)
- [License & Credits](#license--credits)

---

## Introduction

This repository collects the code and notes I wrote while studying *"ROS2 Robot Development: From Beginner to Practice"* ([桑欣 / fishros](https://github.com/fishros), companion repo [fishros/ros2bookcode](https://github.com/fishros/ros2bookcode)).

**This is a derived learning project, NOT an official version.** The original book targets **Ubuntu 22.04 + ROS 2 Humble + Gazebo Classic**. This repo keeps the book's structure and ideas while porting everything to **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic**, which includes:

- Handling Jazzy's breaking changes vs. Humble (removal of `use_stamped_vel`, changed `spawner` arguments, etc.)
- Migrating the Gazebo Classic ecosystem (`gazebo_ros`, `spawn_entity.py`, `gazebo_ros2_control`, `.world` files) to the Gazebo Harmonic ecosystem (`ros_gz_sim`, `create`, `gz_ros2_control`, `.sdf` files)
- Every migration is annotated with a `[旧版: xxx]` ("old version: xxx") comment for side-by-side comparison

The repo also contains 11 personal study notes (`Docs/` directory), of which [About Gazebo Classic vs Harmonic.md](Docs/About%20Gazebo%20Classic%20vs%20Harmonic.md) (in Chinese) gives an in-depth walkthrough of every migration pain point.

## Environment & Differences from the Book

| Item | Original Book | This Repo |
|---|---|---|
| OS | Ubuntu 22.04 | **Ubuntu 24.04** |
| ROS 2 | Humble | **Jazzy** |
| Gazebo | Gazebo Classic 11 | **Gazebo Harmonic** |
| Simulation launch | `gazebo_ros/gazebo.launch.py` | `ros_gz_sim/gz_sim.launch.py` |
| Entity spawning | `spawn_entity.py -entity` | `ros_gz_sim create -name` |
| ros2_control hardware | `gazebo_ros2_control` | `gz_ros2_control` (`GazeboSimSystem`) |
| World file | `.world` (SDF 1.6) | `.sdf` (SDF 1.9+/1.11) |
| Topic/service bridging | automatic | explicit `parameter_bridge` |
| Simulation clock | partially automatic | explicit `use_sim_time: True` required |

> Background: Gazebo Classic reached **end of life in January 2025** and is no longer installable from the Ubuntu 24.04 apt repositories, so moving to Jazzy requires migrating to Gazebo Harmonic (see the migration notes below).

## Gazebo Classic → Harmonic Migration Essentials

When moving from Humble + Classic to Jazzy + Harmonic, beginners most often get stuck because **all simulation commands and file formats changed**. Key differences distilled from this repo's practice:

| Concern | Gazebo Classic (book) | Gazebo Harmonic (this repo) |
|---|---|---|
| Start simulation | `gazebo_ros` package, `gazebo.launch.py`, args `world` / `verbose` | `ros_gz_sim` package, `gz_sim.launch.py`, arg `gz_args: "-r -v 4 <world>"` |
| Spawn robot | `spawn_entity.py -entity fishbot -topic /robot_description` | `ros_gz_sim create -name fishbot -topic /robot_description` |
| ros2_control | `gazebo_ros2_control` plugin | `gz_ros2_control/GazeboSimSystem` hardware interface + `gz_ros2_control-system` plugin |
| Topic bridging | automatic by default | must explicitly `parameter_bridge "<ros_topic>@<ROS_type>[<GZ_type>"` |
| World file | `.world` (SDF 1.6, may reference external `model://` resources) | `.sdf` (SDF 1.9+/1.11, `<sdf><world>` root, fully inlined models, explicit system plugins such as `gz-sim-physics-system`) |
| Simulation clock | partially aligned by default | must set `use_sim_time: True` for `robot_state_publisher`, `controller_manager`, etc., otherwise TF timestamps go wrong |
| Velocity commands | `diff_drive_controller` supports `use_stamped_vel` | Jazzy removes that param; use `twist_stamper` to convert `Twist` → `TwistStamped` |
| Controller startup | old `spawner` args | `spawner --param-file <file> --controller-manager-timeout 30` + `OnProcessExit` event chain |

**Detailed tutorial** (in Chinese): [About Gazebo Classic vs Harmonic.md](Docs/About%20Gazebo%20Classic%20vs%20Harmonic.md) — an ~500-line note covering the Classic EOL timeline, side-by-side comparison of launching/bridging/control, a complete `.world` → `.sdf` world-file migration walkthrough with a checklist, and a quick-reference table of 8 common errors (e.g., `spawn_entity.py: command not found`, `libgazebo_ros2_control.so: cannot open shared object file`).

A representative migration example: `YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/launch/gazebo_sim.launch.py`, where every Harmonic change is annotated with a `# 旧版: xxx` comment.

## Chapter Guide

Code is organized under `YuXiangROS/` following the book's chapters (Chap2 ~ Chap10); each chapter contains self-contained workspaces.

| Chapter | Topic | Highlights |
|---|---|---|
| `Chap2` | ROS 2 basics | Minimal C++/Python nodes; creating Python/C++ packages (`demo_python_pkg`, `demo_cpp_pkg`); colcon workspace (custom topic pub/sub, multithreading) |
| `Chap3` | Topics | Turtlesim topic control (`demo_cpp_topic`); novel-text topic publisher (`demo_python_topic`); system-status monitoring practice (custom `SystemStatus.msg` + publisher + subscriber display) |
| `Chap4` | Services | Custom `srv` (`FaceDetector.srv`, `Patrol.srv`); OpenCV-based face detection server/client in Python; C++ service server & client |
| `Chap5` | TF transforms | Static/dynamic TF broadcasters and listeners (C++ and Python), plus rosbag2 playback data |
| `Chap6` | URDF modeling + RViz + Gazebo | Full fishbot model: URDF/Xacro, joints, sensors (camera/IMU/laser), ros2_control config, RViz display, Gazebo Harmonic simulation (incl. the `custom_room.sdf` three-room world); **hosts the original `Dict_To_URDF` tool** |
| `Chap7` | Nav2 navigation | Patrol application on `nav2_simple_commander` (`patrol_node.py`, `waypoint_follower.py`), speech broadcast service, Nav2 params and maps |
| `Chap8` | Nav2 custom plugins + pluginlib | Custom Nav2 controller plugin, custom global planner plugin (C++, exported via pluginlib), plus a pluginlib teaching example (`motion_control_system`) |
| `Chap9` | Physical robot (micro-ROS/LiDAR) | Bringup integration (`robot_bringup`), simplified fishbot model (`robot_description`), physical-robot Nav2 navigation (`robot_navigation2`); depends on 4 third-party packages you must clone yourself (see below) |
| `Chap10` | ROS 2 advanced | QoS reliability tests, Executor models, intra-process composition, DDS zero-copy loaned messages (`shm_pub`), time synchronization (`message_filter`), lifecycle nodes (`lifecyclenode`), plus FastDDS profile examples |

## Original Tool: Dict_To_URDF

Located at `YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/Dict_To_URDF/`, this is my original **JSON / Python-dict → URDF / Xacro** converter:

- **`json_to_urdf.py`**: JSON → URDF XML converter with full support for URDF 1.0 elements. Built on dataclass data models (`Origin/Geometry/Material/Inertial/Visual/Collision/Joint/Transmission`); top-level tags include `materials/links/joints/transmissions/gazebo/ros2_control`; built-in structural validation (single-root link tree, joint references, `ros2_control` hardware/joint references).
  ```bash
  # Usage: python json_to_urdf.py <input.json> [-o output.urdf] [--no-validate] [--no-pretty]
  python json_to_urdf.py JSON_URDF_demo.json -o JSON_URDF_demo.urdf
  ```
  > Note: structural validation is ON by default; use `--no-validate` to skip, `--no-pretty` for compact XML output.
- **`Python_Xacro_demo.py`**: simulates xacro macro expansion in pure Python and calls `convert()` to generate URDF.
- **`pyacro_demo/`**: a complete fishbot implemented as a "Python acro", building an xacro-equivalent URDF in pure Python (base/actuator/sensor/plugins modules).

Bundled demos: `JSON_URDF_demo.json/.urdf` (simple demo), `Python_Xacro_demo.py/.urdf`.

**Design idea**: URDF is essentially "tree-shaped structured data", which is more intuitive and reusable when expressed as JSON/Python dicts than as XML. This tool separates model definition from generation — treat the model as data, then generate standard URDF/Xacro programmatically — ideal for batch generation or programmatic management of robot models.

## Chap9 Third-Party Dependencies

Under `Chap9/Robot_ws/src/` there are 4 third-party packages that are **git-cloned upstream code**. To avoid nested git repos (gitlinks) and duplicate snapshots, this repo excludes them via `.gitignore` — **you must clone them yourself**:

| Package | Purpose | Source |
|---|---|---|
| `micro-ROS-Agent` | micro-ROS communication agent | https://github.com/micro-ROS/micro-ROS-Agent |
| `micro_ros_msgs` | micro-ROS message definitions | https://github.com/micro-ROS/micro_ros_msgs |
| `ros_serial2wifi` | Serial ↔ WiFi (UDP/TCP) transparent bridge (fishros community example) | https://github.com/fishros/ros_serial2wifi |
| `ydlidar_ros2` | YDLidar LiDAR ROS 2 driver | https://github.com/fishros/ydlidar_ros2 |

```bash
cd YuXiangROS/Chap9/Robot_ws/src
git clone https://github.com/micro-ROS/micro-ROS-Agent.git
git clone https://github.com/micro-ROS/micro_ros_msgs.git
git clone https://github.com/fishros/ros_serial2wifi.git
git clone https://github.com/fishros/ydlidar_ros2.git
```

> Keep them in sync with upstream: just `git pull` — this repo makes no modifications to these packages. The self-written packages (`robot_bringup`, `robot_description`, `robot_navigation2`) are tracked normally.

## License & Credits

- **Original code, notes, and tools** in this repository are licensed under the [Apache License 2.0](LICENSE), Copyright (c) 2026 `HoseaChern`.
- **Original book & reference code**: the code here is adapted from *"ROS2 Robot Development: From Beginner to Practice"* and its companion repo [fishros/ros2bookcode](https://github.com/fishros/ros2bookcode). **Thanks to the original author 桑欣 (fishros)** for the excellent textbook and open-source spirit. This repo is a derived learning project, not an official version; the original structure and comment style are preserved as much as possible, and all migrations are annotated with `[旧版: xxx]`.
- **Third-party packages** (micro-ROS-Agent, micro_ros_msgs, ros_serial2wifi, ydlidar_ros2) belong to their respective authors; follow their own licenses when using them.
- If the original author considers this derived repo inappropriate, feel free to reach out via issues — I will cooperate to modify or take it down.

---

*Maintained by `HoseaChern` for personal ROS 2 learning and sharing.*
