from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package="mini_homework1", executable="time_publisher"),
        Node(package="mini_homework1", executable="publisher"),
        Node(package="mini_homework1", executable="time_and_topic1_subscriber"),
        Node(package="mini_homework1", executable="subscriber1"),
        Node(package="mini_homework1", executable="subscriber2"),
    ])