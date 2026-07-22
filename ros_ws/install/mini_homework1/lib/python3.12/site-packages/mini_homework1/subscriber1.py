import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SubscriberNode1(Node):
    def __init__(self):
        super().__init__("subscriber_node1") 
        self.subscriber1 = self.create_subscription(String, "topic1", self.sub_callback1, 10)
        self.count3 = 0
    
    def sub_callback1(self, msg1):
        self.get_logger().info(f"SubscriberNode1이 받은 메시지 : {msg1.data} {self.count3}")
        self.count3 += 1

def main(args=None):
    rclpy.init(args=args) 
    node = SubscriberNode1()

    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

    if __name__ == '__main__':
        main()