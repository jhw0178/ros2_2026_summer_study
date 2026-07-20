# ros2_2026_summer_study
2026 하계 ROS2 교육

---
#7월20일(월)

1. 환경 구성
    1-1) wsl 설치 (Ubuntu 24.04)
    $wsl --install -d Ubuntu-24.04
    
    1-2) github ID 생성 후 repository 생성
    1-3) wsl (Ubuntu) 터미널에서 git clone "github주소"
    1-4) VScode 설치 후 remote wsl로 접속
    1-5) github 계정 연동
    1-6) 내용 업데이트 방법
    commit -> Commit&Sync로 저장

2. ros2 jazzy 설치 
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

    2-1) basrc 설정
    -> source /opt/ros/jazzy/setup.bash

    2-2) xeyes 설치 => turtlesim GUI 띄우기 위해
    설치 : sudo apt install x11-apps
    실행 : xeyes

3. turtlesim 노드 실행
$ros2 run turtlesim turtlesim_node

    3-1) 새로운 이름의 turtle 생성
    $ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle

    3-2) 노드 리스트 확인
    $ros2 node list

    3-3) 노드 정보 확인
    $ros2 node info "해당 노드 이름"

4. turtle_teleop_key 노드 실행
$ros2 run turtlesim turtle_teleop_key