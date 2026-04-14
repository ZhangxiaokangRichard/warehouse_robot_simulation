# QuickStart 快速启动指南

本指南将逐步指导你从零开始配置和运行仓库机器人自主导航模拟系统。

## 目录
- [系统要求](#系统要求)
- [验证依赖项](#验证依赖项)
- [创建 Catkin 工作空间](#创建-catkin-工作空间)
- [配置 VS Code](#配置-vs-code)
- [编译项目](#编译项目)
- [运行模拟](#运行模拟)

---

## 系统要求

- **操作系统**：Ubuntu 20.04 LTS
- **ROS 版本**：ROS Noetic
- **Gazebo 版本**：Gazebo 11
- **编译工具**：gcc/g++ >= 9.0, cmake >= 3.16, make >= 4.2

---

## 验证依赖项

### 1. 验证 ROS Noetic 安装

```bash
rosversion -d
```

**预期输出**：`noetic`

如果命令不存在或输出不同，请参考 [ROS Noetic 安装指南](http://wiki.ros.org/noetic/Installation/Ubuntu)。

### 2. 验证 Gazebo 11 安装

```bash
gazebo --version
```

**预期输出**：`Gazebo multi-robot simulator, version 11.x.x`

如未安装，执行：
```bash
sudo apt-get update
sudo apt-get install gazebo11 libgazebo11-dev
sudo apt-get install ros-noetic-gazebo-ros-pkgs ros-noetic-gazebo-ros-control
```

### 3. 验证 RViz 安装

```bash
rosrun rviz rviz --version
```

**预期输出**：版本号（如 `1.14.26`）

如未安装，执行：
```bash
sudo apt-get install ros-noetic-rviz
```

### 4. 验证 Xterm 安装

```bash
which xterm
```

**预期输出**：`/usr/bin/xterm`

如未安装，执行：
```bash
sudo apt-get install xterm
```

### 5. 安装其他必需 ROS 包

```bash
sudo apt-get install ros-noetic-amcl \
  ros-noetic-move-base \
  ros-noetic-dwa-local-planner \
  ros-noetic-map-server \
  ros-noetic-teleop-twist-keyboard \
  ros-noetic-gmapping \
  ros-noetic-slam-gmapping
```

### 6. 验证编译工具

```bash
cmake --version  # 预期: >= 3.16
gcc --version    # 预期: >= 9.0
make --version   # 预期: >= 4.2
```

---

## 创建 Catkin 工作空间

### 1. 创建目录结构

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
```

### 2. 初始化 Catkin 工作空间

```bash
catkin_make
```

第一次运行会创建 `build` 和 `devel` 目录。

### 3. 克隆本项目

```bash
cd ~/catkin_ws/src
git clone https://github.com/rodriguesrenato/warehouse_robot_simulation.git
```

或从你的 fork 克隆：
```bash
git clone https://github.com/YOUR_USERNAME/warehouse_robot_simulation.git
```

### 4. 可选：克隆地图构建依赖

如果计划重新构建环境地图，同时克隆：

```bash
cd ~/catkin_ws/src
git clone https://github.com/ros-perception/slam_gmapping.git
git clone https://github.com/ros-teleop/teleop_twist_keyboard
```

---

## 配置 VS Code

### 1. 打开工作空间

```bash
cd ~/catkin_ws
code .
```

### 2. 创建 `.vscode` 目录

```bash
mkdir -p .vscode
```

### 3. 创建 `c_cpp_properties.json`

在 `.vscode/c_cpp_properties.json` 中添加以下内容：

```json
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "${workspaceFolder}/**",
                "/opt/ros/noetic/include/**",
                "/usr/include/**"
            ],
            "defines": [],
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "linux-gcc-x64"
        }
    ],
    "version": 4
}
```

### 4. 创建 `settings.json`

在 `.vscode/settings.json` 中添加以下内容：

```json
{
    "python.autoComplete.extraPaths": [
        "/home/ros-dev/catkin_ws/devel/lib/python3/dist-packages",
        "/opt/ros/noetic/lib/python3/dist-packages"
    ],
    "python.analysis.extraPaths": [
        "/home/ros-dev/catkin_ws/devel/lib/python3/dist-packages",
        "/opt/ros/noetic/lib/python3/dist-packages"
    ],
    "C_Cpp.errorSquiggles": "disabled",
    "cmake.sourceDirectory": "${workspaceFolder}/src/warehouse_robot_simulation",
    "ros.distro": "noetic",
    "editor.formatOnSave": false
}
```

**注意**：如果用户名不是 `ros-dev`，请将路径中的 `ros-dev` 替换为你的用户名。

### 5. 创建 `tasks.json`（可选）

在 `.vscode/tasks.json` 中添加以下内容，可直接在 VS Code 中编译：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "catkin_make",
            "type": "shell",
            "command": "catkin_make",
            "args": [],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always"
            },
            "problemMatcher": "$msCompile"
        },
        {
            "label": "catkin_make warehouse_robot_simulation",
            "type": "shell",
            "command": "catkin_make",
            "args": ["--pkg", "warehouse_robot_simulation"],
            "group": {
                "kind": "build"
            },
            "presentation": {
                "reveal": "always"
            }
        }
    ]
}
```

### 6. VS Code 推荐扩展

在 VS Code 中安装以下扩展以优化开发体验：

- **C/C++ Extension Pack**（Microsoft）
- **ROS**（Microsoft）
- **CMake**（twxs）
- **Python**（Microsoft）

---

## 编译项目

### 1. 返回工作空间根目录

```bash
cd ~/catkin_ws
```

### 2. 编译全部工程

```bash
catkin_make
```

**预期输出**：
```
...
[100%] Built target warehouse_robot_simulation
Linking CXX executable /home/ros-dev/catkin_ws/devel/lib/warehouse_robot_simulation/WarehouseSimulation
[100%] Built target WarehouseSimulation
```

（或在 VS Code 中按 `Ctrl+Shift+B` 执行默认编译任务）

### 3. 仅编译本项目（可选）

如果只修改了本项目代码，可加速编译：

```bash
catkin_make --pkg warehouse_robot_simulation
```

---

## 运行模拟

### 1. Source 环境变量

每次打开新终端时都需要 source 一次：

```bash
cd ~/catkin_ws
source devel/setup.bash
```

**便利做法**：将以下行添加到 `~/.bashrc` 底部，自动加载：

```bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. 设置脚本权限

```bash
cd ~/catkin_ws/src/warehouse_robot_simulation/scripts
chmod +x *.sh *.py
```

验证权限：
```bash
ls -l *.sh *.py
# 应显示: -rwxr-xr-x (包含 x 可执行标记)
```

### 3. 运行模拟

**推荐方法**：使用 `mission.sh` 一键启动所有组件

```bash
cd ~/catkin_ws/src/warehouse_robot_simulation/scripts
./mission.sh
```

**启动流程**：

| 步骤 | 模块 | 等待时间 | 说明 |
|------|------|---------|------|
| 1 | Gazebo + world | — | 启动 Gazebo 仿真环境 |
| 2 | robot_spawner | 10s | 生成机器人到仿真场景 |
| 3 | AMCL + move_base | 7s | 启动定位和导航堆栈 |
| 4 | WarehouseSimulation | 7s | 启动仓库任务控制节点 |
| 5 | 初始订单 | 10s | 自动发布订单消息 |
| 6 | RViz | 3s | （可选）启动可视化工具 |

**预期现象**：
- Gazebo 窗口显示仓库场景，带有机器人、存储架、分配区和移动障碍物
- 机器人自动規划路径，前往存储架取货
- 机器人导航至分配区，完成订单
- RViz 显示机器人位置、地图、路径和感知信息

### 4. 与模拟交互

#### 发布新订单

在新终端中执行（注意需要 source）：

```bash
source ~/catkin_ws/devel/setup.bash
rostopic pub /warehouse/order/add std_msgs/String "data: 'DispatchB ProductB 2 ProductR 3'"
```

**订单格式**：`DispatchName Product1 Qty1 Product2 Qty2 ...`

**可用分配区**：`DispatchA`、`DispatchB`  
**可用产品**：`ProductR`（红）、`ProductG`（绿）、`ProductB`（蓝）

#### 停止模拟

在任意 xterm 窗口中按 **CTRL+C** 停止对应模块。所有窗口都关闭后即完全停止。

### 5. 手动启动各模块（进阶）

如需调试各组件，可分别启动：

```bash
# 终端 1: Gazebo + 动态障碍物
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot_simulation world.launch

# 终端 2: 生成机器人（等待 5-10 秒后）
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot_simulation robot_spawner.launch

# 终端 3: 定位和导航（等待 3-5 秒后）
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot_simulation amcl.launch

# 终端 4: 仓库任务节点（等待 3-5 秒后）
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot_simulation warehouse_simulation.launch

# 终端 5: RViz 可视化（可选）
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot_simulation view_navigation.launch

# 终端 6: 发布订单（等待 10-15 秒后）
source ~/catkin_ws/devel/setup.bash
rostopic pub /warehouse/order/add std_msgs/String "data: 'DispatchA ProductR 3 ProductG 5'"
```

---

## 故障排除

### 问题 1：找不到 `roslaunch` 命令

**原因**：未 source ROS 环境变量  
**解决**：执行 `source ~/catkin_ws/devel/setup.bash`

### 问题 2：`WarehouseSimulation` 可执行文件不存在

**原因**：编译失败或未编译  
**解决**：
```bash
cd ~/catkin_ws
rm -rf build devel
catkin_make
```

### 问题 3：Gazebo 冻结或无响应

**原因**：系统资源不足或显卡驱动问题  
**解决**：
- 关闭其他应用，释放系统资源
- 尝试 `gazebo --verbose` 查看详细日志
- 检查显卡驱动：`glxinfo | grep "OpenGL version"`

### 问题 4：机器人不能建图或定位失败

**原因**：AMCL 或 move_base 初始化失败  
**解决**：
- 检查 `roslaunch warehouse_robot_simulation amcl.launch` 输出
- 在 RViz 中验证 `/map` 和 `/base_link` 是否可见
- 重新启动 amcl 和 move_base 模块

### 问题 5：脚本权限错误 `Permission denied`

**原因**：脚本未标记为可执行  
**解决**：
```bash
chmod +x ~/catkin_ws/src/warehouse_robot_simulation/scripts/*.sh
```

### 问题 6：VS Code C++ IntelliSense 不工作

**原因**：`.vscode/c_cpp_properties.json` 配置错误  
**解决**：
- 检查 `includePath` 中的路径是否存在
- 如果用户名不是 `ros-dev`，修改 `settings.json` 中的路径

---

## 下一步

- 查阅 [README_CN.md](README_CN.md) 了解项目完整文档
- 查阅 [README.md](README.md) 了解英文文档
- 学习 ROS 导航栈的工作原理
- 修改 `launch/` 目录中的参数进行自定义调整
- 在 `worlds/` 目录中编辑环境或添加新障碍物

---

