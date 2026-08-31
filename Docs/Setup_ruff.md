# Ruff 配置笔记

> 职责：Python 代码格式化 + Import 排序 + Lint  
> 其他代码诊断（类型检查、未定义变量等）交给 Pylance 处理  
> 配置风格与 clangd 一致：使用**独立配置文件** `ruff.toml`，而非内嵌 `pyproject.toml` 的 `[tool.ruff]`

---

## 一、配置文件 `ruff.toml`

### 当前配置内容

文件位置：仓库根目录 `/home/changli/Documents/ROS/ruff.toml`

```toml
# Ruff 独立配置文件
# 职责: Python 代码格式化 + Import 排序 + Lint
# 风格与 .clangd 一致: 独立配置文件, 而非内嵌 pyproject.toml
# 其他代码诊断(类型检查、未定义变量等)交给 Pylance

target-version = "py312" # ROS 2 Jazzy 使用 Python 3.12
line-length = 120
indent-width = 4

exclude = [
    "**/.git/**",
    "**/.vscode/**",
    "**/.venv/**",
    "**/build/**",
    "**/install/**",
    "**/log/**",
    "**/__pycache__/**",
    "**/*.egg-info/**",
    "**/.ruff_cache/**",
    "**/.pytest_cache/**",
    "**/.mypy_cache/**",
]

[format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
skip-magic-trailing-comma = false

[lint]
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
    "I",   # isort (import 自动排序)
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
ignore = ["E501"] # 行长度由 formatter 处理, lint 中不再报错

[lint.pydocstyle]
convention = "google"
```

### 配置说明

| 配置项                       | 值                      | 说明                                                                    |
| ---------------------------- | ----------------------- | ----------------------------------------------------------------------- |
| `target-version`             | `"py312"`               | 目标 Python 版本：ROS 2 Jazzy 为 3.12                                   |
| `line-length`                | `120`                   | 行宽限制 120 字符（与 Python 样板一致）                                 |
| `indent-width`               | `4`                     | 缩进宽度 4 个空格                                                       |
| `exclude`                    | 见配置                  | 用 `**/xxx/**` 形式排除任意层级的 `.venv`、`build`、`install`、`log` 等 |
| `quote-style`                | `"double"`              | 统一双引号                                                              |
| `indent-style`               | `"space"`               | 使用空格缩进                                                            |
| `line-ending`                | `"auto"`                | 换行符自动检测（Linux 下为 LF）                                         |
| `skip-magic-trailing-comma`  | `false`                 | 保留尾随逗号，用于控制垂直排版                                          |
| `lint.select`                | `E/F/I/N/W/UP/B/C4/SIM` | Lint 规则集（与 Python 样板一致）                                       |
| `lint.ignore`                | `["E501"]`              | 行长度交给 formatter 处理，lint 不再报错                                |
| `lint.pydocstyle.convention` | `"google"`              | Google 风格 docstring                                                   |

---

## 二、VS Code `settings.json` 配置

### 当前配置（Linux）

文件位置：`/home/changli/Documents/ROS/.vscode/settings.json`

```json
"[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports.ruff": "explicit"
    }
},
"ruff.path": "/home/changli/.local/bin/ruff",
"ruff.configuration": "/home/changli/Documents/ROS/ruff.toml",
"ruff.configurationPreference": "filesystemFirst",
"ruff.organizeImports": true
```

### 关键字段说明

| 字段                           | 说明                                                       |
| ------------------------------ | ---------------------------------------------------------- |
| `editor.defaultFormatter`      | `"charliermarsh.ruff"` 指定 Python 文件使用 Ruff 格式化    |
| `editor.codeActionsOnSave`     | `source.organizeImports.ruff` 保存时自动排序 import        |
| `ruff.path`                    | Ruff 可执行文件的绝对路径（uv tool 托管于 `~/.local/bin`） |
| `ruff.configuration`           | `ruff.toml` 配置文件的绝对路径                             |
| `ruff.configurationPreference` | `"filesystemFirst"` 优先使用文件系统上的配置               |

---

## 三、环境安装

Ruff 通过 `uv tool` 独立托管，与工作区 venv 隔离：

```bash
uv tool install ruff

# 验证
ruff --version
# ruff 0.16.3

# 路径
which ruff
# /home/changli/.local/bin/ruff
```

---

## 四、验证

创建测试文件 `test.py`：

```python
import sys
import os
import numpy as np
from collections import defaultdict
from myproject import utils

x = 1 + 2
```

按 `Ctrl+S` 保存，预期效果：

```python
import os
import sys
from collections import defaultdict

import numpy as np

from myproject import utils

x = 1 + 2
```

- `x=1+2` → `x = 1 + 2`（格式化）
- `import` 语句按标准库 / 第三方 / 第一方分组排序

命令行验证：

```bash
# 检查格式问题（不修改文件）
ruff check --config /home/changli/Documents/ROS/ruff.toml .

# 直接格式化
ruff format --config /home/changli/Documents/ROS/ruff.toml .
```

---

## 五、与 Pylance 的分工

| 功能                               | Ruff   | Pylance |
| ---------------------------------- | ------ | ------- |
| 代码格式化                         | 负责   | 不负责  |
| Import 排序                        | 负责   | 不负责  |
| Lint 规则（E/F/I/N/W/UP/B/C4/SIM） | 负责   | 不负责  |
| 类型检查                           | 不负责 | 负责    |
| 未定义变量                         | 不负责 | 负责    |
| 智能提示                           | 不负责 | 负责    |

> 如果 Pylance 和 Ruff 对 `unused import` 重复提示，可在 VS Code 设置中关闭 Pylance 的该项诊断：
>
> ```json
> "python.analysis.diagnosticSeverityOverrides": {
>     "reportUnusedImport": "none"
> }
> ```
