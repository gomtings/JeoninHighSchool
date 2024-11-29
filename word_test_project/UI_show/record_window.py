from UI_show.UI.record_window_ui import Ui_record
import json
import os
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QListWidget,
)
class record_Window(QMainWindow,Ui_record):
    def __init__(self,parents,path,bring): #init 공부하기
        super(record_Window, self).__init__()
        self.setupUi(self)
        self.path = path
        self.parents = parents
        self.Exam_bring = bring
        self.listcliked = self.findChild(QListWidget,"record_list")
        self.listcliked.itemDoubleClicked.connect(self.clicked_record_list)

    def load_records_from_json(self, file_path):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:    
                line = file.readlines()
                # print(line)
            for data in line:
                self.listcliked.addItem(data)
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # def find_record_files(self ,f_name):
        
    #     self.test_dir = f"{self.Exam_bring}{""}"
    #     for f_name in os.listdir(self.test_dir):
    #         if f_name + ".json" in self.Exam_bring:
    #         # if f_name.endswith('.txt'):
    #             print(f_name)
    def clicked_record_list(self, item):
        itemtext = item.text()
        change_itemtext = itemtext.strip("\n")
        clicked_files_path = f"{self.Exam_bring}{change_itemtext}.json"
        print(change_itemtext)
        print(clicked_files_path)
        if os.path.isfile(clicked_files_path) == True:
            print('1') 
        else:
            print('2')
        #     print(item.text())
        #     print(f"Clicked item: {item.text()}")
        # else:
        #     print(f"The File {item.text()} was not found")


    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        # Load words from JSON file
        os.chdir(os.path.dirname(__file__))
        
        # path = os.chdir("/save_record/d1_exam" )
        self.load_records_from_json(self.path)
    
    def closeEvent(self, event):
        self.parents.show()
        event.accept()
        
