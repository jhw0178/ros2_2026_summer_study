import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jhw0178/ros2_2026_summer_study/ros_ws/install/my_first_package'
