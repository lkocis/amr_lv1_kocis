FROM ros:jazzy-ros-base

RUN apt-get update && apt-get install -y \
    ros-jazzy-turtlesim \
    ros-jazzy-rosbridge-suite \
    python3-colcon-common-extensions

# GUI (2D) podrska
ENV DISPLAY=:0

# ROS radno okruzenje
WORKDIR /ws
COPY src ./src
RUN . /opt/ros/jazzy/setup.sh && colcon build

CMD ["bash", "-c", "source /ws/install/setup.bash && ros2 launch turtle_figure turtle_figure.launch.py"]