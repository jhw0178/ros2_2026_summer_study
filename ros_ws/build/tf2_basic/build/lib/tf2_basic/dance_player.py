# 로봇팔을 움직여서 춤추는 동작을 구현
# random 함수를 활용하여 춤 구현
# position 관련 정보는 data 파일을 로드해서 구현(txt, yaml, sqlite 등)

import os
import random
import yaml

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.task import Future

from ament_index_python.packages import get_package_share_directory

from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from sensor_msgs.msg import JointState

from control_msgs.action import GripperCommand
from control_msgs.action import GripperCommand_GetResult_Response
from action_msgs.msg import GoalStatus


class DancePlayer(Node):

    def __init__(self):
        super().__init__("dance_player")

        #################################################
        # Publisher
        #################################################

        self.pub = self.create_publisher(
            JointTrajectory,
            "arm_controller/joint_trajectory",
            10
        )

        #################################################
        # Gripper Action
        #################################################

        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            "grippercontroller/gripper_cmd"
        )

        #################################################
        # Joint Subscriber
        #################################################

        self.create_subscription(
            JointState,
            "joint_states",
            self.joint_callback,
            10
        )

        #################################################
        # Current State
        #################################################

        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.current_gripper_position = 0.0

        #################################################
        # Motion Time
        #################################################

        self.duration_sec = 2.0

        #################################################
        # YAML Load
        #################################################

        package_path = get_package_share_directory("tf2_basic")

        yaml_path = os.path.join(
            package_path,
            "data",
            "dance.yaml"
        )

        with open(yaml_path, "r") as file:
            self.motion_data = yaml.safe_load(file)

        self.poses = self.motion_data["poses"]
        self.dances = self.motion_data["dances"]

        #################################################
        # Dance Select
        #################################################

        self.select_new_dance()

        #################################################
        # Timer
        #################################################

        self.timer = self.create_timer(
            3.0,
            self.timer_callback
        )

        self.get_logger().info("Dance Player Started")

    #####################################################
    # Random Dance
    #####################################################

    def select_new_dance(self):

        self.current_dance_name = random.choice(
            list(self.dances.keys())
        )

        self.current_sequence = self.dances[
            self.current_dance_name
        ]

        self.sequence_index = 0

        self.get_logger().info(
            f"Selected Dance : {self.current_dance_name}"
        )

    #####################################################
    # Joint Callback
    #####################################################

    def joint_callback(self, msg: JointState):

        if len(msg.position) >= 4:
            self.current_joint_position = list(
                msg.position[:4]
            )

    #####################################################
    # Timer Callback
    #####################################################

    def timer_callback(self):

        if self.sequence_index >= len(self.current_sequence):

            self.select_new_dance()
            return

        pose_name = self.current_sequence[
            self.sequence_index
        ]

        pose = self.poses[pose_name]

        joint_position = pose["joints"]
        gripper_position = pose["gripper"]

        msg = JointTrajectory()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "dance"

        msg.joint_names = [
            "joint1",
            "joint2",
            "joint3",
            "joint4"
        ]

        point = JointTrajectoryPoint()

        point.positions = joint_position

        sec = int(self.duration_sec)
        nanosec = int(
            (self.duration_sec - sec)
            * 1000000000
        )

        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nanosec

        msg.points.append(point)

        self.pub.publish(msg)

        self.move_gripper(gripper_position)

        self.get_logger().info(
            f"{self.current_dance_name} : {pose_name}"
        )

        self.sequence_index += 1
        
    #####################################################
    # Move Gripper
    #####################################################

    def move_gripper(
        self,
        position: float,
        max_effort: float = 10.0,
        timeout_sec: float = 5.0,
    ):

        if not self.gripper_client.wait_for_server(
            timeout_sec=timeout_sec
        ):
            self.get_logger().error(
                "Cannot find Gripper Action Server."
            )
            return

        goal = GripperCommand.Goal()

        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)

        send_goal_future = self.gripper_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(
            self.goal_callback
        )

    #####################################################
    # Goal Callback
    #####################################################

    def goal_callback(
        self,
        future: Future
    ):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().warn(
                "Gripper Goal Rejected"
            )

            return

        self.get_logger().info(
            "Gripper Goal Accepted"
        )

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            self.get_result_callback
        )

    #####################################################
    # Feedback Callback
    #####################################################

    def feedback_callback(self, msg):

        feedback = msg.feedback

        try:

            self.get_logger().info(
                f"Gripper Position : {feedback.position:.4f}"
            )

        except Exception:

            pass

    #####################################################
    # Result Callback
    #####################################################

    def get_result_callback(
        self,
        future: Future
    ):

        result: GripperCommand_GetResult_Response = future.result()

        if result.status == GoalStatus.STATUS_SUCCEEDED:

            self.get_logger().info(
                "Gripper Motion Success"
            )

        elif result.status == GoalStatus.STATUS_ABORTED:

            self.get_logger().warn(
                "Gripper Motion Aborted"
            )

        elif result.status == GoalStatus.STATUS_CANCELED:

            self.get_logger().warn(
                "Gripper Motion Canceled"
            )

        else:

            self.get_logger().warn(
                f"Unknown Result : {result.status}"
            )


#########################################################
# Main
#########################################################

def main(args=None):

    rclpy.init(args=args)

    node = DancePlayer()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        node.get_logger().info(
            "Keyboard Interrupt"
        )

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()