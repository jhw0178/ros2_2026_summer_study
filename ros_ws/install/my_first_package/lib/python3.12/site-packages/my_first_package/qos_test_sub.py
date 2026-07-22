import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy

class QosSub(Node):
    def __init__(self):
        super().__init__("qos_test_sub") 
        self.qos_profile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_ALL,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
        )
        self.qos_sub = self.create_subscription(String, "qos_test_topic", self.qos_sub_callback, 10)

        self.count = 0

    def qos_sub_callback(self, msg: String):
        self.get_logger().info(f"수신 메시지: {msg.data} {self.count}")
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = QosSub() 

    try:
        rclpy.spin(node) 
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

    if __name__ == '__main__':
        main()