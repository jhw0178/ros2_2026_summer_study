import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SubscriberNode2(Node):
    def __init__(self):
        super().__init__("subscriber_node2") 
        self.subscriber2 = self.create_subscription(String, "topic2", self.sub_callback2, 10)
        self.count4 = 0
    
    def sub_callback2(self, msg2):
        self.get_logger().info(f"SubscriberNode2이 받은 메시지 : {msg2.data} {self.count4}")
        self.count4 += 1

def main(args=None):
    rclpy.init(args=args) 
    node = SubscriberNode2() 

    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

    if __name__ == '__main__':
        main()