#!/bin/sh
# Mission launch script - starts all nodes in sequence with delays
# Usage: bash scripts/mission.sh

# 1. Launch Gazebo world + dynamic barriers
xterm -e "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; roslaunch warehouse_robot_simulation world.launch" &
sleep 10

# 2. Spawn robot into Gazebo
xterm -e "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; roslaunch warehouse_robot_simulation robot_spawner.launch" &
sleep 7

# 3. Start AMCL localization and move_base navigation
xterm -e "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; roslaunch warehouse_robot_simulation amcl.launch" &
sleep 7

# 4. Start WarehouseSimulation node
xterm -e "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; roslaunch warehouse_robot_simulation warehouse_simulation.launch" &
sleep 10

# 5. Publish initial order (DispatchA: 3x ProductR, 5x ProductG)
xterm -e "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; rostopic pub -1 /warehouse/order/add std_msgs/String \"data: 'DispatchA ProductR 3 ProductG 5'\"" &
sleep 3

# 6. (Optional) Start RViz for visualization
# xterm -e "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; roslaunch warehouse_robot_simulation view_navigation.launch" &