import os
import sys
from project_main_ui import Ui_Select_Day
import wordlist_ui


from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton
)

class Main_Windows(QMainWindow,Ui_Select_Day):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Integrated_Control_System")

        self.Day1 = self.findChild(QPushButton, "Day1")
        self.Day1.clicked.connect(Day1_wordlist)
        self.Day2 = self.findChild(QPushButton, "Day2")
        self.Day2.clicked.connect(Day2_wordlist)
        self.Day3 = self.findChild(QPushButton, "Day3")
        self.Day3.clicked.connect(Day3_wordlist)
        self.Day4 = self.findChild(QPushButton, "Day4")
        self.Day4.clicked.connect(Day4_wordlist)
        self.Day5 = self.findChild(QPushButton, "Day5")
        self.Day5.clicked.connect(Day5_wordlist)
        self.Day6 = self.findChild(QPushButton, "Day6")
        self.Day6.clicked.connect(Day6_wordlist)
        self.Day7 = self.findChild(QPushButton, "Day7")
        self.Day7.clicked.connect(Day7_wordlist)
        self.Day8 = self.findChild(QPushButton, "Day8")
        self.Day8.clicked.connect(Day8_wordlist)


def Day1_wordlist(self):
        if not hasattr(self, "Day1_wordlist") or not self.Wordlist_d1.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()
def Day2_wordlist(self):
        if not hasattr(self, "Day2_wordlist") or not self.Wordlist_d2.isVisible():
            self.Wordlist_d2 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d2.show()
def Day3_wordlist(self):
        if not hasattr(self, "Day3_wordlist") or not self.Wordlist_d3.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()
def Day4_wordlist(self):
        if not hasattr(self, "Day4_wordlist") or not self.Wordlist_d4.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()                                    
def Day5_wordlist(self):
        if not hasattr(self, "Day5_wordlist") or not self.Wordlist_d5.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()
def Day6_wordlist(self):
        if not hasattr(self, "Day6_wordlist") or not self.Wordlist_d6.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()
def Day7_wordlist(self):
        if not hasattr(self, "Day7_wordlist") or not self.Wordlist_d7.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()
def Day8_wordlist(self):
        if not hasattr(self, "Day8_wordlist") or not self.Wordlist_d8.isVisible():
            self.Wordlist_d1 = wordlist_ui.wordlist_ui1(self)
            self.Wordlist_d1.show()


app = QApplication(sys.argv)
app.setStyle("Windowsvista")

window = Main_Windows()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())