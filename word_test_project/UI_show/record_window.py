from UI_show.UI.record_window_ui import Ui_record
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
    def __init__(self, parents, path, bring):  # init 공부하기
        super(record_Window, self).__init__()
        self.setupUi(self)
        self.path = path
        self.parents = parents
        self.Exam_bring = bring
        self.listcliked = self.findChild(QListWidget, "record_list")
        self.listcliked.itemDoubleClicked.connect(self.clicked_record_list)
        self.clicked_file_path = None

    def load_records_from_json(self, file_path):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
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
        clicked_files_path = f"{self.Exam_bring}{change_itemtext}.json"

        if os.path.isfile(clicked_files_path):  # 파일이 존재할 경우
            self.show_file_in_dialog(clicked_files_path)
        else:
            print(f"File {clicked_files_path} does not exist.")

    def show_file_in_dialog(self, file_path):
        # QDialog로 파일 내용을 표시하는 함수
        dialog = QDialog(self)  # 새로운 QDialog 창 생성
        dialog.setWindowTitle("File Content")  # 창 제목 설정

        # 텍스트 편집기를 추가하여 파일 내용을 표시
        text_edit = QTextEdit(dialog)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            text_edit.setText(file_content)  # 텍스트 편집기에 내용 설정
        except Exception as e:
            text_edit.setText(f"Error reading file: {e}")

        # 텍스트 편집기를 읽기 전용으로 설정
        text_edit.setReadOnly(True)  # 사용자가 입력을 할 수 없도록 설정

        # QDialog에 레이아웃을 설정하여 text_edit를 배치
        layout = QVBoxLayout(dialog)
        layout.addWidget(text_edit)

        dialog.setLayout(layout)
        dialog.exec()  # 다이얼로그 띄우기

    def showEvent(self, event):
        super().showEvent(event)  # 부모 클래스의 showEvent 메서드 호출
        self.load_records_from_json(self.path)

    def closeEvent(self, event):
        self.parents.show()
        event.accept()
