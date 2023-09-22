import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont
from bell import bell_window
import random
form_class = uic.loadUiType("pushbuttonTest.ui")[0]
form_class2 = uic.loadUiType("complet.ui")[0]
table_text = None
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
        global table_text
        print("확인되었습니다")
        table_text =self.plainTextEdit.toPlainText()
        self.hide()
        self.loding = Ui_MainWindow()
        self.loding.show()
        self.loding.edit_text(table_text)
        #self.second = second_window()
        #self.second.show()
        #self.second.edit_text(a)

    def show_main_window(self):
        self.second.deleteLater()
        self.show()

class Ui_MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.text_label.mousePressEvent = self.next_window
    def setupUi(self):
        self.setWindowTitle('LineEdit')
        self.resize(811, 480)
        self.setStyleSheet("background-color: black;")
        self.text_label = QLabel(self)
        self.text_label.move(70, 160)
        self.text_label.resize(691,111)
        font = QFont("궁서", 40)
        self.text_label.setStyleSheet("color: white;")
        self.text_label.setFont(font)
        self.text_label.setText('Hello world')
        self.show()

    def edit_text(self,text):
        self.text_label.setText(f"{text}번 테이블로 서빙중입니다") # label에 text 설정하기
        self.table_num = text
    def next_window(self,event):
        self.arrive = arrive_window()
        #self.arrive.backup_table_num(self.table_num)
        self.arrive.show()

class arrive_window(QMainWindow,form_class2):
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
        global table_text
        self.bell = bell_window()
        self.bell.edit_text(table_text)
        self.bell.show()
    #def backup_table_num(self,n):
    #    self.n = n

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()