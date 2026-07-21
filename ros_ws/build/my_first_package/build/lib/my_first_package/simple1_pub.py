import rclpy
from rclpy.node import Node

def timer_callback():
    print("첫번째 프로그램입니다.")

def main():
    rclpy.init(args=None) #rmw 활성화
    node = Node("simple1_pub") #노드 이름 설정

    # 타이머 블럭
    node.create_timer(1, timer_callback) #1초마다 timer_callback 호출

    try:
        rclpy.spin(node) #블럭 (무한루프) 
    except KeyboardInterrupt: #강제 종료 시 오류 뜨지 않도록
        node.get_logger().info("키보드 인터럽트") #강제 종료 시 프린트문 출력보다는 log 형식으로 출력되도록 진행
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()