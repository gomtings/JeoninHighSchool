"""
문제 추가를 위한 FTP 접속 코드.
"""
import ftplib
from UI_show.UI.wordlist_ui import Ui_wordlist_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)
class add_question_window(QMainWindow, Ui_wordlist_windows):
    def __init__(self):
        super(add_question_window, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(f"add_question_window")
        
        """
        # Initialize variables and connect signals to slots
        self.word_Widgets = []
        self.Meaning_Widgets = []

        for i in range(1, 41): 
            text_edit = self.findChild(QLabel, f"Word_{i}") 
            if text_edit: 
                self.word_Widgets.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit Word_{i} not found")  
            text_edit = self.findChild(QLabel, f"Meaning_{i}") 
            if text_edit: 
                self.Meaning_Widgets.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit Meaning_{i} not found")  
        """
    
    def upload_files(self):
        SERVER_IP = self.ftp_dict["SERVER_IP"]
        PORT = self.ftp_dict["PORT"]
        username = self.ftp_dict["username"]
        password = self.ftp_dict["password"]
        session = ftplib.FTP()
        try:
            self.upload_state.setText(f"파일 업로드 시작")
            session.connect(SERVER_IP, PORT)
            session.login(username, password)
            # 원하는 디렉토리로 이동
            session.cwd("/html/OTA_TEST")
            # QListWidget에서 파일 경로 가져오기
            if self.update_file_list.count() > 0:
                for index in range(self.update_file_list.count()):
                    filepath = self.update_file_list.item(index).text()
                    file_size = os.path.getsize(filepath)
                    uploaded_size = 0

                    def handle_binary(more_data):
                        nonlocal uploaded_size
                        uploaded_size += len(more_data)
                        progress = int((uploaded_size / file_size) * 100)
                        self.upload_state.setText(f"파일 업로드 중: {progress}%")

                    with open(filepath, "rb") as uploadfile:
                        session.encoding = "utf-8"
                        session.storbinary(
                            "STOR " + os.path.basename(filepath),
                            uploadfile,
                            callback=handle_binary,
                        )
                session.quit()
                self.upload_state.setText("파일 업로드 완료")
            else:
                self.show_message("Not file update", "업데이트 할 파일이 없습니다.")

        except ftplib.all_errors as e:  # FTP 관련 모든 오류 처리
            self.upload_state.setText("파일 업로드 오류")
            self.log_msg += f"파일 업로드 중 오류 발생: {e} \n"
            self.show_message("Error", "파일 업로드 중 오류 발생")

        self.sw_update.setStyleSheet("background-color: #0088ff; color: white")
        self.sw_update.setEnabled(True)
        self.update_btn = True

    def download_file(self):
        SERVER_IP = self.ftp_dict["SERVER_IP"]
        PORT = self.ftp_dict["PORT"]
        username = self.ftp_dict["username"]
        password = self.ftp_dict["password"]
        session = ftplib.FTP()
        content = "알수 없음"
        try:
            session.connect(SERVER_IP, PORT)
            session.login(username, password)
            # 원하는 디렉토리로 이동
            session.cwd("/html/OTA_TEST")
            # 파일 다운로드
            filename = "latestInfo.txt"
            local_filename = os.path.join("./config/", filename)
            # 바이너리 모드로 전환
            session.voidcmd("TYPE I")
            # 파일 크기 가져오기
            file_size = session.size(filename)
            downloaded_size = 0

            def handle_binary(more_data):
                nonlocal downloaded_size
                downloaded_size += len(more_data)
                file.write(more_data)
                progress = int((downloaded_size / file_size) * 100)
                self.ver_value.setText(f"버전 정보 가져오는중: {progress}%")

            with open(local_filename, "wb") as file:
                session.retrbinary("RETR " + filename, handle_binary)

            session.quit()
            # self.ver_value.setText("파일 다운로드 완료")
            # 파일 내용 읽기
            with open(local_filename, "r", encoding="utf-8") as file:
                content = file.read()
            content = content.split(".")[0]
            if self.update_btn:
                self.upload_state.setText("대기중.....")
                self.update_btn = False
        except ftplib.all_errors as e:  # FTP 관련 모든 오류 처리
            self.log_msg += f"파일 다운로드 중 오류 발생: {e} \n"
            content = "알수 없음"
            self.ver_value.setText("파일 다운로드 중 오류 발생")
        return content
     
"""
app = QApplication(sys.argv)

window = test_Window()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
"""