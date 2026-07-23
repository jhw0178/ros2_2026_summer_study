import threading
import time

import rclpy
from rclpy.node import Node

from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle

from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from user_interface.action import Fibonacci


class ActionThreadServer(Node):

    def __init__(self):
        super().__init__("action_thread_server")

        # 공유 데이터 보호용
        self.lock = threading.Lock()

        # 여러 callback을 동시에 실행할 수 있도록 허용
        self.callback_group = ReentrantCallbackGroup()

        self.action_server = ActionServer(
            self,
            Fibonacci,
            "fibonacci_server",
            execute_callback=self.execute_callback,
            callback_group=self.callback_group,
        )

    def execute_callback(self, goal_handle: ServerGoalHandle):

        self.get_logger().info(
            f"Goal received : step={goal_handle.request.step}"
        )

        goal = goal_handle.request
        step = goal.step

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.temp_seq = [0, 1]

        for i in range(1, step):

            # 실제 공유 자원이 있다면 여기처럼 보호
            with self.lock:
                next_value = (
                    feedback_msg.temp_seq[i]
                    + feedback_msg.temp_seq[i - 1]
                )
                feedback_msg.temp_seq.append(next_value)

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f"Feedback : {feedback_msg.temp_seq}"
            )

            time.sleep(1)

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.seq = feedback_msg.temp_seq

        self.get_logger().info(
            f"Result : {result.seq}"
        )

        return result


def main(args=None):

    rclpy.init(args=args)

    node = ActionThreadServer()

    executor = MultiThreadedExecutor(num_threads=4)

    executor.add_node(node)

    try:
        executor.spin()

    except KeyboardInterrupt:
        node.get_logger().info("Keyboard Interrupt")

    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()