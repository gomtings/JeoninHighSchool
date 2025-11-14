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

    def update(self, dt, mn, mx, kp, ki, kd):
        self.dt = dt
        self.min = mn
        self.max = mx
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.prev_error = 0

    def calc(self, setpoint, pv):
        error = setpoint - pv
        self.integral += error * self.dt
        derivative = (error - self.prev_error) / self.dt if self.dt != 0 else 0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        output = max(self.min, min(self.max, output))
        self.prev_error = error
        desc = f"오차: {error:.3f}, 제어값: {output:.3f} (P: {self.kp*error:.2f}, I: {self.ki*self.integral:.2f}, D: {self.kd*derivative:.2f})"
        return output, desc

QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySide6 PID 시뮬레이터')
        self.initUi()

    def initUi(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        gb1 = QGroupBox('실시간 응답곡선')
        gb2 = QGroupBox('PID 계수 설정')
        gb3 = QGroupBox('설명/진행상황')
        vbox.addWidget(gb1)

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

        # 2. PID 계수 설정
        gbox = QGridLayout()
        gb2.setLayout(gbox)
        _txt = ('갱신시간(ms)', '최소', '최대', '목표치', '비례게인(kp):', '적분게인(ki):', '미분게인(kd):')
        self.def_Coef = (0.1, -200., 200., 50., 0.1, 0.5, 0.01)
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
        gbox.addWidget(self.btn, len(_txt)+1, 0)
        gbox.addWidget(self.btnReset, len(_txt)+1, 1)

        # 3. 진행상황/설명
        vbox3 = QVBoxLayout()
        gb3.setLayout(vbox3)
        self.desc = QLabel()
        vbox3.addWidget(self.desc)

        # signal
        self.btn.clicked.connect(self.onClickStart)
        self.btnReset.clicked.connect(self.onClickReset)

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

    def onClickReset(self):
        if hasattr(self, 'ani'):
            self.stopChart()
            self.fig.clear()
            self.canvas.draw()
            del self.ani
        self.btn.setChecked(False)
        self.btn.setText('Start')
        self.enableCoefficient(True)

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
        _dt, _min, _max, _sv, _kp, _ki, _kd = self.resetCoefficient(False)
        self.pid.update(_dt, _min, _max, _kp, _ki, _kd)
        self.ani.event_source.interval = int(_dt * 1000)
        self.ax.set_ylim(_min, _max)

    def startChart(self):
        self.resetCoefficient(False)
        _dt = self.coef[0] * 1000
        self.ani = animation.FuncAnimation(
            fig=self.fig,
            func=self.drawChart,
            init_func=self.initPlot,
            blit=False,
            interval=int(_dt)
        )
        self.canvas.draw()

    def stopChart(self):
        self.ani._stop()

    def initPlot(self):
        _dt, _min, _max, _sv, _kp, _ki, _kd = self.resetCoefficient(False)
        _dt_sec_for_pid = _dt / 1000.0
        self.pid = PID_Control(_dt_sec_for_pid, _min, _max, _kp, _ki, _kd)
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

    def drawChart(self, i):
        inc, desc = self.pid.calc(self.coef[3], self.pv)
        self.desc.setText(desc)
        self.pv += inc
        self.y.append(self.pv)
        self.x.append(i)
        self.hy.append(self.coef[3])
        self.line.set_data(self.x, self.y)
        self.spline.set_data(self.x, self.hy)
        self.ax.relim()
        self.ax.autoscale_view(True, True, False)
        return self.line, self.spline

if __name__ == '__main__':
    # PySide6는 PyQt5의 QT_QPA_PLATFORM_PLUGIN_PATH 환경 변수를 자동으로 설정할 필요가 없습니다.
    # 하지만 특정 환경에서 필요할 수 있으므로, 주석 처리된 상태로 남겨둡니다.
    # os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = r"C:/Users/김동현/AppData/Local/Programs/Python/Python311/Lib/site-packages/PySide6/Qt/plugins"

    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec()) # PySide6에서는 exec_() 대신 exec()를 사용합니다.