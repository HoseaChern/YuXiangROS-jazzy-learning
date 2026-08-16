# CMake 基础入门笔记 (Ubuntu 24.04 环境)

## 1. 什么是 CMake？

- **定位**: 一款**跨平台**的构建工具生成器。它不是一个直接的编译器，而是用来生成 Makefile 或 IDE 工程文件的“管家”。
- **核心哲学**: **“源外构建” (Out-of-source build)**——编译产生的所有临时文件（`.o`、可执行文件等）都放在单独的 `build` 目录中，绝不污染源代码目录。
- **一句话总结**: 程序员写 `CMakeLists.txt`，CMake 读取它并自动适配当前系统（Linux/Mac/Windows）的编译环境。

## 2. 为什么不用直接的 g++ 命令？

| 直接使用 g++                             | 使用 CMake                                   |
| :--------------------------------------- | :------------------------------------------- |
| 适合单文件或极少数文件测试               | 适合**任何规模**的正式项目                   |
| 每次需手动输入完整命令，文件多了极难维护 | 只需描述项目结构，自动生成编译指令           |
| 不支持增量编译（改一个文件需重编全部）   | 自动支持**增量编译**，只重编修改过的文件     |
| 链接第三方库需手动指定 `-I` 和 `-L` 路径 | 通过 `find_package` 自动查找库路径，便于移植 |

## 3. 安装与验证 (Ubuntu 24.04)

```bash
# 安装
sudo apt update
sudo apt install cmake -y

# 验证是否安装成功
cmake --version
# 预期输出: cmake version 3.28.x
```

## 4. 黄金法则: 源外构建 (Out-of-source Build)

**永远不要在源代码目录下直接运行 `cmake .`**。

标准操作流程:

```bash
mkdir build          # 1. 创建构建目录
cd build             # 2. 进入构建目录
cmake ..             # 3. 生成 Makefile（指向上一级的源码）
make                 # 4. 开始编译
./可执行文件名        # 5. 运行程序
```

## 5. 最小必备 CMakeLists.txt 模板

创建一个名为 `CMakeLists.txt` 的文件，这是 CMake 的配置入口。以下是最基础的通用模板:

```cmake
# 1. 指定最低 CMake 版本（必写，首行）
cmake_minimum_required(VERSION 3.10)

# 2. 定义项目名称（必写，第二行）
project(MyProject)

# 3. 设置 C++ 标准（推荐）
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 4. 生成可执行文件
#    语法: add_executable(目标名 源文件1 源文件2 ...)
add_executable(my_app main.cpp)

# 5. （可选）链接第三方库
# target_link_libraries(my_app 库名)
```

## 6. 核心指令速查表

| 指令                             | 作用                                     | 示例                                                |
| :------------------------------- | :--------------------------------------- | :-------------------------------------------------- |
| **`cmake_minimum_required`**     | 设定所需最低 CMake 版本                  | `cmake_minimum_required(VERSION 3.10)`              |
| **`project`**                    | 定义工程名称                             | `project(HelloWorld)`                               |
| **`add_executable`**             | 指定源文件生成可执行文件                 | `add_executable(run main.cpp util.cpp)`             |
| **`add_library`**                | 生成静态库(`.a`)或动态库(`.so`)          | `add_library(mylib STATIC lib.cpp)`                 |
| **`target_link_libraries`**      | 为目标链接依赖库                         | `target_link_libraries(run mylib)`                  |
| **`target_include_directories`** | 为目标指定头文件搜索路径（现代推荐用法） | `target_include_directories(run PRIVATE ./include)` |
| **`find_package`**               | 自动查找系统中的第三方库                 | `find_package(OpenCV REQUIRED)`                     |
| **`set`**                        | 设置或修改变量                           | `set(SOURCES main.cpp helper.cpp)`                  |

> **💡 现代 CMake 最佳实践**: 尽量使用带 `target_` 前缀的命令（如 `target_include_directories`）代替全局命令（如 `include_directories`），这样能精确控制依赖的传递性，避免污染其他模块。

## 7. Debug 与 Release 切换

无需修改 `CMakeLists.txt`，在 `cmake` 配置阶段指定构建类型即可:

```bash
# Debug 模式（包含调试符号 -g，无优化）
cmake -DCMAKE_BUILD_TYPE=Debug ..
make

# Release 模式（开启优化 -O2/-O3）
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

## 8. 多目录项目结构示例

当一个项目有多个子文件夹时（如 `src`、`include`、`lib`），推荐在根目录的 `CMakeLists.txt` 中使用 `add_subdirectory`。

**目录结构**:

```plaintext
Project/
├── CMakeLists.txt   (根目录)
├── src/
│   ├── CMakeLists.txt
│   └── main.cpp
└── lib/
    ├── CMakeLists.txt
    └── math.cpp
```

**根目录 CMakeLists.txt**:

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# 添加子目录（顺序很重要，依赖库需先添加）
add_subdirectory(lib)
add_subdirectory(src)
```

**子目录 src/CMakeLists.txt**:

```cmake
# 链接父目录定义的库
add_executable(my_app main.cpp)
target_link_libraries(my_app math_lib) # 链接 lib 目录生成的库
```

## 9. 常用构建命令简写

为了不记忆 `make` 的具体细节，可以使用跨平台的 CMake 构建命令:

```bash
# 相当于进入 build 目录执行 make
cmake --build build
```

## 10. 清理项目

由于采用“源外构建”，清理编译产物非常简单，**直接删除 build 目录即可**，源码目录毫发无损。

```bash
rm -rf build
```
