import sys
import math
import os
import time

from UI_show.UI.Main_window_ui import Ui_Form
from UI_show.test_window import test_Window
from UI_show.daylist_window import daylist_window
from UI_show.record_window import record_Window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    
)
# pyside6-designer
#pyside6-uic main.ui -o Main_window_ui.py
#pyside6-uic record.ui -o record_window_ui.py
#pyside6-uic daylist.ui -o daylist_window_ui.py
#pyside6-uic wordlist.ui -o wordlist_ui.py
#cd word_test_project/UI_save
class Main_Windows(QMainWindow, Ui_Form):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        self.path = os.getcwd() +"/save_record/d2_exam"
        # Initialize variables and connect signals to slots
        self.test_Window = None
        self.daylist_window = None
        self.record_Window = None

        self.strat = self.findChild(QPushButton, "questions")
        self.strat.clicked.connect(self.open_test_Window)
        
        self.Select_test_range = self.findChild(QPushButton, "Recode")
        self.Select_test_range.clicked.connect(self.open_record_window)
        
        self.Add_test_scope = self.findChild(QPushButton, "Addition")
        #self.Add_test_scope.clicked.connect(self.close_windows)
        
        self.vocabulary_book = self.findChild(QPushButton, "note")
        self.vocabulary_book.clicked.connect(self.open_daylist_window)
        
        self.end = self.findChild(QPushButton, "closed")
        self.end.clicked.connect(self.close_windows)

    def open_test_Window(self):
        if self.test_Window is None or not self.test_Window.isVisible(): 
            self.test_Window = test_Window() 
            self.test_Window.show()
    
    def open_daylist_window(self):
        if self.daylist_window is None or not self.daylist_window.isVisible(): 
            self.daylist_window = daylist_window() 
            self.daylist_window.show()

    def close_windows(self):
        self.close()
    
    def open_record_window(self):
        if self.record_Window is None or not self.record_Window.isVisible(): 
            self.record_Window = record_Window(self.path)
            self.record_Window.show()

app = QApplication(sys.argv)

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
