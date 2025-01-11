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
from UI_show.login_window import LoginWindow
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
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
#cd UI_save

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
        self.login_window = None

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

        self.login = self.findChild(QPushButton, "login_btn")
        self.login.clicked.connect(self.login_windows)

        self.info = self.findChild(QLabel, "info")


        self.download_Workbook()
    
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
            print(f"키 파일  다운로드 완료: {os.path.basename(self.key_path)}")

        except ftplib.all_errors as e:
            print(f"키 파일  다운로드 중 오류가 발생했습니다: {str(e)}")
        finally:
            session.quit()

    def download_Workbook(self):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        
        try:
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)
            session.cwd("/html/word_test_project/Workbook/")

            # 서버 버전 파일을 가져옴
            server_version = []
            session.retrlines("RETR version.txt", server_version.append)
            server_version = ''.join(server_version).strip()

            # 로컬 버전 파일 읽기
            local_version_path = os.path.join(self.Workbook_path, "version.txt")
            if os.path.exists(local_version_path):
                with open(local_version_path, "r") as f:
                    local_version = f.read().strip()
            else:
                local_version = ""

            # 버전 비교
            if server_version != local_version:
                print("새로운 버전이 감지되었습니다. 파일을 다운로드합니다...")
                files = session.nlst()  # 현재 디렉토리의 모든 파일 목록을 가져옴
                
                for file_name in files:
                    local_path = os.path.join(self.Workbook_path, file_name)
                    with open(local_path, "wb") as keyfile:
                        session.encoding = "utf-8"
                        session.retrbinary("RETR " + file_name, keyfile.write)
                    print(f"문제집 다운로드 완료: {file_name}")
                
                # 새로운 버전을 로컬에 저장
                with open(local_version_path, "w") as f:
                    f.write(server_version)
            else:
                print("새로운 버전이 감지되지 않았습니다. 파일을 다운로드할 필요가 없습니다.")

        except ftplib.all_errors as e:
            print(f"문제집 다운로드 중 오류가 발생했습니다: {str(e)}")
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
            self.select_window = Subject_select_window(self,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path,self.Base_path) 
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

    def login_windows(self):
        if self.login_window is None or not self.login_window.isVisible(): 
            self.login_window = LoginWindow(self,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path,self.Base_path) 
            self.hide()
            self.login_window.show()

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
