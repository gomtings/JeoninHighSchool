from UI_show.UI.Sinup_window_ui import Ui_Sinup_window
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QMessageBox
)
class Sinup_window(QMainWindow,Ui_Sinup_window):
    def __init__(self,parents):
        super(Sinup_window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("회원가입")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Edit_ID = self.findChild(QLineEdit,"Edit_ID") #  로그인
        self.Edit_Password = self.findChild(QLineEdit,"Edit_Password") #  로그인

        self.sinup = self.findChild(QPushButton,"sinup")
        self.sinup.clicked.connect(self.join_db)
        self.sinup.setStyleSheet(
            """
        QPushButton {background-color: #0090ff; color: black;}
        QPushButton:hover {background-color: #b0b0b0; color: black;}
        """
        )
    
    def join_db(self):
        name = self.Edit_ID.text()
        stunum = self.Edit_Password.text()
        if name or stunum:
            post = {'name': name, 'stunum': stunum}
            response = requests.post('http://solimatics.dothome.co.kr/Math_Books Review Pre_Test_App/db/insert_id.php', data=post)
            result = response.json()
            if result['result'] == 'success':
                self.membership = True
                self.popupwindows("회원가입 성공!",f"{name} 의 계정이 성공적으로 생성되었습니다.")
                # 창 닫기...
                self.close()
        else:
            self.popupwindows("입력 오류!","아이디 혹은 비밀번호가 입력되지 않았습니다.")
    
    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()