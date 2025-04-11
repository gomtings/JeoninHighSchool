import sys
import ftplib
import json
import os
import requests
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
)
from UI_show.UI.Login_Window_ui import Ui_Login_Window
from UI_show.Admin_Menu_windows import Admin_Menu_windows
from UI_show.User_Menu_windows import User_Menu_windows
from UI_show.Sinup_window import Sinup_window


class Login_Windows(QMainWindow, Ui_Login_Window):
    def __init__(self):
        super(Login_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Math_Books Review Pre_Test_App")
        self.ver = "25-01-22.01"
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

        # 상태 초기화
        self.Admin_Menu_window = None
        self.User_Menu_window = None
        self.Sinup_window = None
        self.Successlogin = False
        self.admin = False
        self.Workbook_ver = None
        self.name = ""

        # UI 요소 연결
        self.Edit_ID = self.findChild(QLineEdit, "Edit_ID")
        self.Edit_Password = self.findChild(QLineEdit, "Edit_Password")

        self.login = self.findChild(QPushButton, "login_Btn")
        self.login.clicked.connect(self.login_windows)
        self.login.setStyleSheet(
            """
            QPushButton {background-color: #0090ff; color: black;}
            QPushButton:hover {background-color: #b0b0b0; color: black;}
            """
        )

        self.Sinup = self.findChild(QPushButton, "Sinup_Btn")
        self.Sinup.clicked.connect(self.Open_Sinup_window)
        self.Sinup.setStyleSheet(
            """
            QPushButton {background-color: #b0b0b0; color: black;}
            QPushButton:hover {background-color: #0090ff; color: black;}
            """
        )

        # ✅ Workbook 폴더가 없거나 비어 있을 경우만 FTP에서 다운로드
        Workbook_path = os.path.join(self.Base_path, "Workbook")
        if not os.path.exists(Workbook_path) or not os.listdir(Workbook_path):
            self.download_folder_from_ftp(Workbook_path)

    def login_windows(self):
        ID = self.Edit_ID.text()
        Password = self.Edit_Password.text()
        if ID or Password:
            post = {'name': ID, 'stunum': Password}
            response = requests.post(
                'http://solimatics.dothome.co.kr/Math_Books Review Pre_Test_App/db/login.php',
                data=post
            )
            result = response.json()
            if result['result'] == 'success':
                self.name = result["name"]
                self.admin = result["admin"] != 0
                self.Successlogin = True
                if self.admin:
                    self.Open_Admin_Menu_window()
                else:
                    self.Open_User_Menu_window()
                self.popupwindows("로그인 성공!", "로그인 되었습니다.")
            else:
                self.popupwindows("로그인 실패!", "아이디 또는 비밀번호 확인")
        else:
            self.popupwindows("경고", "아이디 또는 비밀번호를 입력해 주세요!")

    def Open_Sinup_window(self):
        if self.Sinup_window is None or not self.Sinup_window.isVisible():
            self.Sinup_window = Sinup_window(self)
            self.hide()
            self.Sinup_window.show()

    def Open_Admin_Menu_window(self):
        if self.Admin_Menu_window is None or not self.Admin_Menu_window.isVisible():
            self.Admin_Menu_window = Admin_Menu_windows(
                self, self.Base_path, self.name, self.Workbook_ver)
            self.hide()
            self.Admin_Menu_window.show()

    def Open_User_Menu_window(self):
        if self.User_Menu_window is None or not self.User_Menu_window.isVisible():
            self.User_Menu_window = User_Menu_windows(
                self, self.Base_path, self.name, self.Workbook_ver)
            self.hide()
            self.User_Menu_window.show()

    def closeEvent(self, event):
        pass

    def popupwindows(self, title, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def download_folder_from_ftp(self, local_folder):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()

        try:
            remote_folder = "/html/Math_Books Review Pre_Test_App/Workbook"
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)

            if not os.path.exists(local_folder):
                os.makedirs(local_folder)

            def download_recursive(remote_path, local_path):
                try:
                    session.cwd(remote_path)
                    items = session.nlst()
                    for item in items:
                        remote_item_path = f"{remote_path}/{item}"
                        local_item_path = os.path.join(local_path, item)
                        try:
                            session.cwd(remote_item_path)
                            if not os.path.exists(local_item_path):
                                os.makedirs(local_item_path)
                            download_recursive(remote_item_path, local_item_path)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login_Windows()
    window.show()
    try:
        app_exec = app.exec
    except AttributeError:
        app_exec = app.exec_
    sys.exit(app_exec())
