from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python import get_package_share_directory
from launch.actions import DeclareLaunchArgument

import os

def generate_launch_description():
    param_dir = LaunchConfiguration('param_dir', default=os.path.join(get_package_share_directory("my_first_package"), "param", "my_param.yaml"))
    return LaunchDescription(
        [
            DeclareLaunchArgument('param_dir', default_value=param_dir, description="launch parameter를 지정하는 옶션"),
            Node(package="my_first_package", executable="my_param", parameters=[{"my_param": "launch에서 설정한 값"}])
        ]
    )