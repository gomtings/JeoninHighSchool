from UI_show.UI.record_window_ui import Ui_record
from UI_show.Memo_window import Memo_window
import json
import os
from PySide6.QtWidgets import (
    QMainWindow,
    QListWidget,
    QTextEdit,
    QDialog,  # 새로운 창을 띄우기 위해 추가
    QVBoxLayout  # 레이아웃을 위해 추가
)

class record_Window(QMainWindow, Ui_record):
    def __init__(self, parents,Workbook_path, Exam_record_path, bring):  # init 공부하기
        super(record_Window, self).__init__()
        self.setupUi(self)
        self.Exam_record_path = Exam_record_path
        self.Workbook_path = Workbook_path
        self.parents = parents
        self.Exam_bring = bring
        self.Memo_window = None
        self.Range = None
        self.listcliked = self.findChild(QListWidget, "record_list")
        self.listcliked.itemDoubleClicked.connect(self.clicked_record_list)
        self.clicked_file_path = None

    def load_records_from_json(self, file_path):
        try:
            with open(self.Exam_record_path, 'r', encoding='utf-8') as file:
                line = file.readlines()
            for data in line:
                self.listcliked.addItem(data.strip())  # 각 항목을 리스트에 추가
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        except json.JSONDecodeError:
            print("Error: JSON decoding error. Check the file format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def clicked_record_list(self, item):
        itemtext = item.text()
        change_itemtext = itemtext.strip("\n")
        parts = change_itemtext.split("_")
        self.Range = parts[2]
        clicked_files_path = f"{self.Exam_bring}{change_itemtext}.json"

        if os.path.isfile(clicked_files_path):  # 파일이 존재할 경우
            self.show_file_in_dialog(clicked_files_path,self.Range)
        else:
            print(f"File {clicked_files_path} does not exist.")

    def show_file_in_dialog(self, file_path,Range):
        if self.Memo_window is None or not self.Memo_window.isVisible(): 
            self.Memo_window = Memo_window(self,self.Workbook_path,file_path,Range)
            self.hide()
            self.Memo_window.show()

    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        self.load_records_from_json(self.Exam_record_path)

    def closeEvent(self, event):
        self.parents.show()
        event.accept()
