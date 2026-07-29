import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import GripperCommand
from sensor_msgs.msg import JointState

class MoveManipulator(Node):
    def __init__(self):
        super().__init__("manipulator_move")
        self.create_timer(3.0, self.timer_callback)
        self.pub = self.create_publisher(JointTrajectory, "arm_controller/joint_trajectory", 10)
        self.gripper_client = ActionClient(self, GripperCommand, "grippercontroller/gripper_cmd")
        self.joint_state_subscription = self.create_subscription(JointState, "joint_states", self.joint_callback, 10)
        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.current_gripper_position = 0.0
        self.joint_state_received = False
        self.count = True
        self.duration_sec = 0.5
        
    def timer_callback(self):
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "move_manipulator"
        msg.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        point = JointTrajectoryPoint()
        if self.count == True:
            point.positions = [0.8888888, -0.5858585, -0.26767676, -0.6343434]
            self.count = False
        else:
            point.positions = [0.46767676, 0.4191919, -0.32222222, 0.3333333]
            self.count = True
        seconds = int(self.duration_sec)
        nanoseconds = int((self.duration_sec - seconds) * 1_000_000_000)
        
        point.time_from_start.sec = seconds
        point.time_from_start.nanosec = nanoseconds
        
        msg.points.append(point) # type: ignore
        self.pub.publish(msg)
        
    def joint_callback(self, msg: JointState):
        self.current_joint_position = msg.position
        
def main(args=None):
    rclpy.init(args=args) 
    node = MoveManipulator()
    try:
        rclpy.spin(node)  
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()