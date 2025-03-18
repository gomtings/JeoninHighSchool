from UI_show.UI.Create_question_window_2_ui import Ui_Create_question_window
import os
import time
import json
import shutil
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QFileDialog
)
from PySide6.QtGui import QPixmap
from UI_show.UI.Create_question_window_2_ui import Ui_Create_question_window

class Create_question_window_2(QMainWindow, Ui_Create_question_window):
    def __init__(self, parent=None, book=None):
        super(Create_question_window_2, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.book = book
        self.setWindowTitle("주관식 문제 출제")
        
        # UI 요소 가져오기
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.find_picture = self.findChild(QPushButton, "find_picture")
        self.submit_btn = self.findChild(QPushButton, "submit_btn")
        self.Edit_Description = self.findChild(QLineEdit, "Edit_Description")
        self.correct_answer = self.findChild(QTextEdit, "correc_answer_Edit")

        # 버튼 이벤트 연결
        self.find_picture.clicked.connect(self.select_image)
        self.submit_btn.clicked.connect(self.submit_answer)

        # 이미지 경로 저장 변수
        self.selected_image_path = None  

    def select_image(self):
        """이미지 파일 선택 후 QLabel에 표시하는 함수"""
        file_name, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "Images (*.png *.jpg *.bmp *.gif)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.picture_view.setPixmap(pixmap)
            self.picture_view.setScaledContents(True)  # QLabel 크기에 맞게 조정
            self.selected_image_path = file_name  # 이미지 경로 저장

    def submit_answer(self):
        """사용자가 입력한 문제와 답안을 JSON으로 저장"""
        entered_description = self.Edit_Description.text().strip()
        entered_correct_answer = self.correct_answer.toPlainText().strip()

        if not entered_description:
            QMessageBox.warning(self, "경고", "문제 설명을 입력해주세요.")
            return

        if not entered_correct_answer:
            QMessageBox.warning(self, "경고", "정답을 입력해주세요.")
            return

        # 파일 저장 경로 설정
        save_directory = os.path.join(os.getcwd(), "question_answer")
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)  # 디렉토리가 없으면 생성

        timestamp = time.strftime("%Y%m%d_%H%M%S")  # 파일 이름에 타임스탬프 추가
        file_name = os.path.join(save_directory, f"submission_{timestamp}.json")

        # 저장할 데이터 구조
        submission_data = {
            "entered_description": entered_description,  # 문제 설명
            "entered_correct_answer": entered_correct_answer,  # 정답
            "image_path": self.selected_image_path if self.selected_image_path else None,  # 이미지 경로 (선택 사항)
        }

        # JSON 파일로 저장
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(submission_data, f, ensure_ascii=False, indent=4)

        # 이미지 복사 (선택한 경우)
        if self.selected_image_path:
            image_name = f"image_{timestamp}" + os.path.splitext(self.selected_image_path)[1]
            image_dest = os.path.join(save_directory, image_name)
            shutil.copy(self.selected_image_path, image_dest)

        QMessageBox.information(self, "성공", "문제와 정답이 저장되었습니다.")

    def popupwindows(self):
        """권한 없음 알림창"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("마스터 계정은 변경이 불가 합니다.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        """창 닫을 때 부모 윈도우 표시"""
        self.parents.show()
        event.accept()

