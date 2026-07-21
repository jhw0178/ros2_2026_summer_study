# ros2_2026_summer_study
2026 하계 ROS2 교육

---
## 7월20일(월) - 1일차

### 1. 환경 구성
##### 1-1. wsl 설치 (Linux Ubuntu 24.04)
    $wsl --install -d Ubuntu-24.04
    
##### 1-2. github ID 생성 후 repository 생성

##### 1-3. github 주소 접속
    $git clone "github 주소"

##### 1-4. VScode 설치 후 remote wsl로 접속
    Remote Explorer을 통해 접속

##### 1-5. github 계정 연동

##### #내용 업데이트 방법
    수정할 내용 작성 후commit -> Commit&Sync로 저장
### 2. ros2 jazzy 설치
#### https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

##### 2-1. basrc 설정
    -> source /opt/ros/jazzy/setup.bash

##### 2-2. xeyes 설치 => turtlesim GUI 띄우기 위해
    설치 : sudo apt install x11-apps
    실행 : xeyes

### 3. turtlesim 노드 실행
#### $ros2 run turtlesim turtlesim_node
##### 3-1. turtle_node 실행
    $ros2 run turtlesim turtlesim_node

##### 3-2. 새로운 이름의 turtle 생성
    $ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle

##### 3-3. 노드 리스트 확인
    $ros2 node list

##### 3-4. 노드 정보 확인
    $ros2 node info "해당 노드 이름"

### 4. turtle_teleop_key 노드 실행
#### $ros2 run turtlesim turtle_teleop_key
##### 4-1. 조작
    방향키 혹은 G,B,V,C,D,E,R,T로 조작

##### 4-2. 방향 확인
    $ros2 topic echo /turtle1/cmd_vel
    거북이 기준으로 바라보는 쪽이 linear x축의 +, 반시계 방향이 angular z축의 +

### 5. Topic(토픽) 발행
#### $ros2 topic pub "발행 횟수" "대상 토픽" "인터페이스 종류" "원하는 입력"
##### 5-1. 토픽 목록 확인
    $ros2 topic list

##### 5-2. 원하는 토픽의 인터페이스 확인
    $ros2 topic list "대상 토픽"

##### 5-3. 인터페이스 형태 확인
    $ros2 inferface show "인터페이스 종류"
    
##### 5-4. 일정 간격 회전 토픽 발행
    $ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"

##### #RQT_GRAPH
    $rqt_graph
    실행 중인 노드와 메시지의 관계를 파악하는 데 용이

##### 5-5. rqt로 topic 발행
    rqt 실행 후 plugins의 topics -> message publisher를 통해 원하는 토픽 발행 가능

### 6. Service(서비스) 발행
#### $ros2 service call "대상 서비스" "인터페이스 종류" "원하는 입력"
##### 6-1. 서비스 목록 확인
    $ros2 service list

##### 6-2. clear 서비스 발행
    $ros2 service call /clear std_srvs/srv/Empty {}

##### 6-3. spawn 서비스 발행
    $ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'my_turtle'}"

##### 6-4. rqt로 서비스 발행
    rqt를 실행하고 plugins의 services -> service caller를 실행하면 service call 가능

### 7. Action(액션) 발행
#### $ros2 action send_goal "대상 액션" "인터페이스 종류" "원하는 입력"
##### 7-1. 액션 목록 확인
    $ros2 action list

##### 7-2. 액션 발행
    $ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}"
    : 3시 방향을 바라보는 turtle1이 반시계 방향으로 90도 회전하여 12시 방향을 바라 봄

    #rqt
    action은 rqt로 발행할 수 없음
    
### 8. Param(파라미터) 설정
#### $ros2 param list
#### : 파라미터 리스트를 확인

##### 8-1. background 색상 확인
    $ros2 param get /turtlesim background_r #r(빨강) 색상 정도 파악
    $ros2 param get /turtlesim background_g #g(초록) 색상 정도 파악
    $ros2 param get /turtlesim background_b #b(파랑) 색상 정도 파악
    : 기본 색상인 파란 바탕화면

##### 8-2. background 색상 설정
    $ros2 param set /turtlesim background_r "150"
    $ros2 param set /turtlesim background_g "255"
    $ros2 param set /turtlesim background_b "33"
    : 형광 연두색을 가진 배경으로 바뀜

##### 8-3. param 변경 값 저장
    $ros2 param dump /turtlesim > "원하는 파일 이름.yaml" => $ros2 param dump /turtlesim > turtlesim.yaml

