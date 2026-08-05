---
name: yuxiang-ros2-jazzy 仓库发布计划
overview: 为已 git init 的 ROS 学习项目（Docs 笔记 + YuXiangROS 代码）完成发布前整理：更新 .gitignore 排除第三方 clone 包、编写根 README 与 Apache-2.0 LICENSE、提交前检查，并安排联系原作者确认许可，最终创建 GitHub 公开仓库并推送。
todos:
  - id: update-gitignore
    content: 更新根 .gitignore 排除 Chap9 四个第三方包，并用 git check-ignore 验证忽略生效
    status: pending
  - id: add-license
    content: 在仓库根目录添加 Apache-2.0 LICENSE 文件，版权行使用用户确认的署名
    status: pending
    dependencies:
      - update-gitignore
  - id: write-readme
    content: 用 [subagent:code-explorer] 核实各章内容，编写根 README.md（环境适配、各章导读、Chap9 clone 清单、致谢原作者）
    status: pending
    dependencies:
      - update-gitignore
  - id: pre-commit-check
    content: 提交前全面检查：git status --ignored、大文件与敏感信息扫描、gitlink 确认，异常时用 [skill:debugging-and-error-recovery] 排查
    status: pending
    dependencies:
      - add-license
      - write-readme
  - id: create-repo-push
    content: 检查 gh 认证，创建 GitHub public 仓库（YuXiangROS 相关命名）并完成首次提交与 push
    status: pending
    dependencies:
      - pre-commit-check
  - id: contact-author
    content: 在 fishros/ros2bookcode 提 issue 联系原作者确认衍生发布许可，附仓库链接与改动说明模板
    status: pending
    dependencies:
      - create-repo-push
---

## 用户需求
将已完成 git init 的学习项目发布为 GitHub public 仓库，包含：
- `Docs/`：个人学习笔记（11 个 md）
- `YuXiangROS/`：参考《ROS2机器人开发 从入门到实践》（桑欣 著，配套仓库 fishros/ros2bookcode）的学习代码，主要差异：适配 Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic（相对原书 humble + Gazebo Classic）；自研 JSON/Python 字典转 URDF/Xacro 工具（`Chap6/.../fishbot_description/Dict_To_URDF`）

## 已确认决策
1. **Chap9 第三方包**：`micro-ROS-Agent`、`micro_ros_msgs`、`ros_serial2wifi`、`ydlidar_ros2` 四个 git clone 包不纳入仓库，通过 `.gitignore` 排除，并在 README 中给出读者需自行 clone 的清单与命令
2. **许可证**：用户原创部分采用 **Apache-2.0**
3. **仓库结构**：单一仓库（Docs + YuXiangROS），命名采用 YuXiangROS 相关名称
4. **配套工作**：编写根 README.md（含致谢原作者并附链接）、统一整理 `.gitignore` 与提交前检查、安排联系原作者确认许可

## 核心功能
- 干净、可复现的仓库内容（排除构建产物、venv、第三方 clone 包，约 420 文件 / 17MB）
- README 完整说明项目背景、环境适配差异、各章导读、Chap9 依赖包获取方式
- 尊重原作者的致谢与许可确认流程


## 技术栈
- Git + GitHub（优先 `gh` CLI，未登录时回退网页创建）
- 仓库当前状态：main 分支、零提交、无 .gitmodules

## 实施策略
### 1. 更新根 .gitignore（关键）
在现有基础上追加精确路径模式，排除 Chap9 四个第三方包（避免误伤同名目录）：
```
# Chap9 第三方 git clone 包（读者自行 clone，见 README）
YuXiangROS/Chap9/Robot_ws/src/micro-ROS-Agent/
YuXiangROS/Chap9/Robot_ws/src/micro_ros_msgs/
YuXiangROS/Chap9/Robot_ws/src/ros_serial2wifi/
YuXiangROS/Chap9/Robot_ws/src/ydlidar_ros2/
```
要点：这些包当前被 git 识别为"悬挂 gitlink"（有 .git 但无 .gitmodules 登记），必须被 ignore 掉，否则 `git add -A` 会以 gitlink 形式误提交。用 `git check-ignore -v` 验证每个路径命中规则。同目录下自写的 `robot_bringup`、`robot_description`、`robot_navigation2` 正常跟踪。

### 2. 许可证与版权
- 根目录新增 `LICENSE`（Apache-2.0 全文），版权行 `Copyright (c) 2026 <GitHub用户名>`（执行时由用户确认署名）
- 各包内已有 Apache-2.0 LICENSE（ROS 模板）保留不动，避免无谓改动

### 3. 根 README.md 结构（markdown）
- 项目简介 + 与参考书的关系声明（衍生、非官方）
- 环境说明：Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic，列出与原书（humble + Classic）的主要差异表（可引用 `Docs/About Gazebo Classic vs Harmonic.md` 素材：gazebo_ros→ros_gz_sim、gazebo_ros2_control→gz_ros2_control 等）
- 各章导读（Chap2~Chap10，基于工作区目录名与包内容，经 code-explorer 核实）
- Chap9 依赖包清单：4 个仓库 URL + 读者需执行的 `git clone` 命令 + 说明"以 README 所列 commit 为参考、按需拉取最新版"
- 原创工具亮点：`Dict_To_URDF`（JSON→URDF、Python dict→Xacro，含 CLI/校验）
- 致谢：桑欣《ROS2机器人开发 从入门到实践》、fishros/ros2bookcode 链接，声明本仓库为个人学习适配版、与原书/作者无隶属关系
- 许可证说明（Apache-2.0）+ 第三方包各自版权归其作者

### 4. 提交前检查（防回归）
- `git status --short --ignored`：确认 4 个包被忽略、无 gitlink 条目、无意外文件
- 大文件扫描（>5MB）与敏感信息扫描（密钥/令牌），确保无 .venv、build 产物误入
- 确认跟踪文件数 ~420、总量 ~17MB 与预期一致

### 5. 创建仓库与发布
- 检查 `gh auth status`；已登录则 `gh repo create <YuXiangROS相关命名> --public --source . --push`；未登录则给出网页创建 + `git remote add origin` + `git push -u origin main` 指引
- 仓库命名建议：`YuXiangROS` 或 `ros2-yuxiang-learning-jazzy`，最终由用户拍板

### 6. 联系原作者确认许可（尊重原作者）
- 在 fishros/ros2bookcode 提 issue（附模板）：说明本仓库为个人学习适配（jazzy/Harmonic）、公开意图、请求确认衍生发布许可，附仓库 URL
- 模板要点：自述身份与用途、列出改动范围（适配 + 自研工具）、承诺署名与链接、接受作者要求的任何修改/下架请求


## Agent Extensions
### Skill
- **debugging-and-error-recovery**
  - Purpose: 在提交前检查阶段，若出现 git 状态异常（如 gitlink 未被正确忽略、大文件/敏感文件误入跟踪、ignore 规则未生效）时，按系统化根因排查流程定位并修复，而非猜测性操作
  - Expected outcome: 提交前的 git 状态与预期完全一致，无异常条目
### SubAgent
- **code-explorer**
  - Purpose: 编写 README 各章导读前，探索 YuXiangROS 各 Chap 下的工作区与核心包内容，核实每章主题、关键包与适配改动，确保 README 导读准确
  - Expected outcome: README 各章导读与实际代码结构一一对应，无虚构描述
