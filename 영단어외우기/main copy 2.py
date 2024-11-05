import sys
import math
import os
import time
from Main_window import Ui_Form
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton
)

class Main_Windows(QMainWindow, Ui_Form):
    def __init__(self):
        super(Main_Windows, self).__init__()  # QMainWindow의 __init__을 명시적으로 호출
        self.setupUi(self)  # Ui_Form의 UI 설정
        self.setWindowTitle("Main_Windows")  # 윈도우 제목 설정

        self.strat = self.findChild(QPushButton, "pushButton")
        self.strat.clicked.connect(self.strat_connect)
        
    def strat_connect(self):
        if not hasattr(self, "login_window") or not self.login_window.isVisible():
            self.login_window = Login.Login_Windows(self)
            self.login_window.show()

app = QApplication(sys.argv)

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
