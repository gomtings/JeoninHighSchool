from UI_show.UI.Select_Type_Window_ui import Ui_Select_Type_Window
from UI_show.Create_question_window import Create_question_window as Type1
from UI_show.Create_question_window_2 import Create_question_window_2 as Type2
import json
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox
)
from PySide6.QtGui import QColor

class Select_Type_Window(QMainWindow, Ui_Select_Type_Window):
    def __init__(self,parent=None,Base_path=None):  # init 공부하기
        super(Select_Type_Window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.Base_path = Base_path
        self.Workbook_path = os.path.join(self.Base_path, "Workbook")
        self.Create_question_window1 = None
        self.Create_question_window2 = None
        self.num = 0
        self.setWindowTitle("출제 유형 선택")
        self.SelectInfo = self.findChild(QLabel, "SelectInfo")
        self.BookBox = self.findChild(QComboBox, "BookBox")
        for i in range(1,88):
            book = f"{i}권"
            self.BookBox.addItem(book)
        self.BookBox.currentIndexChanged.connect(self.on_selection_change)
        self.SelectTypeBox = self.findChild(QComboBox, "SelectTypeBox")
        self.SelectTypeBox.currentIndexChanged.connect(self.on_selection_change)
        self.submitbtn = self.findChild(QPushButton, "submitbtn")
        self.submitbtn.clicked.connect(self.open_Windows)
        self.on_selection_change(0)

    def open_Windows(self):
        type = self.SelectTypeBox.currentText()
        book = self.BookBox.currentText()
        if type == "객관식":
            self.Create_question_window(book)
        else:
            self.Create_question_window_2(book)
    
    def get_questions_number(self,type):
        book = self.BookBox.currentText()
        settype = "Multiple" if type == "객관식" else "Subjective"
        count = 0  # 해당 유형의 파일 개수를 세기 위한 변수
        prefix = None
        save_directory = os.path.join(self.Workbook_path, book)
        if os.path.exists(save_directory):
            for file_name in os.listdir(save_directory):
                if file_name.endswith(".json"):  # JSON 파일만 읽기
                    count += 1  # settype과 일치하는 파일 개수 증가
        return count
    
    def on_selection_change(self,index):
        selected_value = self.SelectTypeBox.currentText()  # 선택된 텍스트 가져오기
        self.num = self.get_questions_number(selected_value) + 1
        print(self.num)
        self.SelectInfo.setText(f"{selected_value} 의 현재까지 출제된 문제는{self.num}개 입니다.")  


    def Create_question_window(self,book):
        if self.Create_question_window1 is None or not self.Create_question_window1.isVisible(): 
            self.Create_question_window1 = Type1(self,book,self.Base_path,self.num) 
            self.hide()
            self.Create_question_window1.show()

    def Create_question_window_2(self,book):
        if self.Create_question_window2 is None or not self.Create_question_window2.isVisible(): 
            self.Create_question_window2 = Type2(self,book,self.Base_path,self.num)
            self.hide()
            self.Create_question_window2.show()

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
