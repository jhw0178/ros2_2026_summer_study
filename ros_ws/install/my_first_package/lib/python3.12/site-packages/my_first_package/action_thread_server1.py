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

        # Goal 번호를 위한 공유 변수
        self.goal_count = 0

        # goal_count 보호용 Lock
        self.lock = threading.Lock()

        # 동시에 여러 Callback 허용
        self.callback_group = ReentrantCallbackGroup()

        self.action_server = ActionServer(
            self,
            Fibonacci,
            "fibonacci_server",
            execute_callback=self.execute_callback,
            callback_group=self.callback_group,
        )

    def execute_callback(self, goal_handle: ServerGoalHandle):

        # Goal 번호 부여 (공유 변수 보호)
        with self.lock:
            self.goal_count += 1
            goal_number = self.goal_count

        goal = goal_handle.request
        step = goal.step

        self.get_logger().info(
            f"[Goal #{goal_number}] Goal received (step={step})"
        )

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.temp_seq = [0, 1]

        for i in range(1, step):

            next_value = (
                feedback_msg.temp_seq[i]
                + feedback_msg.temp_seq[i - 1]
            )

            feedback_msg.temp_seq.append(next_value)

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f"[Goal #{goal_number}] Feedback : {feedback_msg.temp_seq}"
            )

            # 오래 걸리는 작업을 흉내내기 위한 예제
            time.sleep(1)

        # Goal 성공 처리
        goal_handle.succeed()

        result = Fibonacci.Result()
        result.seq = feedback_msg.temp_seq

        self.get_logger().info(
            f"[Goal #{goal_number}] Result : {result.seq}"
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