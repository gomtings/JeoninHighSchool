from UI_show.UI.Create_question_window_ui import Ui_Create_question_window
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
from PySide6.QtGui import QColor

class Create_question_window(QMainWindow, Ui_Create_question_window):
    def __init__(self,parent=None,book=None):  # init 공부하기
        super(Create_question_window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.book = book
        self.Radio_Widgets = []
        self.Edit_Widgets = []

        self.setWindowTitle("객관식 문제 출제")
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.find_picture = self.findChild(QPushButton, "find_picture")
        self.submit_btn = self.findChild(QPushButton, "submit_btn")
        self.Edit_Description = self.findChild(QLineEdit, "Edit_Description")
        
        for i in range(1, 6): 
            RadioBtn = self.findChild(QRadioButton, f"answer_{i}") 
            if RadioBtn: 
                self.Radio_Widgets.append(RadioBtn) 
            else: 
                print(f"Warning: QRadioButton Word_{i} not found")
    
        for i in range(1, 6): 
            LineEdit = self.findChild(QLineEdit, f"answer_ex{i}") 
            if LineEdit:
                self.Edit_Widgets.append(LineEdit) 
            else: 
                print(f"Warning: QLineEdit Word_{i} not found")
                
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
