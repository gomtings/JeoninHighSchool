import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_second_window = uic.loadUiType("loding.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class second_window(QMainWindow, form_second_window) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.text_label = self.label
        self.widget = QLabel()
        self.widget.mousePressEvent = self.complete
        

    def complete(self,event):
        print("도착")
        return 1
    def edit_text(self,t):
        
        self.text_label.setText(t)

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = second_window() 
    myWindow.show()
    app.exec_()