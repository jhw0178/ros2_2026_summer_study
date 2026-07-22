import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Header

class TimeAndTopic1SubscriberNode(Node):
    def __init__(self):
        super().__init__("time_and_topic1_subscriber_node")
        self.subscriber3 = self.create_subscription(String, "topic1", self.sub_callback3, 10)
        self.subscriber4 = self.create_subscription(Header, "timetopic", self.sub_callback4, 10)
        self.count5 = 0
        self.count6 = 0

    def sub_callback3(self, msg1):
        self.get_logger().info(f"time_and_topic1_subscriber 노드가 받은 topic1 메시지 : {msg1.data} {self.count5}")
        self.count5 += 1

    def sub_callback4(self, msg):
        self.get_logger().info(f"time_and_topic1_subscriber 노드가 받은 timetopic 메시지 : {msg.stamp} {self.count6}")
        self.count6 += 1
       
def main(args=None):
    rclpy.init(args=args) 
    node = TimeAndTopic1SubscriberNode()
    
    try:
        rclpy.spin(node)  
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

    if __name__ == '__main__':
        main()