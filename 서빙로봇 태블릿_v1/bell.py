import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont
import time
import random
form_class = uic.loadUiType("bell.ui")[0]

class bell_window(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.oder = random.randrange(1,4)
        self.btn_1:QPushButton
        self.btn_2:QPushButton
        self.btn_3:QPushButton
        self.btn_4:QPushButton
        self.label:QLabel




if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = bell_window()
    ui.show()
    app.exec_()
    sys.exit(app.exec_())