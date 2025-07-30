from UI_show.UI.Chat_Window_ui import Ui_Chat_Window
import os
import requests
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
        self.setWindowTitle(f"{self.friend_name}")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.Ancestor = Ancestor
        self.parents = parents
        self.Base_path = Base_path
        self.Myname = Myname
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
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.Update_Msg)  # 타임아웃마다 함수 호출
        self.timer.start(100)  # 100ms = .1초 간격

    def Update_Msg(self):
        msg = self.parents.Chat_msg.pop(self.Myname,None)
        if msg is not None:
            self.ChatListWidget.addItem(f"{self.friend_name}: {msg}")

    def Send_message(self):
        Message = self.Message.text()
        self.Ancestor.msg(f"Event/Chat/{self.friend_name}",Message)
        self.ChatListWidget.addItem(f"{self.Myname}: {Message}")
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