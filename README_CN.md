# warehouse_robot_simulation（仓库机器人模拟）

![仓库模拟](docs/images/warehouse_simulation.gif)

该项目是一个自动化仓库模拟系统，包含一个自主移动机器人，能够根据`订单`请求从`存储单元`获取所需的`产品`，并将其送往相应的`分配区`。

> 该项目开发用于Udacity C++工程师纳米学位项目的"顶石项目"。在开发时结合了Udacity机器人软件工程师纳米学位项目所学内容，该项目之前开发过一个家庭服务机器人模拟系统（代码库[在这里](https://github.com/rodriguesrenato/rse-nd-home-service-robot)），机器人能够在两个目标位置之间自主导航。

# 依赖项

该项目在 **Ubuntu 20.04 LTS** 上开发和运行。需要以下依赖/包：

- gcc/g++ >= 9.0
- make >= 4.2
- cmake >= 3.16
- ROS Noetic
- Gazebo 11
- RViz
- ROS Noetic 包：
    - amcl
    - move_base
    - dwa-local-planner
    - map_server
    - gmapping（可选，仅用于重新建图）
    - teleop_twist_keyboard（可选，仅用于手动建图）

# 安装

## 1. 检查并安装 ROS Noetic

如果尚未安装 ROS Noetic，请参考 [ROS Noetic 安装指南](http://wiki.ros.org/noetic/Installation/Ubuntu)。

验证安装：
```bash
rosversion -d
# 应输出: noetic
```

## 2. 检查并安装 Gazebo 11

ROS Noetic 默认配套 Gazebo 11，通常随 `ros-noetic-desktop-full` 一同安装。

验证安装：
```bash
gazebo --version
# 应输出: Gazebo multi-robot simulator, version 11.x.x
```

如未安装，执行：
```bash
sudo apt-get update
sudo apt-get install gazebo11 libgazebo11-dev
sudo apt-get install ros-noetic-gazebo-ros-pkgs ros-noetic-gazebo-ros-control
```

## 3. 检查并安装 RViz

验证安装：
```bash
rosrun rviz rviz --version
# 应输出版本号，如: 1.14.x
```

如未安装，执行：
```bash
sudo apt-get install ros-noetic-rviz
```

## 4. 安装 ROS 依赖包

通过 **apt-get** 安装必需和可选的 ROS 包：

```bash
sudo apt-get install ros-noetic-amcl
sudo apt-get install ros-noetic-move-base
sudo apt-get install ros-noetic-dwa-local-planner
sudo apt-get install ros-noetic-map-server
sudo apt-get install ros-noetic-teleop-twist-keyboard
sudo apt-get install ros-noetic-gmapping
sudo apt-get install ros-noetic-slam-gmapping
```

## 5. 克隆并编译项目

假设你的 catkin 工作空间 `catkin_ws` 位于 `~/` 目录，在 src 文件夹中克隆此存储库：

```bash
cd ~/catkin_ws/src
git clone https://github.com/rodriguesrenato/warehouse_robot_simulation.git
```

- 可选：如果你计划为此模拟构建新地图，请同时克隆以下存储库：
    ```bash
    git clone https://github.com/ros-perception/slam_gmapping.git
    git clone https://github.com/ros-teleop/teleop_twist_keyboard
    ```

- 注意：如果选择了不同的项目目录，则需要在编译前手动更改 `src/WarehouseSimulation.cpp` 文件中的 `projectDirectory` 值（默认相对于 `~/.ros/`）。

编译并 source：

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## 6. 安装 Xterm 并设置脚本权限

**Xterm** 用于在独立终端窗口中执行各启动文件。如果未安装，请运行：

```bash
sudo apt-get install xterm
```

使脚本文件可执行：

```bash
cd ~/catkin_ws/src/warehouse_robot_simulation/scripts
chmod +x *.sh
```

# 使用方法

运行模拟有以下选项：

- **推荐**：在 `scripts` 文件夹中打开终端并运行 `mission.sh`，它会按正确启动顺序在独立 xterm 窗口中依次启动所有节点，并自动发布初始订单：

    ```bash
    cd ~/catkin_ws/src/warehouse_robot_simulation/scripts
    ./mission.sh
    ```

    各步骤启动顺序如下：
    1. `world.launch`：启动 Gazebo 并加载 `warehouse.world`（含动态障碍物）
    2. `robot_spawner.launch`（等待 10s 后）：在仿真中生成机器人
    3. `amcl.launch`（等待 7s 后）：启动 AMCL 定位和 move_base 导航
    4. `warehouse_simulation.launch`（等待 7s 后）：启动仓库任务节点
    5. 自动发布初始订单（等待 10s 后）
    6. `view_navigation.launch`（等待 3s 后）：启动 RViz 可视化（可选）

- 或按指定顺序手动启动各 `.launch` 文件：

    1. `roslaunch warehouse_robot_simulation world.launch`：启动 Gazebo 并加载 `warehouse.world` 文件。
    2. `roslaunch warehouse_robot_simulation robot_spawner.launch`：在模拟中生成机器人。
    3. `roslaunch warehouse_robot_simulation amcl.launch`：启动 AMCL 和 move_base 节点。
    4. `roslaunch warehouse_robot_simulation warehouse_simulation.launch`：启动仓库模拟。

与模拟交互的唯一方式是通过ROS话题`/warehouse/order/add`发布`订单`消息。`订单`消息将被正在运行的`OrderController`接收。

最简单的方法是直接在终端中发布ROS消息。`订单`定义为遵循此模式的单行纯文本字符串：`target_dispatch_model_name product product_quantity product_n product_n_quantity`

例如，要发布以下订单：`DispatchA ProductR 3 ProductG 5`，请在终端中运行：

```bash
rostopic pub /warehouse/order/add std_msgs/String "data: 'DispatchA ProductR 3 ProductG 5'"
```

- 上述命令将在模拟中放置一个`订单`，其中包含3个`ProductR`和5个`ProductG`要在`DispatchA`处分配。

- 以下模型对象可用于构建订单：
    - 产品：`ProductR`、`ProductG`和`ProductB`
    - 分配区：`DispatchA`和`DispatchB`

- 如果尝试发送包含无效分配区、产品或数量的订单，该订单将被模拟在内部丢弃。

要结束模拟，只需在运行WarehouseSimulation节点的终端上按**CTRL+C**，并等待其完成关闭过程。

如果要在rviz中检查导航，请运行：

```
roslaunch warehouse_robot_simulation view_navigation.launch
```

如果要使用SLAM gmapping生成新的地图文件，请按照以下步骤操作：

- 在scripts文件夹中打开终端并运行映射脚本：`./mapping_slam.sh`
    - 它在Gazebo中启动世界和机器人，然后运行`slam_gmapping.launch`

- 使用teleop键盘导航机器人穿过你的地图，直到覆盖大部分区域。如果Rviz中显示的生成的地图不够好，请在`slam_gmapping.launch`文件中调整gmapping参数并重新启动此过程。

- 如果Rviz中显示的生成的地图足够好，打开新终端，更改目录到该项目的`map`文件夹，然后通过运行以下命令保存新地图：

```
rosrun map_server map_saver -f warehouse.
```

# 模拟

模拟具有以下主要组件：
- Gazebo中的仓库世界
- URDF机器人
- AMCL和导航节点
- WarehouseSimulation ROS节点

## 仓库世界

![仓库世界](docs/images/warehouse_world.png)

该世界是仓库的简化版本，设计成存储区在上面图像的右侧，分配区在左侧，因此机器人必须通过走廊获取产品并将其送到开放区域的左侧，类似于一些物流仓库的配置。

## URDF机器人

![URDF机器人](docs/images/urdf_robot.png)

该机器人采用两轮配置设计，在边缘处有脚轮轮子，后部有货物床，以及用于映射和定位的两个传感器（摄像头和Lidar）。

它使用URDF格式和.xacro文件构建，基于并改进了我之前的项目[home_service_robot](https://github.com/rodriguesrenato/rse-nd-home-service-robot)，添加了一些宏函数来帮助调整参数和计算惯性值。

## 映射、定位和导航节点

这些节点基于[home_service_robot](https://github.com/rodriguesrenato/rse-nd-home-service-robot)项目。

SLAM`gmapping`包用于构建仓库地图。地图通过`map_server`包加载，定位由`AMCL`包执行，导航由`move_base`包执行。
导航参数基于koburi/turtlebot导航参数作为起点，并针对此应用进行了调整。`inflation_radius`参数已增加以避免过于接近墙壁和地面物体

## WarehouseSimulation ROS节点

这是主模拟节点，使用ROS和C++开发。除了机器人和必须事先启动的定位/导航节点外，模拟中的所有对象都在warehouseSimulation节点中实例化/处理。下面의列表显示了该节点的主要操作流程。

1. 初始化WarehouseSimulation节点并创建仓库控制器和对象。

2. 由modelController类加载将在模拟中使用的所有SDF模型，并将其文件内容存储在`modelname:fileContent`的字典中。模型文件可在`models/warehouseObjects`文件夹中找到。

3. 读取存储单元和分配区配置文件以将Storage和Dispatch对象添加到模拟中。这些对象在配置文件的每一行中定义。InstatiateWarehouseObjects函数逐行处理这些配置文件，用读取的值构造相应对象，并将其推送回相应对象的向量。如果此过程中发生任何异常/问题，模拟将中止。

4. 创建`机器人`对象并配置它。模拟被设计为处理多个机器人，但在当前版本中只使用一个机器人。查看`Robot`构造函数获取更多有关设置多个`机器人`所需参数的信息。

5. 迭代每个创建的`存储单元`、`分配区`和`机器人`，以启动操作线程和/或在Gazebo模拟中生成其对象模型。`存储单元`操作线程负责保持`存储单元`以最大容量生产`产品`。`机器人`操作线程负责在执行`订单`和与所有其他仓库对象交互时循环执行任务。

6. 在话题`warehouse/order/add`设置ROS仓库以接收`订单`请求并将其发送到`OrderController::AddOrder`。此订阅函数在内部打开新线程来调用作为引用传递的`OrderController`的AddOrder成员函数。

7. 设置新的`SIGINT`处理程序，以让模拟在完整的ros关闭前调用之前生成的所有模型的`ModelController::Delete`。第1步中的`ros::init`使用标志`ros::init_options::NoSigintHandler`设置，以允许设置自定义处理程序。

8. while循环保持调用`ros::spinOnce()`以处理单轮ROS回调，直到全局变量`isShutdown`被设置或ROS关闭。

9. 当按下**CTRL+C**时，`isShutdown`设置为true，迭代所有Storage、Dispatch和Robot以从Gazebo模拟中调用删除模型

10. 从Gazebo删除生成的模型后，通过调用`ros::shutdown()`完全关闭此ros节点

## C++类结构

对每个实现的类的简要说明
- 程序C++类
    - WarehouseObject
    - Robot
    - Storage
    - Dispatch
    - Product
    - Order
    - OrderController
    - ModelController

### WarehouseObject

这是该模拟的所有对象和控制器的基类。它负责生成唯一id，通过`Print()`成员函数打印受互斥体保护的终端消息，通过`GetName()`检索其唯一名称，并将所有启动的线程存储在向量中以在其析构函数上构建线程屏障。它以编程方式实现了结束对象（`Storage`和`Robot`）成员函数的方法，这些成员函数在线程中启动（在后面部分中说明）。

### Robot

![URDF机器人](docs/images/urdf_robot.png)

在该模拟中，使用两轮移动机器人。它后部有货物床以携带`产品`，有Lidar和摄像头传感器以在环境中定位自己并导航，并且它可以与其他`仓库对象`交互。

`Robot`类具有设置/返回其状态的成员函数，返回货物床中的产品名称列表，以及负责启动运行`Operate()`的线程的StartOperation成员函数。它还具有构建具有当前订单中产品的存储向量、与SimpleActionClient交互以移动机器人以及根据RobotStatus操作机器人的私有成员函数。

在`Operate()`私有成员函数中，实现了`RobotStatus`的状态机，它连续运行直到_status设置为`offline`。每个`RobotStatus`负责下面列出的任务。一些操作变量在状态机范围之前创建，以在状态之间循环时保持持久性。采用此策略是为了连续检查机器人_status是否设置为`offline`，然后终止该线程。调用`Robot`析构函数时，它将_status设置为`offline`。

可用的`RobotStatus`任务：

- `offline`：机器人不可操作并关闭。

- `startup`：初始化SimpleActionClient并等待其准备好将_status更改为`requestOrder`。

- `standby`：只是等待_status更改。

- `requestOrder`：向OrderController请求订单，如果得到订单则更改_status为`processOrder`。

- `processOrder`：清除操作变量，获取存储列表以获取订单产品并获取目标分配区共享指针。如果找不到任何存储或有效分配区，则将_state设置为`closeOrder`。

- `plan`：在此状态下，设置下一个目标存储，从storagesToGo向量中删除此存储并将_state设置为`moveToStorage`。如果storagesToGo变空，则将_state设置为`moveToDispatch`。

- `moveToStorage`：将机器人移动到存储产品输出位置。如果到达目标，则将_status设置为`requestProduct`，否则在下一个状态机迭代中重试。

- `requestProduct`：调用目标存储的`RequestProduct()`成员函数，直到获得订单中指定的有效产品数量。`RequestProduct()`返回一个**unique_ptr<Product>**，将被移动到Robot`_cargoBinProducts`属性，将产品的所有权从存储传递给机器人。当存储没有可用产品时，它将返回nullptr，不会被计算和添加到`_cargoBinProducts`。

- `moveToDispatch`：将机器人移动到分配区产品拾取位置。如果到达目标，则将_status设置为`dispatchOrder`，否则在下一个状态机迭代中重试。

- `dispatchOrder`：调用目标分配区`PickProduct()`成员函数，一一移动`_cargoBinProducts`中的产品，将产品所有权从机器人传递给分配区，直到`_cargoBinProducts`变空。之后，将_status设置为`closeOrder`。

- `closeOrder`：关闭此订单并将_state设置为`requestOrder`以请求新订单。

### Storage

![存储单元](docs/images/storage_unit.png)

`Storage`类负责在构造函数中定义的产品的生产、存储和处理。

`Production()`私有成员函数连续生产指定的`产品`直到达到最大容量。此函数由`StartOperation`公共成员函数在线程中启动。

`RequestProduct()`公共成员函数处理在指定的`产品输出位置`生成`产品`的`产品`请求。它返回生产的`std::unique_ptr<Product>`，将所有权从存储传递给调用者。

它还具有返回其位置和模型名称的成员函数，以及其产品输出位置和模型名称。

### Dispatch

![存储单元](docs/images/dispatch_unit.png)

`Dispatch`类负责在机器人请求时从其`PickProducts()`成员函数拾取所有订单产品。

它还具有返回其位置和模型名称的成员函数，以及拾取产品的位置。

### Product

![存储单元](docs/images/productR.png)

`Product`类是将在此模拟中处理的产品的简单表示。它存储模型名称，由`GetModelName()`成员函数返回。

### Order

`Order`类表示单个订单"配方"，其中包含目标分配区和产品及其相应数量的无序映射。它还存储处理此订单的机器人名称的信息。

### OrderController

`OrderController`负责接收和请求的订单队列的管理。

订单通过`AddOrder()`成员函数添加到队列中，该函数设置为节点句柄订阅函数在话题`warehouse/order/add`上的回调函数。要添加订单，请在此话题上发布纯文本，以此顺序模式遵循，用单个空格分隔item：

`target_dispatch_model_name product product_quantity product_n product_n_quantity`

机器人可以通过调用`RequestNextOrder()`或`RequestNextOrderWithTimeout()`向队列请求订单。在两个成员函数中都实现了条件变量以等待队列中可用的订单并避免并发问题。`RequestNextOrderWithTimeout()`设置超时时间以避免在等待订单时卡住，其状态机实现在获得可用订单前多次调用此函数。这允许机器人在订单可用前执行其他任务。

对于图形订单监视器的未来实现，`GetOrdersTracking()`函数返回由机器人处理的所有订单。这是订单创建为`std::shared_ptr<Order>`的原因，所以可以使多个机器人和主控制器之间协作处理订单。

### Model Controller

`ModelController`类负责与Gazebo模拟交互。

`Add()`成员函数读取模型XML文件内容并将其存储在与其模型名称作为键值关联的无序映射中。

`Spawn()`成员函数接收唯一对象名称、对象的模型名称和对象要生成的所需位置。此函数获取之前加载的所需模型名称的预加载模型XML，并调用`GazeboSpawn()`私有函数，该函数负责使用正确的参数在`gazebo/spawn_sdf_model`话题上调用ros服务以在模拟中生成此对象。

`Delete()`成员函数的工作方式类似于`Spawn()`，它调用`GazeboDelete()`私有成员函数，该函数负责在`gazebo/delete_model`话题上调用ros服务以从模拟中删除对象。

还有`ReadModel()`私有成员函数，它读取指定文件路径的文件，将整个文件内容转换为字符串格式并返回。此函数由`Add()`使用。

# 实现的现代C++特性

- 所有类都使用OOP设计和构建。

- warehouseObject类设计为具有所有其他类之间的公共功能和信息，如`objectName`和受互斥体保护的`Print()`函数。调用析构函数时，它使线程屏障确保由子类启动的所有线程在超出范围前完成。

- `WarehouseObject::Print()`负责将`std::cout`输出标准化为格式`[ObjectName] message`。

- 创建了两个配置文件来定义将创建多少个`存储单元`和`分配区`，以及对每个进行配置，因此不需要对这些配置进行硬编码。这些文件在`warehouseSimulation.cpp`中处理。

- 在文件读取操作中，设置了try catch表达式以防止加载错误的`存储单元`和/或`分配区`配置和字符串到int/float异常。在这种情况下，它警告用户修复相应的配置文件并在向Gazebo生成任何模型前完成模拟。

- 所有将在模拟中使用的SDF模型都加载并在`ModelController`类中存储其文件XML内容，以避免多次读取文件。它们存储在unordered_map字典中，内容的键是文件名。文件名定义为模型名称。

- 除了`Product`类外，所有类都实例化为**shared pointers**。`产品`是模拟中的唯一对象，只有一个类必须拥有所有权，因此它们始终实例化为**unique pointers**，**std::move**用于在仓库对象之间传递其所有权。

- **shared pointers**的创建类被复制到其构造函数中的本地成员属性，以供该类成员函数在内部使用。

- `Storage`和`Robot`类通过其`StartOperation()`成员函数在模拟中启动线程。

    - `Storage::StartOperation()`启动线程以运行私有成员函数`Production()`。此函数运行while循环直到私有属性`_productionModelName`为空（调用析构函数时，`_productionModelName`被清除以编程方式完成此线程）。此循环以2秒的固定速率将新的`unique_ptr<Product>`添加到私有属性`_storedProducts`，直到达到`_maxCapacity`。

    - `Storage::_storedProducts`总是在创建`Storage::_storageMtx`互斥体的lock_guard后读取/修改。

    - `Robot::StartOperation()`启动线程以运行私有成员函数`Operate()`。此函数运行while循环直到私有属性`_status`为空（调用析构函数时，`_status`设置为`RobotStatus::offline`以编程方式完成此线程）。此循环负责循环遍历RobotStatus任务，设计为状态机行为模式。采用此方法是为了使多个行为路径成为可能，接受外部命令来更改计划，并持续检查何时需要结束该线程。

    - `Robot::_cargoBinProducts`总是在创建`Robot::_cargoBinMtx`互斥体的lock_guard或unique_lock后读取/修改。

- `ModelController`类被构建以处理与Gazebo相关的所有内容，并直接进行ros服务调用以从Gazebo生成和删除模型。由于复杂性，机器人生成取决于其他ros节点如amcl和move_base，所以此功能将在未来版本中添加。

- `OrderController`实现一个队列，该队列使用**条件变量**和**互斥体**（`OrderController::_queueMtx`）来处理`订单`请求，防止并发错误。

- `OrderController::AddOrder()`接收来自ros的字符串消息，并用`std::istringstream`处理它来解析值并构建`订单`。此`订单`在使用`std::lock_guard`与`OrderController::_queueMtx`互斥体的锁下添加到`OrderController::_queue`。

- `Order`和`Product`类只是存储其对象信息并通过其他仓库对象共享/移动的简单类。

- `Dispatch::PickProduct()`成员函数只是接收移动的`std::unique_ptr<Product>`，并让此`产品`在范围末尾析构。这样做是因为我们在模拟中以后没有对此`产品`执行任何操作。

# 项目评分要点

> 提交必须编译并运行。
 
- 为了在Udacity工作空间中工作，必须在脚本文件的声明路径中进行一些路径调整（source kinetic而不是melodic）
- 有一个项目在Udacity工作空间中运行的屏幕截图。
![仓库模拟在Udacity工作空间中运行](docs/images/simulation_udacity_workspace.png)
- 由于高处理能力，从脚本中删除了Rviz可视化。

## 循环、函数、输入/输出

> 项目展示了对C++函数和控制结构的理解。

- 项目类根据其在模拟中的目的进行了很好的组织

> 项目从文件读取数据并处理数据，或程序写入数据到文件。

- `ModelController`类读取SDF模型文件，`WarehouseSimulation.cpp`在本地函数`InstatiateWarehouseObjects`中读取两个配置文件。

## 面向对象编程

> 项目使用面向对象编程技术。

- 所有类都使用OOP，并在`warehouseSimulation.cpp`中使用。

> 类为类成员使用适当的访问说明符。

- 所有成员属性通过访问器和变异器函数从外部访问/修改。

> 类从其接口抽象实现细节。

> 类封装行为。

> 类遵循适当的继承层次结构。

- 所有类都有`WarehouseObject`类作为父类

## 内存管理

> 项目在函数声明中使用引用。

> 项目适当地使用析构函数。

- `WarehouseObject`类使用析构函数构建线程屏障并等待所有启动的线程完成。
- 在`Storage`和`Robot`类中，析构函数用于将成员属性设置为将在其内部周期中触发由它们启动的所有线程终止的值。

> 项目使用move semantics来移动数据，而不是在可能的情况下复制它。

- std:move用于在`Robot`（Robot.cpp第278、323行）、`Storage`（Storage.cpp第57、60、91行）和`Dispatch`对象之间移动`std::unique_ptr<Products>`对象。它也在`OrderController.cpp`（第76、113、412行）中使用来在`_queue`成员属性中移入/移出`订单`。

> 项目使用智能指针代替原始指针。

- 广泛使用共享指针，唯一指针用于处理`Product`类。

## 并发

> 项目使用多线程。

- `Storage.cpp`（第72行）和`Robot`（第76行）通过其`StartOperation()`成员函数在模拟中启动线程。

> 项目中使用互斥体或锁。

- 在`WarehouseObject.cpp`（第38行）中通过使用具有`std::lock_guard`的`_coutMtx`互斥体来保护对std::cout的打印。

- 在`Storage.cpp`（第51、86行）中保护`_storedProducts`免受`Storage::Production()`和`Storage::RequestProduct()`的并发访问/修改。

- 在`Robot.cpp`（第58、277、322行）中保护`_cargoBinProducts`免受`Robot::Operate()`和`GetCargoBinProductsName()`的并发访问/修改。

- 在`OrderController.cpp`（第75、108、132行）中保护deque`_queue`，（第87、98、119、148行）保护vector`_ordersTracking`免受并发访问/修改

> 项目中使用条件变量。

- 它在`OrderController.cpp`中用于从`Robots`处理`订单`请求（第109、133行），并在`订单`被添加到`_queue`时通知（第77行）。

# 下一步要实现的功能

- 从warehouseSimulation节点启动机器人和相应的amcl/move_base节点
- 使用ncurses设计完整的操作仪表板以跟踪所有仓库对象
- 多个机器人在模拟中
- 测试其他路径规划算法以定义"车道"和在存储单元和分配区的等待队列。

# 许可证

此存储库的内容受MIT许可证保护。

# 参考资料

- Ros wiki：(http://wiki.ros.org/)
- C++参考：(https://www.cplusplus.com/)
- 如何在ros中添加编译器选项`pthreads`：(https://stackoverflow.com/questions/67300703/how-do-i-use-the-pthreads-in-a-ros-c-node)
