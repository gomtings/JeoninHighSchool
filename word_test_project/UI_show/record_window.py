from UI_show.UI.record_window_ui import Ui_record
import json
import os
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QListWidget
)
import shutil
class record_Window(QMainWindow,Ui_record):
    def __init__(self,parents,path): #init 공부하기
        super(record_Window, self).__init__()
        self.setupUi(self)
        self.parents = parents
        self.path = path
        # 창 크기를 고정 
        self.setFixedSize(self.size())
        self.listcliked = self.findChild(QListWidget,"record_list")
        self.listcliked.itemDoubleClicked.connect(self.find_record_files)
    def load_records_from_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                records = json.load(file)
                # print(records)ㅁㄴㅇ
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        # Load words from JSON file
        os.chdir(os.path.dirname(__file__))
        
        # path = os.chdir("/save_record/d1_exam" )
        self.load_records_from_json(self.path)

    def find_record_files(self, item, f_name):

        for f_name in os.listdir('test_dir'):
            if f_name.endswith('.txt'):
                print(f_name)

    def closeEvent(self, event):
        self.parents.show()
        event.accept()