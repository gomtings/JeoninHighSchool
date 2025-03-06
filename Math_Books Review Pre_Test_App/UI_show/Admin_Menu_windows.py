import sys
import ftplib
import json
import os
from cryptography.fernet import Fernet
from UI_show.UI.Admin_Menu_window_ui import Ui_Admin_Menu_window
from UI_show.assignment_window import get_assignment_Window
from UI_show.Remove_window import Account_remove_Windows
from UI_show.Grade_window import grade_manager_Windows
from UI_show.Select_Type_Window import Select_Type_Window
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

class Admin_Menu_windows(QMainWindow, Ui_Admin_Menu_window):
    def __init__(self,parents,Base_path,name,Workbook_ver):
        super(Admin_Menu_windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        self.ver = "25-01-22.01"
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Base_path = Base_path
        self.name = name
        self.Workbook_ver = Workbook_ver

        # Initialize variables and connect signals to slots
        self.assignment_Windows = None
        self.Account_Remove_windows = None
        self.Grade_Manager_Windows = None
        self.uploading_window = None
        self.Manager_window = None
        self.login_window = None
        self.Select_Type_Window = None
        self.Successlogin = False
        self.admin = False

        self.Manager_Setup = self.findChild(QPushButton, "Manager_Setup") # 관리자 권한 관리리
        self.Manager_Setup.clicked.connect(self.Manager_Setup_Window)

        self.Account_Remove = self.findChild(QPushButton, "Account_Remove") # 계정 제거거
        self.Account_Remove.clicked.connect(self.Account_Remove_window)

        self.Grade_Manager = self.findChild(QPushButton, "Grade_Manager") #기록 확인 
        self.Grade_Manager.clicked.connect(self.Grade_Manager_Window)

        self.Addition = self.findChild(QPushButton, "Addition")
        self.Addition.clicked.connect(self.Addition_window) # 문제 출제제

        self.end = self.findChild(QPushButton, "closed") # 창닫기 
        self.end.clicked.connect(self.close_windows)

        self.info = self.findChild(QLabel, "info")
        self.info.setText(f"{self.name} 님 로그인을 환영합니다.")
        self.version = self.findChild(QLabel, "version")
        self.version.setText(f"SW 버전 : {self.ver}  |  학습지 버전 : {self.Workbook_ver}")
        

    def Manager_Setup_Window(self):
        if self.assignment_Windows is None or not self.assignment_Windows.isVisible(): 
            self.assignment_Windows = get_assignment_Window(self) 
            self.hide()
            self.assignment_Windows.show()

    def Account_Remove_window(self):
        if self.Account_Remove_windows is None or not self.Account_Remove_windows.isVisible(): 
            self.Account_Remove_windows = Account_remove_Windows(self) 
            self.hide()
            self.Account_Remove_windows.show()

    def Grade_Manager_Window(self):
        if self.Grade_Manager_Windows is None or not self.Grade_Manager_Windows.isVisible(): 
            self.Grade_Manager_Windows = grade_manager_Windows(self,self.Base_path) 
            self.hide()
            self.Grade_Manager_Windows.show()

    def Addition_window(self):
        if self.Select_Type_Window is None or not self.Select_Type_Window.isVisible(): 
            self.Select_Type_Window = Select_Type_Window(self) 
            self.hide()
            self.Select_Type_Window.show()

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

