from UI_show.UI.membership_ui import Ui_MembershipWindow
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QMessageBox
)
from UI_show.test_window import test_Window
class membership_window(QMainWindow,Ui_MembershipWindow):
    def __init__(self,parents,Exam_record_path,Wrong_list_path,Workbook_path,Base_path,callback=None):
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
        self.callback = callback # 콜백 함수 추가
        self.membership = False
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
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/insert_id.php', data=post)
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        result = response.json()
        if result['result'] == 'success':
            self.membership = True
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("회원가입 성공!")
            msg_box.setText(f"{name} 의 계정이 성공적으로 생성되었습니다.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            # 창 닫기...
            self.close()

    def closeEvent(self, event):
        if self.callback:
            self.callback(self.membership)  # 닫힐 때 콜백 함수 호출 및 값 전달
        self.parents.show()
        event.accept()