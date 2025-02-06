from UI_show.UI.assignment_ui import Ui_assignment_window
import json
import os
import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QListWidget,
    QTextEdit,
    QDialog,  # 새로운 창을 띄우기 위해 추가
    QVBoxLayout,  # 레이아웃을 위해 추가
    QListWidgetItem,
    QMessageBox
)
from PySide6.QtGui import QColor

class Account_remove_Windows(QMainWindow, Ui_assignment_window):
    def __init__(self,parent=None):  # init 공부하기
        super(Account_remove_Windows, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.setWindowTitle("계정 삭제")
        self.listcliked = self.findChild(QListWidget, "Account_list")
        self.listcliked.itemDoubleClicked.connect(self.clicked_record_list)

        # 계정목록 가져오기...
        result = self.Get_account()
        self.Add_account_list(result)
    
    def Add_account_list(self, result):
        # 여기에 계정목록이 출력 됩니다. 
        pass

    def clicked_record_list(self, item):
        # 더블클릭시 해당 계정을 삭제 합니다.
        pass


    def Get_account(self):
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/Get_account.php')
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        return response.json()
    
    def Remove_account(self,name):
        post = {'name': name}
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/Remove_account.php', data=post)
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        return response.json()
    
    def popupwindows(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("마스터 계정은 제거 불가 합니다.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()
