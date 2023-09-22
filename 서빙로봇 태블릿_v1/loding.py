import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont
from arrive import arrive_window
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
        self.arrive.backup_table_num(self.table_num)
        self.arrive.show()

if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()

    sys.exit(app.exec_())