import sys
import typing
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QFont
#from bell import bell_window

form_class = uic.loadUiType("oder\order.ui")[0]
class oder(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label:QLabel
    def edit_text(self,text):
        self.label.setText(f"{text}번 테이블 호출")


if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = oder()
    ui.show()
    app.exec_()
    sys.exit(app.exec_())