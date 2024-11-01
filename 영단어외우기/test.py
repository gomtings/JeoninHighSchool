import sys
import math
import os
import time
from ui_elee import Ui_Form
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListWidget,
    QTextEdit
)

class test_Window(QMainWindow, Ui_Form):
    def __init__(self):
        super(test_Window, self).__init__()  # QMainWindow의 __init__을 명시적으로 호출
        self.setupUi(self)  # Ui_Form의 UI 설정
        self.setWindowTitle("test_Window")  # 윈도우 제목 설정
    
    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        random_selection = random.sample(words, 20)
        word=[]
        # 결과 출력
        print("선택된 20개 단어:")
        for word in random_selection:
        print(word) 

    def test(self):
        self.test_words = self.findChild(QListWidget, "listWidget_1")

        self.test_words = self.findChild(QListWidget, "listWidget_2")

        self.test_words = self.findChild(QListWidget, "listWidget_3")
        self.end.clicked.connect(self.closed)
    
        self.test_words = self.findChild(QListWidget, "listWidget_4")
    
        self.Korean_answer__1= self.findChild(QTextEdit,"Korean_answer_1")

        self.Korean_answer__2= self.findChild(QTextEdit,"Korean_answer_2")

        self.Korean_answer__3= self.findChild(QTextEdit,"Korean_answer_3")

        self.Korean_answer__4= self.findChild(QTextEdit,"Korean_answer_4")
        
        self.Korean_answer__5= self.findChild(QTextEdit,"Korean_answer_5")

        self.Korean_answer__6= self.findChild(QTextEdit,"Korean_answer_6")

        self.Korean_answer__7= self.findChild(QTextEdit,"Korean_answer_7")

        self.Korean_answer__8= self.findChild(QTextEdit,"Korean_answer_8")

        self.Korean_answer__9= self.findChild(QTextEdit,"Korean_answer_9")

        self.Korean_answer__10= self.findChild(QTextEdit,"Korean_answer_10")

        self.Korean_answer__11= self.findChild(QTextEdit,"Korean_answer_11")

        self.Korean_answer__12= self.findChild(QTextEdit,"Korean_answer_12")
        
        self.Korean_answer__13= self.findChild(QTextEdit,"Korean_answer_13")

        self.Korean_answer__14= self.findChild(QTextEdit,"Korean_answer_14")

        self.Korean_answer__15= self.findChild(QTextEdit,"Korean_answer_15")

        self.Korean_answer__16= self.findChild(QTextEdit,"Korean_answer_16")

        self.Korean_answer__17= self.findChild(QTextEdit,"Korean_answer_17")

        self.Korean_answer__18= self.findChild(QTextEdit,"Korean_answer_18")

        self.Korean_answer__19= self.findChild(QTextEdit,"Korean_answer_19")

        self.Korean_answer__20= self.findChild(QTextEdit,"Korean_answer_20")

        self.Korean_answer__21= self.findChild(QTextEdit,"Korean_answer_21")

        self.Korean_answer__22= self.findChild(QTextEdit,"Korean_answer_22")

        self.Korean_answer__23= self.findChild(QTextEdit,"Korean_answer_23")

        self.Korean_answer__24= self.findChild(QTextEdit,"Korean_answer_24")

        self.Korean_answer__25= self.findChild(QTextEdit,"Korean_answer_25")

        self.Korean_answer__26= self.findChild(QTextEdit,"Korean_answer_26")

        self.Korean_answer__27= self.findChild(QTextEdit,"Korean_answer_27")

        self.Korean_answer__28= self.findChild(QTextEdit,"Korean_answer_28")

        self.Korean_answer__29= self.findChild(QTextEdit,"Korean_answer_29")

        self.Korean_answer__30= self.findChild(QTextEdit,"Korean_answer_30")

        self.Korean_answer__31= self.findChild(QTextEdit,"Korean_answer_31")

        self.Korean_answer__32= self.findChild(QTextEdit,"Korean_answer_32")

        self.Korean_answer__33= self.findChild(QTextEdit,"Korean_answer_33")

        self.Korean_answer__34= self.findChild(QTextEdit,"Korean_answer_34")

        self.Korean_answer__35= self.findChild(QTextEdit,"Korean_answer_35")

        self.Korean_answer__36= self.findChild(QTextEdit,"Korean_answer_36")

        self.Korean_answer__37= self.findChild(QTextEdit,"Korean_answer_37")

        self.Korean_answer__38= self.findChild(QTextEdit,"Korean_answer_38")

        self.Korean_answer__39= self.findChild(QTextEdit,"Korean_answer_39")

        self.Korean_answer__40= self.findChild(QTextEdit,"Korean_answer_40")



"""
app = QApplication(sys.argv)

window = test_Window()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
"""