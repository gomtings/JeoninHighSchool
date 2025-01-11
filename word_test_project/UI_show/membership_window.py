from UI_show.UI.membership_ui import Ui_MembershipWindow
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit
)
from UI_show.test_window import test_Window
class membership_window(QMainWindow,Ui_MembershipWindow):
    def __init__(self,parents,Exam_record_path,Wrong_list_path,Workbook_path,Base_path):
        super(membership_window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("회원가입")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Exam_record_path = Exam_record_path
        self.Wrong_list_path = Wrong_list_path
        self.Workbook_path = Workbook_path
        self.select_day = "DAY1"
        self.test_Window = None
        self.Base_path = Base_path
        
        self.name = self.findChild(QLineEdit,"name") #  로그인
        self.stunum = self.findChild(QLineEdit,"stunum") #  로그인

        self.start_exam = self.findChild(QPushButton,"insert_info")
        self.start_exam.clicked.connect(self.open_test_Window)

    def update_button_text(self, text):
        self.select_day = text
        Title = f"{self.select_day} 시험 보기"
        self.start_exam.setText(Title)

    def open_test_Window(self):
        name = self.name.text()
        stunum = self.stunum.text()
        post = {'name': name, 'stunum': stunum}
        response = requests.post('http://tkddn4508.dothome.co.kr/math101/insert_data.php', data=post)

    def closeEvent(self, event):
        self.parents.show()
        event.accept()