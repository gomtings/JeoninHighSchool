from UI_show.UI.login_window_ui import Ui_LoginWindow
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit
)
from UI_show.membership_window import membership_window
class LoginWindow(QMainWindow,Ui_LoginWindow):
    def __init__(self,parents,Exam_record_path,Wrong_list_path,Workbook_path,Base_path):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("로그인")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Exam_record_path = Exam_record_path
        self.Wrong_list_path = Wrong_list_path
        self.Workbook_path = Workbook_path
        self.select_day = "DAY1"
        self.membershipwindow = None
        self.Base_path = Base_path
        
        self.name = self.findChild(QLineEdit,"name") #  로그인
        self.stunum = self.findChild(QLineEdit,"stunum") #  로그인

        self.start_exam = self.findChild(QPushButton,"login") #  로그인
        self.start_exam.clicked.connect(self.Login)

        self.start_exam = self.findChild(QPushButton,"insert_btn") # 회원가입
        self.start_exam.clicked.connect(self.membership_window)

    def Login(self):
        pass

    def membership_window(self):
        if self.membershipwindow is None or not self.membershipwindow.isVisible():
            self.hide()
            self.membershipwindow = membership_window(self,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path,self.Base_path) 
            self.membershipwindow.show()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()