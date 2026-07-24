# ros2 run turtlesim turtlesim_node
# rviz2
# ros2 run tf2_basic dynamic_turtle_tf2_broadcaster
# ros2 run tf2_basic tf_listener
# ros2 run turtlesim turtle_teleop_key
# 과제 : turtlesim을 따라가는 두번째 turtle2를 생성 -> turtle spawn은 service 코드 사용
# timer는 1.0 간격으로 회전과 정지, 전진을 tf look-up 정보로 구현

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class TurtleTfListener(Node):
    def __init__(self):
        super().__init__("tf_listener")
        self.target_frame = (self.declare_parameter("target_frame", "turtle1").get_parameter_value().string_value)
        self.source_frame = (self.declare_parameter("source_frame", "world").get_parameter_value().string_value)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.create_timer(1, self.timer_callback)
        
    def timer_callback(self):
        try:
            t: TransformStamped = self.tf_buffer.lookup_transform(self.target_frame, self.source_frame, Time())
            self.get_logger().info(f"{t}")
        except:
            pass
        
def main(args=None):
    rclpy.init(args=args)  # rmw 활성화
    node = TurtleTfListener()
    try:
        rclpy.spin(node)  # 블럭 (무한 루프)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()        