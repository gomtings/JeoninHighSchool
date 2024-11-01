import sys
import math
import os
import time
from ui_untitled import Ui_Form
import test
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
        self.test_Window = None

        self.strat = self.findChild(QPushButton, "pushButton")
        self.strat.clicked.connect(self.strat_connect)

        self.Select_test_range = self.findChild(QPushButton, "pushButton_2")
        self.Select_test_range.clicked.connect(self.closed)

        self.end = self.findChild(QPushButton, "pushButton_3")
        self.end.clicked.connect(self.closed)

        self.Add_test_scope = self.findChild(QPushButton, "pushButton_4")
        self.Add_test_scope.clicked.connect(self.closed)
    
        self.vocabulary_book = self.findChild(QPushButton, "pushButton_5")
        self.vocabulary_book.clicked.connect(self.closed)
    def strat_connect(self):
        if not hasattr(self, "login_window") or not self.login_window.isVisible():
            self.test_Window = test.test_Window()
            self.test_Window.show()
    def closed(self):
         self.close()



app = QApplication(sys.argv)

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
