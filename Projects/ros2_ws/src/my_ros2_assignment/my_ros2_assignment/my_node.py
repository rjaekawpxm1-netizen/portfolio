import sys
import rclpy
from rclpy.node import Node
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from sensor_msgs.msg import JointState
from dsr_msgs2.srv import MoveLine

# 1. 로봇 제어 전용 스레드 
class RobotWorker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, node):
        super().__init__()
        self.node = node
        # 두산 로봇 직선 이동 서비스 클라이언트 생성
        self.client = self.node.create_client(MoveLine, '/dsr01/move/movel')

    def move_robot(self, x, y, z, speed, accel, is_abs):
        if not self.client.wait_for_service(timeout_sec=1.0):
            self.log_signal.emit("오류: 로봇 서비스를 찾을 수 없습니다. (dsr_bringup 실행 확인)")
            return

        req = MoveLine.Request()
        # 목표 좌표 설정 (x, y, z, r1, r2, r3)
        req.pos = [float(x), float(y), float(z), 0.0, 0.0, 0.0]
        req.vel = float(speed)
        req.acc = float(accel)
        req.mode = 0 if is_abs else 1  # 0: 절대좌표, 1: 상대좌표
        req.time = 0.0
        req.radius = 0.0
        req.blend_type = 0
        req.sync_type = 0

        self.log_signal.emit(f"명령 전송: {x}, {y}, {z} (속도: {speed})")
        self.client.call_async(req)

# 2. 메인 GUI 클래스 (PyQt5)
class MyRobotGui(QWidget):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.worker = RobotWorker(node)
        self.worker.log_signal.connect(self.update_log)
        
        # 조인트 상태 구독
        self.subscription = self.node.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10)
        self.current_joints = [0.0] * 6
        
        self.initUI()
        
        # GUI 갱신을 위한 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.spin_node)
        self.timer.start(100)

    def initUI(self):
        layout = QVBoxLayout()

        # --- 제어 부분 ---
        self.abs_rel_box = QCheckBox("절대좌표 기준 사용 (체크 해제 시 상대좌표)", self)
        layout.addWidget(self.abs_rel_box)

        self.coord_input = QLineEdit(self)
        self.coord_input.setPlaceholderText("목표 좌표 입력 (예: 400, 0, 500)")
        layout.addWidget(self.coord_input)

        self.speed_input = QLineEdit(self)
        self.speed_input.setPlaceholderText("최대 속도 (예: 100)")
        self.speed_input.setText("100")
        layout.addWidget(self.speed_input)

        self.accel_input = QLineEdit(self)
        self.accel_input.setPlaceholderText("최대 가속도 (예: 100)")
        self.accel_input.setText("100")
        layout.addWidget(self.accel_input)

        self.btn_run = QPushButton("로봇 이동 실행", self)
        self.btn_run.clicked.connect(self.on_click_run)
        layout.addWidget(self.btn_run)

        # --- 상태 확인 부분 ---
        self.angle_label = QLabel("현재 Joint 각도: [0, 0, 0, 0, 0, 0]", self)
        layout.addWidget(self.angle_label)

        self.log_view = QTextEdit(self)
        self.log_view.setReadOnly(True)
        layout.addWidget(QLabel("실시간 로그"))
        layout.addWidget(self.log_view)

        self.setLayout(layout)
        self.setWindowTitle('Doosan E0509 Controller - Final')
        self.resize(400, 500)
        self.show()

    def joint_callback(self, msg):
        self.current_joints = msg.position

    def on_click_run(self):
        try:
            coords = self.coord_input.text().split(',')
            x, y, z = coords[0].strip(), coords[1].strip(), coords[2].strip()
            speed = self.speed_input.text().strip()
            accel = self.accel_input.text().strip()
            is_abs = self.abs_rel_box.isChecked()
            
            self.worker.move_robot(x, y, z, speed, accel, is_abs)
        except Exception as e:
            self.update_log("입력 에러: 좌표를 'x, y, z' 형식으로 입력하세요.")

    def update_log(self, message):
        self.log_view.append(message)

    def spin_node(self):
        # 조인트 각도 레이블 업데이트
        angles = [round(a, 2) for a in self.current_joints]
        self.angle_label.setText(f"현재 Joint 각도: {angles}")
        rclpy.spin_once(self.node, timeout_sec=0)

def main():
    rclpy.init()
    node = Node('my_robot_gui_node')
    app = QApplication(sys.argv)
    gui = MyRobotGui(node)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
