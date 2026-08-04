import cv2
import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import (
    FollowJointTrajectory,
    FollowJointTrajectory_GetResult_Response,
    GripperCommand,
    GripperCommand_GetResult_Response,
)
from cv_bridge import CvBridge
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
from sensor_msgs.msg import Image, JointState
from trajectory_msgs.msg import JointTrajectoryPoint


class Manipulator_pub(Node):
    def __init__(self):
        self.last_joint = [0.0, 0.0, 0.0, 0.0]
        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.image_width = 640
        self.image_height = 480
        self.ball_area = 0
        self.log_count = 0
        
        super().__init__("manipulator_pub")  # 노드 이름
        self.joint_client = ActionClient(
            self, FollowJointTrajectory, "/arm_controller/follow_joint_trajectory"
        )
        self.gripper_client = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.joint_state_subscription = self.create_subscription(
            JointState, "joint_states", self.joint_callback, 10
        )
        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.current_gripper_position = 0.0
        self.joint_state_received = False
        self.count = True
        self.duration_sec = 1
        self.brige = CvBridge()
        self.create_subscription(Image, "/gripper_camera/image_raw", self.image_callback, 10)

    def image_callback(self, msg: Image):
        img_sub = self.brige.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        hsv = cv2.cvtColor(img_sub, cv2.COLOR_BGR2HSV)
        lower = np.array([0,40,40], dtype=np.uint8)
        upper = np.array([10,255,255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            contour=max(contours, key=cv2.contourArea)
            area=cv2.contourArea(contour)
            if area > 20:
                x,y,w,h=cv2.boundingRect(contour)
                center_x=x+w//2
                center_y=y+h//2
                self.ball_area=area
                self.get_logger().info(f"ball x:{center_x} y:{center_y} area:{area}")
                distance=self.calc_distance(area)
                self.log_count += 1
                if self.log_count % 10 == 0:
                    self.get_logger().info(f"ball area={area:.1f}, distance={distance:.3f} m")

                self.control_arm(center_x, center_y)

                cv2.rectangle(img_sub, (x,y), (x+w,y+h), (0,255,0), 2)

        cv2.imshow("camera", img_sub)
        cv2.imshow("mask", mask)
        cv2.waitKey(1)
        # x 좌표를 기반으로 해서 좌우로 움직이기 joint 1
        # y 좌표를 기반으로 해서 위아래로 움직이기 joint2~4
        # joint_state subscription -> point 변화.
        # 공의 거리를 추측 area 기반으로 공의 거리를 로깅을 찍으세요.
        # self.move_gripper(-0.01) 안움직여도 됨
        # self.move_joint(point)

    # 거리 계산 함수
    def calc_distance(self, area):
        if area <= 0:
            return 0.0
        # camera intrinsic
        fx = 554.254646
        # 실제 공 지름(m)
        real_ball_diameter = 0.04
        # contour area -> pixel diameter
        pixel_diameter = 2 * np.sqrt(area / np.pi)
        if pixel_diameter <= 0:
            return 0.0
        # Z = fx * real_size / pixel_size
        distance = (fx * real_ball_diameter / pixel_diameter)
        return distance

    def joint_callback(self, msg: JointState):
        joint_map = dict(zip(msg.name, msg.position))
        self.current_joint_position = [joint_map["joint1"], joint_map["joint2"], joint_map["joint3"], joint_map["joint4"]]
        
    # joint 움직이는 함수
    def control_arm( self, x, y):
        center_x=320
        center_y=240

        error_x=x-center_x
        error_y=y-center_y

        joint1 = self.current_joint_position[0]
        joint2 = self.current_joint_position[1]
        joint3 = self.current_joint_position[2]
        joint4 = self.current_joint_position[3]

        # 좌우
        if abs(error_x)>20:
            joint1 += error_x * 0.001
        # 상하
        if abs(error_y)>20:
            joint2 += -error_y * 0.001
            joint3 += -error_y * 0.001
            joint4 += -error_y * 0.001
        point=JointTrajectoryPoint()
        point.positions=[joint1, joint2, joint3, joint4]
        point.time_from_start.sec = 1
        point.time_from_start.nanosec = 0
        self.move_joint(point)
        self.last_joint=[ joint1, joint2, joint3, joint4]

    def move_gripper(self, position: float, max_effort=10.0, timeout_sec=5.0):
        if not self.gripper_client.wait_for_server(timeout_sec=timeout_sec):
            self.get_logger().info("gripper_controller Action 서버를 찾지 못햇습니다.")
        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)
        send_goal_future = self.gripper_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_callback)

    def goal_callback(self, future: Future):
        self.goal_handle = future.result()  # type: ignore
        self.get_result_future = self.goal_handle.get_result_async()  # type: ignore
        self.get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(
        self,
        msg: GripperCommand.Impl.FeedbackMessage,
    ):
        feedback: GripperCommand.Feedback = msg.feedback
        self.get_logger().info(f"{feedback.position}")

    def get_result_callback(self, future: Future):
        result: GripperCommand_GetResult_Response = (
            future.result()  # type: ignore
        )
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"succeeded result: {result.result.position}")
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("aborted!!")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("canceled!!")

    def move_joint(self, point: JointTrajectoryPoint):
        if not self.joint_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("joint_controller Action 서버를 찾지 못햇습니다.")
        goal = FollowJointTrajectory.Goal()
        # todo :
        goal.trajectory.header.stamp = self.get_clock().now().to_msg()
        goal.trajectory.header.frame_id = "move_manipulator"
        goal.trajectory.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        goal.trajectory.points.append(point)  # type: ignore

        send_goal_future = self.joint_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_joint_callback)

    def goal_joint_callback(self, future: Future):
        self.goal_handle = future.result()  # type: ignore
        self.get_result_future = self.goal_handle.get_result_async()  # type: ignore
        self.get_result_future.add_done_callback(self.get_joint_result_callback)

    def feedback_joint_callback(
        self,
        msg: FollowJointTrajectory.Impl.FeedbackMessage,
    ):
        feedback: FollowJointTrajectory.Feedback = msg.feedback
        self.get_logger().info(f"{feedback.actual.positions}")

    def get_joint_result_callback(self, future: Future):
        result: FollowJointTrajectory_GetResult_Response = (
            future.result()  # type: ignore
        )
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"succeeded result: {result.result.error_string}")
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("aborted!!")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("canceled!!")


def main(args=None):
    rclpy.init(args=args)  # rmw 활성화
    node = Manipulator_pub()
    try:
        rclpy.spin(node)  # 블럭 (무한 루프)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()