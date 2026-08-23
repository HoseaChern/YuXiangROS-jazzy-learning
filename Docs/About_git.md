# Git 使用笔记

> 整理时间：2026-08-16
> 适用环境：Ubuntu 24.04 + Zsh/Bash + Clash Verge（混合端口 7897）
> 内容参考：《ROS2机器人开发 从入门到实践》第 3.5 / 5.6 / 7.6 节，并按个人实践经验扩充

---

## 1. git 命令行全解

> 对应原书：3.5 git 入门（新建仓库/提交/忽略）、5.6 git 进阶（查看修改/撤销/分支）、7.6 git 仓库托管（README/托管平台）

### 1.1 新建代码仓库（原书 3.5.1）

```bash
# 方式一：在已有目录初始化
cd 项目目录
git init                      # 生成隐藏目录 .git/
git branch -m main            # 默认分支命名为 main（可选）

# 方式二：克隆远程仓库
git clone https://github.com/<用户名>/<仓库名>.git
git clone git@github.com:<用户名>/<仓库名>.git   # SSH 方式（见第 4 节）
```

### 1.2 提交代码（原书 3.5.2）

```bash
git status                    # 查看工作区状态（改动/未跟踪文件）
git add <文件>                # 暂存单个文件
git add .                     # 暂存全部改动（谨慎，注意 .gitignore 是否生效）
git commit -m "docs: xxx"     # 提交（信息规范见第 2 节）
git log --oneline             # 查看提交历史（单行）
git log --oneline --graph     # 带分支图
```

> 提交前务必 `git status` + `git diff` 确认改了什么，只提交本次任务相关的文件。

### 1.3 忽略文件（原书 3.5.3）

仓库根目录的 `.gitignore` 决定哪些文件不进版本库：

```gitignore
# 构建产物
build/
.pio/
log/

# Python 虚拟环境
.venv/
__pycache__/
*.pyc

# 第三方 clone 的包（避免嵌套 git 仓库产生 gitlink，见第 3 节）
YuXiangROS/Chap9/Robot_ws/src/micro-ROS-Agent/
```

```bash
git status                    # 忽略规则生效后，被忽略文件不再显示
git check-ignore -v <文件>    # 排查某个文件被哪条规则忽略
```

> 注意：`.gitignore` 只对**未跟踪**文件生效；已被 `git add` 过的文件需 `git rm --cached <文件>`
> 才能取消跟踪。

### 1.4 查看修改内容（原书 5.6.1）

```bash
git status                     # 哪些文件改了（工作区/暂存区）
git diff                       # 工作区 vs 暂存区（未 add 的改动）
git diff --cached              # 暂存区 vs 最近提交（已 add 的改动）
git diff HEAD                  # 工作区 vs 最近提交（全部改动）
git diff <提交A> <提交B>        # 两个提交之间的差异
git show <提交>                # 查看某次提交的完整改动
git log --oneline -5           # 最近 5 条提交
```

### 1.5 撤销代码（原书 5.6.2）

| 场景                                   | 命令（现代写法）                   | 旧写法（仍可用）         |
| -------------------------------------- | ---------------------------------- | ------------------------ |
| 丢弃工作区改动（未 add）               | `git restore <文件>`               | `git checkout -- <文件>` |
| 取消暂存（已 add 未 commit）           | `git restore --staged <文件>`      | `git reset HEAD <文件>`  |
| 撤销最近一次提交（保留改动）           | `git reset --soft HEAD~1`          | —                        |
| 撤销最近一次提交（清空暂存，保留改动） | `git reset --mixed HEAD~1`（默认） | `git reset HEAD~1`       |
| 撤销提交并丢弃改动                     | `git reset --hard HEAD~1`          | 不可找回                 |
| 已 push 的提交，反向撤销               | `git revert <提交>`                | —                        |
| 只改最近一次提交的信息                 | `git commit --amend`               | —                        |

> `--hard` 会永久丢弃工作区改动，慎用；已 push 到远程的历史不要用 `reset` 改写，用 `revert`。

### 1.6 分支（原书 5.6.3）

```bash
git branch                      # 查看本地分支（* 标记当前分支）
git branch <分支名>             # 新建分支
git switch -c <分支名>          # 新建并切换（旧写法：git checkout -b <分支名>）
git switch <分支名>             # 切换分支（旧写法：git checkout <分支名>）
git branch -d <分支名>          # 删除已合并的分支（-D 强制删除）
git merge <分支名>              # 把该分支合并到当前分支
```

