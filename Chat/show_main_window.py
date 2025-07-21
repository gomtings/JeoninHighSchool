import sys
import ftplib
import json
import os
import requests
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
)

from UI_show.UI.Login_Window_ui import Ui_Login_Window
from UI_show.friend_list_window import friend_list_window
from UI_show.Sinup_window import Sinup_window
from UI_show.Modules.mqtt_module import MQTTClient       

# cd Chat/
# pyside6-uic friend_list_window.ui -o friend_list_window_ui.py
# pyside6-uic Setting_Window.ui -o Setting_Window_ui.py
class Login_Windows(QMainWindow, Ui_Login_Window):
    def __init__(self):
        super(Login_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Simple Talk")
        self.ver = "25-01-22.01"
        self.setFixedSize(self.size())
        self.local = MQTTClient()  # 관리 프로그램과 통신 할 MQTT 로컬연결..
        self.Base_path = os.getcwd()
        self.key_path = os.path.join(self.Base_path, "info", "encryption_key.key")

        # 상태 초기화
        self.friend_list_window = None
        self.Sinup_window = None
        self.Successlogin = False
        self.admin = False
        self.Workbook_ver = None
        self.name = ""

        # UI 요소 연결
        self.Edit_ID = self.findChild(QLineEdit, "Edit_ID")
        self.Edit_Password = self.findChild(QLineEdit, "Edit_Password")

        self.login = self.findChild(QPushButton, "login_Btn")
        self.login.clicked.connect(self.login_windows)
        self.login.setStyleSheet(
            """
            QPushButton {background-color: #0090ff; color: black;}
            QPushButton:hover {background-color: #b0b0b0; color: black;}
            """
        )

        self.Sinup = self.findChild(QPushButton, "Sinup_Btn")
        self.Sinup.clicked.connect(self.Open_Sinup_window)
        self.Sinup.setStyleSheet(
            """
            QPushButton {background-color: #b0b0b0; color: black;}
            QPushButton:hover {background-color: #0090ff; color: black;}
            """
        )


    def login_windows(self):
        ID = self.Edit_ID.text()
        Password = self.Edit_Password.text()
        if ID or Password:
            post = {'name': ID, 'stunum': Password}
            response = requests.post(
                'http://solimatics.dothome.co.kr/Math_Books Review Pre_Test_App/db/login.php',
                data=post
            )
            result = response.json()
            if result['result'] == 'success':
                self.name = result["name"]
                self.admin = result["admin"] != 0
                self.Successlogin = True
                self.Open_Admin_Menu_window()
                #self.popupwindows("로그인 성공!", "로그인 되었습니다.")
            else:
                self.popupwindows("로그인 실패!", "아이디 또는 비밀번호 확인")
        else:
            self.popupwindows("경고", "아이디 또는 비밀번호를 입력해 주세요!")

    def Open_Sinup_window(self):
        if self.Sinup_window is None or not self.Sinup_window.isVisible():
            self.Sinup_window = Sinup_window(self)
            self.hide()
            self.Sinup_window.show()

    def Open_Admin_Menu_window(self):
        if self.friend_list_window is None or not self.friend_list_window.isVisible():
            self.friend_list_window = friend_list_window(self,self.name,self.Base_path)
            self.hide()
            self.local.connecting()  # MQTT 서버 연결
            self.local.loop_start()  # MQTT 시작
            self.friend_list_window.show()

    def closeEvent(self, event):
        pass

    def popupwindows(self, title, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login_Windows()
    window.show()
    try:
        app_exec = app.exec
    except AttributeError:
        app_exec = app.exec_
    sys.exit(app_exec())
