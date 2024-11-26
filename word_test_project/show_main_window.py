import sys
import math
import os
import time

from UI_show.UI.Main_window_ui import Ui_Form
from UI_show.record_window import record_Window
from UI_show.daylist_window import daylist_window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    
)
from UI_show.UI.Main_window_ui import Ui_Form
from UI_show.Subject_select_window import Subject_select_window
from UI_show.daylist_window import daylist_window
from UI_show.record_window import record_Window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,)
# pyside6-designer
#pyside6-uic main.ui -o Main_window_ui.py
#pyside6-uic Subject_select.ui -o Subject_select_ui.py
#pyside6-uic record.ui -o record_window_ui.py
#pyside6-uic daylist.ui -o daylist_window_ui.py
#pyside6-uic wordlist.ui -o wordlist_ui.py
#cd word_test_project/UI_save
class Main_Windows(QMainWindow, Ui_Form):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.Exam_record_path = os.getcwd() +"/Exam_test/Exam_record.txt"
        self.Wrong_list_path = os.getcwd() +"/Exam_test/"
        self.Workbook_path = os.getcwd() +"/Workbook/"

        self.select_window = None
        self.daylist_window = None
        self.record_Window = None

        self.strat = self.findChild(QPushButton, "questions")
        self.strat.clicked.connect(self.open_test_Window)
        
        self.Select_test_range = self.findChild(QPushButton, "Recode")
        self.Select_test_range.clicked.connect(self.open_record_window)
        
        self.Add_test_scope = self.findChild(QPushButton, "Addition")
        self.Add_test_scope.clicked.connect(self.close_windows)
        
        self.vocabulary_book = self.findChild(QPushButton, "note")
        self.vocabulary_book.clicked.connect(self.open_daylist_window)
        
        self.end = self.findChild(QPushButton, "closed")
        self.end.clicked.connect(self.close_windows)

    def open_test_Window(self):
        if self.select_window is None or not self.select_window.isVisible(): 
            self.select_window = Subject_select_window(self,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path) 
            self.hide()
            self.select_window.show()
    
    def open_daylist_window(self):
        if self.daylist_window is None or not self.daylist_window.isVisible(): 
            self.daylist_window = daylist_window(self)
            self.hide()
            self.daylist_window.show()
    
    def open_record_window(self):
        
        if self.record_Window is None or not self.record_Window.isVisible(): 
            self.record_Window = record_Window(self,self.Exam_record_path)
            self.hide()
            self.record_Window.show()

    def close_windows(self):
        print(self.Workbook_path)
        self.close()            

    def closeEvent(self, event):
        pass


app = QApplication(sys.argv)

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
