import sys
import ftplib
import json
import os
import random
from cryptography.fernet import Fernet
from UI_show.UI.User_Menu_window_ui import Ui_User_Menu_window
from UI_show.User_question_window import Create_question_window as Type1
from UI_show.User_question_window_2 import Create_question_window_2 as Type2
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
    def __init__(self,parents,Base_path,name,Workbook_ver):
        super(User_Menu_windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        self.ver = "25-01-22.01"
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Base_path = Base_path
        self.Workbook_path = self.Base_path + "/Workbook"
        self.name = name
        self.Workbook_ver = Workbook_ver

        self.Create_question_window1 = None
        self.Create_question_window2 = None

        self.strat = self.findChild(QPushButton, "questions") # 시험 보기 
        self.strat.clicked.connect(self.open_test_Window)

        self.Select_test_range = self.findChild(QPushButton, "Recode") # 기록
        #self.Select_test_range.clicked.connect(self.open_record_window)

        self.end = self.findChild(QPushButton, "closed") # 창닫기 
        self.end.clicked.connect(self.close_windows)

        self.info = self.findChild(QLabel, "info")
        self.info.setText(f"{self.name} 님 로그인을 환영합니다.")
        self.version = self.findChild(QLabel, "version")
        self.version.setText(f"SW 버전 : {self.ver}  |  학습지 버전 : {self.Workbook_ver}")
    
    def load_or_download_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            self.download_key_file()
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()

    def open_Windows(self):
        # 폴더 내 모든 파일 탐색
        num = 1#random.randrange(1,7)
        prefix = None
        for file_name in os.listdir(self.Workbook_path):
            if file_name.endswith(".json"):  # JSON 파일만 읽기
                file_path = os.path.join(self.Workbook_path, file_name)    
                
                # 파일 이름에서 "_"를 기준으로 분리
                prefix = file_name.split("_")[0]  # "Multiple" 또는 "Subjective" 추출
                numver = int(file_name.split("_")[1]) # 문제 번호 추출

                if numver == num:
                    break
        
        if prefix != None:
            if prefix == "Multiple":
                self.Create_question_window(file_path)
            elif prefix == "Subjective":
                self.Create_question_window_2(file_path)

    def Create_question_window(self,file_path):
        if self.Create_question_window1 is None or not self.Create_question_window1.isVisible(): 
            self.Create_question_window1 = Type1(self,file_path) 
            self.hide()
            self.Create_question_window1.show()

    def Create_question_window_2(self,file_path):
        if self.Create_question_window2 is None or not self.Create_question_window2.isVisible(): 
            self.Create_question_window2 = Type2(self,file_path)
            self.hide()
            self.Create_question_window2.show()
            
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