> 开发新功能/修复时开独立分支，合入后再删除，主分支（main）保持可运行状态。

### 1.7 远程仓库（原书 7.6）

```bash
git remote add origin <远程URL>   # 关联远程仓库
git push -u origin main          # 首次推送并建立跟踪（之后可直接 git push）
git push                         # 推送当前分支
git pull                         # 拉取并合并远程改动（= fetch + merge）
git fetch                        # 只拉取不合并
git remote -v                    # 查看远程地址
```

---

## 2. git commit 提交信息格式规范

采用 **Conventional Commits（约定式提交）**，格式为：

```plaintext
<type>(<scope>): <subject>

<body>
```

### 2.1 常用类型

| type       | 含义                      | 示例                                      |
| ---------- | ------------------------- | ----------------------------------------- |
| `feat`     | 新功能                    | `feat: add patrol node`                   |
| `fix`      | 修复 bug                  | `fix: correct build_src_filter typo`      |
| `docs`     | 仅文档改动                | `docs: add network proxy notes`           |
| `style`    | 格式/命名调整（不改逻辑） | `style: rename md notes, to remove space` |
| `refactor` | 重构（不改功能）          | `refactor: extract URDF utils`            |
| `perf`     | 性能优化                  | `perf: cache query result`                |
| `test`     | 测试相关                  | `test: add unit tests`                    |
| `build`    | 构建系统/依赖             | `build: bump cmake minimum version`       |
| `ci`       | CI 配置                   | `ci: add github actions workflow`         |
| `chore`    | 杂项（初始化、工具链）    | `chore: initial commit`                   |

### 2.2 书写要点

- **subject 用祈使句、简洁**：一句话说清"做了什么"，如 `docs: add xxx notes to PIO guide`
- **scope（可选）**：括注影响范围，如 `feat(parser): support xacro macros`
- **破坏性变更**：加 `!` 或 footer 写 `BREAKING CHANGE: xxx`
- **正文（可选）**：复杂改动在空一行后补充 why / how
- 本仓库历史示例：
  - `chore: initial commit - ROS2 Jazzy learning workspace adapted from "ROS2
    Robot Development"`
  - `docs: add network proxy config & src/ subdir filter notes to PIO CLI guid
    e`
  - `style: rename md notes, to remove space and lint warn`

---

## 3. repo 的目录管理规范

以本仓库（ROS 学习工作区）为例：

```plaintext
ROS/
├── README.md             # 项目自描述：简介、环境差异、各章导读、使用方式
├── README_EN.md          # 英文版（可选）
├── LICENSE               # 许可证（如 Apache 2.0）
├── Docs/                 # 个人学习笔记
│   ├── About_*.md        # 主题笔记（git / ROS2 / CMake ...）
│   └── Setup_*.md        # 环境配置记录
└── YuXiangROS/           # 代码按原书章节组织
    ├── Chap2/ Chap3/ ... Chap10/
    └── .gitignore
```

### 3.1 规范要点

| 维度               | 建议                                                                                                                                     |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **顶层文件**       | `README.md` 必须有（仓库门面）；LICENSE 明确版权                                                                                         |
| **命名**           | 全小写 + 下划线/连字符；避免空格（会引发工具链/shebang 问题）；笔记文件名避免空格（如 `About pyvenv.md` → `About_pyvenv.md`）            |
| **README 内容**    | 项目简介、环境说明、目录结构、快速开始、常见问题、许可证与致谢                                                                           |
| **.gitignore**     | 排除构建产物、虚拟环境、IDE 配置；**第三方 clone 的包单独忽略**                                                                          |
| **嵌套 git 仓库**  | 严禁把 `git clone` 的第三方仓库直接提交进来（会产生 gitlink 子模块引用）；用 .gitignore 排除，并让使用者自行 clone（见 README 对应小节） |
| **笔记与代码分离** | 学习笔记放独立 `Docs/`，与代码仓库同管，便于检索与版本回溯                                                                               |

---

## 4. git 的 HTTP 代理与 SSH 配置（push 与 clone）

> 背景：国内直连 GitHub 的 clone / push 常超时或龟速。git 有两条网络通道 ——
> **HTTPS**（走 `git config` 或环境变量）和 **SSH**（走 `~/.ssh/config`），两条通道的代理配置互不相干，
> 都要分别处理。

