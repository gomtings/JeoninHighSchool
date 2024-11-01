import sys
import math
import os
import time
from ui_ele import Ui_Form
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton
)

class test_Window(QMainWindow, Ui_Form):
    def __init__(self):
        super(test_Window, self).__init__()  # QMainWindow의 __init__을 명시적으로 호출
        self.setupUi(self)  # Ui_Form의 UI 설정
        self.setWindowTitle("test_Window")  # 윈도우 제목 설정

        

"""
app = QApplication(sys.argv)

window = test_Window()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
"""