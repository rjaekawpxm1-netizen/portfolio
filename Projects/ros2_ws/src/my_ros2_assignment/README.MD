Doosan E0509 Robot GUI Controller 프로젝트
본 프로젝트는 ROS2 Humble 환경에서 두산 로봇(E0509)의 상태를 실시간으로 모니터링하고, 사용자 입력에 따라 로봇을 제어할 수 있는 PyQt5 기반의 GUI 인터페이스입니다.

1. 프로젝트 개요 및 작동 로직
통신 아키텍처: ROS2의 Topic 구독(Subscription)과 Service 호출(Client) 방식을 혼합하여 설계하였습니다.

상태 모니터링: /joint_states 토픽을 실시간으로 구독하여 로봇의 6개 축 관절 각도를 GUI에 즉각 반영합니다.

로봇 제어 로직: 사용자가 입력한 (x, y, z) 좌표와 속도/가속도 데이터를 dsr_msgs2/srv/MoveLine 서비스 요청에 담아 로봇 컨트롤러에 전송합니다.

멀티스레딩 구현: QThread를 활용하여 로봇이 이동 명령을 수행하는 동안에도 GUI 창이 멈추지(Freezing) 않고 실시간 로그와 각도 데이터를 계속 업데이트하도록 구현하였습니다.

2. GUI 구성 설명
목표 좌표 입력: 로봇이 이동할 목표 지점의 x, y, z 좌표를 입력하는 에디트 박스입니다.

이동 옵션: 최대 속도와 가속도를 설정할 수 있으며, 체크박스를 통해 절대좌표(Absolute) 또는 상대좌표(Relative) 기준 이동을 선택할 수 있습니다.

현재 상태 표시: 현재 로봇의 6개 관절 각도(Joint Angles)를 실시간 리스트 형식으로 보여줍니다.

실시간 로그: 명령 전송 상태, 서비스 연결 오류, 사용자 입력 에러 등을 텍스트 박스에 출력하여 사용자에게 피드백을 제공합니다.

3. 실행 방법 (터미널 3개 사용)
모든 터미널은 워크스페이스 설정이 완료된 상태여야 합니다 (source ~/ros2_ws/install/setup.bash).

Step 1. 로봇 가상 컨트롤러 및 RViz 실행 (서버)

ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py model:=e0509 mode:=virtual

Step 2. GUI 제어 노드 실행 (리모컨)

ros2 run my_ros2_assignment my_node

Step 3. Joint State Publisher GUI 실행 (테스트용 조절기)

ros2 run joint_state_publisher_gui joint_state_publisher_gui