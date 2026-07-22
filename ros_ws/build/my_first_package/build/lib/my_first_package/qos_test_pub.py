import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy
from std_msgs.msg import String

# from rclpy.qos import qos_profile_default #default_pub을 생성하기 위한 library

class QosPub(Node):
    def __init__(self):
        super().__init__("qos_test_pub") 
        self.create_timer(1, self.timer_callback) 
        
        self.qos_profile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_ALL,  
            reliability=QoSReliabilityPolicy.RELIABLE, 
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
        )
        self.qos_pub = self.create_publisher(String, "qos_test_topic", self.qos_profile)
        self.count = 0

        # self.default_pub = self.create_publisher(String, "qos_test_topic_default", qos_profile_default) #default library를 사용한 publisher 생성
    
    def timer_callback(self):
        msg = String() 
        msg.data = f"첫번째 프로그램입니다. {self.count}" 
        self.get_logger().info(msg.data)
        self.qos_pub.publish(msg) 
        self.count += 1

def main(args=None):
    rclpy.init(args=args) 
    node = QosPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()