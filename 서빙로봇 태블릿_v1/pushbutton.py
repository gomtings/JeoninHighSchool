import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from loding import Ui_MainWindow
from bell import bell_window
import time
#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("pushbuttonTest.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #버튼에 기능을 연결하는 코드
        self.btn_1.clicked.connect(self.button1Function)
        self.btn_2.clicked.connect(self.button2Function)
        self.btn_3.clicked.connect(self.button3Function)

    #btn_1이 눌리면 작동할 함수
    def button1Function(self) :
        print("btn_1 Clicked")

    #btn_2가 눌리면 작동할 함수
    def button2Function(self) :
        print("btn_2 Clicked")
    
    def button3Function(self) :
        print("확인되었습니다")
        a =self.plainTextEdit.toPlainText()
        self.hide()
        self.loding = Ui_MainWindow()
        self.loding.show()
        self.loding.edit_text(a)
        #self.second = second_window()
        #self.second.show()
        #self.second.edit_text(a)

    def show_main_window(self):
        self.second.deleteLater()
        self.show()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()