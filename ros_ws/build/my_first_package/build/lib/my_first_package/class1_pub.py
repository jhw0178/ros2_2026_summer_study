import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class message1_pub(Node):
    def __init__(self):
        super().__init__("class1_pub") #노드 이름 설정
        # 타이머 등록
        self.create_timer(1, self.timer_callback) #1초마다 timer_callback 호출
        self.pub = self.create_publisher(String, "message", 10)
        self.count = 0

    def timer_callback(self):
        msg = String() #DDS에 보낼 객체 초기화
        msg.data = f"첫번째 프로그램입니다. {self.count}" #data를 입력으로
        self.get_logger().info(msg.data)
        self.pub.publish(msg) #DDS에 msg를 publish
        self.count += 1

def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = message1_pub() #클래스 불러옴

    try:
        rclpy.spin(node) #블럭 (무한루프) 
    except KeyboardInterrupt: #강제 종료 시 오류 뜨지 않도록
        node.get_logger().info("키보드 인터럽트") #강제 종료 시 프린트문 출력보다는 log 형식으로 출력되도록 진행
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()