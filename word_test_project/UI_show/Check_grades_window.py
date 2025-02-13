"""
문제 추가를 위한 FTP 접속 코드.
"""
import ftplib
import json
import os
from cryptography.fernet import Fernet
from UI_show.UI.Check_grades_ui import Ui_Check_grades_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)
class Check_grades_window(QMainWindow, Ui_Check_grades_windows):
    def __init__(self, parent=None,Base_path = None,path = None,DAY = None):
        super(Check_grades_window, self).__init__(parent)
        self.setupUi(self)
        self.path = path
        self.gradefile = None
        self.Base_path = Base_path
        self.parents = parent
        self.file_save = self.Base_path+"/Workbook/"+f"{DAY}.json"
        self.setWindowTitle(f"Check_grades")
        
        # 키 파일 경로 정의
        self.key_path = os.path.join(self.Base_path, "info", "encryption_key.key")
        self.key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

        # Initialize variables and connect signals to slots
        self.word_Widgets = []
        self.Meaning_Widgets = []
        self.My_Meaning = []
        
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                self.gradefile = json.load(file)
        except Exception as e:
            print(f"Error reading file: {e}")

        self.name = self.findChild(QLabel, "name")
        self.subject = self.findChild(QLabel, "subject") 
        self.correct = self.findChild(QLabel, "correct") 
        self.wrong = self.findChild(QLabel, "wrong")
        self.time = self.findChild(QLabel, "time") 

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

            text_edit = self.findChild(QLabel, f"My_answer_{i}") 
            if text_edit: 
                self.My_Meaning.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit My_answer__{i} not found")

        self.load_words_from_json(self.file_save,self.gradefile)   

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
        
    def load_words_from_json(self, file_save, gradefile):
        try:
            self.name.setText(gradefile["이름"])
            self.subject.setText(gradefile["과제"])
            self.correct.setText(str(gradefile["맞춘 갯수"]))
            self.wrong.setText(str(gradefile["틀린 갯수"]))
            ms = gradefile.get("시간", 0)
            if ms != 0:
                minutes = ms // 60
                seconds = ms % 60
                self.time.setText(f"{minutes}분 {seconds}초")
            else:
                self.time.setText("정보 없음")
            with open(file_save, 'r', encoding='utf-8') as file:
                self.words = json.load(file)
            
            word_data = self.words.get("word_data", [])
            correct = gradefile["정답"]
            wrong = gradefile["오답"]
            
            # 데이터와 위젯 리스트 크기를 비교하여 작은 크기까지만 처리
            for i in range(min(len(self.word_Widgets), len(word_data))):
                word = word_data[i]["word"]
                encrypted_meanings = word_data[i]["meaning"]
                meanings = [self.decrypt_meaning(meaning) for meaning in encrypted_meanings]  # 복호화
                meanings_str = ", ".join(meanings)  # 리스트를 문자열로 변환

                self.word_Widgets[i].setText(word)
                self.Meaning_Widgets[i].setText(meanings_str)  # 문자열을 설정

                # My_Meaning 텍스트 설정
                if word in correct:
                    meaning_text = correct
                elif word in wrong:
                    meaning_text = wrong
                else:
                    meaning_text = "안푼 문제"
                    
                self.My_Meaning[i].setText(meaning_text)

                # 일치하는 경우 텍스트 색상을 빨간색으로 설정
                if word in correct:
                    self.word_Widgets[i].setStyleSheet("color: blue;")
                    self.Meaning_Widgets[i].setStyleSheet("color: blue;")
                else:
                    self.word_Widgets[i].setStyleSheet("color: red;")
                    self.Meaning_Widgets[i].setStyleSheet("color: red;")
                    
        except FileNotFoundError:
            print(f"Error: The file {file_save} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    
    def closeEvent(self, event):
        self.parents.show()
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