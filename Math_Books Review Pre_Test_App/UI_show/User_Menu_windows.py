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
    QFileDialog    
    )
from PySide6.QtGui import QColor, QPixmap

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
        self.Workbook_path = os.path.join(self.Base_path, "question_answer")
        self.name = name
        self.Workbook_ver = Workbook_ver
        self.picture_view = self.findChild(QLabel, "picture_view")

        self.Create_question_window1 = None
        self.Create_question_window2 = None
        self.User_question_window = None
        self.User_question_window2 = None

        self.strat = self.findChild(QPushButton, "questions") # 시험 보기 
        self.strat.clicked.connect(self.open_Windows)

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

    # def bring_in_image(self):
        # file_name = "C:/Users/LG10/Pictures/과제1.png"
        # pixmap = QPixmap(file_name)
        # self.picture_view.setPixmap(pixmap)
        # self.picture_view.setScaledContents(True)  # QLabel에 맞게 크기 조정
        # self.selected_image_path = file_name  # 이미지 경로 저장

    def open_Windows(self):
        prefix  = None
        folder_count = sum(1 for entry in os.scandir(self.Workbook_path) if entry.is_dir())
        # 랜덤 숫자 생성
        if folder_count == 1:
            random_folder = 1  # 폴더가 1개라면 1로 고정
        else:
            random_folder = random.randrange(1, folder_count + 1)  # 범위를 1부터 folder_count까지 포함
        book = f"{random_folder}권"
        # 폴더 내 모든 파일 탐색
        save_directory = os.path.join(self.Workbook_path, book)
        # .json 파일 갯수 계산
        if os.path.exists(save_directory):
            json_count = sum(1 for file in os.listdir(save_directory) if file.endswith('.json'))
            if json_count == 1:
                answer = 1  # 폴더가 1개라면 1로 고정
            else:
                answer = random.randrange(1, json_count + 1)  # 범위를 1부터 folder_count까지 포함
            for file_name in os.listdir(save_directory):
                if file_name.endswith(".json"):  # JSON 파일만 읽기
                    file_path = os.path.join(save_directory, file_name)    
                    # 파일 이름에서 "_"를 기준으로 분리
                    prefix = file_name.split("_")[1]  # "Multiple" 또는 "Subjective" 추출
                    numver = (file_name.split("_")[-1]) # 문제 번호 추출
                    numver = int(numver.split(".")[0])
                    if numver == answer:
                        break
        #print(""+prefix+","+str(numver))
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
