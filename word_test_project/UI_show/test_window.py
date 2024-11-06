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
    QTextEdit,
    QLabel,
    QListWidgetItem
)
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
            text_edit = self.findChild(QTextEdit, f"kr_answer_{i}") 
            if text_edit: 
                self.word_answer.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit kr_answer_{i} not found")        
        
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
        # Reset counters
        self.correct_answer = 0
        self.wrong_answer = 0

        # Get QTextEdit values
        text_values = [edit.toPlainText() for edit in self.word_answer]

        # Compare values
        for text, item in zip(text_values, self.random_words):
            if text == item["meaning"]:
                self.correct_answer += 1
            else:
                self.wrong_answer += 1
                print(f"Not Matched: {text} vs {item['meaning']}")

        # Output results
        print(f"Correct Answers: {self.correct_answer}")
        print(f"Wrong Answers: {self.wrong_answer}")

    def load_words_from_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                words = json.load(file)

            # Select 20 random words
            random_words = random.sample(words, 20)

            # Add words to QListWidget
            for item in random_words:
                QListWidgetItem(item["word"], self.En_word_1)
                QListWidgetItem(item["meaning"], self.meaning_ilst_1)

            # Set random_words as class variable for comparison
            self.random_words = random_words

        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        # Load words from JSON file
        self.load_words_from_json("d1_exam")


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