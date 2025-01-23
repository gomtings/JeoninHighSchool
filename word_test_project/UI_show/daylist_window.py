import os
import sys
from UI_show.UI.daylist_window_ui import Ui_Select_Day
from UI_show.wordlist_window import wordlist_window


from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton
)

class daylist_window(QMainWindow,Ui_Select_Day):
    def __init__(self,parents,Base_path):
        super(daylist_window, self).__init__()
        self.setupUi(self)
        self.parents = parents
        self.Base_path = Base_path
        # Initialize variables and connect signals to slots
        self.Wordlist = None
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        # Initialize buttons and connect signals
        for day in range(1, 9):
            day_button = self.findChild(QPushButton, f"Day{day}")
            if day_button:
                day_button.clicked.connect(lambda checked, d=day: self.Day_wordlist(f"Day{d}"))


    def Day_wordlist(self, day):
        if not self.Wordlist or not self.Wordlist.isVisible():
            self.Wordlist = wordlist_window(self, day,self.Base_path)
            self.Wordlist.show()
    
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