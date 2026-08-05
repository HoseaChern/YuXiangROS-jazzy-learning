#!/bin/zsh
WS_DIR="/home/changli/Documents/ROS/YuXiangROS/Chap4/4.2_4.3_Service_ws"
cd "$WS_DIR"

source .venv/bin/activate
export PATH="$WS_DIR/.venv/bin:$PATH"

source /opt/ros/jazzy/setup.zsh
source ./install/setup.zsh

echo "ROS 2 workspace ready: $WS_DIR"
echo "Python: $(which python3)"
echo "colcon: $(which colcon)"
