import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class Move_Turtle(Node):
    def __init__(self):
        super().__init__('move_turtle')
        self.publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.count = 0.0

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.0 + self.count
        msg.angular.z = 1.0
        self.publisher.publish(msg)
        self.count += 0.01

def main(args=None):
    rclpy.init(args=args)
    node = Move_Turtle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()
        rclpy.shutdown()
if  __name__ == '__main__':
    main()

