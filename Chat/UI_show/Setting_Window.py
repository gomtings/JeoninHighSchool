from UI_show.UI.Setting_Window_ui import Ui_Setting_Window
import os
import requests
import threading
import json
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QListWidget
)
from PySide6.QtCore import QSettings
from UI_show.Modules.Thread import getfriendThread

class Setting_Window(QMainWindow,Ui_Setting_Window):
    def __init__(self, parent=None,descendent = None,Name=None,Base_path = None):
        super(Setting_Window, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("설정")
        self.Parent = parent # Login_Windows
        self.descendent = descendent # friend_list_window
        self.Name = Name
        self.Base_path = Base_path
        self.friend = []
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.settings = QSettings("Simple Talk", "Talk")
        self.Allow_search = self.findChild(QPushButton,"Allow_search") #  친구검색 허용
        self.Allow_search.clicked.connect(self.Set_Allow_search)
        self.Allow_search.setStyleSheet(
        """
        QPushButton {background-color: #0090ff; color: black;}
        QPushButton:hover {background-color: #b0b0b0; color: black;}
        """
        )
        self.Set_Allow_search()
 
        self.friendlist = self.findChild(QListWidget,"friendlist") 
        self.friend_input = self.findChild(QLineEdit,"friend_input") 
        self.addlist = self.findChild(QPushButton,"addlist") 
        self.addlist.clicked.connect(self.search_friend)
        
        self.config_path = r"info\friend_list.json"
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding='utf-8') as f:
                    self.friend_list = json.load(f)
        except Exception as e:
            print(f"friend_list.json 읽기 실패({str(e)})")
        for value in self.friend_list:
            self.friendlist.addItem(value)

        # 새로운 쓰레드 시작
        self.interest_thread = getfriendThread(self.Parent,self.Name)
        self.interest_thread.update_signal.connect(self.Parent.local.update_friend)
        self.interest_thread.update_signal.connect(self.update_friend)
        self.interest_thread.start()

    def Set_Allow_search(self):
        self.Allow = self.settings.value("Allow_search", False, type=bool)
        if self.Allow:
            self.Allow_search.setText("친구 검색 허용(불허)")
            self.settings.setValue("Allow_search", False)
        else:
            self.Allow_search.setText("친구 검색 허용(허용)")
            self.settings.setValue("Allow_search", True)
        self.descendent.start_interest_system()

    def update_friend(self,friend):
        self.friend = friend


    def search_friend(self):
        add_list = False
        nmae = self.friend_input.text()
        if nmae in self.friend:
            if not self.is_already_in_listwidget(self.friendlist, nmae):
                self.friendlist.addItem(nmae)
                self.popupwindows(f"{nmae} 추가 성공","친구가 추가 되었습니다.")
                add_list = True
            else:
                self.popupwindows("추가 실패", "이미 친구 목록에 있습니다.")
        else:
            self.popupwindows(f"추가 실패","검색된 친구가 없습니다.")    
        self.friend_input.clear()
        if add_list:
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self.friend_list, f, ensure_ascii=False, indent=4)
                    print("friend_list.json 저장 완료")
            except Exception as e:
                print(f"friend_list.json 저장 실패({str(e)})")
            add_list = False

    def is_already_in_listwidget(self,listwidget, text):
        for i in range(listwidget.count()):
            if listwidget.item(i).text() == text:
                return True
        return False


    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.interest_thread.stop()
        event.accept()  # 이벤트를 수락해서 현재 창 닫기