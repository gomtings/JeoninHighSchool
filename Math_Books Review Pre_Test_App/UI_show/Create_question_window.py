from UI_show.UI.Create_question_window_ui import Ui_Create_question_window
import time
import json
import os
import requests
import shutil
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
    QRadioButton,
    QFileDialog
)
from PySide6.QtGui import QColor, QPixmap

class Create_question_window(QMainWindow, Ui_Create_question_window):
    def __init__(self, parent=None, book=None,Base_path=None,num = 0):
        super(Create_question_window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.book = book
        self.Base_path = Base_path
        self.num = num
        self.Radio_Widgets = []
        self.LineEdit_Widgets = []
        self.selected_image_path = None  # 이미지 경로를 저장할 변수
        

        self.setWindowTitle("객관식 문제 출제")
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.find_picture = self.findChild(QPushButton, "find_picture")
        self.submit_btn = self.findChild(QPushButton, "submit_btn")
        self.Edit_Description = self.findChild(QLineEdit, "Edit_Description")

        # find_picture 버튼에 클릭 이벤트 연결
        self.find_picture.clicked.connect(self.select_image)
        # submit_btn 버튼에 클릭 이벤트 연결
        self.submit_btn.clicked.connect(self.submit_answer)

        for i in range(1, 6): 
            RadioBtn = self.findChild(QRadioButton, f"answer_{i}") 
            if RadioBtn: 
                self.Radio_Widgets.append(RadioBtn) 
            else: 
                print(f"Warning: answer_{i} not found")

        for i in range(1, 6): 
            LineEdit = self.findChild(QLineEdit, f"answer_ex{i}") 
            if LineEdit: 
                self.LineEdit_Widgets.append(LineEdit)
            else: 
                print(f"Warning: answer_ex{i} not found")

    def select_image(self):
        """이미지 파일 선택 후 QLabel에 표시하는 함수"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "Images (*.png *.jpg *.bmp *.gif)"
        )

        if file_name:
            # 선택된 이미지 파일을 QPixmap으로 로드하고 QLabel에 표시
            pixmap = QPixmap(file_name)
            self.picture_view.setPixmap(pixmap)
            self.picture_view.setScaledContents(True)  # QLabel에 맞게 크기 조정
            self.selected_image_path = file_name  # 이미지 경로 저장

    def submit_answer(self):
        """사용자가 입력한 답안, 텍스트, 이미지를 저장하는 함수"""
        # 사용자가 선택한 답을 추출
        selected_answer = None
        for i, radio_button in enumerate(self.Radio_Widgets):
            if radio_button.isChecked():
                selected_answer = f"{i+1}"  # "답안 1", "답안 2" 등으로 표시
                break
        
        answer_ex = []
        for LineEdit in self.LineEdit_Widgets:
            text = LineEdit.text()
            answer_ex.append(text)

        # 사용자가 입력한 텍스트 추출
        entered_description = self.Edit_Description.text()

        if not selected_answer or not entered_description or not answer_ex:
            QMessageBox.warning(self, "경고", "입력안된 항목이 존재합니다.")
            return

        # 파일 저장 경로 설정
        save_directory = os.path.join(self.Base_path, "question_answer", self.book)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)  # 디렉토리가 없으면 생성

        timestamp = time.strftime("%Y-%m-%d-%H.%M.%S")  # YYYYMMDD_HHMMSS 형식
        file_name = os.path.join(save_directory, f"{timestamp}_Multiple_{self.num}.json")
        image_name = f"Multiple_image{self.num}" + os.path.splitext(self.selected_image_path)[1]
        image_dest = os.path.join(save_directory, image_name)
        # file_name = os.path.join("submission.json")
            # 저장할 데이터 구조
        submission_data = {
            "answer_ex": answer_ex,
            "selected_answer": selected_answer,
            "entered_description": entered_description,
            "image_path": image_dest,
        }

        # 데이터 파일로 저장
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(submission_data, f, ensure_ascii=False, indent=4)
        
        # 이미지 파일 복사 (선택한 이미지가 있다면)
        if self.selected_image_path:
            if self.selected_image_path != image_dest:
                shutil.copy(self.selected_image_path, image_dest)
            

        QMessageBox.information(self, "성공", "답안과 이미지가 저장되었습니다.")
        self.close()

    def popupwindows(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("마스터 계정은 변경이 불가 합니다.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()