cmake_minimum_required(VERSION 3.8)
project(user_interface)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED) #추가한 부분 : 해당 이름의 패키지 찾아보고 없으면 중지
find_package(std_msgs REQUIRED) #Header를 추가하기 위한 패키지 탐색 명령어

#추가할 인터페이스를 작성할 부분
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/UserInt.msg"
  "srv/AddAndOdd.srv"
  "action/Fibonacci.action"
  DEPENDENCIES std_msgs #DEPENDENCIES를 적어주어야 Header를 잘 불러올 수 있음.
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_dependencies(rosidl_default_runtime) # 추가한 부분

ament_package()
