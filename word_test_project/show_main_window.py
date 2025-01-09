import sys
import math
import time
import ftplib
import json
import os
from cryptography.fernet import Fernet
from UI_show.UI.Main_window_ui import Ui_Form
from UI_show.Subject_select_window import Subject_select_window
from UI_show.daylist_window import daylist_window
from UI_show.record_window import record_Window
from UI_show.Uploading_window import uploading_window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    )
#pyside6-designer
#pyside6-uic main.ui -o Main_window_ui.py
#pyside6-uic Subject_select.ui -o Subject_select_ui.py
#pyside6-uic record.ui -o record_window_ui.py
#pyside6-uic daylist.ui -o daylist_window_ui.py
#pyside6-uic wordlist.ui -o wordlist_ui.py
#pyside6-uic Uploading.ui -o Uploading_ui.py
#cd word_test_project/UI_save
class Main_Windows(QMainWindow, Ui_Form):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.Exam_bring = os.getcwd() +"/Exam_test/"
        self.Exam_record_path = os.getcwd() +"/Exam_test/Exam_record.txt"
        self.Wrong_list_path = os.getcwd() +"/Exam_test/"
        self.Workbook_path = os.getcwd() +"/Workbook/"
        self.Base_path = os.getcwd()
        
        # Initialize variables and connect signals to slots
        self.select_window = None
        self.daylist_window = None
        self.record_Window = None
        self.uploading_window = None
        
        # FTP 정보 로드
        try:
            FTP_path = os.path.join(self.Base_path, "info", "Report_FTP.json")
            with open(FTP_path, "r", encoding="UTF-8") as f:
                self.report_dist = json.load(f)
        except Exception as e:
            print(f'FTP.json 데이터가 없습니다. {e}')
        
        # 키 파일 경로 설정
        self.key_path = os.path.join(self.Base_path, "info", "encryption_key.key")
        self.load_or_download_key()

        self.strat = self.findChild(QPushButton, "questions")
        self.strat.clicked.connect(self.open_test_Window)
        
        self.Select_test_range = self.findChild(QPushButton, "Recode")
        self.Select_test_range.clicked.connect(self.open_record_window)
        
        self.Add_test_scope = self.findChild(QPushButton, "Addition")
        self.Add_test_scope.clicked.connect(self.open_uploading_window)
        
        self.vocabulary_book = self.findChild(QPushButton, "note")
        self.vocabulary_book.clicked.connect(self.open_daylist_window)
        
        self.end = self.findChild(QPushButton, "closed")
        self.end.clicked.connect(self.close_windows)

    def download_key_file(self):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        
        try:
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)
            session.cwd("/html/word_test_project/key/")

            with open(self.key_path, "wb") as keyfile:
                session.encoding = "utf-8"
                session.retrbinary(
                    "RETR " + os.path.basename(self.key_path),
                    keyfile.write,
                )
            print(f"키 파일 다운로드 완료: {os.path.basename(self.key_path)}")

        except ftplib.all_errors as e:
            print(f"키 파일 다운로드 중 오류가 발생했습니다: {str(e)}")
        finally:
            session.quit()

    def load_or_download_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            self.download_key_file()
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
            
    def open_test_Window(self):
        if self.select_window is None or not self.select_window.isVisible(): 
            self.select_window = Subject_select_window(self,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path) 
            self.hide()
            self.select_window.show()

    def open_record_window(self):
        if self.record_Window is None or not self.record_Window.isVisible(): 
            self.record_Window = record_Window(self,self.Workbook_path,self.Exam_record_path,self.Exam_bring,self.Base_path)
            self.hide()
            self.record_Window.show()

    def open_daylist_window(self):
        if self.daylist_window is None or not self.daylist_window.isVisible(): 
            self.daylist_window = daylist_window(self)
            self.hide()
            self.daylist_window.show()

    def open_uploading_window(self):
        if self.uploading_window is None or not self.uploading_window.isVisible(): 
            self.uploading_window = uploading_window(self,self.Base_path)
            self.hide()
            self.uploading_window.show()
            
    def close_windows(self):
        print(self.Workbook_path)
        self.close()            

    def closeEvent(self, event):
        pass

app = QApplication(sys.argv)

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
