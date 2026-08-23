# clang-format 配置笔记

> 职责：C/C++ 代码格式化
> 风格基础：LLVM，自定义覆盖关键项
> 生效：VS Code clangd 扩展（保存时自动格式化）

---

## 一、配置文件 `.clang-format`

### 当前配置内容

与仓库根目录 `.clang-format` 保持一致：

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100
ReflowComments: Never
BreakBeforeBraces: Attach
PointerAlignment: Left
ReferenceAlignment: Pointer
BinPackArguments: false
AlignAfterOpenBracket: BlockIndent
AllowAllArgumentsOnNextLine: false
NamespaceIndentation: None
```

### 配置说明

| 配置项 | 值 | 说明 |
| --- | --- | --- |
| `BasedOnStyle` | `LLVM` | 以 LLVM 风格为基础，只覆盖差异项 |
| `IndentWidth` / `TabWidth` | `4` | 缩进宽度 4 个空格 |
| `UseTab` | `Never` | 全部使用空格缩进，禁用 Tab |
| `ColumnLimit` | `100` | 行宽限制 100 字符 |
| `ReflowComments` | `Never` | 注释过长时不自动换行/拆段 |
| `BreakBeforeBraces` | `Attach` | 左大括号不换行（K&R 风格） |
| `PointerAlignment` | `Left` | 指针星号靠左：`int* p` |
| `ReferenceAlignment` | `Pointer` | 引用符与指针星号对齐方式一致靠左 |
| `BinPackArguments` | `false` | 函数调用参数换行时每参数独占一行 |
| `AlignAfterOpenBracket` | `BlockIndent` | 参数换行统一缩进，避免和括号对齐混用 |
| `AllowAllArgumentsOnNextLine` | `false` | 不允许所有参数挤在第二行 |
| `NamespaceIndentation` | `None` | 命名空间内代码不额外缩进 |

> **与旧版 clang-format 的差异**：
>
> 1. `ReflowComments`：clang-format 18 起由布尔值改为枚举（`Never` /
>    `Always` / `BlockCommentOnly`），旧的 `false` / `true` 写法已废弃；
> 2. `AllowAllArgumentsOnNextLine`：clang-format 16 起取代旧名
>    `AllowAllArgumentsOnASingleLine`，语义一致。

---

## 二、VS Code 集成（clangd 体系）

自 **2026-08-23** 起，本仓库全面弃用 cpptools，统一采用 clang 体系：
clangd 接管 C/C++ IntelliSense，clang-format 通过 clangd 扩展的保存时格式化
（`editor.formatOnSave`）自动生效，**不再使用** cpptools 的 `C_Cpp.*` 系列
配置（如 `C_Cpp.formatting`、`C_Cpp.clang_format_style`）。

完整配置（含编译数据库机制、`.clangd` 说明）见
[README「C++ 工具链：clang 系列配置」](../README.md#c-工具链clang-系列配置2026-08-23)。
`.vscode/` 刻意不入库，留给读者自由配置的空间。

---

## 三、环境安装

### Linux (Ubuntu/Debian)

Ubuntu 24.04 默认 `/usr/bin/clang-format` 即为较新版本（本机为 21.x），
直接安装即可：

```bash
# 安装（系统默认版本）
sudo apt install clang-format

# 或按需指定大版本（如 21）
sudo apt install clang-format-21

# 验证
clang-format --version
```

> 说明：本机曾安装 clang-format-17（`/usr/lib/llvm-17` 仍保留），
> 现默认命令已指向更新的 21.x；`.clang-format` 中的枚举语法
> （如 `ReflowComments: Never`）以较新版本为准。

### Windows

1. 从 [LLVM Releases](https://github.com/llvm/llvm-project/releases) 下载安装包
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
