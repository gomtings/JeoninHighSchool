import sys
import math
import os
import time
import json
import random
from UI_show.UI.test_window_ui import Ui_Form
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListWidget,
    QLineEdit,
    QLabel,
    QListWidgetItem
)

from datetime import datetime

#pyside6-designer
#pyside6-uic ele.ui -o ui_elee.py
from PySide6.QtCore import QTimer, QTime

class test_Window(QMainWindow, Ui_Form):
    def __init__(self):
        super(test_Window, self).__init__()  # QMainWindow의 __init__을 명시적으로 호출
        self.setupUi(self)  # Ui_Form의 UI 설정
        
        self.setWindowTitle("test_Window")  # 윈도우 제목 설정
        self.correct_answer = 0
        self.wrong_answer = 0
        self.time_out = self.findChild(QLabel, "Time_limit")
    
        # Initialize QTimer 
        self.timer = QTimer(self) 
        self.timer.timeout.connect(self.update_label) 
        self.timer.start(1000) # Update every 1 second
        # Initialize start time 
        self.start_time = QTime(0, 0, 0) # Start at 00:00:00
        # Set total duration (e.g., 10 minutes = 600 seconds) 
        self.total_duration = 600
        self.elapsed_time = 0

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
    def load_words_from_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.words = json.load(file)
            
            # Select 20 random words
            
            
            self.word_as=[]
            self.meaning_as=[]
            self.wor=self.words[0:20]
            self.chcek_list=[]
            random_words = random.sample(self.wor, 20)
            for i in range(20):
                self.chcek_list.append(random_words[i]['meaning'])
                self.word_as.append(random_words[i]['word'])
            
            random_words = random.sample(self.wor, 20)
            for i in range(20):
                self.meaning_as.append(random_words[i]['meaning'])
            # Add words to QListWidget

            for word in self.word_as:
                QListWidgetItem(word, self.En_word_1)
            for meaning in self.meaning_as:
                QListWidgetItem(meaning, self.meaning_ilst_1)
                
                

            

            
            # Set random_words as class variable for comparison
            self.random_words = random_words

        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
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
        day="임시"
        time_aim=f" {now.year}년  {now.month}월 {now.day} 일 {now.hour} 시  {now.minute} 분 {day}..\n"
        self.correct_answer = 0
        self.wrong_answer = 0

        with open("time_list.txt", 'a', encoding='utf-8') as file:
            file.write(time_aim)   
    # Get QTextEdit values

        
        text_values = [edit.text() for edit in self.word_answer]
        # Compare values
        for text, item, a in zip(text_values, self.chcek_list,self.word_as):
            if text == item:

                self.correct_answer += 1
                print(f"Matched: {text} == {a}")
            else:
                key = f"word{self.wrong_answer}"
                self.wrong_answer += 1
                Answer_check[key]=a

                print(f"Not Matched: {text} vs {item}")
                print(f"Matched: {item} == {a}")
        # Output results
        print(f"Correct Answers: {self.correct_answer}",text_values)
        print(f"Wrong Answers: {self.wrong_answer}")
    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        # Load words from JSON file
        self.load_words_from_json("d1_exam")
        



        

        # Output results
        #print(f"Correct Answers: {self.correct_answer}")
        #print(f"Wrong Answers: {self.wrong_answer}")



