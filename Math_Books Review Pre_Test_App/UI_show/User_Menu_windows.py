import sys
import ftplib
import json
import os
import random
from cryptography.fernet import Fernet
from UI_show.UI.User_Menu_window_ui import Ui_User_Menu_window
from UI_show.User_question_window import Create_question_window as Type1
from UI_show.User_question_window_2 import Create_question_window as Type2

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog    
)
from PySide6.QtGui import QColor, QPixmap

class User_Menu_windows(QMainWindow, Ui_User_Menu_window):
    def __init__(self, parents, Base_path, name, Workbook_ver):
        super(User_Menu_windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        self.ver = "25-01-22.01"
        self.setFixedSize(self.size())
        
        self.parents = parents
        self.Base_path = Base_path
        self.Workbook_path = os.path.join(self.Base_path, "Workbook")
        self.name = name
        self.Workbook_ver = Workbook_ver
        self.picture_view = self.findChild(QLabel, "picture_view")
        
        self.Create_question_window1 = None
        self.Create_question_window2 = None

        self.prefix_list = []
        self.file_list = []
        self.point = {}
        self.current_index = 0

        self.strat = self.findChild(QPushButton, "questions")
        self.strat.clicked.connect(self.open_Windows)

        self.Select_test_range = self.findChild(QPushButton, "Recode")
        # self.Select_test_range.clicked.connect(self.open_record_window)

        self.end = self.findChild(QPushButton, "closed")
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
        random_folder = 1 if folder_count == 1 else random.randrange(1, folder_count + 1)
        book = f"{random_folder}권"
        save_directory = os.path.join(self.Workbook_path, book)
        self.point["book"] = book

        self.file_list.clear()
        self.prefix_list.clear()

        if os.path.exists(save_directory):
            for file_name in os.listdir(save_directory):
                if file_name.endswith(".json"):
                    file_path = os.path.join(save_directory, file_name)
                    prefix = file_name.split("_")[1]
                    self.file_list.append(file_path)
                    self.prefix_list.append(prefix)

        combined_list = list(zip(self.file_list, self.prefix_list))
        random.shuffle(combined_list)

        if combined_list:
            self.file_list, self.prefix_list = map(list, zip(*combined_list))  # ✅ 튜플 → 리스트로 변환
        else:
            self.file_list = []
            self.prefix_list = []

        self.point["total"] = len(self.file_list)

        if self.file_list:
            self.show_next_question(book, self.point)
        else:
            self.popup_message("문제 파일이 없습니다.", "확인")

    def show_next_question(self, book, point):
        if self.current_index < len(self.file_list):
            file_path = self.file_list[self.current_index]
            prefix = self.prefix_list[self.current_index]

            if prefix == "Multiple":
                self.Create_question_window(file_path, book, point)
            elif prefix == "Subjective":
                self.Create_question_window_2(file_path, book, point)

            self.current_index += 1
        else:
            save_path = os.path.join(self.Base_path, "Management", self.name)
            os.makedirs(save_path, exist_ok=True)
            file_name = os.path.join(save_path, f"{self.name}_{book}.json")
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(point, f, ensure_ascii=False, indent=4)
            print(f"✅ {book}의 모든 문제를 풀었습니다!")
            self.popup_message("모든 문제를 완료했습니다!", "확인")

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

    def popup_message(self, text, title="알림"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
