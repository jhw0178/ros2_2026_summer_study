import time

import rclpy
from rclpy.node import Node
from user_interface.action import Fibonacci
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle

class ActionServerMake(Node):
    def __init__(self):
        super().__init__("action_server")
        self.action_server = ActionServer(self, Fibonacci, "fibonacci_server", execute_callback=self.execute_callback)

    def execute_callback(self, goal_handle: ServerGoalHandle):
        self.get_logger().info(f"{goal_handle.status}")
        goal: Fibonacci.Goal = goal_handle.request
        step = goal.step
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.temp_seq = [0, 1]
        for i in range(1, step):
            feedback_msg.temp_seq.append(feedback_msg.temp_seq[i] + feedback_msg.temp_seq[i-1])
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"{goal_handle.status}")
        self.get_logger().info(f"{goal_handle.status}")
        result = Fibonacci.Result()
        result.seq = feedback_msg.temp_seq
        return result

def main(args=None):
    rclpy.init(args=args) 
    node = ActionServerMake() 

    try:
        rclpy.spin(node) 
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()