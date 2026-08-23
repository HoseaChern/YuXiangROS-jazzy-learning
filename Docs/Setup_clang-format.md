# clang-format 配置笔记

> 职责：C/C++ 代码格式化  
> 风格基础：LLVM，自定义覆盖关键项  
> 路径：通过 VS Code `settings.json` 显式指定

---

## 一、配置文件 `.clang-format`

### 当前配置内容

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100
ReflowComments: false
BreakBeforeBraces: Attach
PointerAlignment: Left
BinPackArguments: false
AlignAfterOpenBracket: BlockIndent
AllowAllArgumentsOnASingleLine: false
```

### 配置说明

| 配置项                           | 值            | 说明                                       |
| -------------------------------- | ------------- | ------------------------------------------ |
| `BasedOnStyle`                   | `LLVM`        | 以 LLVM 风格为基础，只覆盖差异项           |
| `IndentWidth` / `TabWidth`       | `4`           | 缩进宽度 4 个空格                          |
| `UseTab`                         | `Never`       | 全部使用空格缩进，禁用 Tab                 |
| `ColumnLimit`                    | `100`         | 行宽限制 100 字符                          |
| `ReflowComments`                 | `false`       | 注释过长时不自动换行/拆段                  |
| `BreakBeforeBraces`              | `Attach`      | 左大括号不换行（K&R 风格）                 |
| `PointerAlignment`               | `Left`        | 指针星号靠左：`int* p`                     |
| `BinPackArguments`               | `false`       | 函数调用参数一旦换行，每个参数独占一行     |
| `AlignAfterOpenBracket`          | `BlockIndent` | 参数列表换行时统一缩进，避免和括号对齐混用 |
| `AllowAllArgumentsOnASingleLine` | `false`       | 不允许所有参数挤在第二行                   |

---

## 二、VS Code `settings.json` 配置

### Linux 版本

```json
{
    "editor.formatOnSave": true,

    "C_Cpp.formatting": "clangFormat",
    "C_Cpp.clang_format_style": "file:path/to/.clang-format",
    "C_Cpp.clang_format_path": "/usr/lib/llvm-17/bin/clang-format",

    "[cpp]": {
        "editor.defaultFormatter": "ms-vscode.cpptools",
        "editor.formatOnSave": true
    },
    "[c]": {
        "editor.defaultFormatter": "ms-vscode.cpptools",
        "editor.formatOnSave": true
    }
}
```

### Windows 版本

```json
{
    "editor.formatOnSave": true,

    "C_Cpp.formatting": "clangFormat",
    "C_Cpp.clang_format_style": "file:path\\to\\.clang-format",
    "C_Cpp.clang_format_path": "path\\to\\LLVM\\bin\\clang-format.exe",

    "[cpp]": {
        "editor.defaultFormatter": "ms-vscode.cpptools",
        "editor.formatOnSave": true
    },
    "[c]": {
        "editor.defaultFormatter": "ms-vscode.cpptools",
        "editor.formatOnSave": true
    }
}
```

### 关键字段说明

| 字段                       | 说明                                                         |
| -------------------------- | ------------------------------------------------------------ |
| `C_Cpp.formatting`         | 必须设为 `"clangFormat"`，不能用 `"default"` 或 `"vcFormat"` |
| `C_Cpp.clang_format_style` | `"file"` 表示读取目录树中的 `.clang-format` 文件             |
| `C_Cpp.clang_format_path`  | clang-format 可执行文件的**绝对路径**                        |
| `editor.defaultFormatter`  | 指定 C/C++ 文件使用 C/C++ 扩展内置的格式化器                 |

---

## 三、环境安装

### Linux (Ubuntu/Debian)

```bash
# 安装
sudo apt install clang-format-17

# 创建软链接（否则终端里敲 clang-format 找不到）
sudo ln -s /usr/lib/llvm-17/bin/clang-format /usr/bin/clang-format

# 验证
clang-format --version
```

### Windows

1. 下载 LLVM 安装包：[GitHub Releases](https://github.com/llvm/llvm-project/releases)
2. 运行 `LLVM-xx.x.x-win64.exe`
3. **勾选** "Add LLVM to the system PATH for all users"
4. 验证：`clang-format --version`

> 或通过包管理器安装：
>
> ```powershell
> winget install LLVM.LLVM
> ```

---

## 四、验证

打开任意 `.cpp` 文件，写入：

```cpp
void test(int a,int b,int c,int d,int e){
    if(a>0){return;}
}
```

按 `Shift+Alt+F` 或保存（`Ctrl+S`），预期格式化为：

```cpp
void test(
    int a,
    int b,
    int c,
    int d,
    int e) {
    if (a > 0) {
        return;
    }
}
```
