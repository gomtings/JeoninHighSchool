from UI_show.UI.Setting_Window_ui import Ui_Setting_Window
import os
import requests
import threading

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
        super(Setting_Window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("회원가입")
        self.Parent = parent # Login_Windows
        self.descendent = descendent # friend_list_window
        self.Name = Name
        self.Base_path = Base_path
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

        # 새로운 쓰레드 시작
        self.interest_thread = getfriendThread(self.Parent,self.Name)
        self.interest_thread.update_signal.connect(self.local.update_friend)
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

    def interest_loop(self):
        while True:
            self.Parent.local.msg("Event/State/", self.Name)  # 주변에 내 닉네임을 발송함.
            
            msg = self.Parent.local.get_State_message()
            if msg != self.Name:
                self.friend[msg] = msg
                self.Parent.local.update_friend(self.friend)

    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        event.accept()