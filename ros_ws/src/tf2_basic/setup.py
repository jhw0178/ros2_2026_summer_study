from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'tf2_basic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob(os.path.join("launch", "*.launch.py"))),
        ("share/" + package_name + "/urdf", glob(os.path.join("urdf", "*.*"))),
        ("share/" + package_name + "/rviz", glob(os.path.join("rviz", "*.*"))),
        ("share/" + package_name + "/meshes", glob(os.path.join("meshes", "*.*"))),
        ("share/" + package_name + "/data", glob(os.path.join("data", "*.yaml"))),
    ],
    install_requires=['setuptools', 'PyYAML'],
    zip_safe=True,
    maintainer='jhw0178',
    maintainer_email='jhw0178@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "static_turtle_tf2_broadcaster = tf2_basic.static_turtle_tf2_broadcaster:main",
            "dynamic_turtle_tf2_broadcaster = tf2_basic.dynamic_turtle_tf2_broadcaster:main",
            "tf_listener = tf2_basic.tf_listener:main",
            "tf_motion = tf2_basic.tf_motion:main",
            "move_manipulator = tf2_basic.move_manipulator:main",
            "dance_player = tf2_basic.dance_player:main",
            "move_manipulator_action = tf2_basic.move_manipulator_action:main",
            "dance_player_action = tf2_basic.dance_player_action:main",
            "teach_manipulator = tf2_basic.teach_manipulator:main",
            "teach_manipulator2 = tf2_basic.teach_manipulator2:main",
            "play_recorded_dance = tf2_basic.play_recorded_dance:main",
            "teach_manipulator3 = tf2_basic.teach_manipulator3:main",
            "dance_manipulator = tf2_basic.dance_manipulator:main",
            "moveit_test = tf2_basic.moveit_test:main",
            "moveit_class = tf2_basic.moveit_class:main",
            "moveit_class2 = tf2_basic.moveit_class2:main",
            "moveit_scene_monitor = tf2_basic.moveit_scene_monitor:main",
            "moveit_attached = tf2_basic.moveit_attached:main",
            "moveit_mini_project = tf2_basic.moveit_mini_project:main",
        ],
    },
)