### 4.1 通道一：HTTPS（HTTP 代理，已配置 ✅）

git 不读"系统代理"，只认环境变量或 `git config`。推荐**只对 github.com 定向代理**（不依赖环境变量，最稳）：

```bash
# 配置（Clash Verge 混合端口 7897）
git config --global http.https://github.com.proxy http://127.0.0.1:7897
git config --global https.https://github.com.proxy http://127.0.0.1:7897

# 验证：应秒回
git ls-remote https://github.com/fishros/micro_ros_platformio.git HEAD

# 查看 / 移除
git config --global --get-regexp 'proxy'
git config --global --unset-all http.https://github.com.proxy
```

> 只对 github.com 生效，gitee 等国内源不受影响。若 gitee 也慢可同理加 `https://gitee.com` 的代理条目。

### 4.2 通道二：SSH（密钥 + 代理）

#### 第一步：生成密钥并添加

```bash
ssh-keygen -t ed25519 -C "你的邮箱"      # 一路回车，生成 ~/.ssh/id_ed25519(.pub)
cat ~/.ssh/id_ed25519.pub                # 复制公钥
```

- GitHub：Settings → SSH and GPG keys → New SSH key
- Gitee：设置 → SSH 公钥 → 添加

#### 第二步：验证（未走代理时可能卡住/失败）

```bash
ssh -T git@github.com    # 成功回 "Hi <用户名>! You've successfully authenticated...
"
ssh -T git@gitee.com
```

#### 第三步：SSH 走代理（`~/.ssh/config`）

```sshconfig
# github.com 走本地代理（Clash Verge 7897 为 HTTP+SOCKS5 混合端口）
Host github.com
    HostName github.com
    User git
    ProxyCommand nc -X connect -x 127.0.0.1:7897 %h %p
    # SOCKS5 写法：ProxyCommand nc -X 5 -x 127.0.0.1:7897 %h %p
```

> `nc` 为 OpenBSD netcat（`sudo apt install netcat-openbsd`）；不想装 nc
> 也可用 `connect-proxy`：`ProxyCommand connect -H 127.0.0.1:7897 %h %p`。

##### 可选：走 GitHub 的 443 端口（防火墙场景）

```sshconfig
Host github.com
    HostName ssh.github.com
    Port 443
    User git
```

#### 第四步：把 clone 地址从 HTTPS 换成 SSH

```bash
git clone git@github.com:<用户名>/<仓库名>.git
# 已有 HTTPS remote 的仓库改地址：
git remote set-url origin git@github.com:<用户名>/<仓库名>.git
```

### 4.3 排查速查

```bash
env | grep -i proxy                      # 当前环境变量代理
git config --global --get-regexp 'proxy' # git 的 HTTP 代理配置
ssh -T git@github.com -v                 # SSH 调试（看卡在哪一步）
ss -tlnp | grep 127.0.0.1                # 找本机代理真实端口
curl -x http://127.0.0.1:7897 -I https://github.com   # 验证端口可用
```

- 报错 `Failed to connect to 127.0.0.1 port XXXX after 0 ms` = 该端口没有代理进程监听，检查
  Clash Verge 是否开启、端口是否 7897
- HTTPS clone 慢 → 检查 4.1；SSH clone 慢/超时 → 检查 4.2 的 ProxyCommand

---

## 5. 常见问题速查

| 问题                            | 解决                                                                                            |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| clone 龟速/超时                 | 4.1 HTTPS 定向代理；SSH 地址则配 4.2 ProxyCommand                                               |
| `git push` 提示非 fast-forward  | 先 `git pull` 合并远程改动再 push；或确认分支跟踪                                               |
| 误提交了大文件/敏感文件         | `git rm --cached` + 更新 .gitignore；已 push 需重写历史（慎用）                                 |
| 想把本地仓库托管到 gitee/github | 平台上新建空仓库 → 4.1/4.2 配好网络 → `git remote add origin <URL>` → `git push -u origin main` |
| 仓库里出现子模块（gitlink）     | 第三方 clone 包未忽略，见 3.1 规范，用 .gitignore 排除                                          |

---

> **记住**：网络问题上 HTTPS 通道看 `git config`，SSH 通道看 `~/.ssh/config`，两条路独立配置；commit
> 信息统一用 Conventional Commits，仓库才经得起回看。
