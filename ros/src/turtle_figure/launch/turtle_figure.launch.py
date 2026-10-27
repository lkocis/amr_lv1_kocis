import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # putanja do rosbridge launch datoteke (XML) unutar instaliranog paketa
    rosbridge_launch = os.path.join(
        get_package_share_directory('rosbridge_server'),
        'launch',
        'rosbridge_websocket_launch.xml',
    )

    return LaunchDescription([
        # 1. turtlesim simulator (GUI prozor)
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        # 2. cvor koji vodi kornjacu po krivulji
        Node(
            package='turtle_figure',
            executable='figure_controller',
            name='figure_controller',
            output='screen',
        ),
        # 3. rosbridge server (WebSocket, port 9090)
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(rosbridge_launch),
            launch_arguments={'port': '9090'}.items(),
        ),
    ])