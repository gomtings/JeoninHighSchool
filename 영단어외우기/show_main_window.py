import sys
import math
import os
import time
from Main_window import Ui_Form
import test_window
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton
)
class Main_Windows(QMainWindow, Ui_Form):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("영단어외우기")
        
        # Initialize variables and connect signals to slots
        self.test_Window = None
        
        self.strat = self.findChild(QPushButton, "questions")
        self.strat.clicked.connect(self.strat_connect)
        
        self.Select_test_range = self.findChild(QPushButton, "Select_Range")
        self.Select_test_range.clicked.connect(self.close_windows)
        
        self.Add_test_scope = self.findChild(QPushButton, "Addition")
        self.Add_test_scope.clicked.connect(self.close_windows)
        
        self.vocabulary_book = self.findChild(QPushButton, "note")
        self.vocabulary_book.clicked.connect(self.close_windows)
        
        self.end = self.findChild(QPushButton, "closed")
        self.end.clicked.connect(self.close_windows)

    def strat_connect(self):
        if self.test_Window is None or not self.test_Window.isVisible(): 
            self.test_Window = test_window.test_Window() 
            self.test_Window.show()

    def close_windows(self):
        self.close()




app = QApplication(sys.argv)

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
