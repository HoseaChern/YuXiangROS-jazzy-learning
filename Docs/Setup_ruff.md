# Ruff 配置笔记

> 职责：Python 代码格式化 + Import 排序  
> 其他代码诊断（类型检查、未定义变量等）交给 Pylance 处理  
> 路径：通过 VS Code `settings.json` 显式指定

---

## 一、配置文件 `ruff.toml`

### 当前配置内容

```toml
# Ruff 全局配置文件
# 职责: 格式化排版 + Import 排序
# 其他代码诊断交给 Pylance

target-version = "py311"
line-length = 100
indent-width = 4

exclude = [
    ".git",
    ".venv",
    ".tox",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
]

[format]
quote-style = "preserve"
indent-style = "space"
line-ending = "lf"
skip-magic-trailing-comma = false

[lint]
select = ["I"]
ignore = []

[lint.isort]
combine-as-imports = true
force-single-line = false
force-sort-within-sections = false
lines-between-types = 1
split-on-trailing-comma = false

section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]
```

### 配置说明

| 配置项                      | 值           | 说明                                                      |
| --------------------------- | ------------ | --------------------------------------------------------- |
| `target-version`            | `"py311"`    | 目标 Python 版本（根据实际环境修改）                      |
| `line-length`               | `100`        | 行宽限制 100 字符                                         |
| `indent-width`              | `4`          | 缩进宽度 4 个空格                                         |
| `quote-style`               | `"preserve"` | 保留原有引号，不强制单/双引号转换                         |
| `indent-style`              | `"space"`    | 使用空格缩进                                              |
| `line-ending`               | `"lf"`       | 换行符为 LF（Linux）；Windows 可改为 `"crlf"`             |
| `skip-magic-trailing-comma` | `false`      | 保留尾随逗号，用于控制垂直排版                            |
| `lint.select`               | `["I"]`      | 仅启用 **I**（isort）规则，只做 Import 排序，其他诊断关闭 |
| `combine-as-imports`        | `true`       | 合并 `from x import a, b` 中的 as 导入                    |
| `section-order`             | 见配置       | Import 分组顺序：标准库 → 第三方 → 第一方 → 本地          |

---

## 二、VS Code `settings.json` 配置

### Linux 版本

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": "explicit"
        }
    },
    "ruff.path": "path/to/ruff",
    "ruff.configuration": "path/to/ruff.toml",
    "ruff.configurationPreference": "filesystemFirst",
    "ruff.organizeImports": true
}
```

### Windows 版本

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": "explicit"
        }
    },

    "ruff.path": "path\\to\\ruff.exe",
    "ruff.configuration": "path\\to\\ruff.toml",
    "ruff.configurationPreference": "filesystemFirst",
    "ruff.organizeImports": true
}
```

### 关键字段说明

| 字段                           | 说明                                                    |
| ------------------------------ | ------------------------------------------------------- |
| `editor.defaultFormatter`      | `"charliermarsh.ruff"` 指定 Python 文件使用 Ruff 格式化 |
| `editor.codeActionsOnSave`     | `source.organizeImports.ruff` 保存时自动排序 import     |
| `ruff.path`                    | Ruff 可执行文件的**绝对路径**（Windows 下推荐显式指定） |
| `ruff.configuration`           | `ruff.toml` 配置文件的**绝对路径**                      |
| `ruff.configurationPreference` | `"filesystemFirst"` 优先使用文件系统上的配置            |

---

## 三、环境安装

### Linux

```bash
pip install ruff

# 验证
ruff --version

# 路径
which ruff
```

### Windows（miniforge base）

```bash
pip install ruff

# 验证
ruff --version

#路径
where ruff #CMD
Get-Command ruff #Powershell
```

---

## 四、验证

创建一个测试文件 `test.py`：

```python
import sys
import os
import numpy as np
from collections import defaultdict
from myproject import utils

x=1+2
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

---

## 五、与 Pylance 的分工

| 功能        | Ruff     | Pylance  |
| ----------- | -------- | -------- |
| 代码格式化  | ✅ 负责   | ❌ 不负责 |
| Import 排序 | ✅ 负责   | ❌ 不负责 |
| 类型检查    | ❌ 不负责 | ✅ 负责   |
| 未定义变量  | ❌ 不负责 | ✅ 负责   |
| 智能提示    | ❌ 不负责 | ✅ 负责   |

> 如果 Pylance 和 Ruff 对 `unused import` 重复提示，可在 VS Code 设置中关闭 Pylance 的该项诊断：
> ```json
> "python.analysis.diagnosticSeverityOverrides": {
>     "reportUnusedImport": "none"
> }
> ```
