from UI_show.UI.login_window_ui import Ui_LoginWindow
import os
import requests
import json
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QMessageBox
)
from UI_show.membership_window import membership_window
class LoginWindow(QMainWindow,Ui_LoginWindow):
    def __init__(self,parents,Exam_record_path,Wrong_list_path,Workbook_path,Base_path):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("로그인")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Exam_record_path = Exam_record_path
        self.Wrong_list_path = Wrong_list_path
        self.Workbook_path = Workbook_path
        self.select_day = "DAY1"
        self.membershipwindow = None
        self.Base_path = Base_path
        self.logininfo = None

        self.name = self.findChild(QLineEdit,"name") #  로그인
        self.stunum = self.findChild(QLineEdit,"stunum") #  로그인

        self.start_exam = self.findChild(QPushButton,"login") #  로그인
        self.start_exam.clicked.connect(self.Login)

        self.start_exam = self.findChild(QPushButton,"insert_btn") # 회원가입
        self.start_exam.clicked.connect(self.membership_window)

    def Login(self):
        name = self.name.text()
        stunum = self.stunum.text()
        post = {'name': name, 'stunum': stunum}
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/login.php', data=post)
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        result = response.json()
        if result['result'] == 'success':
            version_path = os.path.join(self.Base_path, "info", "logininfo")
            with open(version_path, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            self.logininfo = result
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("로그인 성공!")
            msg_box.setText(f"{name} 로그인 되었습니다.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            # 창 닫기...
            self.close()
        else:
            pass
    
    def membership_callback(self, result):
        print("Membership Window Result:", result)
        # 여기서 콜백 값에 따른 추가 작업 수행 가능

    def membership_window(self):
        if self.membershipwindow is None or not self.membershipwindow.isVisible():
            self.hide()
            self.membershipwindow = membership_window(self,self.Exam_record_path,self.Wrong_list_path,self.Workbook_path,self.Base_path,self.membership_callback) 
            self.membershipwindow.show()

    def closeEvent(self, event):
        self.parents.show()
        self.parents.login_success()
        event.accept()