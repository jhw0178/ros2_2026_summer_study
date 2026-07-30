# 중복된 코드를 함수화 해서 적용하기 -> object 추가
# srdf 수정해서 custom pose 추가 후 운용 configuration에 문자로 작동하도록
# 벽을 여러 개 추가해서 로봇팔이 벽 사이를 이동하게 작성 -> 360도 주위를 다 활용
# Attached 코드는 하지 않아도 됨 but, 하고 싶으면 해도 됨

import os
import sys
import math

import rclpy
from geometry_msgs.msg import Pose
from moveit.core.kinematic_constraints import construct_joint_constraint
from moveit.core.robot_state import RobotState
from moveit.planning import MoveItPy
from moveit_msgs.msg import CollisionObject, AttachedCollisionObject #AttachedCollisionObject 추가
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive


class MoveItAttached(Node):
    def __init__(self):
        super().__init__("open_manipulator_controller")
        self.moveit = MoveItPy(node_name="open_manipulator_moveit_py")
        self.arm = self.moveit.get_planning_component("arm")
        self.gripper = self.moveit.get_planning_component("gripper")
        self.planning_scene_monitor = self.moveit.get_planning_scene_monitor()
        self.add_table()
        self.add_wall()
        self.object_id = "grasped_box"
         # 물체를 잡을 때 필요함
        self.attach_link = "end_effector_link"
        self.touch_links = ["end_effector_link", "gripper_left_link", "gripper_right_link"] # 충돌 방지 피하려고
        
        self.move_manipulator()

    def move_manipulator(self):
        self.add_pick_object()
        # 초기 자세
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration="init",
            controller_name="arm_controller",
        )
        #gripper open
        self.plan_and_execute(
                    self.moveit,
                    self.gripper,
                    configuration="open",
                    controller_name="gripper_controller",
                )
        # 물체 잡기 직전 자세
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration={
                "joint1": 1.5800002115220035,
                "joint2": -1.3560390164911138,
                "joint3": -1.1382137446113525,
                "joint4": -1.5846021538860742,
            },
            controller_name="arm_controller",
        )
        
        # gripper 닫기
        self.plan_and_execute(
            self.moveit,
            self.gripper,
            configuration="close",
            controller_name="gripper_controller",
        )
        # 물체를 로봇 부착
        self.attach_object()
        # # 물체를 든 상태로 이동1
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration={
                "joint1": -1.0707185899443843,
                "joint2": 0.45405831321394263,
                "joint3": 0.1978835216370407,
                "joint4": -0.8789709914586794,
            },
            controller_name="arm_controller",
        )
        
        # # 물체를 든 상태로 이동2
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration={
                "joint1": -0.5460971604874953,
                "joint2": 0.7869321441851271,
                "joint3": -0.0506213660004331,
                "joint4": -0.7378447589732002,
            },
            controller_name="arm_controller",
        )
        # # 물체를 든 상태로 이동3
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration={
                "joint1": 0.05215534678790501,
                "joint2": 0.37735927381966095,
                "joint3": 0.4141748127289162,
                "joint4": -0.9142525495800489,
            },
            controller_name="arm_controller",
        )
        # # 물체를 든 상태로 이동4
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration={
                "joint1": 0.5875146417599937,
                "joint2": 0.6642136811542758,
                "joint3": 0.1656699250914424,
                "joint4": -0.8068738944280542,
            },
            controller_name="arm_controller",
        )

         
        # 그리퍼 열기
        self.plan_and_execute(
            self.moveit,
            self.gripper,
            configuration="open",
            controller_name="gripper_controller",
        )
        # attached_object 제거
        self.detach_object()
        # world에 box 다시 추가
        self.add_placed_object(0.0, -0.3, 0.065)
        # 초기 위치로 이동
        self.plan_and_execute(
            self.moveit,
            self.arm,
            configuration="init",
            controller_name="arm_controller",
        )
        

    def plan_and_execute(
        self,
        moveit: MoveItPy,
        component,
        configuration: str | dict[str, float],
        controller_name: str,
    ) -> bool:
        """Named state까지 경로를 계획하고 실행한다."""
        component.set_start_state_to_current_state()
        if issubclass(type(configuration), str):
            component.set_goal_state(configuration_name=configuration)
        else:
            robot_model = self.moveit.get_robot_model()
            robot_state = RobotState(robot_model)
            robot_state.joint_positions = configuration
            joint_model_group = robot_model.get_joint_model_group("arm")
            joint_constraint = construct_joint_constraint(
                robot_state=robot_state, joint_model_group=joint_model_group
            )
            component.set_goal_state(motion_plan_constraints=[joint_constraint])

        plan_result = component.plan()

        moveit.execute(
            plan_result.trajectory,
            controllers=[controller_name],
        )
        return True

    def add_table(self):
        collision_object = CollisionObject()
        collision_object.header.frame_id = "world"
        collision_object.id = "table"

        table = SolidPrimitive()
        table.type = SolidPrimitive.BOX
        table.dimensions = [0.8, 0.8, 0.05]  # x, y, z , --m 단위

        table_pose = Pose()
        table_pose.position.x = 0.0
        table_pose.position.y = 0.00
        table_pose.position.z = -0.03

        table_pose.orientation.x = 0.0
        table_pose.orientation.y = 0.0
        table_pose.orientation.z = 0.0
        table_pose.orientation.w = 1.0

        collision_object.primitives.append(table)  # type: ignore
        collision_object.primitive_poses.append(table_pose)  # type: ignore
        collision_object.operation = CollisionObject.ADD

        success = self.planning_scene_monitor.process_collision_object(collision_object)

        if success:
            self.get_logger().info("table을 추가 했습니다")

        with self.planning_scene_monitor.read_only() as scene:
            scene_msg = scene.planning_scene_message

            self.get_logger().info(f"planning frame: {scene.planning_frame}")

            for obj in scene_msg.world.collision_objects:
                self.get_logger().info(
                    f"collision object: id={obj.id}, frame={obj.header.frame_id}"
                )

    def add_wall(self):
        # 테이블 중심 (0.0, 0.0)에 맞춰 벽의 중심도 조정
        center_x = 0.0
        center_y = 0.0

        inner_radius = 0.12    # 중심부 빈 공간 확보 (반경 12cm까지는 벽 없음)
        wall_length = 0.25     # 벽의 길이
        wall_thickness = 0.02
        wall_height = 0.04     # 로봇이 넘나들 수 있는 낮은 높이

        for i in range(6):
            angle = math.radians(i * 60)

            collision_object = CollisionObject()
            collision_object.header.frame_id = "world"
            collision_object.id = f"wall_{i}"

            wall = SolidPrimitive()
            wall.type = SolidPrimitive.BOX
            wall.dimensions = [wall_length, wall_thickness, wall_height]

            pose = Pose()

            # 벽의 중심 좌표: 빈 공간(inner_radius) + 벽 길이의 절반
            offset = inner_radius + (wall_length / 2.0)
            pose.position.x = center_x + offset * math.cos(angle)
            pose.position.y = center_y + offset * math.sin(angle)
            pose.position.z = wall_height / 2.0

            # 벽 회전
            pose.orientation.z = math.sin(angle / 2.0)
            pose.orientation.w = math.cos(angle / 2.0)

            collision_object.primitives.append(wall)
            collision_object.primitive_poses.append(pose)
            collision_object.operation = CollisionObject.ADD

            self.planning_scene_monitor.process_collision_object(collision_object)

        self.get_logger().info("중앙이 빈 피자 조각 모양의 방사형 벽 6개 생성 완료")

    def add_pick_object(self):
        collision_object = CollisionObject()
        collision_object.header.frame_id = "world"
        collision_object.header.stamp = self.get_clock().now().to_msg()
        collision_object.id = self.object_id
        
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.04, 0.04, 0.08]
        
        box_pose = Pose()
        box_pose.position.x = 0.0
        box_pose.position.y = -0.3
        box_pose.position.z = 0.065
        box_pose.orientation.w = 1.0
        
        collision_object.primitives.append(box)                 # type: ignore
        collision_object.primitive_poses.append(box_pose)       # type: ignore
        collision_object.operation = CollisionObject.ADD
        
        success = self.planning_scene_monitor.process_collision_object(collision_object)
        if success:
            self.get_logger().info("world에 box 추가 성공")
        return success
    
    def attach_object(self):
        if not self.remove_world_object(self.object_id):
            return False
        attached_object = AttachedCollisionObject()

        attached_object.link_name = self.attach_link
        attached_object.object.id = self.object_id
        attached_object.object.header.frame_id = self.attach_link
        attached_object.object.header.stamp = self.get_clock().now().to_msg()
        
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.04, 0.04, 0.08]
        
        box_pose = Pose()
        box_pose.position.x = 0.0
        box_pose.position.y = 0.0
        box_pose.position.z = 0.06
        box_pose.orientation.w = 1.0
        
        attached_object.object.primitives.append(box)                 # type: ignore
        attached_object.object.primitive_poses.append(box_pose)       # type: ignore
        attached_object.object.operation = CollisionObject.ADD
        
        attached_object.touch_links = self.touch_links
        
        with self.planning_scene_monitor.read_write() as scene:
            success = scene.process_attached_collision_object(attached_object)
            scene.current_state.update()
            
        if success:
            self.get_logger().info("부착 성공!!")
        return success
    
    def remove_world_object(self, object_id: str):
        remove_object = CollisionObject()
        remove_object.header.frame_id = "world"
        remove_object.header.stamp = self.get_clock().now().to_msg()
        remove_object.id = self.object_id
        remove_object.operation = CollisionObject.REMOVE
        
        success = self.planning_scene_monitor.process_collision_object(remove_object)
        if success:
            self.get_logger().info("world에 box 제거 성공")
        return success
    
    def detach_object(self):
        attached_object = AttachedCollisionObject()

        attached_object.link_name = self.attach_link
        attached_object.object.id = self.object_id
        attached_object.object.header.frame_id = self.attach_link
        attached_object.object.header.stamp = self.get_clock().now().to_msg()
        attached_object.object.operation = CollisionObject.REMOVE
        
        with self.planning_scene_monitor.read_write() as scene:
            success = scene.process_attached_collision_object(attached_object)
            scene.current_state.update()
            
        if success:
            self.get_logger().info("분리 성공!!")
        return success

    def add_placed_object(self, x, y, z):
        collision_object = CollisionObject()
        collision_object.header.frame_id = "world"
        collision_object.header.stamp = self.get_clock().now().to_msg()
        collision_object.id = self.object_id
        
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.04, 0.04, 0.08]
        
        box_pose = Pose()
        box_pose.position.x = x
        box_pose.position.y = y
        box_pose.position.z = z
        box_pose.orientation.w = 1.0

        collision_object.primitives.append(box)                 # type: ignore
        collision_object.primitive_poses.append(box_pose)       # type: ignore
        collision_object.operation = CollisionObject.ADD
        
        success = self.planning_scene_monitor.process_collision_object(collision_object)
        if success:
            self.get_logger().info("world에 내려 놓은 box 추가 성공")
        return success
    
def main() -> None:
    rclpy.init()

    node = MoveItAttached()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.try_shutdown()
        # todo : moveitpy shutdown 작동 되는지 확인하고 수정하기
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)


if __name__ == "__main__":
    main()