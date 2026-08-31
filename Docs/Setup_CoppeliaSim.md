# Ubuntu 24.04 + CoppeliaSim Edu 4.10 安装后配置手册

> 适用环境：Ubuntu 24.04 LTS (Noble)，Shell 为 Zsh，Python 包使用 uv 管理。
>
> 本文整理 **CoppeliaSim 安装完成后** 的配置与使用流程（启动方式、Python 桥接、升级维护）。
> 软件本身的介绍、能力与选型对比见 [About_CoppeliaSim.md](About_CoppeliaSim.md)。

---

## 1. 环境概览

| 项目        | 值                                          |
| :---------- | :------------------------------------------ |
| 软件        | CoppeliaSim Edu（教育版，免费非商用）       |
| 版本        | 4.10（见第 2 节版本核实）                   |
| 安装方式    | tarball（官网 tar.xz 解压，无 apt 源）      |
| 安装位置    | `/opt/CoppeliaSim`                          |
| 命令入口    | `/opt/CoppeliaSim/coppeliaSim.sh`（无软链） |
| Python 桥接 | `/opt/CoppeliaSim/.venv`（uv 管理）         |

> 安装方式属于"tarball 维护"范畴，维护方法见
> `/home/changli/Documents/Others/软件维护清单.md` 中的 B 类软件说明。

---

## 2. 版本核实

安装目录内存在版本线索冲突，需以实测为准：

| 线索文件                                    | 内容          | 结论                                 |
| :------------------------------------------ | :------------ | :----------------------------------- |
| `readme.txt` 首行                           | 写 "V4.9.0"   | 上游模板未同步的遗留                 |
| `coppeliaSimEduV410XX-LicenseAgreement.txt` | 文件名含 4.10 | 实际版本                             |
| 全部文件构建时间                            | 2025-05-15    | 与官方 4.10 发布日（2025-05-14）吻合 |

判定依据：CoppeliaSim 4.10 于 2025-05-14 发布（该版本首次支持 Mac 平台），与本机发行包构建时间吻合，
故实际版本为 **4.10**，`readme.txt` 的 V4.9.0 是上游遗留，可忽略。

---

## 3. 启动方式

CoppeliaSim **未做软链**——它自带大量动态库（`/opt/CoppeliaSim/lib*.so`），
从目录外直接运行二进制会因找不到库而失败，必须从安装目录内启动：

```bash
# GUI 启动（推荐日常使用）
/opt/CoppeliaSim/coppeliaSim.sh

# 无界面启动（服务端 / 批量仿真场景）
/opt/CoppeliaSim/coppeliaSim.sh --headless
```

> 提示：若在任意目录下都希望直接敲命令启动，可自行在 `~/.zshrc` 添加别名：
> `alias coppelia='/opt/CoppeliaSim/coppeliaSim.sh'`。

---

## 4. Python 桥接配置（核心）

### 4.1 背景与选型

CoppeliaSim 官方推荐通过 ZeroMQ Remote API 用 Python 外部控制仿真。
Python 客户端需要 `pyzmq` 与 `cbor` 依赖，但 **Ubuntu 24.04 禁止向系统 Python 直接 pip 安装**
（PEP 668，`/usr/lib/python3.12/EXTERNALLY-MANAGED`），社区标准做法是使用 **venv**。
本机采用 **uv 管理 venv**，与系统 Python 完全隔离。

### 4.2 创建 venv 并安装官方客户端

`/opt/CoppeliaSim` 目录属主为 root，创建 venv 需要 sudo（注意 sudo 下 PATH 不含 `~/.local/bin`，
必须写 uv 全路径）：

```bash
# 1. 创建 venv（位于安装目录内，与程序本体放一起）
sudo /home/changli/.local/bin/uv venv /opt/CoppeliaSim/.venv --python 3.12

# 2. 归当前用户所有（关键一步，此后 uv 操作不再需要 sudo）
sudo chown -R "$USER":"$USER" /opt/CoppeliaSim/.venv

# 3. 安装官方客户端（自动携带 pyzmq + cbor，见 4.3）
uv pip install -p /opt/CoppeliaSim/.venv/bin/python coppeliasim-zmqremoteapi-client
```

安装结果（实测）：

```text
 + cbor==1.0.0
 + coppeliasim-zmqremoteapi-client==2.0.4
 + pyzmq==27.2.0
```

### 4.3 依赖说明（容易踩坑）

