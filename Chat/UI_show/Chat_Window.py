from UI_show.UI.Chat_Window_ui import Ui_Chat_Window
import os
import requests
import json
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QListWidget,
    QLabel
)
from PySide6.QtCore import QTimer

class Chat_Window(QMainWindow,Ui_Chat_Window):
    def __init__(self,parents,Ancestor,Base_path,Myname,friend_name):
        super(Chat_Window, self).__init__(parents)
        self.setupUi(self)
        self.setWindowTitle(f"{friend_name}")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.Ancestor = Ancestor
        self.parents = parents
        self.Base_path = Base_path
        self.name = Myname
        self.friend_name = friend_name
        self.chat_name = self.findChild(QLabel,"chat_name") #  메시지 전송
        self.chat_name.setText(self.friend_name)
        self.transmit = self.findChild(QPushButton,"transmit") #  메시지 전송
        self.transmit.clicked.connect(self.Send_message)
        self.transmit.setStyleSheet(
            """
        QPushButton {background-color: #0090ff; color: black;}
        QPushButton:hover {background-color: #b0b0b0; color: black;}
        """
        )
        self.Message = self.findChild(QLineEdit,"Message") #  전송할 메시지
        self.ChatListWidget = self.findChild(QListWidget,"ChatListWidget")
    
    def Chat_Msg_update(self, friend):
        if not friend:
            return

        buffer = friend.get(self.friend_name, None)
        if not buffer:
            return

        # 문자열이면 JSON 파싱
        if isinstance(buffer, str):
            try:
                buffer = json.loads(buffer)
            except json.JSONDecodeError as e:
                print(f"[JSON 파싱 오류] {e}")
                return

        # buffer가 dict일 때만 pop 사용
        if isinstance(buffer, dict):
            msg = buffer.pop("msg", None)
            if msg:
                self.ChatListWidget.addItem(f"{self.friend_name}: {msg}")
                friend.pop(self.friend_name)

    def Send_message(self):
        Message = self.Message.text()
        topic = f"Event/Chat/Msg/{self.friend_name}"
        result = json.dumps({
            "from": self.name,   # 보내는 사람
            "to": self.friend_name,    # 받는 사람
            "msg": Message       # 메시지 내용
        }).encode("utf-8")
        self.Ancestor.local.msg(topic,result)
        self.ChatListWidget.addItem(f"{self.name}: {Message}")
        self.Message.clear()
    
    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        super().closeEvent(event)
        event.accept()