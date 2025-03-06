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
        try:
            self.listcliked.clear()  # 기존 항목 모두 제거
            # 'data' 키의 값들을 순회하며 'name' 값을 QListWidget에 추가
            for item in result['data']:
                name = item['name']
                admin = item['admin']
                if name:  # name 값이 비어있지 않은 경우에만 추가
                    list_item = QListWidgetItem(f"{name} - 관리자" if admin == 1 else f"{name} - 사용자")
                    list_item.setForeground(QColor('blue') if admin == 1 else QColor('black'))
                    self.listcliked.addItem(list_item)
        except Exception as e:
            print(f"Exception error: {e}")

    def clicked_record_list(self, item):
        itemtext = item.text()
        change_itemtext = itemtext.strip("\n")
        parts = change_itemtext.split(" - ")  # " - "를 기준으로 문자열 분리
        name = parts[0]  # 첫 번째 부분을 self.Range에 할당
        if name != "JeoninHighSchool":
            result = self.Remove_account(name)
            if result["result"] == "success":
                # 계정목록 가져오기...
                result = self.Get_account()
                self.Add_account_list(result)
        else:
            self.popupwindows()


    def Get_account(self):
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/Get_account.php' , timeout=30)
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        return response.json()
    
    def Remove_account(self,name):
        post = {'name': name}
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/Remove_account.php', data=post , timeout=30)
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
