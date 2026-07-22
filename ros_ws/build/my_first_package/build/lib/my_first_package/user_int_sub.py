import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from user_interface.msg import UserInt

class UserIntSub(Node):
    def __init__(self):
        super().__init__("user_int_sub") 
        self.UserInt_sub = self.create_subscription(UserInt, "user_int", self.sub_callback, 10)
        self.count = 0

    def sub_callback(self, msg: UserInt):
        self.get_logger().info(f"수신 메시지: {msg.user_int1} {msg.user_int2} {msg.user_int3} {msg.header.frame_id} : {msg.header.stamp} : {self.count}")
        self.count += 1

def main(args=None):
    rclpy.init(args=args) 
    node = UserIntSub() 

    try:
        rclpy.spin(node)
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

    if __name__ == '__main__':
        main()