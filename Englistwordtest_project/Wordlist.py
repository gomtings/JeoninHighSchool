
import os
import sys
from ui_main import Ui_Word_list
import Wordlist_day1
import Login
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton
)
# pyside6-uic main_Report.ui -o ui_main_Report.py UI 파일 python파일로 변경함 
#               바꿀 UI             #저장할 이름
class Main_Windows(QMainWindow,Ui_Word_list):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Integrated_Control_System")

        self.Login = self.findChild(QPushButton, "btn_1")
        self.Login.clicked.connect(self.Day1_wordlist)

    def Day1_wordlist(self):
        if not hasattr(self, "Day1_wordlist") or not self.login_window.isVisible():
            self.login_window = Wordlist_day1.Main_Windows(self)
            self.login_window.show()


app = QApplication(sys.argv)
app.setStyle("Windowsvista")

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())