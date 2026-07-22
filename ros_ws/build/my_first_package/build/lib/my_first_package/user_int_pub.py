import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from user_interface.msg import UserInt

class UserIntPUb(Node):
    def __init__(self):
        super().__init__("user_int_pub") 
        self.create_timer(1, self.timer_callback) 
        self.UserInt_pub = self.create_publisher(UserInt, "user_int", 10)
        self.count = 0

    def timer_callback(self):
        msg = UserInt()
        msg.user_int1 = 12
        msg.user_int2 = 23
        msg.user_int3 = 53
        msg.header.frame_id = "time_test"
        msg.header.stamp = self.get_clock().now().to_msg()
        self.get_logger().info(f"user_interface의 UserInt 인터페이스로 발행하는 메시지 : {msg.user_int1} {msg.user_int2} {msg.user_int3}")
        self.UserInt_pub.publish(msg)
        self.count += 1

def main(args=None):
    rclpy.init(args=args) 
    node = UserIntPUb() 

    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()
