import rclpy
from rclpy.node import Node

class message_pub(Node):
    def __init__(self):
        super().__init__("class_pub") #노드 이름 설정
    # 타이머 블럭
        self.create_timer(1, self.timer_callback) #1초마다 timer_callback 호출
        self.count = 0

    def timer_callback(self):
       self.get_logger().info(f"첫번째 프로그램입니다. {self.count}")
       self.count += 1

def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = message_pub() #클래스 불러옴

    try:
        rclpy.spin(node) #블럭 (무한루프) 
    except KeyboardInterrupt: #강제 종료 시 오류 뜨지 않도록
        node.get_logger().info("키보드 인터럽트") #강제 종료 시 프린트문 출력보다는 log 형식으로 출력되도록 진행
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()