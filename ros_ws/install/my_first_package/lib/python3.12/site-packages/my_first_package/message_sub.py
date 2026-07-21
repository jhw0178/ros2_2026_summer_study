import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class message_sub(Node):
    def __init__(self):
        super().__init__("message_sub") #노드 이름 설정
        # subcription 등록
        self.create_subscription(String, "message", self.sub_callback, 10)

        self.count = 0

    def sub_callback(self, msg: String):
        self.get_logger().info(f"수신 메시지: {msg.data} {self.count}")
        self.count += 1

def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = message_sub() #클래스 불러옴

    try:
        rclpy.spin(node) #블럭 (무한루프) 
    except KeyboardInterrupt: #강제 종료 시 오류 뜨지 않도록
        node.get_logger().info("키보드 인터럽트") #강제 종료 시 프린트문 출력보다는 log 형식으로 출력되도록 진행
    finally:
        node.destroy_node()

    if __name__ == '__main__':
        main()