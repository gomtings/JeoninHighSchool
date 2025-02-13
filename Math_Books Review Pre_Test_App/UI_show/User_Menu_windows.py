import sys
import ftplib
import json
import os
from cryptography.fernet import Fernet
from UI_show.UI.User_Menu_window_ui import Ui_User_Menu_window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    )

#pyside6-designer
#pyside6-uic main.ui -o Main_window_ui.py
#pyside6-uic Subject_select.ui -o Subject_select_ui.py
#pyside6-uic record.ui -o record_window_ui.py
#pyside6-uic daylist.ui -o daylist_window_ui.py
#pyside6-uic wordlist.ui -o wordlist_ui.py
#pyside6-uic Uploading.ui -o Uploading_ui.py
#pyside6-uic test_window.ui -o test_window_ui.py
#pyside6-uic login.ui -o login_window_ui.py
#pyside6-uic membership.ui -o membership_ui.py
#pyside6-uic Manager.ui -o Manager_ui.py
#pyside6-uic assignment.ui -o assignment_ui.py
#pyside6-uic grade_manager.ui -o grade_manager_ui.py
#pyside6-uic Check_grades.ui -o Check_grades_ui.py
#cd UI_save

class User_Menu_windows(QMainWindow, Ui_User_Menu_window):
    def __init__(self,parents,Base_path,name):
        super(User_Menu_windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        self.ver = "25-01-22.01"
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Base_path = Base_path
        self.name = name
        
        # Initialize variables and connect signals to slots
        self.select_window = None
        self.daylist_window = None
        self.record_Window = None
        self.uploading_window = None
        self.Manager_window = None
        self.login_window = None
        self.Successlogin = False
        self.admin = False
        self.Workbook_ver = None

        self.strat = self.findChild(QPushButton, "questions") # 시험 보기 
        #self.strat.clicked.connect(self.open_test_Window)

        self.Select_test_range = self.findChild(QPushButton, "Recode") # 기록
        #self.Select_test_range.clicked.connect(self.open_record_window)

        self.vocabulary_book = self.findChild(QPushButton, "note") #단어장 
        #self.vocabulary_book.clicked.connect(self.open_daylist_window)

        self.end = self.findChild(QPushButton, "closed") # 창닫기 
        self.end.clicked.connect(self.close_windows)

        self.Manager_btn = self.findChild(QPushButton, "Manager_btn") # 관리자 모드 
        #self.Manager_btn.clicked.connect(self.Manager_windows)

        self.info = self.findChild(QLabel, "info")
        self.version = self.findChild(QLabel, "version")
        self.info.setText(f"   {self.name} 님 로그인 환영합니다.")
        self.version.setText(f"SW 버전 : {self.ver}  |  학습지 버전 : 2025-01-10 10:55")


    def close_windows(self):
        self.close()            

    def closeEvent(self, event):
        pass

    def popupwindows(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("로그인후 사용해 주세요!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
