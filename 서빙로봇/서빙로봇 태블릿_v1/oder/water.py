import sys
import typing
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QFont
#from bell import bell_window
form_class = uic.loadUiType("oder\water_select.ui")[0]
class water(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label:QLabel
        self.label2:QLabel
        self.label3:QLabel
        self.label4:QLabel
        self.spinBOx:QSpinBox
        #self.label4.mousePressEvent = 
    def edit_text(self,text):
        self.label.setText(f"{text}번 테이블 호출")

if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = water()
    ui.show()
    app.exec_()
    sys.exit(app.exec_())