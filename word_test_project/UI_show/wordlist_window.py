import json
import os
from cryptography.fernet import Fernet
from UI_show.UI.wordlist_ui import Ui_wordlist_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
)
class wordlist_window(QMainWindow, Ui_wordlist_windows):
    def __init__(self, parent=None, day=None,Base_path = None):
        super(wordlist_window, self).__init__(parent)
        self.setupUi(self)
        self.Base_path = Base_path
        self.day = day
        self.setWindowTitle(f"Wordlist for {day}")
        self.word_Widgets = []
        self.Meaning_Widgets = []

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

        self.change_Subject(self.day)

    def load_or_generate_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            return key
   
    def encrypt_meaning(self, meaning):
        return self.cipher_suite.encrypt(meaning.encode('utf-8')).decode('utf-8')
    
    def decrypt_meaning(self, encrypted_meaning):
        return self.cipher_suite.decrypt(encrypted_meaning.encode('utf-8')).decode('utf-8')

    def change_Subject(self, day):
        self.setWindowTitle(f"Workbook for {day}")
        try:
            Workbook_path = os.path.join(self.Base_path, "Workbook", f"{day}.json")
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