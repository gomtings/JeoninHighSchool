import sys
import typing
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget
#from oder.water import water
#from oder.dish import dish
#from oder.oder import oder
form_class = uic.loadUiType("bell.ui")[0]
form_class2 = uic.loadUiType("oder\water_select.ui")[0]
form_class3 = uic.loadUiType("oder\dish_select.ui")[0]
form_class4 = uic.loadUiType("oder\order2.ui")[0]
form_class5 = uic.loadUiType("oder\\thank.ui")[0]
t = None
class warter(QMainWindow,form_class2):
    def __init__(self):
        super().__init__()
        #self.ui = uic.loadUi("oder\water_select.ui",self)
        self.setupUi(self)
        self.label:QLabel
        self.label_2:QLabel
        self.label_3:QLabel
        self.label_4:QLabel
        self.spinBOx:QSpinBox
        #self.show()
        self.label_4.mousePressEvent = self.back
    def edit_text(self,text):
        self.label.setText(f"{text}번 테이블 호출")
    def back(self,event):
        self.hide()
        a = bell_window()
        a.show()
class dish(QMainWindow,form_class3):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label:QLabel
        self.label_2:QLabel
        self.label_3:QLabel
        self.label_4:QLabel
        self.spinBOx:QSpinBox
        self.label_4.mousePressEvent = self.back
    def edit_text(self,text):
        self.label.setText(f"{text}번 테이블 호출")
    def back(self,event):
        self.hide()
        a = bell_window()
        a.edit_text(t)
        a.show()
class oder(QMainWindow,form_class4):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label:QLabel
        self.pushButton_1:QPushButton
        self.pushButton_2:QPushButton
        self.pushButton_3:QPushButton
        self.pushButton_4:QPushButton
        self.pushButton_5:QPushButton
        self.pushButton_6:QPushButton
        self.pushButton_7:QPushButton
        self.pushButton_8:QPushButton
        self.pushButton_9:QPushButton
        self.pushButton_10:QPushButton
        self.pushButton_11:QPushButton
        self.pushButton_12:QPushButton
        self.pushButton_18:QPushButton
        self.pushButton_19:QPushButton
        self.pushButton_18.clicked.connect(lambda:self.back())
        self.pushButton_19.clicked.connect(lambda:self.back())

    def edit_text(self,text):
        self.label.setText(f"{text}번 테이블 호출")
    def back(self):
        self.hide()
        #a = bell_window()
        #a.edit_text(t)
        #a.show()
        b = thank()
        b.show()
class thank(QMainWindow,form_class5):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label:QLabel
        self.text_label.mousePressEvent = self.cilck
    def cilck(self,event):
        print("틍 아잇1!")
class bell_window(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_1:QPushButton
        self.btn_2:QPushButton
        self.btn_3:QPushButton
        self.btn_4:QPushButton
        self.label:QLabel
        self.btn_1.clicked.connect(lambda:self.buttonFunction(1))
        self.btn_2.clicked.connect(lambda:self.buttonFunction(2))
        self.btn_3.clicked.connect(lambda:self.buttonFunction(3))
        self.btn_4.clicked.connect(lambda:self.buttonFunction(4))
    def buttonFunction(self,n):
        global t
        if(n == 1):
            #self.ui = water()
            #self.ui.edit_text(self.t)
            #self.ui.show()
            self.ui = warter()
            self.ui.edit_text(t)
            self.ui.show()
        if(n == 2):
            #self.ui = dish()
            #self.ui.show()
            self.ui = dish()
            self.ui.edit_text(t)
            self.ui.show()
        if(n == 3):
            self.ui = oder()
            self.ui.edit_text(t)
            self.ui.show()
    def edit_text(self,text):
        global t
        self.label.setText(f"{text}번 테이블 호출")
        t = text
if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = bell_window()
    ui.show()
    app.exec_()
    #sys.exit(app.exec_())