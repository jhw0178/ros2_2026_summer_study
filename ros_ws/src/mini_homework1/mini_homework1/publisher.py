import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PublisherNode(Node):
    def __init__(self):
        super().__init__("publisher_node")
        self.publisher1 = self.create_publisher(String, "topic1", 10)
        self.publisher2 = self.create_publisher(String, "topic2", 10)
        self.timer1 = self.create_timer(1.0, self.timer_callback1)
        self.count1 = 0
        self.count2 = 0

    def timer_callback1(self):
        msg1 = String()
        msg1.data = f"첫 번째 토픽입니다. {self.count1}"
        self.publisher1.publish(msg1)
        self.get_logger().info(msg1.data)
        self.count1 += 1

        msg2 = String()
        msg2.data = f"두 번째 토픽입니다. {self.count2}"
        self.publisher2.publish(msg2)
        self.get_logger().info(msg2.data)
        self.count2 += 1
        
def main(args=None):
    rclpy.init(args=args)
    node = PublisherNode()
    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()