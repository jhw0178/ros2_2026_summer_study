import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import Twist
import math

class TfListener(Node):
    def __init__(self):
        super().__init__("tf_listener")
        self.target_frame = (self.declare_parameter("target_frame", "turtle2").get_parameter_value().string_value)
        self.source_frame = (self.declare_parameter("source_frame", "turtle1").get_parameter_value().string_value)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.tf_timer = self.create_timer(1, self.timer_callback)
        
        self.cmd_pub = self.create_publisher(Twist, "/turtle2/cmd_vel", 10)
        
        
    def timer_callback(self):

        try:
            t = self.tf_buffer.lookup_transform(
                self.target_frame,
                self.source_frame,
                Time()
                )

            x = t.transform.translation.x
            y = t.transform.translation.y

            distance = math.sqrt(x*x + y*y)
            angle = math.atan2(y, x)

            self.get_logger().info(
                f"x={x:.2f}, y={y:.2f}, d={distance:.2f}, angle={angle:.2f}"
            )

            msg = Twist()

            if abs(angle) > 0.3:
                msg.linear.x = 0.0
                msg.angular.z = angle
            else:
                msg.linear.x = 0.5 * distance
                msg.angular.z = angle

            self.cmd_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(str(e))
        
        
    
def main(args=None):
        rclpy.init(args=args)  # rmw 활성화
        node = TfListener()
        try:
            rclpy.spin(node)  # 블럭 (무한 루프)
        except KeyboardInterrupt:
            print("키보드 인터럽트")
        finally:
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
        main()         