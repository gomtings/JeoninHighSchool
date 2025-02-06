import sys
import math
import time
import ftplib
import json
import os
from cryptography.fernet import Fernet
from UI_show.UI.Manager_ui import Ui_Manager_window
from UI_show.assignment_window import get_assignment_Window
from UI_show.Remove_window import Account_remove_Windows
from UI_show.grade_window import grade_manager_Windows

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
#cd UI_save

class Manager_Windows(QMainWindow, Ui_Manager_window):
    def __init__(self, parent=None,Base_path = None):
        super(Manager_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("관리자 모드")
        self.parents = parent
        self.Base_path = Base_path
        self.ver = "25-01-22.01"
        # 창 크기를 고정 
        self.setFixedSize(self.size())

        # Initialize variables and connect signals to slots
        self.assignment_Windows= None
        self.Account_remove_Windows = None
        self.Grade_Manager_Windows = None

        self.assignment = self.findChild(QPushButton, "assignment") # 시험 보기 
        self.assignment.clicked.connect(self.assignment_Window)

        self.Account_remove = self.findChild(QPushButton, "Account_remove") # 시험 보기 
        self.Account_remove.clicked.connect(self.Account_remove_Window)

        self.Grade_Manager = self.findChild(QPushButton, "Grade_Manager") # 시험 보기 
        self.Grade_Manager.clicked.connect(self.Grade_Manager_Window)

    def assignment_Window(self):
        if self.assignment_Windows is None or not self.assignment_Windows.isVisible(): 
            self.assignment_Windows = get_assignment_Window(self) 
            self.hide()
            self.assignment_Windows.show()         

    def Account_remove_Window(self):
        if self.Account_remove_Windows is None or not self.Account_remove_Windows.isVisible(): 
            self.Account_remove_Windows = Account_remove_Windows(self) 
            self.hide()
            self.Account_remove_Windows.show() 

    def Grade_Manager_Window(self):
        if self.Grade_Manager_Windows is None or not self.Grade_Manager_Windows.isVisible(): 
            self.Grade_Manager_Windows = grade_manager_Windows(self,self.Base_path) 
            self.hide()
            self.Grade_Manager_Windows.show()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()

    def popupwindows(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("로그인후 사용해 주세요!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
