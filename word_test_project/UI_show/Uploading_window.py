import ftplib
import json
import os
from datetime import datetime
from cryptography.fernet import Fernet
from UI_show.UI.Uploading_ui import Ui_uploading_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QPushButton,
    QComboBox
)
class uploading_window(QMainWindow, Ui_uploading_windows):
    def __init__(self, parent=None, Base_path=None,version = None):
        super(uploading_window, self).__init__(parent)
        self.setupUi(self)
        self.day = 'DAY1'
        self.Base_path = Base_path
        self.Workbook = None
        self.parents = parent
        self.version = version
        self.seconds = 600
        self.setWindowTitle(f"uploading for {self.day}")

        # 키 파일 경로 정의
        self.key_path = os.path.join(self.Base_path, "info", "encryption_key.key")
        self.key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

        # FTP 정보 로드
        try:
            FTP_path = os.path.join(self.Base_path, "info", "Report_FTP.json")
            with open(FTP_path, "r", encoding="UTF-8") as f:
                self.report_dist = json.load(f)
        except Exception as e:
            print(f'FTP.json 데이터가 없습니다. {e}')
        
        self.initialize_ui_elements()
        self.change_Subject('DAY1')
    
    def load_or_generate_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            return key

    def initialize_ui_elements(self):
        self.word_Widgets = []
        self.Meaning_Widgets = []
        
        self.uploading = self.findChild(QPushButton, "upload")
        self.uploading.clicked.connect(self.upload_report)

        self.Subject_select = self.findChild(QComboBox, "Subject_select")
        self.Subject_select.currentTextChanged.connect(self.change_Subject)
        
        self.timeout = self.findChild(QComboBox, "timeout")
        self.timeout.currentTextChanged.connect(self.change_Time)

        for i in range(1, 41): 
            text_edit_word = self.findChild(QLineEdit, f"Word_{i}") 
            text_edit_meaning = self.findChild(QLineEdit, f"Meaning_{i}")

            if text_edit_word: 
                self.word_Widgets.append(text_edit_word) 
            else: 
                print(f"Warning: QLineEdit Word_{i} not found")

            if text_edit_meaning:
                self.Meaning_Widgets.append(text_edit_meaning)
            else:
                print(f"Warning: QLineEdit Meaning_{i} not found")

    def encrypt_meaning(self, meaning):
        return self.cipher_suite.encrypt(meaning.encode('utf-8')).decode('utf-8')
    
    def decrypt_meaning(self, encrypted_meaning):
        return self.cipher_suite.decrypt(encrypted_meaning.encode('utf-8')).decode('utf-8')

    def change_Time(self, text):
        current_text = self.timeout.currentText()
        minutes = int(current_text.strip('분'))
        
        # 분을 초로 변환
        self.seconds = minutes * 60
       
    def change_Subject(self, text):
        self.day = text
        self.setWindowTitle(f"uploading for {self.day}")
        try:
            Workbook_path = os.path.join(self.Base_path, "Workbook", f"{self.day}.json")
            with open(Workbook_path, "r", encoding="UTF-8") as f:
                self.Workbook = json.load(f)

            word_data = self.Workbook.get("word_data", [])
            timeout = self.Workbook.get("timeout", 0)
            # 데이터의 길이가 위젯 수와 같지 않은 경우 빈 데이터로 채우기
            if len(word_data) < len(self.word_Widgets):
                for i in range(len(word_data), len(self.word_Widgets)):
                    word_data.append({"word": "", "meaning": [""]})

            for i in range(len(self.word_Widgets)):
                word = word_data[i]["word"]
                encrypted_meanings = word_data[i]["meaning"]
                meanings = []
                for meaning in encrypted_meanings:
                    try:
                        # 암호화된 경우
                        meanings.append(self.decrypt_meaning(meaning))
                    except Exception:
                        # 암호화되지 않은 경우
                        meanings.append(meaning)
                self.word_Widgets[i].setText(word)
                self.Meaning_Widgets[i].setText(", ".join(meanings))
                
            print(f"워크북 데이터가 로드되었습니다: {Workbook_path}")
        except FileNotFoundError:
            print(f'Workbook 파일을 찾을 수 없습니다: {Workbook_path}')
        except json.JSONDecodeError:
            print(f'JSON 디코딩 오류가 발생했습니다: {Workbook_path}')
        except IndexError as e:
            print(f'Workbook 데이터를 로드하는 중 오류가 발생했습니다: {e}')
        except Exception as e:
            print(f'워크북 데이터를 로드하는 중 예상치 못한 오류가 발생했습니다: {e}')

    def upload_report(self):
        try:
            data = []
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M")
            Workbook_path = os.path.join(self.Base_path, "Workbook", f"{self.day}.json")
            version_path = os.path.join(self.Base_path, "Workbook", "version.txt")
            for i in range(len(self.word_Widgets)):
                word = self.word_Widgets[i].text()
                meanings = self.Meaning_Widgets[i].text().split(", ")
                encrypted_meanings = [self.encrypt_meaning(meaning) for meaning in meanings]
                data.append({"word": word, "meaning": encrypted_meanings})
            
            # timeout 데이터 추가
            final_data = {"word_data": data}
            final_data["timeout"] = self.seconds
            
            with open(Workbook_path, 'w', encoding='utf-8') as file:
                json.dump(final_data, file, ensure_ascii=False, indent=4)
            self.version = f"{formatted_time}"
            
            with open(version_path, 'w', encoding='utf-8') as file:
                file.write(self.version)
            
            print(f"데이터가 파일에 저장되었습니다: {Workbook_path}")
        except Exception as e:
            print(f"파일 저장 중 오류가 발생했습니다: {str(e)}")

        # encryption_key.key 파일 경로
        key_path = os.path.join(self.Base_path, "info", "encryption_key.key")

        # 두 파일을 함께 업로드 (문제 파일 경로 리스트와 키 파일 경로를 함께 전달)
        self.upload_to_ftp([Workbook_path,version_path], key_path)

    def upload_to_ftp(self, file_paths, key_file_path):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        try:
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)
            
            # 문제 파일 업로드
            session.cwd("/html/word_test_project/Workbook/")
            for file_path in file_paths:
                file_size = os.path.getsize(file_path)
                uploaded_size = 0

                def handle_binary(more_data):
                    nonlocal uploaded_size
                    uploaded_size += len(more_data)
                    progress = int((uploaded_size / file_size) * 100)
                    print(f"Progress: {progress}%")

                with open(file_path, "rb") as uploadfile:
                    session.encoding = "utf-8"
                    session.storbinary(
                        "STOR " + os.path.basename(file_path),
                        uploadfile,
                        callback=handle_binary,
                    )
                print(f"업로드 완료: {os.path.basename(file_path)}")

            # 키 파일 업로드 (서버에 키 파일이 없는 경우에만)
            session.cwd("/html/word_test_project/key/")
            if os.path.basename(key_file_path) not in session.nlst():
                file_size = os.path.getsize(key_file_path)
                uploaded_size = 0

                with open(key_file_path, "rb") as keyfile:
                    session.encoding = "utf-8"
                    session.storbinary(
                        "STOR " + os.path.basename(key_file_path),
                        keyfile,
                        callback=handle_binary,
                    )
                print(f"키 파일 업로드 완료: {os.path.basename(key_file_path)}")
            else:
                print(f"키 파일이 이미 서버에 존재합니다: {os.path.basename(key_file_path)}")

        except ftplib.all_errors as e:
            print(f"업로드 중 오류가 발생했습니다: {str(e)}")
        finally:
            session.quit()

    def closeEvent(self, event):
        self.parents.show()
        self.parents.update_version(self.version)
        event.accept()

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