import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont
import time
import random
from bell import bell_window
form_class = uic.loadUiType("complet.ui")[0]

class arrive_window(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.oder = random.randrange(1,4)
        self.btn_1:QPushButton
        self.btn_2:QPushButton
        self.btn_3:QPushButton
        self.btn_4:QPushButton
        self.label_4:QLabel
        self.label_4.setText(f"{self.oder}번")
        self.label_2:QLabel
        self.btn_1.clicked.connect(lambda:self.buttonFunction(1))
        self.btn_2.clicked.connect(lambda:self.buttonFunction(2))
        self.btn_3.clicked.connect(lambda:self.buttonFunction(3))
        self.btn_4.clicked.connect(self.bell)
    #def setupUi(self):
        #self.setWindowTitle('LineEdit')
        #self.text_label = QLabel(self)
        #self.text_label.move(460, 180)   
        #self.text_label.resize(141,71)
        #font = QFont("궁서", 20)
        #self.text_label.setStyleSheet("color: white;")
        #self.text_label.setFont(font)
        #self.text_label.setText('n번 칸에서 ')
        #self.btn_1 = QPushButton(self)
        #self.btn_2 = QPushButton(self)
        #self.btn_3 = QPushButton(self)
        #self.show()

    def buttonFunction(self,num):
        print(self.oder)
        print(num)
        if(self.oder == num):
            self.label_4.hide
            self.label_2.setText("감사합니다")
        else:
            self.label_4.hide
            self.label_2.setText("거기는 꺼내는 곳이 아니얏❤")
    def bell(self):
        self.bell = bell_window()
        self.bell.edit_text(self.n)
        self.bell.show()
    def backup_table_num(self,n):
        self.n = n
if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = arrive_window()
    ui.show()
    app.exec_()
    sys.exit(app.exec_())