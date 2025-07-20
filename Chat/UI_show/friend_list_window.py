##############################################################################
#              천공기 통합 관제 시스템
#
# 시작일: 2024-04-30
# Developer: 이상우 , 
##############################################################################
#cd '.\Integrated Control System\'
#python -m venv venv # 처음 한번 가상환경 생성...
#pip install pyside6
#.\venv\Scripts\activate
#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser #  4번에서 오류 발생시..
#pyside6-designer
#C:/Python/Python310/python.exe "c:/GitHub/solimatics/Integrated Control System/Integrated Control System.py"
#pip install paho-mqtt
import json
import re
import os
import threading
import time
from PySide6.QtWidgets import QMainWindow,QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea,QPushButton,QMessageBox
from UI_show.UI.friend_list_window_ui import Ui_friend_list_window
from UI_show.Setting_Window import Setting_Window
from UI_show.Modules.Thread import InterestThread

class friend_list_window(QMainWindow, Ui_friend_list_window):
    def __init__(self, parent=None,Name=None,Base_path = None):
        super(friend_list_window, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("설정")
        self.setFixedSize(self.size())
        self.Parent = parent
        self.Name = Name
        self.Base_path = Base_path
        self.label_edit_pairs = [] #  label_edit_pairs 리스트 초기화
        self.position_data = {}
        self.friend_list = None
        self.setting_window = None
        self.interest_thread = None
        self.running = None
        self.friend = {}
        self.config_path = r"info\friend_list.json"
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding='utf-8') as f:
                    self.friend_list = json.load(f)
        except Exception as e:
            print(f"friend_list.json 읽기 실패({str(e)})")

        if self.friend_list:
            self.init_ui()
            
        self.Scroll_Area = self.findChild(QScrollArea, 'Scroll_Area')
        self.setupBtn = self.findChild(QPushButton, 'setupBtn')
        self.setupBtn.clicked.connect(self.setting)
        self.setupBtn.setStyleSheet(
        """
        QPushButton {background-color: #37b6fa; color: black;}
        QPushButton:hover {background-color: #c5c5c5; color: black;}
        """
        )
         
    def start_interest_system(self):
        # 기존 쓰레드 종료
        if hasattr(self, "interest_thread") and self.interest_thread.isRunning():
            self.interest_thread.stop()
            self.interest_thread.quit()
            self.interest_thread.wait()
            print("쓰레드가 중단되었습니다.")

        # 새로운 쓰레드 시작
        self.interest_thread = InterestThread(self.Parent, self.Name)
        self.interest_thread.start()
        print("새로운 QThread 쓰레드가 시작되었습니다.")

    def closeEvent(self, event):
        if self.Parent:
            self.Parent.close()
        event.accept()  # 이벤트를 수락해서 현재 창 닫기

    def init_ui(self):
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)

        for value in self.friend_list:
            button = QPushButton(value)
            button.setFixedHeight(50)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 26px;
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 2px solid #000000;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #c0c0ff;
                }
            """)
            button.clicked.connect(lambda checked, v=value: self.handle_button_click(v))

            layout.addWidget(button)  # 버튼을 수직 레이아웃에 바로 추가!

        self.Scroll_Area.setWidget(container_widget)
        self.Scroll_Area.setWidgetResizable(True)

    def handle_button_click(self, friend_name):
        print(f"{friend_name} 버튼이 클릭되었습니다!")
        # 또는 메시지 박스를 띄우거나 다른 UI 로직을 수행할 수 있어요

            
    def setting(self):
        if self.setting_window is None or not self.setting_window.isVisible():
            self.setting_window = Setting_Window(self.Parent,self,self.Name,self.Base_path)
            self.setting_window.show()

"""                           
app = QApplication(sys.argv)
window = Setup_Windows()
window.show()
try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
"""