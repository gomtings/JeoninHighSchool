import sys
import math
import os
import time
import json
import random
from cryptography.fernet import Fernet
from UI_show.UI.test_window_ui import Ui_Form
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListWidget,
    QLineEdit,
    QLabel,
    QListWidgetItem,
    QMessageBox
)

from datetime import datetime

#pyside6-designer
#pyside6-uic ele.ui -o ui_elee.py
from PySide6.QtCore import QTimer, QTime

class test_Window(QMainWindow, Ui_Form):
    def __init__(self,parents,DAY,Exam_record_path,Wrong_list_path,Workbook_path,Base_path):
        super(test_Window, self).__init__()  # QMainWindow의 __init__을 명시적으로 호출
        self.setupUi(self)  # Ui_Form의 UI 설정

        self.Exam_record_path = Exam_record_path
        self.Wrong_list_path = Wrong_list_path
        self.Workbook_path = Workbook_path
        self.select_day = DAY
        self.file_save=f"{self.Workbook_path}{self.select_day}.json"
        self.Base_path  = Base_path
        self.parents = parents
        self.setWindowTitle(f"{self.select_day} 시험")  # 윈도우 제목 설정
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.correct_answer = 0
        self.wrong_answer = 0
        self.total_duration = 600
        self.elapsed_time = 0
        # Initialize QTimer
        self.timer = QTimer(self) 
        self.timer.timeout.connect(self.update_label) 
        self.timer.start(1000) # Update every 1 second
        # Initialize start time 
        self.start_time = QTime(0, 0, 0) # Start at 00:00:00
        # Set total duration (e.g., 10 minutes = 600 seconds) 

        # 키 파일 경로 정의
        self.key_path = os.path.join(self.Base_path, "info", "encryption_key.key")
        self.key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

        self.time_out = self.findChild(QLabel, "Time_limit")
        self.update_label()
        
        self.En_word_1 = self.findChild(QListWidget, "En_word_1")

        self.meaning_ilst_1 = self.findChild(QListWidget, "meaning_ilst_1")

        self.En_word_2 = self.findChild(QListWidget, "En_word_2")
    
        self.meaning_ilst_2 = self.findChild(QListWidget, "meaning_ilst_2")

        self.chk_answer = self.findChild(QPushButton,"pushButton")
        self.chk_answer.clicked.connect(self.compare_values)

        self.word_answer = []
        for i in range(1, 41): 
            text_edit = self.findChild(QLineEdit, f"kr_answer_{i}") 
            if text_edit: 
                self.word_answer.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit kr_answer_{i} not found")        
        
        # 문제 불러오기....
        self.load_words_from_json(self.file_save)

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

    def load_words_from_json(self, file_save):
        try:
            self.word_as = []
            self.meaning_as = []
            self.chcek_list = []
            self.words = {}
            with open(file_save, 'r', encoding='utf-8') as file:
                self.words = json.load(file)

            # 첫 번째 부분
            random_words = random.sample(self.words[0:25], min(25, len(self.words[0:25])))
            for word in random_words:
                for meaning in word['meaning']:  # meaning이 리스트이므로 각각을 추가
                    decrypted_meaning = self.decrypt_meaning(meaning)  # 복호화
                    self.chcek_list.append(decrypted_meaning)
                    self.meaning_as.append(decrypted_meaning)
                    QListWidgetItem(decrypted_meaning, self.meaning_ilst_1)
                self.word_as.append(word['word'])
                QListWidgetItem(word['word'], self.En_word_1)

            # 두 번째 부분
            random_words = random.sample(self.words[25:], min(25, len(self.words[25:])))
            for word in random_words:
                for meaning in word['meaning']:
                    decrypted_meaning = self.decrypt_meaning(meaning)  # 복호화
                    self.chcek_list.append(decrypted_meaning)
                    self.meaning_as.append(decrypted_meaning)
                    QListWidgetItem(decrypted_meaning, self.meaning_ilst_2)
                self.word_as.append(word['word'])
                QListWidgetItem(word['word'], self.En_word_2)

            # Add words to QListWidget
            #             
            # Set random_words as class variable for comparison
            self.random_words = random_words

        except FileNotFoundError:
            print(f"Error: The file {file_save} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def update_label(self):
        self.elapsed_time += 1
        remaining_time = self.total_duration - self.elapsed_time
        remaining_minutes = remaining_time // 60
        remaining_seconds = remaining_time % 60
        self.time_out.setText(f"{remaining_minutes:02}분 {remaining_seconds:02}초 남음")

        # Optionally, handle when time is up
        if remaining_time <= 0:
            self.timer.stop()
            self.time_out.setText("시간 종료")
            self.compare_values()

    def compare_values(self):
        Answer_check={}
        # Reset counters
        now = datetime.now()
        record_time = f"{now.year}{now.month}{now.day}{now.hour}_{now.minute}_{self.select_day}"
        self.correct_answer = 0
        self.wrong_answer = 0 
        
        rlacl=[]
        text_values = [edit.text() for edit in self.word_answer]
        # Compare values
        for text, item, a in zip(text_values, self.chcek_list,self.word_as):
            if text == item:
                rlacl.append(f"{text}와 {a}이 일치합니다. \n")
                self.correct_answer += 1
            else:
                rlacl.append(f"{text}와 {a}이 불일치합니다. \n ")
                self.wrong_answer += 1
                Answer_check[a]=text
        
        with open(self.Exam_record_path, 'a', encoding='utf-8') as file:
            time = record_time + "\n"
            file.write(time)
        
        list_path = self.Wrong_list_path + record_time +".json"
        with open(list_path, 'a', encoding='utf-8') as file:
           json.dump(Answer_check, file, indent=4)

        # 팝업 창 띄우기
        self.show_result_popup(self.correct_answer,self.wrong_answer)

        self.close() # 체점이 끋났다면 테스트 창을 종료 한다.
    
    def show_result_popup(self,correct,wrong):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Test Results")
        msg_box.setText(f"Correct Answers: {correct}\nWrong Answers: {wrong}")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def closeEvent(self, event):
        self.parents.show()
        event.accept()
        
        # Output results
        #print(f"Correct Answers: {self.correct_answer}")
        #print(f"Wrong Answers: {self.wrong_answer}")



