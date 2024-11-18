from UI_show.UI.Subject_select_ui import Ui_Subject
from UI_show.test_window import test_Window
import os
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QComboBox
)
class Subject_select_window(QMainWindow,Ui_Subject):
    def __init__(self,parents,Exam_record_path,Wrong_list_path,Workbook_path):
        super(Subject_select_window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("시험과목선택")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Exam_record_path = Exam_record_path
        self.Wrong_list_path = Wrong_list_path
        self.Workbook_path = Workbook_path
        self.select_day = "DAY1"
        self.test_Window = None
        self.start_exam = self.findChild(QPushButton,"start_exam")
        self.start_exam.clicked.connect(self.open_test_Window)
        
        self.Subject_select = self.findChild(QComboBox,"Subject_select")
        self.Subject_select.currentTextChanged.connect(self.update_button_text)

    def update_button_text(self, text):
        self.select_day = text
        Title = f"{self.select_day} 시험 보기"
        self.start_exam.setText(Title)

    def open_test_Window(self):
        if self.test_Window is None or not self.test_Window.isVisible():
            self.hide()
            self.test_Window = test_Window(self,self.select_day,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path) 
            self.test_Window.show()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()