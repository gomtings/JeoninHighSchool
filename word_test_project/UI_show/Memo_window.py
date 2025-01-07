"""
문제 추가를 위한 FTP 접속 코드.
"""
import ftplib
import json
from UI_show.UI.wordlist_ui import Ui_wordlist_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)
class Memo_window(QMainWindow, Ui_wordlist_windows):
    def __init__(self, parent=None,Workbook_path = None,file_path = None,Range = None):
        super(Memo_window, self).__init__(parent)
        self.setupUi(self)
        self.Workbook_path = Workbook_path
        self.file_path = file_path
        self.Range = Range
        self.file_content = None
        self.file_save=f"{self.Workbook_path}{self.Range}"
        self.setWindowTitle(f"Memo_window")
        
        # Initialize variables and connect signals to slots
        self.word_Widgets = []
        self.Meaning_Widgets = []
        self.My_Meaning = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.file_content = json.load(file)
        except Exception as e:
            print(f"Error reading file: {e}")

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

        self.load_words_from_json(self.file_save,self.file_content)   
    
    def load_words_from_json(self, file_save,file_content):
        try:
            with open(file_save, 'r', encoding='utf-8') as file:
                self.words = json.load(file)
            # 데이터와 위젯 리스트 크기를 비교하여 작은 크기까지만 처리
            for i in range(min(len(self.word_Widgets), len(self.words))):
                word = self.words[i]["word"]
                meaning = self.words[i]["meaning"]
                self.word_Widgets[i].setText(word)
                self.Meaning_Widgets[i].setText(meaning)
                # My_Meaning 텍스트 설정
                meaning_text = file_content.get(word, "")
                if meaning_text == "" or meaning_text is None:
                    meaning_text = "안푼 문제"
                self.My_Meaning[i].setText(meaning_text)
                # 일치하는 경우 텍스트 색상을 빨간색으로 설정
                if word in file_content.keys():
                    self.word_Widgets[i].setStyleSheet("color: red;")
                    self.Meaning_Widgets[i].setStyleSheet("color: red;")
                else:
                    self.word_Widgets[i].setStyleSheet("color: blue;")
                    self.Meaning_Widgets[i].setStyleSheet("color: blue;")                    
        except FileNotFoundError:
            print(f"Error: The file {file_save} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
     
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