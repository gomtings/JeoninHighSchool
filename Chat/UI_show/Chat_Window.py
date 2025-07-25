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
class Chat_Window(QMainWindow,Ui_Chat_Window):
    def __init__(self,parents,Base_path,name):
        super(Chat_Window, self).__init__(parents)
        self.setupUi(self)
        self.setWindowTitle(f"{name}")
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.parents = parents
        self.Base_path = Base_path
        self.name = name
        self.chat_name = self.findChild(QLabel,"chat_name") #  메시지 전송
        self.chat_name.setText(self.name)
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
    
    def Send_message(self):
        Message = self.Message.text()
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