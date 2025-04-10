import sys
import ftplib
import json
import os
import requests
from cryptography.fernet import Fernet
from UI_show.UI.Login_Window_ui import Ui_Login_Window
from UI_show.Admin_Menu_windows import Admin_Menu_windows
from UI_show.User_Menu_windows import User_Menu_windows
from UI_show.Sinup_window import Sinup_window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
    )

#pyside6-designer
#pyside6-uic Login_Window.ui -o Login_Window_ui.py
#pyside6-uic Menu_window.ui -o Menu_window_ui.py
#pyside6-uic Admin_Menu_window.ui -o Admin_Menu_window_ui.py
#pyside6-uic User_Menu_window.ui -o User_Menu_window_ui.py
#pyside6-uic Sinup_window.ui -o Sinup_window_ui.py
#pyside6-uic Create_question_window.ui -o Create_question_window_ui.py
#pyside6-uic Create_question_window_2.ui -o Create_question_window_2_ui.py
#pyside6-uic user_question_window.ui -o user_question_window_ui.py
#pyside6-uic user_question_window2.ui -o user_question_window2_ui.py
#cd UI_save

class Login_Windows(QMainWindow, Ui_Login_Window):
    def __init__(self):
        super(Login_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Math_Books Review Pre_Test_App")
        self.ver = "25-01-22.01"
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.Base_path = os.getcwd()
        self.key_path = os.path.join(self.Base_path, "info", "encryption_key.key")
        self.report_dist = None

        # FTP 정보 로드
        try:
            FTP_path = os.path.join(self.Base_path, "info", "Report_FTP.json")
            with open(FTP_path, "r", encoding="UTF-8") as f:
                self.report_dist = json.load(f)
        except Exception as e:
            print(f'FTP.json 데이터가 없습니다. {e}')

        # Initialize variables and connect signals to slots
        self.Admin_Menu_window = None
        self.User_Menu_window = None
        self.Sinup_window = None
        self.Successlogin = False
        self.admin = False
        self.Workbook_ver = None
        self.name = ""

        self.Edit_ID = self.findChild(QLineEdit, "Edit_ID") # 아이디
        self.Edit_Password = self.findChild(QLineEdit, "Edit_Password") # 비밀번호

        self.login = self.findChild(QPushButton, "login_Btn") # 로그인
        self.login.clicked.connect(self.login_windows)
        self.login.setStyleSheet(
            """
        QPushButton {background-color: #0090ff; color: black;}
        QPushButton:hover {background-color: #b0b0b0; color: black;}
        """
        )
        self.Sinup = self.findChild(QPushButton, "Sinup_Btn") # 회원가입
        self.Sinup.clicked.connect(self.Open_Sinup_window)
        self.Sinup.setStyleSheet(
            """
        QPushButton {background-color: #b0b0b0; color: black;}
        QPushButton:hover {background-color: #0090ff; color: black;}
        """
        )
        Workbook_path = os.path.join(self.Base_path, "Workbook")
        self.download_folder_from_ftp(Workbook_path)
    
    def login_windows(self):
        ID = self.Edit_ID.text()
        Password = self.Edit_Password.text()
        if ID or Password:
            post = {'name': ID, 'stunum': Password}
            response = requests.post('http://solimatics.dothome.co.kr/Math_Books Review Pre_Test_App/db/login.php', data=post)
            # 응답이 성공 메시지일 때 팝업 창 띄우기
            result = response.json()
            if result['result'] == 'success':
                self.name = result["name"]
                self.admin = False if result["admin"] == 0 else True
                self.Successlogin = True
                if self.admin:
                    self.Open_Admin_Menu_window()
                else:
                    self.Open_User_Menu_window()
                self.popupwindows("로그인 성공!","로그인 되었습니다.")
            else:
                self.popupwindows("로그인 실패!","아이디 또는 비밀번호 확인")
        else:
            self.popupwindows("경고","아이디 또는 비밀번호를 입력해 주세요!")


    def Open_Sinup_window(self):
        if self.Sinup_window is None or not self.Sinup_window.isVisible(): 
            self.Sinup_window = Sinup_window(self) 
            self.hide()
            self.Sinup_window.show()

    def Open_Admin_Menu_window(self):
        if self.Admin_Menu_window is None or not self.Admin_Menu_window.isVisible(): 
            self.Admin_Menu_window = Admin_Menu_windows(self,self.Base_path,self.name,self.Workbook_ver) 
            self.hide()
            self.Admin_Menu_window.show()

    def Open_User_Menu_window(self):
        if self.User_Menu_window is None or not self.User_Menu_window.isVisible(): 
            self.User_Menu_window = User_Menu_windows(self,self.Base_path,self.name,self.Workbook_ver) 
            self.hide()
            self.User_Menu_window.show()

    def close_windows(self):
        self.close()            

    def closeEvent(self, event):
        pass

    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def download_key_file(self):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        
        try:
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)
            session.cwd("/html/Math_Books Review Pre_Test_App/key/")

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

    def download_folder_from_ftp(self, local_folder):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        try:
            remote_folder = f"/html/Math_Books Review Pre_Test_App/Workbook"
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)

            # 📂 로컬 폴더가 없으면 생성
            if not os.path.exists(local_folder):
                os.makedirs(local_folder)

            def download_recursive(remote_path, local_path):
                try:
                    session.cwd(remote_path)  # FTP 서버에서 해당 폴더로 이동
                    items = session.nlst()  # 폴더 및 파일 목록 가져오기

                    for item in items:
                        remote_item_path = f"{remote_path}/{item}"
                        local_item_path = os.path.join(local_path, item)

                        try:
                            session.cwd(remote_item_path)  # 폴더인지 확인
                            if not os.path.exists(local_item_path):
                                os.makedirs(local_item_path)  # 로컬 폴더 생성
                            download_recursive(remote_item_path, local_item_path)  # 내부 파일/폴더 재귀 다운로드
                        except ftplib.error_perm:
                            with open(local_item_path, "wb") as local_file:
                                session.retrbinary(f"RETR {remote_item_path}", local_file.write)
                            print(f"✅ 다운로드 완료: {local_item_path}")

                except ftplib.error_perm as e:
                    print(f"⚠️ {remote_path} 접근 중 오류 발생: {str(e)}")

            download_recursive(remote_folder, local_folder)

        except ftplib.all_errors as e:
            print(f"⚠️ 다운로드 중 오류 발생: {str(e)}")
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
            
app = QApplication(sys.argv)

window = Login_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
