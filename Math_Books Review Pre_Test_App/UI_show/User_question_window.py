from UI_show.UI.user_question_window_ui import Ui_Create_question_window
import json
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
    QRadioButton,
    )
from PySide6.QtGui import QColor,QPixmap

class Create_question_window(QMainWindow, Ui_Create_question_window):
    def __init__(self,parent=None,file_path=None):  # init 공부하기
        super(Create_question_window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.file_path = os.path.join(os.getcwd(), "question_answer")
        self.Radio_Widgets = []
        self.Label_Widgets = []

        self.setWindowTitle("객관식 문제 출제")

        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as json_file:
            self.data = json.load(json_file)
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.exam = self.findChild(QLabel, "label_6")
        # print("Loaded JSON data:", self.data)
        
        for i in range(1, 6): 
            RadioBtn = self.findChild(QRadioButton, f"answer_{i}") 
            if RadioBtn: 
                self.Radio_Widgets.append(RadioBtn)
            else: 
                print(f"Warning: QRadioButton Word_{i} not found")
    
        for i in range(1, 6):
            Label = self.findChild(QLabel, f"answer_ex{i}") 
            if Label:
                self.Label_Widgets.append(Label) 
            else: 
                print(f"Warning: Label Word_{i} not found")
                
        self.show_image()


    
class Create_question_window(QMainWindow, Ui_Create_question_window):
    def __init__(self, parent=None, file_path=None):
        super(Create_question_window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.file_path = os.path.join(os.getcwd(), "question_answer")
        self.Radio_Widgets = []
        self.Label_Widgets = []
        
        self.setWindowTitle("객관식 문제 출제")

        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as json_file:
            self.data = json.load(json_file)
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.exam = self.findChild(QLabel, "label_6")
        print('ddd')
        # show_image 메서드 호출
        self.show_image()

    def show_image(self):
        print('---')
        image_path = self.data.get("image_path")
        selected_answer = self.data.get("selected_answer")
        entered_description = self.data.get("entered_description")
        print(entered_description)
        self.exam.setText(entered_description)
        if image_path and os.path.exists(image_path): 
            pixmap = QPixmap(image_path) 
            self.picture_view.setPixmap(pixmap)  
            self.picture_view.setScaledContents(True) 
            print(10)
        else:
            print(f"Error: Image file not found at {image_path}")

    
        
    def popupwindows(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("마스터 계정은 변경이 불가 합니다.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()
