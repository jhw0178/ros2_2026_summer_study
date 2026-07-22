import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from user_interface.srv import AddAndOdd
import time
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

class ServiceThreadServer(Node):
    def __init__(self):
        super().__init__("service_thread_server")
        self.callback_group = ReentrantCallbackGroup()
        self.service = self.create_service(AddAndOdd, "add_server", self.add_callback, callback_group=self.callback_group)

    def add_callback(self, request: AddAndOdd.Request, response: AddAndOdd.Response):
        response.sum = request.inta + request.intb

        time.sleep(10) # 3초 지연

        if response.sum % 2:
            response.odd = "Two ints sum is odd"
        else:
            response.odd = "Two ints sum is not odd"

        return response

def main(args=None):
    rclpy.init(args=args) 
    node = ServiceThreadServer()

    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        executor.shudown()
        node.destroy_node()

if __name__ == '__main__':
    main()