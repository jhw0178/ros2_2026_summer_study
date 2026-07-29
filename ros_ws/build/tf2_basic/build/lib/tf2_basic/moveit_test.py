"""MoveItPy로 OpenManipulator-X의 arm과 gripper를 제어한다."""

import time

import rclpy
from moveit.planning import MoveItPy


def plan_and_execute(
    moveit: MoveItPy,
    component,
    configuration_name: str,
    controller_name: str,
) -> bool:
    """Named state까지 경로를 계획하고 실행한다."""
    component.set_start_state_to_current_state()
    # 수정: goal_name 문자열이 아니라 전달받은 configuration_name을 사용해야 함
    component.set_goal_state(configuration_name=configuration_name)

    plan_result = component.plan()

    if not plan_result:
        print(f"경로 계획 실패: {configuration_name}")
        return False

    # 컨트롤러 이름이 리스트 형태여야 함
    moveit.execute(
        plan_result.trajectory,
        controllers=[controller_name],
    )

    return True


def main() -> None:
    rclpy.init()
    moveit = MoveItPy(node_name="open_manipulator_moveit_py")
    arm = moveit.get_planning_component("arm")
    gripper = moveit.get_planning_component("gripper")
    
    # 수정: "goal_name"이라는 문자열이 아닌 변수 goal_name을 전달해야 함
    for goal_name in ("home", "init", "home", "init"):    
        plan_and_execute(
            moveit,
            arm,
            configuration_name=goal_name, # 따옴표 제거
            controller_name="arm_controller",
        )
        time.sleep(0.5)
    
    for goal_name in ("open", "close", "open", "close"):
        plan_and_execute(
            moveit,
            gripper,
            configuration_name=goal_name, # 변수 전달
            controller_name="gripper_controller",
        )
        time.sleep(0.7)

    print("실습 완료")
    
    # 노드 종료 절차
    rclpy.shutdown()


if __name__ == "__main__":
    main()