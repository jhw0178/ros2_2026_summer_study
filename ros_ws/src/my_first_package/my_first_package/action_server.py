import time

import rclpy
from rclpy.node import Node
from user_interface.action import Fibonacci
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle

class ActionServer(Node):
    def __init__(self):
        super().__init__("action_server")
        self.action_server = ActionServer(self, Fibonacci, "fibonacci_server", executecallback=self.executor_callback)

    def executor_callback(self, goal_handle: ServerGoalHandle):
        self.get_logger().info(f"{goal_handle.status}")
        goal: Fibonacci.Goal = goal_handle.request
        step = goal.step
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.temp_seq = [0, 1]
        for i in range(1, step):
            feedback_msg.temp_seq.append(feedback_msg.temp_seq[i] + feedback_msg.temp_seq[i-1])
            goal_handle.publish_feedback(feedback_msg)
        result = Fibonacci.Result()
        return result

def main(args=None):
    rclpy.init(args=args) 
    node = ActionServer() 

    try:
        rclpy.spin(node) 
    except KeyboardInterrupt: 
        node.get_logger().info("키보드 인터럽트") 
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()