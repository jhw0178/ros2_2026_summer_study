import math
from enum import Enum, auto

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState


class MotionState(Enum):
    IDLE = auto()

    LOOK_LEFT = auto()
    LOOK_RIGHT = auto()

    ARM_FORWARD = auto()
    ARM_BACKWARD = auto()

    OPEN_GRIPPER = auto()
    CLOSE_GRIPPER = auto()

    DRIVE = auto()

    DANCE = auto()


class TfMotion(Node):

    def __init__(self):

        super().__init__("tf_motion")

        ####################################################
        # Publisher
        ####################################################

        self.pub = self.create_publisher(
            JointState,
            "/joint_states",
            10,
        )

        ####################################################
        # Timer (10 Hz)
        ####################################################

        self.timer = self.create_timer(
            0.1,
            self.timer_callback,
        )

        ####################################################
        # 현재 Joint 값
        ####################################################

        self.head = 0.0

        self.shoulder = 0.0

        self.elbow = 0.0

        self.left_gripper = 0.0
        self.right_gripper = 0.0

        self.left_front = 0.0
        self.right_front = 0.0

        self.left_back = 0.0
        self.right_back = 0.0

        ####################################################
        # 목표 Joint 값
        ####################################################

        self.target_head = 0.0

        self.target_shoulder = 0.0

        self.target_elbow = 0.0

        self.target_left_gripper = 0.0
        self.target_right_gripper = 0.0

        ####################################################
        # Motion State
        ####################################################

        self.state = MotionState.IDLE

        self.state_time = 0.0

        ####################################################
        # Motion Speed
        ####################################################

        self.head_speed = 0.02

        self.arm_speed = 0.015

        self.gripper_speed = 0.02

        self.wheel_speed = 0.05

        self.get_logger().info("TF Motion Started")
        
    def timer_callback(self):

        ####################################################
        # 현재 상태 시간
        ####################################################

        self.state_time += 0.1

        ####################################################
        # State Machine
        ####################################################

        ####################################################
        # IDLE
        ####################################################

        if self.state == MotionState.IDLE:

            if self.state_time > 2.0:

                self.state = MotionState.LOOK_LEFT
                self.state_time = 0.0

                self.target_head = 0.6

        ####################################################
        # LOOK LEFT
        ####################################################

        elif self.state == MotionState.LOOK_LEFT:

            if abs(self.head - self.target_head) < 0.02:

                if self.state_time > 2.0:

                    self.state = MotionState.LOOK_RIGHT
                    self.state_time = 0.0

                    self.target_head = -0.6

        ####################################################
        # LOOK RIGHT
        ####################################################

        elif self.state == MotionState.LOOK_RIGHT:

            if abs(self.head - self.target_head) < 0.02:

                if self.state_time > 2.0:

                    self.state = MotionState.ARM_FORWARD
                    self.state_time = 0.0

                    self.target_head = 0.0
                    self.target_shoulder = -0.6
                    self.target_elbow = -0.9

        ####################################################
        # ARM FORWARD
        ####################################################

        elif self.state == MotionState.ARM_FORWARD:

            finished = (
                abs(self.shoulder - self.target_shoulder) < 0.02 and
                abs(self.elbow - self.target_elbow) < 0.02
            )

            if finished:

                if self.state_time > 2.0:

                    self.state = MotionState.OPEN_GRIPPER
                    self.state_time = 0.0

                    self.target_left_gripper = 0.4
                    self.target_right_gripper = -0.4

        ####################################################
        # OPEN GRIPPER
        ####################################################

        elif self.state == MotionState.OPEN_GRIPPER:

            finished = (
                abs(self.left_gripper - self.target_left_gripper) < 0.02
            )

            if finished:

                if self.state_time > 2.0:

                    self.state = MotionState.CLOSE_GRIPPER
                    self.state_time = 0.0

                    self.target_left_gripper = 0.0
                    self.target_right_gripper = 0.0

        ####################################################
        # CLOSE GRIPPER
        ####################################################

        elif self.state == MotionState.CLOSE_GRIPPER:

            finished = (
                abs(self.left_gripper - self.target_left_gripper) < 0.02
            )

            if finished:

                if self.state_time > 2.0:

                    self.state = MotionState.ARM_BACKWARD
                    self.state_time = 0.0

                    self.target_shoulder = 0.0
                    self.target_elbow = 0.0

        ####################################################
        # ARM BACKWARD
        ####################################################

        elif self.state == MotionState.ARM_BACKWARD:

            finished = (
                abs(self.shoulder - self.target_shoulder) < 0.02 and
                abs(self.elbow - self.target_elbow) < 0.02
            )

            if finished:

                if self.state_time > 2.0:

                    self.state = MotionState.DRIVE
                    self.state_time = 0.0

        ####################################################
        # DRIVE
        ####################################################

        elif self.state == MotionState.DRIVE:

            self.left_front += self.wheel_speed
            self.right_front += self.wheel_speed
            self.left_back += self.wheel_speed
            self.right_back += self.wheel_speed

            if self.state_time > 6.0:

                self.state = MotionState.DANCE
                self.state_time = 0.0

        ####################################################
        # DANCE
        ####################################################

        elif self.state == MotionState.DANCE:

            self.target_head = 0.5 * math.sin(self.state_time)

            self.target_shoulder = 0.4 * math.sin(self.state_time)

            self.target_elbow = -0.6 + 0.3 * math.cos(self.state_time)

            self.left_front += self.wheel_speed * 0.4
            self.right_front -= self.wheel_speed * 0.4

            self.left_back += self.wheel_speed * 0.4
            self.right_back -= self.wheel_speed * 0.4

            if self.state_time > 8.0:

                self.state = MotionState.IDLE
                self.state_time = 0.0

        ####################################################
        # 목표각도로 천천히 이동
        ####################################################

        self.head = self.move_to_target(
            self.head,
            self.target_head,
            self.head_speed,
        )

        self.shoulder = self.move_to_target(
            self.shoulder,
            self.target_shoulder,
            self.arm_speed,
        )

        self.elbow = self.move_to_target(
            self.elbow,
            self.target_elbow,
            self.arm_speed,
        )

        self.left_gripper = self.move_to_target(
            self.left_gripper,
            self.target_left_gripper,
            self.gripper_speed,
        )

        self.right_gripper = self.move_to_target(
            self.right_gripper,
            self.target_right_gripper,
            self.gripper_speed,
        )

        ####################################################
        # publish
        ####################################################

        self.publish_joint()    
    ####################################################
    # 현재값 -> 목표값으로 조금씩 이동
    ####################################################
    def move_to_target(
        self,
        current,
        target,
        speed,
    ):

        if current < target:

            current += speed

            if current > target:
                current = target

        elif current > target:

            current -= speed

            if current < target:
                current = target

        return current
    
    def publish_joint(self):

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = [
            "head_swivel",
            "shoulder_joint",
            "elbow_joint",
            "left_gripper_joint",
            "right_gripper_joint",
            "left_front_wheel_joint",
            "right_front_wheel_joint",
            "left_back_wheel_joint",
            "right_back_wheel_joint",
        ]

        msg.position = [
            self.head,
            self.shoulder,
            self.elbow,
            self.left_gripper,
            self.right_gripper,
            self.left_front,
            self.right_front,
            self.left_back,
            self.right_back,
        ]

        self.pub.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)  # rmw 활성화
    node = TfMotion()
    try:
        rclpy.spin(node)  # 블럭 (무한 루프)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()        