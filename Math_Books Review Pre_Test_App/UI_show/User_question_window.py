from UI_show.UI.user_question_window_ui import Ui_Create_question_window
import json
import os
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QMessageBox,
    QRadioButton,
)
from PySide6.QtGui import QPixmap


class Create_question_window(QMainWindow, Ui_Create_question_window):
    def __init__(self, parent=None, file_path=None):
        super(Create_question_window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.file_path = os.path.join(os.getcwd(), "question_answer")
        self.Radio_Widgets = []
        self.Label_Widgets = []

        self.setWindowTitle("객관식 문제 출제")

        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as json_file:
            self.data = json.load(json_file)

        # UI 요소 연결
        self.picture_view = self.findChild(QLabel, "picture_view")
        self.exam = self.findChild(QLabel, "label_6")
        self.submitbtn = self.findChild(QPushButton, "submitbtn")
        self.submitbtn.clicked.connect(self.chk_answer)

        # 객관식 라디오 버튼 등록
        for i in range(1, 6):
            RadioBtn = self.findChild(QRadioButton, f"answer_{i}")
            if RadioBtn:
                self.Radio_Widgets.append(RadioBtn)
            else:
                print(f"Warning: QRadioButton answer_{i} not found")

        # 보기 설명 레이블 등록 (옵션)
        for i in range(1, 6):
            Label = self.findChild(QLabel, f"answer_ex{i}")
            if Label:
                self.Label_Widgets.append(Label)
            else:
                print(f"Warning: QLabel answer_ex{i} not found")

        # 이미지와 문제 설명 표시
        self.show_image()

    def show_image(self):
        image_path = self.data.get("image_path",None)
        entered_description = self.data.get("entered_description", None)
        self.exam.setText(entered_description)
        answer_ex = self.data.get("answer_ex", None)
        if answer_ex:
            for i, ex in enumerate(answer_ex):
                if i < len(self.Label_Widgets):
                    self.Label_Widgets[i].setText(ex)
        if image_path != None:
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                self.picture_view.setPixmap(pixmap)
                self.picture_view.setScaledContents(True)
            else:
                print(f"[이미지 에러]: 파일을 찾을 수 없습니다 - {image_path}")

    def chk_answer(self):
        selected_index = None

        # 어떤 버튼이 체크되었는지 확인
        for idx, radio_btn in enumerate(self.Radio_Widgets):
            if radio_btn.isChecked():
                selected_index = idx + 1  # answer_1이면 1, answer_2이면 2 ...
                break

        if selected_index is None:
            print("답안을 선택해주세요.")
            return

        # JSON에서 정답 문자열: "답안 2" → 숫자만 추출
        correct_index = int(self.data.get("selected_answer", None))
        print("selected_index"+str(selected_index)+"correct_index"+str(correct_index))
        if selected_index == correct_index:
            print("정답입니다")
        else:
            print("오답입니다")
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
