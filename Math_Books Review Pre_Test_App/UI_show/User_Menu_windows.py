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
        self.Workbook_path = os.path.join(self.Base_path, "Workbook")
        self.name = name
        self.Workbook_ver = Workbook_ver
        self.picture_view = self.findChild(QLabel, "picture_view")
        
        self.Create_question_window1 = None
        self.Create_question_window2 = None
        self.User_question_window = None
        self.User_question_window2 = None

        self.prefix_list = []
        self.file_list = []
        self.file_list = []
        self.point = {}
        self.current_index = 0  # 현재 문제 인덱스 저장

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
            
    def open_Windows(self):
        folder_count = sum(1 for entry in os.scandir(self.Workbook_path) if entry.is_dir())

        # 랜덤 폴더 선택
        random_folder = 1 if folder_count == 1 else random.randrange(1, folder_count + 1)
        book = f"{random_folder}권"
        save_directory = os.path.join(self.Workbook_path, book)
        self.point["book"] = book
        # 폴더 내 JSON 파일 리스트 생성
        if os.path.exists(save_directory):
            for file_name in os.listdir(save_directory):
                if file_name.endswith(".json"):
                    file_path = os.path.join(save_directory, file_name)

                    # 파일 이름에서 "_"를 기준으로 분리하여 문제 유형 저장
                    prefix = file_name.split("_")[1]  # "Multiple" 또는 "Subjective" 추출
                    self.file_list.append(file_path)
                    self.prefix_list.append(prefix)

        # ✅ 문제를 랜덤하게 섞기
        combined_list = list(zip(self.file_list, self.prefix_list))
        random.shuffle(combined_list)  # 문제를 섞어서 랜덤하게 출제
        self.file_list, self.prefix_list = zip(*combined_list)  # 다시 분리하여 저장
        # self.point["total"] = len(self.file_list)
        self.file_list = list(self.file_list)         # 튜플을 리스트로 변환
        self.prefix_list = list(self.prefix_list)  
        if self.file_list:  # JSON 파일이 있으면 실행
            self.show_next_question(book,self.point)

    def show_next_question(self, book, point):
        """ 다음 문제를 출제하는 함수 """
        if self.current_index < len(self.file_list):  # 아직 남은 문제가 있다면
            file_path = self.file_list[self.current_index]  # 파일 경로
            prefix = self.prefix_list[self.current_index]

            # 문제 유형에 따라 창 열기
            if prefix == "Multiple":
                self.Create_question_window(file_path, book, point)
            elif prefix == "Subjective":
                self.Create_question_window_2(file_path, book, point)

            self.current_index += 1  # 다음 문제로 이동
        else:
            # 데이터 파일로 저장
            if not self.file_list:
                print("파일 목록이 비어있습니다!")
                return

            # 마지막 문제의 파일 경로를 file_name으로 설정
            file_name = self.file_list[-1]  # 마지막 문제 파일 경로
            dir_path = os.path.dirname(file_name)  # 파일 경로에서 디렉토리 부분 추출
            os.makedirs(dir_path, exist_ok=True)

            # 파일 이름 설정
            save_path = os.path.join(self.Base_path, "Management", self.name, f"{self.name}_{book}.json")
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)


            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(point, f, ensure_ascii=False, indent=4)
            print(f"✅ {book}의 모든 문제를 풀었습니다!")

    def Create_question_window(self, file_path, book, point):
        if self.Create_question_window1 is None or not self.Create_question_window1.isVisible():
            self.Create_question_window1 = Type1(self, self.Base_path, file_path, book, point)
            self.hide()
            self.Create_question_window1.show()

    def Create_question_window_2(self, file_path, book, point):
        if self.Create_question_window2 is None or not self.Create_question_window2.isVisible():
            self.Create_question_window2 = Type2(self, self.Base_path, file_path, book, point)
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
