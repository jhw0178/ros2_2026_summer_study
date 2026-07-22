from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package="my_first_package", executable="message1_pub"),
            Node(package="my_first_package", executable="message_sub"),
        ]
    )