import rclpy
from rclpy.node import Node
from std_msgs.msg import Header

class TimePublisherNode(Node):
    def __init__(self):
        super().__init__("time_publisher_node")
        self.timer2 =self.create_timer(1 / 10, self.timer_callback2)
        self.time_publisher = self.create_publisher(Header, "timetopic", 10)

    def timer_callback2(self):
       msg = Header() 
       msg.frame_id = "time test"
       msg.stamp = self.get_clock().now().to_msg() 
       self.time_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TimePublisherNode()

    try:
        rclpy.spin(node) 
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()