##### 8-4. param 변경한 노드 불러오기
    $ros2 run turtlesim turtlesim_node --ros-args --param-file ~/turtlesim.yaml(저장위치)

## 7월21일(화) - 2일차

### 1. ROS2 특징
#### ROS2의 기본적인 특징
##### 1-1. ROS2 Common Packages
##### ROS2에서 흔히 사용되는 패키지들
    Buildsystem : ament_cmake, ament_index_cpp, ament_lint, ament_package, ros_enviroment
    RMW : rmw, rmw_implementation, rmw_vendor, rosidl_typesupport_vendor, Micro-XRCE-DDS
    RCL : rcl, 
##### 1-2. DDS (Data Distribution Service)
##### OMG(Object Management Group)에서 표준화한 실시간 Pub-Sub(Publisher-Subscriber) 방식 통신 미들웨어
    통신 프로토콜 : RTPS(Real Time Publish Subscribe)
    - UDP 기반이지만, QoS 설정을 통해 UDP/TCP의 기능을 선택적으로 사용 가능
    - UDP는 N:1 통신 가능, TCP는 1:1 통신
##### 1-3. Real-time control & deterministic execution & real-time communication
    real-time으로 Executor의 loop를 interrupt 발생 전까지 무한 반복시킴

### 2. ROS2 프로그래밍 언어 RCL
#### 사용자를 위한 ROS2 Code APIs로 다양한 언어 호환성을 갖음
##### 2-1. 노드 Node
##### 최소 단위의 실행 가능한 프로세스
    - ROS에서는 최소한의 실행단위로 프로그램을 나누어 작업함
    - 각 노드는 메시지 통신으로 데이터를 주고 받음
##### 2-2. 토픽 Topic
##### 비동기식 단방향 메시지 송수신 방식
    - Publisher와 Subscriber 간의 통신
    - 1:N, N:1, N:N 통신 가능
##### 2-3. 서비스 Service
##### 동기식 양방향 메시지 송수신 방식
    - Service Server와 Service Client 간의 통신
    - Request와 Response로 구분됨
##### 2-4. 액션 Action
##### 비동기식, 동기식 양방향 메시지 송수신 방식
    - Action Server와 Action Client 간의 통신
    - Goal과 Result로 구분되며 중간에 FeedBack이 제공되는 형태

### 3. 패키지와 노드
#### 노드와 메시지를 정의하는 시스템
##### 3-1. 패키지와 파일 시스템
    비슷한 기능들을 묶어 시스템을 제공하도록 함
##### 3-2. 패키지 생성
##### $ros2 pkg create --build-type "빌드 타입" "패키지 이름"
    $ros2 pkg create --build-type ament_python my_first_package
##### 3-3. colcon build
##### $colcon build
    - 작성한 내용으로 패키지를 빌드하는 명령어
    - 항상 워크스페이스에 이동하여 빌드해야 함
##### 3-4. packag.xml 파일 설정
    패키지에 대한 간단한 기본 설정을 작성
##### 3-5. setup.py 파일 설정
    패키지에 작성된 노드를 추가하는 파일 -> entry_points에 추가하면 됨
##### 3-6. bashrc 설정
    - export _colcon_cd_root=~/ros_ws : colcon_cd 명령어의 기준 디렉토리를 ~/ros_ws로 설정
    - alias cbp='colcon build --symlink-install --packages-select' : 특정 패키지만 빌드하는 명령어 설정
    - alias cb='colcon build ~/ros2_2026_summer_study/ros_ws : 해당 경로를 colcon build 하도록 명령어 설정
##### 3-7. simple_pu.py 노드 생성
##### 간단한 문장을 출력하는 노드 생성
    def main():
        print("This is my first Node")
    if __name__ == '__main__':
        main()
    
##### 3-8. setup.py에 추가
##### entry_points에 추가
     "simple_pub = my_first_package.simple_pub:main"
##### 3-9. bashrc에 source 설정
##### 매번 source 설정을 하기 번거로우니 bashrc에 추가함
    source ~/ros2_2026_summer_study/ros_ws/install/local_setup.bash : 해당 패키지 경로의 install 폴더 안에 있는 local_setup.bash를 source 하면 됨
##### 3-10. 수정한 내용을 Colcon Build
##### 해당 워크스페이스에 이동한 후 Colcon Build를 진행
    $cd ~/ros2_2026_summer_study/ros_ws
    $colcon build 혹은 $cb (alias 설정)
##### 3-11. simple_pub 노드 실행
##### $ros2 run "생성한 패키지 이름" "생성한 노드 이름"
    $ros2 run my_first_package simple_pub
