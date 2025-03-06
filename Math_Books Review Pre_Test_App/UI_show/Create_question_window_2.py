from UI_show.UI.Create_question_window_2_ui import Ui_Create_question_window
import json
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QLineEdit,  # 새로운 창을 띄우기 위해 추가
    QTextEdit,  # 레이아웃을 위해 추가
    QMessageBox
)
from PySide6.QtGui import QColor

class Create_question_window_2(QMainWindow, Ui_Create_question_window):
    def __init__(self,parent=None,book=None):  # init 공부하기
        super(Create_question_window_2, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.book = book
        self.setWindowTitle("주관식 문제 출제")
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.find_picture = self.findChild(QPushButton, "find_picture")
        self.submit_btn = self.findChild(QPushButton, "submit_btn")
        self.Edit_Description = self.findChild(QLineEdit, "Edit_Description")
        self.correc_answer = self.findChild(QTextEdit, "correc_answer_Edit")

    
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
