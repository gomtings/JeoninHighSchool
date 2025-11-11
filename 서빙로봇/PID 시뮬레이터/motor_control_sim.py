import os
import sys
from collections import deque
import matplotlib
matplotlib.use('QtAgg') # Matplotlib에게 Qt 백엔드를 사용하도록 명시
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg # PySide6 호환 백엔드

from PySide6.QtWidgets import (
    QApplication, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
# Remove-Item -Recurse -Force venv_pid #  가상환경 삭제
#python -m venv venv_pid
#./venv_pid/Scripts/activate  # Windows
#pip install PySide6
#pip install matplotlib

# PID 컨트롤러 직접 구현 (별도 파일 필요 없음)
class PID_Control:
    def __init__(self, dt, mn, mx, kp, ki, kd):
        self.update(dt, mn, mx, kp, ki, kd)
        self.integral = 0
        self.prev_error = 0
        self.integral_limit = 100 # C++ 코드와 동일하게 적분 제한 추가 (선택 사항)
        
    def update(self, dt, mn, mx, kp, ki, kd):
        self.dt = dt # 이 dt는 이제 주로 애니메이션 주기 설정에 사용됩니다.
        self.min = mn # 이젠 0 (최소 PWM)
        self.max = mx # 이젠 255 (최대 PWM)
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.prev_error = 0

    def calc(self, setpoint, pv):
        error = setpoint - pv
        self.integral += error # dt를 곱하지 않음
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral)) # 적분 제한
        derivative = (error - self.prev_error) # dt로 나누지 않음
        
        # PID 출력 계산 (이 output은 이제 모터에 인가될 'PWM 값'을 의미합니다)
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        # 출력 제한: 모터 PWM의 실제 범위 (0 ~ 255)
        output = max(self.min, min(self.max, output)) 
        
        self.prev_error = error
        
        # desc 출력은 output이 PWM 값임을 반영하여 변경될 수 있습니다.
        desc = f"오차: {error:.3f}, 제어 PWM: {output:.1f} (P: {self.kp*error:.2f}, I: {self.ki*self.integral:.2f}, D: {self.kd*derivative:.2f})"
        return output, desc # 여기서 반환되는 output은 PWM 값입니다.

#QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Motor Control PID 시뮬레이터')
        
        # === 창 크기 설정 ===
        self.resize(1200, 800) # 가로 1200px, 세로 800px로 설정
        self.elapsed_time_ms = 0.0 # 밀리초 단위로 경과 시간 초기화

        self.initUi()

        # Learning 모드 관련 변수
        self.is_learning_mode = False
        self.learning_kp_current = 0.0 # 학습 모드에서 현재 Kp
        self.learning_kp_step = 0.01   # Kp 증가량
        self.learning_ku = 0.0         # 한계 이득 (Ultimate Gain)
        self.learning_pu = 0.0         # 한계 주기 (Ultimate Period)
        self.oscillation_data = deque(maxlen=200) # 진동 감지를 위한 데이터 저장
        self.prev_pv = 0.0
        self.oscillation_peaks = []    # 진동 피크 시간 저장
        self.oscillation_detected = False
        self.learning_step_count = 0

    def initUi(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        gb1 = QGroupBox('실시간 응답곡선')
        gb2 = QGroupBox('PID 계수 설정')
        gb3 = QGroupBox('설명/진행상황')
        vbox.addWidget(gb1)

        # === 추가할 코드: gb1에 더 많은 공간을 할당 ===
        vbox.setStretchFactor(gb1, 9) # gb1에 전체 세로 공간의 약 70%를 할당 (예시)
                                     # 아래 hbox (gb2, gb3)에는 나머지 30%가 할당됩니다.

        hbox = QHBoxLayout()
        hbox.addWidget(gb2)
        hbox.addWidget(gb3)
        hbox.setStretchFactor(gb2, 5)
        hbox.setStretchFactor(gb3, 5)
        vbox.addLayout(hbox)

        # 1. 차트
        vbox1 = QVBoxLayout()
        gb1.setLayout(vbox1)
        self.fig = plt.Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)
        vbox1.addWidget(self.canvas)
        
        # === 추가할 코드: 캔버스의 최소 크기 설정 ===
        self.canvas.setMinimumSize(1000, 600) # 가로 800px, 세로 600px (예시)
        # 원하는 그래프 크기에 맞춰 이 값을 조절하세요.

        # 2. PID 계수 설정
        gbox = QGridLayout()
        gb2.setLayout(gbox)
        _txt = ('갱신시간(ms)', '최소', '최대', '목표치', '비례게인(kp):', '적분게인(ki):', '미분게인(kd):')
        self.def_Coef = (50., 0., 255., 80., 0.1, 0.5, 0.01)
        self.coef = []
        self.lineEdits = []
        for i in range(len(_txt)):
            Lb = QLabel(_txt[i])
            Le = QLineEdit(str(self.def_Coef[i]))
            Le.setValidator(QDoubleValidator(-10000, 10000, 4))
            gbox.addWidget(Lb, i, 0)
            gbox.addWidget(Le, i, 1)
            self.lineEdits.append(Le)
        self.btn = QPushButton('Start')
        self.btn.setCheckable(True)
        self.btnReset = QPushButton('Reset')
        self.btnLearning = QPushButton('Learning') # 버튼 이름은 원하는 대로
        
        row_for_buttons = len(_txt)

        gbox.addWidget(self.btn, row_for_buttons, 0)             # Start 버튼 (맨 아래 행, 첫 번째 열)
        gbox.addWidget(self.btnReset, row_for_buttons, 1)        # Reset 버튼 (맨 아래 행, 두 번째 열)
        gbox.addWidget(self.btnLearning, row_for_buttons, 2)          # 새 버튼 (맨 아래 행, 세 번째 열)

        # 3. 진행상황/설명
        vbox3 = QVBoxLayout()
        gb3.setLayout(vbox3)
        self.desc = QLabel()
        vbox3.addWidget(self.desc)

        # signal
        self.btn.clicked.connect(self.onClickStart)
        self.btnReset.clicked.connect(self.onClickReset)
        self.btnLearning.clicked.connect(self.onClickLearning)

    def onClickStart(self):
        if self.btn.isChecked():
            self.btn.setText('Stop')
            self.enableCoefficient(False)
            if hasattr(self, 'ani'):
                self.resetAll()
                self.ani.event_source.start()
            else:
                self.startChart()
        else:
            self.btn.setText('Start')
            self.enableCoefficient(True)
            self.ani.event_source.stop()
            if self.is_learning_mode:
                # 학습 중이었다면 학습 중지 및 결과 적용 또는 초기화
                self.is_learning_mode = False
                self.ResetlearningData()

    def onClickLearning(self):
        if not self.is_learning_mode:
            self.is_learning_mode = True
            self.btn.setText('Stop') # 학습 중에는 Start/Stop 버튼이 Stop 상태여야 함
            self.btn.setChecked(True)
            self.enableCoefficient(False) # 계수 설정 비활성화
            self.desc.setText("PID 학습 시작: Ku, Pu 탐색 중...")
            
            # 초기화
            self.learning_kp_current = 0.0
            self.lineEdits[4].setText(str(self.learning_kp_current)) # Kp
            self.lineEdits[5].setText('0.0') # Ki
            self.lineEdits[6].setText('0.0') # Kd
            self.learning_ku = 0.0
            self.learning_pu = 0.0
            self.oscillation_data.clear()
            self.oscillation_peaks.clear()
            self.oscillation_detected = False
            self.learning_step_count = 0

            # 차트 시작 (혹은 재시작)
            if hasattr(self, 'ani'):
                self.resetAll()
                self.ani.event_source.start()
            else:
                self.startChart()
            
            # 목표치를 안정적으로 설정 (학습 동안 변경되지 않도록)
            # 여기서는 현재 설정된 목표치를 그대로 사용
            self.learning_target_pv = float(self.lineEdits[3].text())

        else:
            # 학습 중이었다면 학습 중지 및 결과 적용 또는 초기화
            self.is_learning_mode = False
            self.ResetlearningData()

    def onClickReset(self):
        if hasattr(self, 'ani'):
            self.stopChart()
            self.fig.clear()
            self.canvas.draw()
            del self.ani
        self.btn.setChecked(False)
        self.btn.setText('Start')
        self.desc.setText("")
        self.enableCoefficient(True)

    def ResetlearningData(self):
        self.btn.setText('Start')
        self.btn.setChecked(False)
        self.enableCoefficient(True)
        self.desc.setText("PID 학습 중지.")
        if hasattr(self, 'ani'):
            self.ani.event_source.stop()

    def enableCoefficient(self, flag):
        for le in self.lineEdits:
            le.setEnabled(flag)

    def resetCoefficient(self, isDefault=False):
            self.coef.clear()
            for i in range(len(self.def_Coef)):
                if isDefault:
                    v = self.def_Coef[i]
                    self.lineEdits[i].setText(str(v))
                else:
                    v = float(self.lineEdits[i].text())
                self.coef.append(v)
            return self.coef

    def resetAll(self):
        _dt_ms_from_ui, _min, _max, _sv, _kp, _ki, _kd = self.resetCoefficient(False)
        self.pid.update(_dt_ms_from_ui, _min, _max, _kp, _ki, _kd) 
        self.ani.event_source.interval = int(_dt_ms_from_ui)
        self.ax.set_ylim(_min, _max)

    def startChart(self):
        # UI에서 밀리초 단위로 입력된 dt 값을 읽어옵니다.
        _dt_ms_from_ui, _, _, _, _, _, _ = self.resetCoefficient(False)
        
        self.ani = animation.FuncAnimation(
            fig=self.fig,
            func=self.drawChart,
            init_func=self.initPlot,
            blit=False,
            interval=int(_dt_ms_from_ui), # UI에서 읽은 ms 값을 그대로 사용
            cache_frame_data=False # === 이 줄을 추가합니다 ===
        )
        self.canvas.draw()

    def stopChart(self):
        self.ani._stop()

    def initPlot(self):
        _dt_ms_from_ui, _min, _max, _sv, _kp, _ki, _kd = self.resetCoefficient(False)
        # PID_Control에는 이제 dt가 PID 계산에 직접 사용되지 않으므로,
        # 단순히 애니메이션 주기를 나타내는 값으로 ms 단위를 그대로 전달합니다.
        self.pid = PID_Control(_dt_ms_from_ui, _min, _max, _kp, _ki, _kd) 
        self.pv = _min
        self.x = deque([], 100)
        self.y = deque([], 100)
        self.hy = deque([], 100)
        self.ax = self.fig.subplots()
        self.ax.set_title('PID Control')
        self.ax.set_ylim(_min, _max)
        self.line, = self.ax.plot(self.x, self.y, label='output')
        self.spline, = self.ax.plot(self.x, self.hy, linestyle='--', label='setpoint', color='r', alpha=0.7)
        self.ax.legend()
        return self.line, self.spline
    
    def applyZieglerNicholsCoefficients(self):
        if self.learning_ku > 0 and self.learning_pu > 0:
            # PID 계수 계산 (지글러-니콜스 PID 공식)
            kp_tuned = 0.6 * self.learning_ku
            ki_tuned = (2 * kp_tuned) / self.learning_pu
            kd_tuned = (kp_tuned * self.learning_pu) / 8.0

            self.lineEdits[4].setText(f"{kp_tuned:.3f}") # Kp
            self.lineEdits[5].setText(f"{ki_tuned:.3f}") # Ki
            self.lineEdits[6].setText(f"{kd_tuned:.3f}") # Kd

            self.desc.setText(f"PID 계수 적용됨: Kp={kp_tuned:.3f}, Ki={ki_tuned:.3f}, Kd={kd_tuned:.3f}")

    def drawChart(self, frame_num):
        # 학습 모드일 때
        
        self.elapsed_time_ms += self.pid.dt 
        current_time_seconds = self.elapsed_time_ms / 1000.0 # 초 단위

        if self.is_learning_mode:
            # Kp 값을 점진적으로 증가
            # 일정 스텝마다 Kp 증가. 예를 들어 50번 업데이트마다 Kp 증가
            self.learning_step_count += 1
            
            # 현재 PV와 목표치(self.learning_target_pv) 간의 오차 계산
            current_error = abs(self.learning_target_pv - self.pv)

            # Kp 증가 폭 결정
            if not self.oscillation_detected: # 아직 진동이 감지되지 않았을 때
                if current_error > self.learning_target_pv * 0.5: # 오차가 클 때 (목표치의 50% 이상)
                    self.learning_kp_step = 0.5 # 크게 증가
                elif current_error > self.learning_target_pv * 0.1: # 오차가 중간일 때 (10% ~ 50%)
                    self.learning_kp_step = 0.05 # 중간 정도로 증가
                else: # 오차가 작을 때 (10% 미만)
                    self.learning_kp_step = 0.001 # 작게 증가 (진동 감지에 집중)
            else: # 진동이 감지된 후에는 Kp를 더 이상 증가시키지 않음
                self.learning_kp_step = 0.0 # Ku를 찾았으므로 Kp 고정
                
            if self.learning_step_count % 50 == 0 and not self.oscillation_detected:
                self.learning_kp_current += self.learning_kp_step
                self.lineEdits[4].setText(f"{self.learning_kp_current:.3f}")
                # PID 컨트롤러 업데이트
                self.pid.update(self.coef[0], self.coef[1], self.coef[2], 
                                self.learning_kp_current, 0.0, 0.0) # Ki, Kd는 0
                self.desc.setText(f"PID 학습 중: Kp 증가 중 ({self.learning_kp_current:.3f})...")
                
                if self.learning_kp_current > 10.0: # 안전장치 (시스템에 따라 튜닝)
                    self.desc.setText("Warning: Kp가 너무 커졌습니다. 학습 중지.")
                    self.onClickLearning() 
                    return self.line, self.spline

            # 현재 Kp 값으로 PID 계산 (Ki, Kd는 0)
            current_pwm, desc = self.pid.calc(self.learning_target_pv, self.pv)
            
            # 모터 동역학 시뮬레이션
            max_motor_rpm = 200.0 
            target_rpm_from_pwm = (current_pwm / self.pid.max) * max_motor_rpm 
            motor_inertia_factor = 0.05 
            self.pv += (target_rpm_from_pwm - self.pv) * motor_inertia_factor
            
            self.y.append(self.pv)
            self.x.append(current_time_seconds)
            self.hy.append(self.learning_target_pv)
            
            # 진동 감지 로직
            # 목표치(self.learning_target_pv)를 기준으로 진동하는지 확인
            self.oscillation_data.append(self.pv)

            # 진동 감지 로직 수정 (오버슈트 임계값도 오차에 따라 조정 고려)
            if not self.oscillation_detected:
                # 진동 감지 시작 조건 강화:
                # 1. Kp가 어느 정도 이상이어야 하고 (초기 Kp가 너무 작으면 노이즈성 움직임에도 반응할 수 있음)
                # 2. PV가 목표치에 '충분히' 근접해 있어야 하며 (예: 목표치의 10% 이내)
                # 3. 목표치를 '교차하는' 움직임이 최소 한 번 감지되었을 때 (진동의 핵심)
                
                # PV가 목표치의 10% 이내로 들어왔는지 확인
                is_pv_near_target = abs(self.pv - self.learning_target_pv) < self.learning_target_pv * 0.1

                # PV가 목표치를 교차한 적이 있는지 확인 (최소 한 번 오버슈트/언더슈트)
                # self.oscillation_data[-2]를 사용하려면 len(self.oscillation_data) >= 2 필요
                crossed_target_recently = False
                if len(self.oscillation_data) >= 2:
                    # 이전 PV가 목표치보다 작았고 현재 PV가 목표치보다 크거나 같을 때 (상승 교차)
                    # 또는 이전 PV가 목표치보다 컸고 현재 PV가 목표치보다 작거나 같을 때 (하강 교차)
                    if (self.oscillation_data[-2] < self.learning_target_pv and self.pv >= self.learning_target_pv) or \
                       (self.oscillation_data[-2] > self.learning_target_pv and self.pv <= self.learning_target_pv):
                        crossed_target_recently = True

                # 최종 진동 감지 시작 조건
                if self.learning_kp_current > 0.1 and is_pv_near_target and crossed_target_recently:
                    self.oscillation_detected = True
                    self.learning_ku = self.learning_kp_current
                    self.desc.setText(f"PID 학습: 진동 감지 시작. Ku: {self.learning_ku:.3f}. Pu 측정 중...")

            elif self.oscillation_detected:
                is_significant_peak_or_valley = False
                if len(self.oscillation_data) >= 3: # 최소 3개 데이터가 있어야 피크 감지 가능
                    # 상승 피크 (A < B > C)
                    if self.oscillation_data[-3] < self.oscillation_data[-2] and self.oscillation_data[-2] > self.oscillation_data[-1]:
                        if abs(self.oscillation_data[-2] - self.learning_target_pv) > self.learning_target_pv * 0.05:
                            is_significant_peak_or_valley = True
                            peak_time = current_time_seconds - (self.pid.dt / 1000.0) # 피크가 발생한 시점 (지난 프레임)
                            
                    # 하락 피크 (A > B < C)
                    elif self.oscillation_data[-3] > self.oscillation_data[-2] and self.oscillation_data[-2] < self.oscillation_data[-1]:
                        if abs(self.oscillation_data[-2] - self.learning_target_pv) > self.learning_target_pv * 0.05:
                            is_significant_peak_or_valley = True
                            peak_time = current_time_seconds - (self.pid.dt / 1000.0) # 피크가 발생한 시점 (지난 프레임)

                if is_significant_peak_or_valley:
                    self.oscillation_peaks.append(peak_time) # <<< 여기도 'i'에서 'peak_time'으로 변경되어야 합니다.
                    
                    # 최소 2주기 (3개 피크 또는 4개 피크)를 감지하여 Pu 계산
                    if len(self.oscillation_peaks) >= 3:
                        # 2번째 피크와 3번째 피크 사이의 간격을 한 주기로 간주 (더 안정적)
                        # 또는 (마지막 피크 - 첫 피크) / (피크 개수 - 1)
                        # 이미 초 단위이므로 / 1000.0 / 2.0 필요 없음
                        self.learning_pu = (self.oscillation_peaks[-1] - self.oscillation_peaks[-3]) / 2.0 
                        
                        if self.learning_pu > 0:
                            self.desc.setText(f"PID 학습 완료! Ku: {self.learning_ku:.3f}, Pu: {self.learning_pu:.3f}s")
                            self.applyZieglerNicholsCoefficients()
                            self.onClickLearning() 
                            return self.line, self.spline
                                
            self.prev_pv = self.pv

        # 일반 동작 모드 (기존 코드)
        else:
            current_pwm, desc = self.pid.calc(self.coef[3], self.pv)
            self.desc.setText(desc)
            
            max_motor_rpm = 200.0 
            target_rpm_from_pwm = (current_pwm / self.pid.max) * max_motor_rpm 
            motor_inertia_factor = 0.05 
            self.pv += (target_rpm_from_pwm - self.pv) * motor_inertia_factor
            
            self.y.append(self.pv)
            self.x.append(current_time_seconds)
            self.hy.append(self.coef[3])

        self.line.set_data(self.x, self.y)
        self.spline.set_data(self.x, self.hy)
        self.ax.set_xlim(max(0, current_time_seconds - 5), current_time_seconds + 1) # 최근 5초에서 1초 미래까지 표시 (예시)
        self.ax.relim()
        self.ax.autoscale_view(True, True, False)
        return self.line, self.spline

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec()) # PySide6에서는 exec_() 대신 exec()를 사용합니다.