| 依赖包      | 是否必需 | 说明                                                                                                             |
| :---------- | :------- | :--------------------------------------------------------------------------------------------------------------- |
| `pyzmq`     | 必需     | 官方客户端自动安装                                                                                               |
| `cbor`      | 必需     | 官方客户端自动安装；CoppeliaSim 本地脚本按 `import cbor2` 优先、`import cbor` 兜底 二选一 处理，装 `cbor` 即满足 |
| `cbor2`     | 可选     | 仅在需要显式 `import cbor2` 的场景才补装                                                                         |
| `xmlschema` | 无关     | 只被开发工具 `simStubsGen`（API 桩生成器）使用，终端用户桥接不需要                                               |

> 注意：验证脚本请写 `import cbor`，直接 `import cbor2` 会报
> `ModuleNotFoundError`（本机曾踩坑）。

### 4.4 验证桥接依赖

```bash
/opt/CoppeliaSim/.venv/bin/python -c \
  "import zmq, cbor; from coppeliasim_zmqremoteapi_client import RemoteAPIClient; print('桥接依赖 OK')"
# 预期输出：桥接依赖 OK
```

### 4.5 使用方式（二选一）

```bash
# 方式 A：激活 venv 后直接运行
source /opt/CoppeliaSim/.venv/bin/activate
python your_script.py

# 方式 B：不激活，直接指定解释器（不污染当前 shell）
/opt/CoppeliaSim/.venv/bin/python your_script.py
```

### 4.6 最小示例脚本

```python
# minimal.py：连接本地 CoppeliaSim 并启动/停止仿真
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient()      # 默认连接 localhost:23000
sim = client.require('sim')     # 取得 sim 对象，即可调用 400+ API

print('已连接 CoppeliaSim')
sim.startSimulation()           # 启动仿真
# ... 此处编写控制逻辑（关节、传感器、路径规划等）...
sim.stopSimulation()            # 停止仿真
```

运行前提：先启动 CoppeliaSim GUI（或 `--headless`），脚本会通过 ZeroMQ 连接其
**默认端口 23000**（`RemoteAPIClient(host='localhost', port=23000)`）。

---

## 5. 常见问题

| 问题现象                                       | 可能原因                                                     | 解决方法                                                       |
| :--------------------------------------------- | :----------------------------------------------------------- | :------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'cbor2'` | 官方包装的是 `cbor`，不是 `cbor2`                            | 改用 `import cbor`（见 4.3），或补装 `cbor2`                   |
| 脚本连接失败（`Connection refused`）           | CoppeliaSim 未启动，或端口不是 23000                         | 先启动 CoppeliaSim；自定义端口时改 `RemoteAPIClient(port=...)` |
| `sudo: uv: command not found`                  | sudo 的 PATH 不含 `~/.local/bin`                             | 写 uv 全路径 `/home/changli/.local/bin/uv`                     |
| venv 使用哪个 Python                           | sudo 下 uv 解析到系统 3.12.3；普通用户下优先 uv 托管 3.12.13 | 二者对桥接功能无差异，保持默认即可                             |

---

## 6. 升级与维护

venv 位于 `/opt/CoppeliaSim/.venv`（安装目录内），升级方式决定其命运：

| 升级方式                         | 对 venv 的影响    | 处理                        |
| :------------------------------- | :---------------- | :-------------------------- |
| 官网新版 tar.xz **解压覆盖**目录 | 无影响，venv 保留 | 直接覆盖，无需额外操作      |
| 删除旧目录再解压（干净安装）     | venv 一并删除     | 重建：按 4.2 节四步重新执行 |

升级动作本身：官网下载新版 `tar.xz` → 解压覆盖 `/opt/CoppeliaSim` → 目录内启动验证。
下载走代理（`export https_proxy=http://127.0.0.1:7897`）。

---

## 7. ROS2 联动（可选前瞻）

`/opt/CoppeliaSim/libsimROS2.so` 插件已随包提供，可通过该插件让仿真中的机器人
作为 ROS2 网络节点（发布/订阅 Topic、调用 Service、广播 TF2）。
启用方式与接口细节见官方手册 ZeroMQ/ROS2 章节，首次接入建议先从本机
ROS2 Jazzy（`source /opt/ros/jazzy/setup.zsh`）与该插件联调开始。

---

## 8. 配置总结

1. **tarball 维护**：本体在 `/opt/CoppeliaSim`，无软链，从目录内启动，升级用覆盖式。
2. **Python 桥接隔离**：venv 由 uv 管理，依赖仅为官方客户端的 `pyzmq + cbor`，与系统 Python 零纠缠。
3. **版本以实测为准**：readme 版本号可能滞后，以许可证文件与构建时间佐证。
4. **升级前记住 venv**：覆盖式升级无损，删除式升级需重建 venv。
