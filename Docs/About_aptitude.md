# apt vs aptitude 对比笔记

> 整理时间：2026-07-20
> 适用系统：Debian / Ubuntu 及其衍生发行版

---

## 一、基本定位

| 维度         | `apt`                                          | `aptitude`                     |
| ------------ | ---------------------------------------------- | ------------------------------ |
| **本质**     | 现代高级包管理前端（整合 apt-get + apt-cache） | 更智能的包管理器，带交互式 TUI |
| **底层**     | 调用 `dpkg`                                    | 同样调用 `dpkg`                |
| **设计目标** | 简洁、脚本友好                                 | 智能依赖解决、交互式操作       |
| **出现时间** | 2014年（Debian 8 / Ubuntu 16.04 起推荐）       | 更早（2000年代）               |

---

## 二、核心命令对比

| 操作                   | `apt`                                       | `aptitude`                    |
| ---------------------- | ------------------------------------------- | ----------------------------- |
| **更新包列表**         | `sudo apt update`                           | `sudo aptitude update`        |
| **升级已安装包**       | `sudo apt upgrade`                          | `sudo aptitude safe-upgrade`  |
| **全系统升级**         | `sudo apt full-upgrade`                     | `sudo aptitude full-upgrade`  |
| **安装包**             | `sudo apt install <pkg>`                    | `sudo aptitude install <pkg>` |
| **卸载包（保留配置）** | `sudo apt remove <pkg>`                     | `sudo aptitude remove <pkg>`  |
| **彻底卸载（含配置）** | `sudo apt purge <pkg>`                      | `sudo aptitude purge <pkg>`   |
| **搜索包**             | `apt search <keyword>`                      | `aptitude search <keyword>`   |
| **查看包信息**         | `apt show <pkg>`                            | `aptitude show <pkg>`         |
| **清理旧包缓存**       | `sudo apt autoremove && sudo apt autoclean` | `sudo aptitude autoclean`     |
| **下载源码包**         | `apt source <pkg>`                          | `aptitude source <pkg>`       |

---

## 三、关键差异

### 3.1 依赖冲突处理

| 场景         | `apt`                  | `aptitude`                                 |
| ------------ | ---------------------- | ------------------------------------------ |
| **依赖冲突** | 直接报错，需要手动解决 | **自动提供多种解决方案**，可交互选择       |
| **智能性**   | 较低，按规则执行       | **较高**，会尝试保留/删除/降级包的组合方案 |
| **交互提示** | 较少（Y/n 确认）       | 丰富（列出多种解决策略供选择）             |

> **aptitude 优势**：遇到复杂依赖冲突时，aptitude 能给出多个可行方案（如"删除 A 保留 B"、"降级 C"等），而 apt 往往直接失败。

### 3.2 通配符支持

| 用法                 | `apt`                                               | `aptitude`                            |
| -------------------- | --------------------------------------------------- | ------------------------------------- |
| **Shell glob (`*`)** | `sudo apt install 'pkg-*'`（加引号防止 shell 扩展） | 不支持                                |
| **正则搜索**         | 不支持                                              | `aptitude search '?name(^pkg-)'`      |
| **描述搜索**         | `apt search <keyword>`（模糊匹配）                  | `aptitude search <keyword>`（更灵活） |

> **注意**：在 zsh 中使用 `apt install 'pkg-*'` 时，**必须加引号**，否则 zsh 的 glob 扩展会导致 `no matches found` 错误。

### 3.3 历史记录与撤销

| 功能         | `apt`                             | `aptitude`                             |
| ------------ | --------------------------------- | -------------------------------------- |
| **操作日志** | `/var/log/apt/history.log`        | 内置日志                               |
| **撤销操作** | 无内置撤销                        | `sudo aptitude undo`（可撤销最近操作） |
| **模拟执行** | `apt install -s <pkg>`（dry-run） | `aptitude install -s <pkg>`            |

### 3.4 交互界面

| 特性                | `apt`      | `aptitude`                                |
| ------------------- | ---------- | ----------------------------------------- |
| **TUI（文本界面）** | 无         | `sudo aptitude` 启动全屏包浏览器          |
| **包状态可视化**    | 命令行输出 | TUI 中直观显示（已装/未装/可升级/冲突等） |
| **批量操作**        | 需配合脚本 | TUI 中可批量标记安装/删除                 |

---

## 四、使用建议

| 场景                               | 推荐工具                        |
| ---------------------------------- | ------------------------------- |
| **日常快速操作**（安装/卸载/更新） | `apt`                           |
| **脚本自动化**                     | `apt`（输出更稳定，兼容性更好） |
| **遇到依赖冲突**                   | `aptitude`（智能解决方案）      |
| **需要浏览/批量管理包**            | `aptitude`（TUI 界面）          |
| **需要撤销误操作**                 | `aptitude`                      |
| **使用通配符批量安装**             | `apt`（加引号）                 |

---

## 五、zsh 用户特别注意

zsh 默认启用 `NOMATCH` 选项，glob 字符（`*`、`?`、`[]`）若匹配不到文件会报错。

### 解决方法

```bash
# 方法 1：加引号（推荐）
sudo apt install 'ros-jazzy-rqt-*'

# 方法 2：使用 noglob 前缀
noglob sudo apt install ros-jazzy-rqt-*

# 方法 3：在 ~/.zshrc 中永久设置别名
alias apt='noglob apt'
alias apt-get='noglob apt-get'
```

> aptitude 不支持 shell glob，即使加引号也不行，需用 `?name()` 正则语法或先搜索再安装。

---

## 六、aptitude 正则搜索语法速查

```bash
# 按名称正则匹配
aptitude search '?name(^ros-jazzy-rqt-)'

# 按描述搜索
aptitude search '?description(robot)'

# 组合条件：名称以 ros 开头 + 已安装
aptitude search '?name(^ros) ?installed'

# 查看某个包的依赖关系
aptitude show ros-jazzy-rqt-graph
```

---

## 七、参考

- [Debian apt 文档](https://manpages.debian.org/bookworm/apt/apt.8.en.html)
- [Debian aptitude 文档](https://manpages.debian.org/bookworm/aptitude/aptitude.8.en.html)
- [aptitude 搜索模式手册](https://manpages.debian.org/bookworm/aptitude/aptitude.1.en.html#SEARCH_PATTERNS)
