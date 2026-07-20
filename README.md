# ros2_2026_summer_study
2026 하계 ROS2 교육

---
### 7월20일(월)

#### 1. 환경 구성
    1-1. wsl 설치 (Ubuntu 24.04)
    $wsl --install -d Ubuntu-24.04
    
    1-2. github ID 생성 후 repository 생성

    1-3. github 주소 접속
    $git clone "github 주소"

    1-4. VScode 설치 후 remote wsl로 접속
    Remote Explorer을 통해 접속

    1-5. github 계정 연동

    #내용 업데이트 방법
    수정할 내용 작성 후commit -> Commit&Sync로 저장
#### 2. ros2 jazzy 설치
##### https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

    2-1. basrc 설정
    -> source /opt/ros/jazzy/setup.bash

    2-2. xeyes 설치 => turtlesim GUI 띄우기 위해
    설치 : sudo apt install x11-apps
    실행 : xeyes

#### 3. turtlesim 노드 실행
##### $ros2 run turtlesim turtlesim_node
    3-1. turtle_node 실행
    $ros2 run turtlesim turtlesim_node

    3-2. 새로운 이름의 turtle 생성
    $ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle

    3-3. 노드 리스트 확인
    $ros2 node list

    3-4. 노드 정보 확인
    $ros2 node info "해당 노드 이름"

#### 4. turtle_teleop_key 노드 실행
##### $ros2 run turtlesim turtle_teleop_key
    4-1. 조작
    방향키 혹은 G,B,V,C,D,E,R,T로 조작

    4-2. 방향 확인
    $ros2 topic echo /turtle1/cmd_vel
    거북이 기준으로 바라보는 쪽이 linear x축의 +, 반시계 방향이 angular z축의 +

#### 5. Topic(토픽) 발행
##### $ros2 topic pub "발행 횟수" "대상 토픽" "인터페이스 종류" "원하는 입력"
    5-1. 토픽 목록 확인
    $ros2 topic list

    5-2. 원하는 토픽의 인터페이스 확인
    $ros2 topic list "대상 토픽"

    5-3. 인터페이스 형태 확인
    $ros2 inferface show "인터페이스 종류"
    
    5-4. 일정 간격 회전 토픽 발행
    $ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"

    #RQT_GRAPH
    $rqt_graph
    실행 중인 노드와 메시지의 관계를 파악하는 데 용이

    5-5. rqt로 topic 발행
    rqt 실행 후 plugins의 topics -> message publisher를 통해 원하는 토픽 발행 가능

#### 6. Service(서비스) 발행
##### $ros2 service call "대상 서비스" "인터페이스 종류" "원하는 입력"
    6-1. 서비스 목록 확인
    $ros2 service list

    6-2. clear 서비스 발행
    $ros2 service call /clear std_srvs/srv/Empty {}

    6-3. spawn 서비스 발행
    $ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'my_turtle'}"

    6-4. rqt로 서비스 발행
    rqt를 실행하고 plugins의 services -> service caller를 실행하면 service call 가능

#### 7. Action(액션) 발행
##### $ros2 action send_goal "대상 액션" "인터페이스 종류" "원하는 입력"
    7-1. 액션 목록 확인
    $ros2 action list

    7-2. 액션 발행
    $ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}"
    : 3시 방향을 바라보는 turtle1이 반시계 방향으로 90도 회전하여 12시 방향을 바라 봄

    #rqt
    action은 rqt로 발행할 수 없음
    

