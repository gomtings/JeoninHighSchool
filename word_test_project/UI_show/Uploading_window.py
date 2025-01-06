import ftplib
import json
import os
from UI_show.UI.Uploading_ui import Ui_uploading_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QComboBox
)
class uploading_window(QMainWindow, Ui_uploading_windows):
    def __init__(self, parent=None):
        super(uploading_window, self).__init__(parent)
        self.setupUi(self)
        self.day = 'DAY1'
        self.setWindowTitle(f"uploading for {self.day}")
        # Initialize other UI elements here if needed
        
        try:
            with open("info/Report_FTP.json", "r", encoding="UTF-8") as f:
                self.report_dist = json.load(f)
        except Exception as e:
            print(f'FTP.json 데이터가 없습니다.{e}')
        
        # Initialize variables and connect signals to slots
        self.word_Widgets = []
        self.Meaning_Widgets = []
        
        self.uploading = self.findChild(QPushButton, "upload")
        self.uploading.clicked.connect(self.upload_report)

        self.Subject_select = self.findChild(QComboBox, "Subject_select")
        self.Subject_select.currentTextChanged.connect(self.change_Subject)

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

    def change_Subject(self,text):
        self.setWindowTitle(f"uploading for {text}")
    
    def upload_report(self,file_paths, modes):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        try:
            session.connect(SERVER_IP, PORT)
            session.login(username, password)
            session.cwd("/html/Report/")
            for filepath, mode in zip(file_paths, modes):
                file_size = os.path.getsize(filepath)
                uploaded_size = 0
                def handle_binary(more_data):
                    nonlocal uploaded_size
                    uploaded_size += len(more_data)
                    progress = int((uploaded_size / file_size) * 100)
                    #print(f"Progress: {progress}%")

                with open(filepath, "rb") as uploadfile:
                    session.encoding = "utf-8"
                    session.storbinary(
                        "STOR " + os.path.basename(filepath),
                        uploadfile,
                        callback=handle_binary,
                    )
                print(f"업로드 완료")
        except ftplib.all_errors as e:  # FTP 관련 모든 오류 처리
            print(f"업로드 중 오류가 발생했습니다.")
        finally:
            session.quit()    
    
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