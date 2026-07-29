import os
import random
import yaml

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.task import Future

from ament_index_python.packages import get_package_share_directory

from sensor_msgs.msg import JointState

from control_msgs.action import (
    FollowJointTrajectory,
    GripperCommand,
    GripperCommand_GetResult_Response,
)

from trajectory_msgs.msg import JointTrajectoryPoint

from action_msgs.msg import GoalStatus


class DancePlayer(Node):

    def __init__(self):

        super().__init__("dance_player")

        #################################################
        # Action Clients
        #################################################

        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/arm_controller/follow_joint_trajectory",
        )

        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            "/gripper_controller/gripper_cmd",
        )

        #################################################
        # Subscriber
        #################################################

        self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_callback,
            10,
        )

        #################################################
        # Current State
        #################################################

        self.current_joint_position = [0.0] * 4
        self.current_gripper_position = 0.0

        #################################################
        # Motion
        #################################################

        self.duration_sec = 2.0

        #################################################
        # Busy Flag
        #################################################

        self.busy = False
        self.pending_actions = set()

        #################################################
        # YAML
        #################################################

        package_path = get_package_share_directory(
            "tf2_basic"
        )

        yaml_path = os.path.join(
            package_path,
            "data",
            "dance.yaml"
        )

        with open(yaml_path, "r") as file:
            motion = yaml.safe_load(file)

        self.poses = motion["poses"]
        self.dances = motion["dances"]

        #################################################
        # Random Dance
        #################################################

        self.select_new_dance()

        #################################################
        # Timer
        #################################################

        self.timer = self.create_timer(
            0.2,
            self.timer_callback,
        )

        self.get_logger().info(
            "Dance Player Started"
        )

    #################################################
    # Random Dance
    #################################################

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

    #################################################
    # Joint Callback
    #################################################

    def joint_callback(self, msg: JointState):

        if len(msg.position) >= 4:
            self.current_joint_position = list(
                msg.position[:4]
            )

    #################################################
    # Timer
    #################################################

    def timer_callback(self):

        if self.busy:
            return

        if self.sequence_index >= len(
            self.current_sequence
        ):
            self.select_new_dance()
            return

        arm_ready = self.arm_client.server_is_ready()
        gripper_ready = self.gripper_client.server_is_ready()

        if not arm_ready or not gripper_ready:
            self.get_logger().warn(
                "Waiting Action Server..."
            )
            return

        pose_name = self.current_sequence[
            self.sequence_index
        ]

        pose = self.poses[pose_name]

        joints = pose["joints"]
        gripper = pose["gripper"]

        self.busy = True
        self.pending_actions = {
            "arm",
            "gripper",
        }

        self.send_arm_goal(joints)
        self.send_gripper_goal(gripper)

        self.get_logger().info(
            f"{self.current_dance_name} : {pose_name}"
        )

        self.sequence_index += 1

    #################################################
    # Arm Goal
    #################################################

    def send_arm_goal(self, positions):

        goal = FollowJointTrajectory.Goal()

        goal.trajectory.header.stamp = (
            self.get_clock().now().to_msg()
        )

        goal.trajectory.joint_names = [
            "joint1",
            "joint2",
            "joint3",
            "joint4",
        ]

        point = JointTrajectoryPoint()

        point.positions = [
            float(v)
            for v in positions
        ]

        point.time_from_start.sec = int(
            self.duration_sec
        )

        point.time_from_start.nanosec = int(
            (
                self.duration_sec
                - int(self.duration_sec)
            )
            * 1000000000
        )

        goal.trajectory.points.append(point)

        future = self.arm_client.send_goal_async(
            goal,
            feedback_callback=self.arm_feedback_callback,
        )

        future.add_done_callback(
            self.arm_goal_callback
        )

    #################################################
    # Gripper Goal
    #################################################

    def send_gripper_goal(
        self,
        position,
        max_effort=10.0,
    ):

        goal = GripperCommand.Goal()

        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)

        future = self.gripper_client.send_goal_async(
            goal,
            feedback_callback=self.gripper_feedback_callback,
        )

        future.add_done_callback(
            self.gripper_goal_callback
        )

    #################################################
    # Arm Goal Callback
    #################################################

    def arm_goal_callback(
        self,
        future: Future,
    ):

        try:

            goal_handle = future.result()

        except Exception as error:

            self.get_logger().error(
                f"Arm Goal Send Failed : {error}"
            )

            self.action_finished("arm")
            return

        if not goal_handle.accepted:

            self.get_logger().error(
                "Arm Goal Rejected"
            )

            self.action_finished("arm")
            return

        self.get_logger().info(
            "Arm Goal Accepted"
        )

        result_future = (
            goal_handle.get_result_async()
        )

        result_future.add_done_callback(
            self.arm_result_callback
        )

    #################################################
    # Gripper Goal Callback
    #################################################

    def gripper_goal_callback(
        self,
        future: Future,
    ):

        try:

            goal_handle = future.result()

        except Exception as error:

            self.get_logger().error(
                f"Gripper Goal Send Failed : {error}"
            )

            self.action_finished("gripper")
            return

        if not goal_handle.accepted:

            self.get_logger().error(
                "Gripper Goal Rejected"
            )

            self.action_finished("gripper")
            return

        self.get_logger().info(
            "Gripper Goal Accepted"
        )

        result_future = (
            goal_handle.get_result_async()
        )

        result_future.add_done_callback(
            self.gripper_result_callback
        )

    #################################################
    # Arm Feedback
    #################################################

    def arm_feedback_callback(
        self,
        feedback_message,
    ):

        feedback = feedback_message.feedback

        self.get_logger().debug(

            "Arm Feedback : "

            f"actual={list(feedback.actual.positions)} "

            f"error={list(feedback.error.positions)}"

        )

    #################################################
    # Gripper Feedback
    #################################################

    def gripper_feedback_callback(
        self,
        feedback_message,
    ):

        feedback = feedback_message.feedback

        self.get_logger().debug(

            f"Gripper Position : "

            f"{feedback.position:.4f}"

        )

    #################################################
    # Arm Result
    #################################################

    def arm_result_callback(
        self,
        future: Future,
    ):

        try:

            wrapped_result = future.result()

        except Exception as error:

            self.get_logger().error(
                f"Arm Result Failed : {error}"
            )

            self.action_finished("arm")
            return

        self.log_action_result(
            "Arm",
            wrapped_result.status,
        )

        if wrapped_result.status != GoalStatus.STATUS_SUCCEEDED:

            self.get_logger().error(

                f"error_code={wrapped_result.result.error_code} "

                f"error_string={wrapped_result.result.error_string}"

            )

        self.action_finished("arm")

    #################################################
    # Gripper Result
    #################################################

    def gripper_result_callback(
        self,
        future: Future,
    ):

        try:

            wrapped_result = future.result()

        except Exception as error:

            self.get_logger().error(
                f"Gripper Result Failed : {error}"
            )

            self.action_finished("gripper")
            return

        self.log_action_result(
            "Gripper",
            wrapped_result.status,
        )

        result: GripperCommand_GetResult_Response = (
            wrapped_result.result
        )

        self.get_logger().info(

            "Gripper Result : "

            f"position={result.position:.4f} "

            f"effort={result.effort:.4f} "

            f"stalled={result.stalled} "

            f"reached_goal={result.reached_goal}"

        )

        self.action_finished("gripper")

    #################################################
    # Result Logger
    #################################################

    def log_action_result(
        self,
        name,
        status,
    ):

        if status == GoalStatus.STATUS_SUCCEEDED:

            self.get_logger().info(
                f"{name} Motion Success"
            )

        elif status == GoalStatus.STATUS_ABORTED:

            self.get_logger().warn(
                f"{name} Motion Aborted"
            )

        elif status == GoalStatus.STATUS_CANCELED:

            self.get_logger().warn(
                f"{name} Motion Canceled"
            )

        else:

            self.get_logger().warn(
                f"{name} Unknown Status : {status}"
            )

    #################################################
    # Motion Finished
    #################################################

    def action_finished(
        self,
        name,
    ):

        self.pending_actions.discard(name)

        if len(self.pending_actions) == 0:

            self.busy = False

            self.get_logger().info(
                "Current Pose Finished"
            )
        
#################################################
# Main
#################################################

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

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":

    main()