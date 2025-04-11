from UI_show.UI.user_question_window_ui import Ui_Create_question_window
import json
import os
from pathlib import Path
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
        super().__init__()
        self.setupUi(self)  # ✅ UI 연결 필수
        self.parents = parent
        self.file_path = file_path
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

        if not self.submitbtn:
            print("❌ submitbtn을 UI에서 찾을 수 없습니다. Qt Designer에서 objectName을 확인하세요.")
        else:
            self.submitbtn.clicked.connect(self.chk_answer)

        # 라디오 버튼들 연결
        for i in range(1, 6):
            btn = self.findChild(QRadioButton, f"answer_{i}")
            if btn:
                self.Radio_Widgets.append(btn)
            else:
                print(f"⚠️ answer_{i} 라디오 버튼을 찾을 수 없습니다.")

        # 보기 레이블 연결
        for i in range(1, 6):
            lbl = self.findChild(QLabel, f"answer_ex{i}")
            if lbl:
                self.Label_Widgets.append(lbl)
            else:
                print(f"⚠️ answer_ex{i} 레이블을 찾을 수 없습니다.")

        self.show_image()

    def show_image(self):
        image_path_str = self.data.get("image_path", None)
        entered_description = self.data.get("entered_description", "")
        self.exam.setText(f"문제: {entered_description}")

        # 보기 텍스트 설정
        answer_ex = self.data.get("answer_ex", [])
        for i, ex in enumerate(answer_ex):
            if i < len(self.Label_Widgets):
                self.Label_Widgets[i].setText(ex)

        # 이미지 경로 확인 및 보정
        image_path = Path(image_path_str) if image_path_str else None
        if image_path and not image_path.exists():
            json_folder = Path(self.file_path).parent
            image_path = json_folder / image_path.name
            print(f"🔁 보정된 이미지 경로: {image_path}")

        if image_path and image_path.exists():
            pixmap = QPixmap(str(image_path))
            self.picture_view.setPixmap(pixmap)
            self.picture_view.setScaledContents(True)
        else:
            print(f"[이미지 에러] 파일을 찾을 수 없습니다: {image_path}")

    def chk_answer(self):
        selected_index = None

        for idx, btn in enumerate(self.Radio_Widgets):
            if btn.isChecked():
                selected_index = idx + 1
                break

        if selected_index is None:
            print("⚠️ 답안을 선택해주세요.")
            return

        try:
            correct_index = int(self.data.get("selected_answer"))
        except Exception as e:
            print(f"정답 정보 오류: {e}")
            return

        print(f"📝 선택한 답: {selected_index} / 정답: {correct_index}")
        if selected_index == correct_index:
            print("✅ 정답입니다!")
        else:
            print("❌ 오답입니다.")

    def popupwindows(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("권한 없음")
        msg_box.setText("마스터 계정은 변경이 불가 합니다.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        if self.parents:
            self.parents.show()
        event.accept()