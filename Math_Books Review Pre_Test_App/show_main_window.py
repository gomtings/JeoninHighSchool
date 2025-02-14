import sys
import ftplib
import json
import os
import requests
from cryptography.fernet import Fernet
from UI_show.UI.Login_Window_ui import Ui_Login_Window
from UI_show.Admin_Menu_windows import Admin_Menu_windows
from UI_show.User_Menu_windows import User_Menu_windows
from UI_show.Sinup_window import Sinup_window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
    )

#pyside6-designer
#pyside6-uic Login_Window.ui -o Login_Window_ui.py
#pyside6-uic Menu_window.ui -o Menu_window_ui.py
#pyside6-uic Admin_Menu_window.ui -o Admin_Menu_window_ui.py
#pyside6-uic User_Menu_window.ui -o User_Menu_window_ui.py
#pyside6-uic Sinup_window.ui -o Sinup_window_ui.py
#cd UI_save

class Login_Windows(QMainWindow, Ui_Login_Window):
    def __init__(self):
        super(Login_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Math_Books Review Pre_Test_App")
        self.ver = "25-01-22.01"
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.Base_path = os.getcwd()
        
        # Initialize variables and connect signals to slots
        self.Admin_Menu_window = None
        self.User_Menu_window = None
        self.Sinup_window = None
        self.Successlogin = False
        self.admin = False
        self.name = ""

        self.Edit_ID = self.findChild(QLineEdit, "Edit_ID") # 아이디
        self.Edit_Password = self.findChild(QLineEdit, "Edit_Password") # 비밀번호

        self.login = self.findChild(QPushButton, "login_Btn") # 로그인
        self.login.clicked.connect(self.login_windows)
        self.login.setStyleSheet(
            """
        QPushButton {background-color: #0090ff; color: black;}
        QPushButton:hover {background-color: #b0b0b0; color: black;}
        """
        )
        self.Sinup = self.findChild(QPushButton, "Sinup_Btn") # 회원가입
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
            response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/login.php', data=post)
            # 응답이 성공 메시지일 때 팝업 창 띄우기
            result = response.json()
            if result['result'] == 'success':
                self.name = result["name"]
                self.admin = False if result["admin"] == 0 else True
                self.Successlogin = True
                if self.admin:
                    self.Open_Admin_Menu_window()
                else:
                    self.Open_User_Menu_window()
                self.popupwindows("로그인 성공!","로그인 되었습니다.")
            else:
                self.popupwindows("로그인 실패!","아이디 또는 비밀번호 확인")
        else:
            self.popupwindows("경고","아이디 또는 비밀번호를 입력해 주세요!")


    def Open_Sinup_window(self):
        if self.Sinup_window is None or not self.Sinup_window.isVisible(): 
            self.Sinup_window = Sinup_window(self) 
            self.hide()
            self.Sinup_window.show()

    def Open_Admin_Menu_window(self):
        if self.Admin_Menu_window is None or not self.Admin_Menu_window.isVisible(): 
            self.Admin_Menu_window = Admin_Menu_windows(self,self.Base_path,self.name) 
            self.hide()
            self.Admin_Menu_window.show()

    def Open_User_Menu_window(self):
        if self.User_Menu_window is None or not self.User_Menu_window.isVisible(): 
            self.User_Menu_window = User_Menu_windows(self,self.Base_path,self.name) 
            self.hide()
            self.User_Menu_window.show()

    def close_windows(self):
        self.close()            

    def closeEvent(self, event):
        pass

    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

app = QApplication(sys.argv)

window = Login_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
