import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose, Color

class MoveTurtle1(Node):
    def __init__(self):
        super().__init__('move_turtle')
        self.publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.create_subscription(Pose, 'turtle1/pose', self.pose_callback, 10)
        self.create_subscription(Color, 'turtle1/color_sensor', self.color_callback, 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.count = 0.0
        self.pose = Pose()
        self.color = Color()

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.0 + self.count
        msg.angular.z = 1.0
        self.publisher.publish(msg)
        self.count += 0.01
        if self.count > 3.0:
            self.count = 0.0
    
    def pose_callback(self, msg: Pose):
        self.pose = msg

    def color_callback(self, msg: Color):
        self.color = msg

def main(args=None):
    rclpy.init(args=args)
    node = MoveTurtle1()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()
        rclpy.shutdown()
if  __name__ == '__main__':
    main()

