# YuXiangROS-jazzy-learning

> A ROS 2 learning workspace: code adapted from the book *"ROS2 Robot
> Development: From Beginner to Practice"* (by 桑欣 / Sang Xin), migrated to
> **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic**, plus an original
> JSON/Python-dict-to-URDF/Xacro tool (`Dict_To_URDF`).

[中文版](README.md)

---

## Table of Contents

- [YuXiangROS-jazzy-learning](#yuxiangros-jazzy-learning)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Environment \& Differences from the Book](#environment--differences-from-the-book)
  - [Python Virtual Environment (.venv)](#python-virtual-environment-venv)
  - [C/C++ Toolchain: clang series setup (2026-08-23)](#cc-toolchain-clang-series-setup-2026-08-23)
  - [Gazebo Classic → Harmonic Migration Essentials](#gazebo-classic--harmonic-migration-essentials)
  - [Chapter Guide](#chapter-guide)
  - [Original Tool: Dict\_To\_URDF](#original-tool-dict_to_urdf)
  - [Chap9 Third-Party Dependencies](#chap9-third-party-dependencies)
  - [Chap9 Companion Repo: YuXiangROS-PIO-learning](#chap9-companion-repo-yuxiangros-pio-learning)
  - [License \& Credits](#license--credits)

---

## Introduction

This repository collects the code and notes I wrote while studying *"ROS2
Robot Development: From Beginner to Practice"* ([桑欣 / fishros](https://github.com/fishros),
companion repo [fishros/ros2bookcode](https://github.com/fishros/ros2bookcode)).

**This is a derived learning project, NOT an official version.** The original
book targets **Ubuntu 22.04 + ROS 2 Humble + Gazebo Classic**. This repo
keeps the book's structure and ideas while porting everything to **Ubuntu 24.
04 + ROS 2 Jazzy + Gazebo Harmonic**, which includes:

- Handling Jazzy's breaking changes vs. Humble (removal of `use_stamped_vel`,
  changed `spawner` arguments, etc.)
- Migrating the Gazebo Classic ecosystem (`gazebo_ros`, `spawn_entity.py`,
  `gazebo_ros2_control`, `.world` files) to the Gazebo Harmonic ecosystem
  (`ros_gz_sim`, `create`, `gz_ros2_control`, `.sdf` files)
- Every migration is annotated with a `[旧版: xxx]` ("old version: xxx")
  comment for side-by-side comparison

The repo also contains 12 personal study notes (`Docs/` directory), of which
[About_Gazebo.md](Docs/About_Gazebo.md) (in Chinese) gives an in-depth
walkthrough of every migration pain point.

## Environment & Differences from the Book

| Item                      | Original Book                                              | This Repo                                                                                                               |
| ------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| OS                        | Ubuntu 22.04                                               | **Ubuntu 24.04**                                                                                                        |
| ROS 2                     | Humble                                                     | **Jazzy**                                                                                                               |
| Gazebo                    | Gazebo Classic 11                                          | **Gazebo Harmonic**                                                                                                     |
| Simulation launch         | `gazebo_ros/gazebo.launch.py`                              | `ros_gz_sim/gz_sim.launch.py`                                                                                           |
| Entity spawning           | `spawn_entity.py -entity`                                  | `ros_gz_sim create -name`                                                                                               |
| ros2_control hardware     | `gazebo_ros2_control`                                      | `gz_ros2_control` (`GazeboSimSystem`)                                                                                   |
| World file                | `.world` (SDF 1.6)                                         | `.sdf` (SDF 1.9+/1.11)                                                                                                  |
| Topic/service bridging    | automatic                                                  | explicit `parameter_bridge`                                                                                             |
| Simulation clock          | partially automatic                                        | explicit `use_sim_time: True` required                                                                                  |
| Python package management | system Python, direct `pip install`                        | **uv-managed `.venv`** (`--system-site-packages` to inherit system packages; Ubuntu 23.10+ enforces PEP 668, see below) |
| VS Code C/C++ extension   | C/C++ Extension Pack (`ms-vscode.cpptools-extension-pack`) | **cpptools dropped**; clang toolchain instead (clangd / clang-format / clang-tidy, see below)                           |

> Background: Gazebo Classic reached **end of life in January 2025** and is
> no longer installable from the Ubuntu 24.04 apt repositories, so moving to
> Jazzy requires migrating to Gazebo Harmonic (see the migration notes below).

## Python Virtual Environment (.venv)

**Why .venv?** Since Ubuntu 23.10, the system Python follows [PEP 668](https:
//peps.python.org/pep-0668/) and is marked "externally managed", so
direct `pip install` is rejected (forcing `--break-system-packages` is not
recommended). Meanwhile ROS 2 is bound to the system Python, and conda's own
Python coexists poorly with it. **Since 2026-08-31 this repo manages the ROS 2
workspace virtual environments with [uv](https://docs.astral.sh/uv/)**, keeping
the exact same behavior as the old `python3 -m venv --system-site-packages`
recipe — only the creation/install tool changed to uv (see the "Current
approach: uv" section in [Docs/About_pyvenv.md](Docs/About_pyvenv.md)).
Therefore, **whenever Chapters 4 / 7 / 8 require installing third-party Python
libraries, this repo uniformly uses a `.venv` virtual environment**:

| Chapter                                  | Third-party libraries needed             | Ready-made activation script                         |
| ---------------------------------------- | ---------------------------------------- | ---------------------------------------------------- |
| `Chap4` (face detection service)         | `face_recognition`, `dlib`, OpenCV, etc. | `YuXiangROS/Chap4/4.2_4.3_Service_ws/start_venv.zsh` |
| `Chap7` (Nav2 patrol + speech broadcast) | `espeakng` (speech synthesis), etc.      | `YuXiangROS/Chap7/Navigation_ws/start_venv.zsh`      |
| `Chap8` (Nav2 custom plugins)            | same as Chap7 (`espeakng`)               | `YuXiangROS/Chap8/Nav2_Custom_ws/start_venv.zsh`     |

**Core commands** (the ROS 2 specific recipe — `--system-site-packages` is
required, otherwise `rclpy` is not importable inside the venv; currently
created with uv, see [Docs/About_pyvenv.md](Docs/About_pyvenv.md)):

```bash
uv venv .venv --python 3.12.13 --system-site-packages --seed   # create (uv)
printf '/usr/lib/python3/dist-packages\n/usr/local/lib/python3.12/dist-packages\n' \
  > .venv/lib/python3.12/site-packages/_ros_system.pth          # inject system dist-packages
source .venv/bin/activate                                       # activate
uv pip install colcon-common-extensions <package_name>          # install (no sudo needed)
uv pip install "numpy==1.26.4"                                  # pin numpy to system version
```

> ⚠️ **Two frequent gotchas**:
>
> 1. `ros2 run` uses the system Python and won't see packages installed in
> the venv — install your own `colcon` inside the venv
> (`uv pip install colcon-common-extensions`) and make
> sure `which colcon` points to `.venv/bin/colcon`;
> 2. The workspace path **must not contain spaces**, otherwise
> setuptools-generated shebangs get truncated at the space and `ros2 run`
> fails (`4.2 Service_ws` → `4.2_4.3_Service_ws` was renamed after exactly
> this pitfall).

The full note (the uv-managed approach, prerequisites, zsh auto-activation,
venv vs conda comparison, detailed walkthrough of 4 pitfalls, one-click
activation script template) is in **`Docs/About_pyvenv.md`** (in Chinese).

## C/C++ Toolchain: clang series setup (2026-08-23)

**Background**: the Microsoft C/C++ extension (`ms-vscode.cpptools`) has a
**long-standing memory problem** — unbounded memory growth and high CPU usage
while indexing large projects (see
[issue #14168](https://github.com/microsoft/vscode-cpptools/issues/14168) and
[issue #14689](https://github.com/microsoft/vscode-cpptools/issues/14689):
a single process can eat
multiple GB of RAM and peg one core at 100% for hours). This hits large
multi-workspace projects such as ROS 2 especially hard. Since **2026-08-23**
this repo **fully abandons cpptools** in favor of the **clang toolchain**
(clangd + clang-format + clang-tidy) as the unified C/C++ toolchain.

**Layered structure** (separation of concerns):

| Layer          | Config                                                                                                                                 | Purpose                                 |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Workspace-wide | root `.clang-format` (LLVM base, 4-space indent, ColumnLimit 100), `.clang-tidy` (`clang-analyzer-*` / `bugprone-*` / `performance-*`) | code-quality & discipline standards     |
| Per workspace  | a `.clangd` in every C++ workspace (`CompilationDatabase: build` + `-Wall -Wextra`)                                                    | clangd compilation parsing & completion |

> **Boundary of responsibilities**: `.clang-format` / `.clang-tidy` enforce
> **workspace-wide** code quality & discipline; `.clangd` handles
> **compilation parsing**, which must follow the ROS 2 style — each workspace
> is an independent unit (one `compile_commands.json` per ws), never shared
> across ws.

**Compilation database mechanism**: clangd needs `compile_commands.json` to
resolve ROS 2 headers correctly (`-isystem /opt/ros/jazzy/include/...`).
Every workspace's CMakeLists sets `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)`
(**place it right after the `project(<pkg>)` line** so it takes effect early
in the configure stage, as shown
in `Chap3/3.2_3.3_Topic_ws/src/demo_cpp_topic/CMakeLists.txt`),
so `colcon build` generates `build/<pkg>/compile_commands.json` during the
CMake **configure stage**; these are then merged into the workspace
root `build/compile_commands.json` (which `.clangd` points to).

> ⚠️ `build/` is ignored by `.gitignore`, so **the compilation database is
> NOT committed**. After cloning, rebuild and merge:
>
> ```bash
> cd <workspace>
> colcon build
> python3 - <<'EOF'
> # Read each package's compile database generated at configure time
> import json, glob
> 
> merged = []
> for f in glob.glob("build/*/compile_commands.json"):
>     with open(f) as fh:
>         merged.extend(json.load(fh))
> 
> # Write the merged database to the workspace root, which .clangd points to
> with open("build/compile_commands.json", "w") as fh:
>     json.dump(merged, fh, indent=2)
> EOF
> ```

For everyday `colcon build`, you **do NOT need** to
add `--cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`:
`set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` in the CMakeLists already makes the
configure stage generate each package's `compile_commands.json`; the Python
script above merely **merges** them into the workspace root. This is exactly
why the option is written in the CMakeLists instead of on the command line —
saving that long flag every time.

**VS Code integration (local, not committed)**: `.vscode/` is deliberately
left out of the repo to **give readers freedom to configure it their own
way**. Below is the author's current complete config, **for reference only**
— the core ideas: clangd takes over C/C++ IntelliSense (zero cpptools),
format-on-save for C/C++ is handled by clangd, plus ROS 2 workspace Python
interface-package search paths (including `.venv`):

```jsonc
{
  // clangd takes over IntelliSense (zero cpptools)
  "clangd.path": "/usr/bin/clangd",
  "clangd.arguments": [
    "--background-index",
    "--completion-style=bundled",
    "--pch-storage=memory",
    "--clang-tidy"
  ],
  "[c]": {
    "editor.defaultFormatter": "llvm-vs-code-extensions.vscode-clangd",
    "editor.formatOnSave": true
  },
  "[cpp]": {
    "editor.defaultFormatter": "llvm-vs-code-extensions.vscode-clangd",
    "editor.formatOnSave": true
  },
  // ROS Python package paths (per-workspace interface packages & .venv)
  "python.analysis.extraPaths": [
    "/opt/ros/jazzy/lib/python3.12/site-packages",
    "/home/changli/Documents/ROS/YuXiangROS/Chap3/3.
4_Topic_practice_ws/install/status_interfaces/lib/python3.12/site-packages",
    "/home/changli/Documents/ROS/YuXiangROS/Chap4/4.2_4.3_Service_ws/.
venv/lib/python3.12/site-packages",
    "/home/changli/Documents/ROS/YuXiangROS/Chap4/4.2_4.
3_Service_ws/install/chap4_interfaces/lib/python3.12/site-packages",
    "/home/changli/Documents/ROS/YuXiangROS/Chap7/Navigation_ws/.
venv/lib/python3.12/site-packages",

"/home/changli/Documents/ROS/YuXiangROS/Chap7/Navigation_ws/install/autopatrol
_interfaces/lib/python3.12/site-packages",
    "/home/changli/Documents/ROS/YuXiangROS/Chap8/Nav2_Custom_ws/.
venv/lib/python3.12/site-packages",

"/home/changli/Documents/ROS/YuXiangROS/Chap8/Nav2_Custom_ws/install/autopatro
l_interfaces/lib/python3.12/site-packages"
  ],
  "python.analysis.autoImportCompletions": true,
  "python.analysis.typeCheckingMode": "standard",
  "python.autoComplete.extraPaths": [
    "/opt/ros/jazzy/lib/python3.12/site-packages"
  ],
  "github.copilot.chat.codeGeneration.useInstructionFiles": true
}
```

**Usage notes**:

- `.clangd`'s `CompilationDatabase: build` is a **relative path** — the file
  must live at the workspace **root** (placing it under `src/` once made
  clangd report `Failed to find compilation database`);
- after adding/removing source files, re-run `colcon build` and re-merge the
  database, otherwise new files have no compilation entries and clangd cannot
  analyze them;
- workspaces with `.venv` (Chap4 / 7 / 8) require activating the venv before
  building.

## Gazebo Classic → Harmonic Migration Essentials

When moving from Humble + Classic to Jazzy + Harmonic, beginners most often
get stuck because **all simulation commands and file formats changed**. Key
differences distilled from this repo's practice:

| Concern            | Gazebo Classic (book)                                              | Gazebo Harmonic (this repo)                                                                                                |
| ------------------ | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Start simulation   | `gazebo_ros` package, `gazebo.launch.py`, args `world` / `verbose` | `ros_gz_sim` package, `gz_sim.launch.py`, arg `gz_args: "-r -v 4 <world>"`                                                 |
| Spawn robot        | `spawn_entity.py -entity fishbot -topic /robot_description`        | `ros_gz_sim create -name fishbot -topic /robot_description`                                                                |
| ros2_control       | `gazebo_ros2_control` plugin                                       | `gz_ros2_control/GazeboSimSystem` hardware interface + `gz_ros2_control-system` plugin                                     |
| Topic bridging     | automatic by default                                               | must explicitly `parameter_bridge "<ros_topic>@<ROS_type>[<GZ_type>"`                                                      |
| World file         | `.world` (SDF 1.6, may reference external `model://` resources)    | `.sdf` (SDF 1.9+/1.11, `<sdf><world>` root, fully inlined models, explicit system plugins such as `gz-sim-physics-system`) |
| Simulation clock   | partially aligned by default                                       | must set `use_sim_time: True` for `robot_state_publisher`, `controller_manager`, etc., otherwise TF timestamps go wrong    |
| Velocity commands  | `diff_drive_controller` supports `use_stamped_vel`                 | Jazzy removes that param; use `twist_stamper` to convert `Twist` → `TwistStamped`                                          |
| Controller startup | old `spawner` args                                                 | `spawner --param-file <file> --controller-manager-timeout 30` + `OnProcessExit` event chain                                |

**Detailed tutorial** (in Chinese): [About_Gazebo.md](Docs/About_Gazebo.md) —
an ~500-line note covering the Classic EOL timeline, side-by-side comparison
of launching/bridging/control, a complete `.world` → `.sdf` world-file
migration walkthrough with a checklist, and a quick-reference table of 8
common errors (e.g., `spawn_entity.py: command not found`,
`libgazebo_ros2_control.so: cannot open shared object file`).

A representative migration example:
`YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/launch/gazebo_sim.lau
nch.py`, where every Harmonic change is annotated with a `# 旧版: xxx` comment.

## Chapter Guide

Code is organized under `YuXiangROS/` following the book's chapters (Chap2 ~
Chap10); each chapter contains self-contained workspaces.

> **Chapter 1** covers **system environment setup** (VirtualBox, Ubuntu 22.04,
> basic Linux commands, VS Code, a minimal ROS 2 installation including the
> Turtlesim test, and Python/C++ configuration) — it is **prerequisite
> preparation** with no standalone code directory. You don't need to install
> everything at once; set things up incrementally as later chapters require
> (this repo's environment is fully adapted to Ubuntu 24.04 + Jazzy +
> Harmonic — see the difference table above and the `Docs/` notes).

| Chapter  | Topic                            | Highlights                                                                                                                                                                                                                                                                                                                                        |
| -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Chap2`  | ROS 2 basics                     | Minimal C++/Python nodes; creating Python/C++ packages (`demo_python_pkg`, `demo_cpp_pkg`); colcon workspace (custom topic pub/sub, multithreading)                                                                                                                                                                                               |
| `Chap3`  | Topics                           | Turtlesim topic control (`demo_cpp_topic`); novel-text topic publisher (`demo_python_topic`); system-status monitoring practice (custom `SystemStatus.msg` + publisher + subscriber display)                                                                                                                                                      |
| `Chap4`  | Services                         | Custom `srv` (`FaceDetector.srv`, `Patrol.srv`); OpenCV-based face detection server/client in Python; C++ service server & client                                                                                                                                                                                                                 |
| `Chap5`  | TF transforms                    | Static/dynamic TF broadcasters and listeners (C++ and Python), plus rosbag2 playback data                                                                                                                                                                                                                                                         |
| `Chap6`  | URDF modeling + RViz + Gazebo    | Full fishbot model: URDF/Xacro, joints, sensors (camera/IMU/laser), ros2_control config, RViz display, Gazebo Harmonic simulation (incl. the `custom_room.sdf` three-room world); **hosts the original `Dict_To_URDF` tool**                                                                                                                      |
| `Chap7`  | Nav2 navigation + action         | `Navigation_ws` (book): patrol application on `nav2_simple_commander` (`patrol_node.py`, `waypoint_follower.py`), speech broadcast service, Nav2 params and maps; **`Action_ws` (supplemental, not in book)**: standalone action communication demo, C++/Python action server & client, custom interface `chap7_interfaces/action/NavigateToPose` |
| `Chap8`  | Nav2 custom plugins + pluginlib  | Custom Nav2 controller plugin, custom global planner plugin (C++, exported via pluginlib), plus a pluginlib teaching example (`motion_control_system`)                                                                                                                                                                                            |
| `Chap9`  | Physical robot (micro-ROS/LiDAR) | Bringup integration (`robot_bringup`), simplified fishbot model (`robot_description`), physical-robot Nav2 navigation (`robot_navigation2`); depends on 4 third-party packages you must clone yourself (see below)                                                                                                                                |
| `Chap10` | ROS 2 advanced                   | QoS reliability tests, Executor models, intra-process composition, DDS zero-copy loaned messages (`shm_pub`), time synchronization (`message_filter`), lifecycle nodes (`lifecyclenode`), plus FastDDS profile examples                                                                                                                           |

> **Supplemental workspace note**
> `Chap7/Navigation_ws` in the table is the book's content. The book only
> briefly introduces **action** communication (one of ROS 2's four
> communication mechanisms) at the end of the Nav2 chapter, using "navigation
> calls" as an example, and does **not** provide a standalone action
> communication workspace.
> This repo's **`Chap7/Action_ws` is an extra supplemental workspace (not in
> the book)**: it is independent of `nav2_simple_commander`, providing both a
> C++ and a Python action server & client, with the custom interface
> `chap7_interfaces/action/NavigateToPose` (fields `target_x/target_y`). It
> demonstrates the full goal-accept / feedback / result / cancel flow and can
> serve as a standalone action-communication intro. Build with
> `--symlink-install` and source this workspace when running.

## Original Tool: Dict_To_URDF

Located
at `YuXiangROS/Chap6/RViz_Gazebo_ws/src/fishbot_description/Dict_To_URDF/`,
this is my original **JSON / Python-dict → URDF / Xacro** converter:

- **`json_to_urdf.py`**: JSON → URDF XML converter with full support for URDF
  1.0 elements. Built on dataclass data models
  (`Origin/Geometry/Material/Inertial/Visual/Collision/Joint/Transmission`);
  top-level tags
  include `materials/links/joints/transmissions/gazebo/ros2_control`;
  built-in structural validation (single-root link tree, joint references,
  `ros2_control` hardware/joint references).

  ```bash
  # Usage: python json_to_urdf.py <input.json> [-o output.urdf] [--no-validate] [--no-pretty]
  python json_to_urdf.py JSON_URDF_demo.json -o JSON_URDF_demo.urdf
  ```

  Structural validation is ON by default; use `--no-validate` to skip,
  `--no-pretty` for compact XML output.
- **`Python_Xacro_demo.py`**: simulates xacro macro expansion in pure Python
  and calls `convert()` to generate URDF.
- **`pyacro_demo/`**: a complete fishbot implemented as a "Python acro",
  building an xacro-equivalent URDF in pure Python
  (base/actuator/sensor/plugins modules).

Bundled demos: `JSON_URDF_demo.json/.urdf` (simple demo),
`Python_Xacro_demo.py/.urdf`.

**Design idea**: URDF is essentially "tree-shaped structured data", which is
more intuitive and reusable when expressed as JSON/Python dicts than as XML.
This tool separates model definition from generation — treat the model as
data, then generate standard URDF/Xacro programmatically — ideal for batch
generation or programmatic management of robot models.

## Chap9 Third-Party Dependencies

Under `Chap9/Robot_ws/src/` there are 4 third-party packages that are
**git-cloned upstream code**. To avoid nested git repos (gitlinks) and
duplicate snapshots, this repo excludes them via `.gitignore` — **you must
clone them yourself**:

| Package           | Purpose                                                                | Source                                         |
| ----------------- | ---------------------------------------------------------------------- | ---------------------------------------------- |
| `micro-ROS-Agent` | micro-ROS communication agent                                          | <https://github.com/micro-ROS/micro-ROS-Agent> |
| `micro_ros_msgs`  | micro-ROS message definitions                                          | <https://github.com/micro-ROS/micro_ros_msgs>  |
| `ros_serial2wifi` | Serial ↔ WiFi (UDP/TCP) transparent bridge (fishros community example) | <https://github.com/fishros/ros_serial2wifi>   |
| `ydlidar_ros2`    | YDLidar LiDAR ROS 2 driver                                             | <https://github.com/fishros/ydlidar_ros2>      |

```bash
cd YuXiangROS/Chap9/Robot_ws/src
git clone https://github.com/micro-ROS/micro-ROS-Agent.git
git clone https://github.com/micro-ROS/micro_ros_msgs.git
git clone https://github.com/fishros/ros_serial2wifi.git
git clone https://github.com/fishros/ydlidar_ros2.git
```

> Keep them in sync with upstream: just `git pull` — this repo makes no
> modifications to these packages. The self-written packages (`robot_bringup`,
> `robot_description`, `robot_navigation2`) are tracked normally.

## Chap9 Companion Repo: YuXiangROS-PIO-learning

Chapter 9 focuses on physical robots (micro-ROS / LiDAR). The **PlatformIO +
micro-ROS MCU-side** learning materials (firmware, board support) live in a
separate repository:

- Repo: <https://github.com/HoseaChern/YuxiangROS-PIO-learning>
- Role: **companion to Chap9**. The two PlatformIO notes previously under
  `Docs/` here (toolchain architecture, CLI cheatsheet) have been migrated
  there, so this repo no longer maintains duplicates.

The two repos complement each other: this one covers the ROS 2 host side
(drivers, navigation, micro-ROS Agent), while the PIO repo covers the embedded
MCU side (PlatformIO firmware, micro-ROS board configuration).

## License & Credits

- **Original code, notes, and tools** in this repository are licensed under
  the [Apache License 2.0](LICENSE), Copyright (c) 2026 `HoseaChern`.
- **Original book & reference code**: the code here is adapted from *"ROS2
  Robot Development: From Beginner to Practice"* and its companion repo
  [fishros/ros2bookcode](https://github.com/fishros/ros2bookcode). **Thanks
  to the original author 桑欣 (fishros)** for the excellent textbook and
  open-source spirit. This repo is a derived learning project, not an
  official version; the original structure and comment style are preserved as
  much as possible, and all migrations are annotated with `[旧版: xxx]`.
- **Third-party packages** (micro-ROS-Agent, micro_ros_msgs, ros_serial2wifi,
  ydlidar_ros2) belong to their respective authors; follow their own licenses
  when using them.
- If the original author considers this derived repo inappropriate, feel free
  to reach out via issues — I will cooperate to modify or take it down.

---

*Maintained by `HoseaChern` for personal ROS 2 learning and sharing.*
