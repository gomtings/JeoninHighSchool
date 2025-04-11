from UI_show.UI.user_question_window2_ui import Ui_Create_question_window
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtGui import QPixmap


class Create_question_window_2(QMainWindow, Ui_Create_question_window):
    def __init__(self, parent=None, file_path=None):
        super().__init__()
        self.setupUi(self)
        self.parents = parent
        self.file_path = file_path
        self.setWindowTitle("주관식 문제 출제")

        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                self.data = json.load(json_file)
        except Exception as e:
            QMessageBox.critical(self, "에러", f"JSON 파일을 열 수 없습니다:\n{e}")
            self.close()
            return

        # UI 요소 연결
        self.correct_answer_edit = self.correc_answer_Edit
        self.submitbtn = self.submitbtn
        self.picture_view = self.picture_view
        self.input_Description = self.input_Description

        self.submitbtn.clicked.connect(self.chk_answer)

        self.load_question()

    def load_question(self):
        question_text = self.data.get("entered_description", "")
        self.input_Description.setText(f"문제: {question_text}")

        image_path_str = self.data.get("image_path", "")
        image_path = Path(image_path_str)

        # 디버깅 정보 출력
        print(f"[DEBUG] JSON 파일 경로: {self.file_path}")
        print(f"[DEBUG] image_path 원본: {image_path_str}")

        # 상대 경로일 경우 JSON 위치 기준으로 보정
        if not image_path.is_absolute():
            image_path = Path(self.file_path).parent / image_path

        print(f"[DEBUG] 최종 이미지 경로: {image_path}")

        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            self.picture_view.setPixmap(pixmap)
            self.picture_view.setScaledContents(True)
        else:
            print(f"[이미지 에러] 파일을 찾을 수 없습니다: {image_path}")

    def chk_answer(self):
        user_answer = self.correct_answer_edit.toPlainText().strip().lower()
        correct_answer = self.data.get("entered_correct_answer", "").strip().lower()

        if not user_answer:
            self.show_message("답안을 입력해주세요.", "orange")
            return

        if user_answer == correct_answer:
            self.show_message("✅ 정답입니다!", "green")
        else:
            self.show_message(
                f"❌ 오답입니다.<br>정답: <b>{self.data.get('entered_correct_answer')}</b>",
                "red"
            )

        self.correct_answer_edit.clear()

    def show_message(self, text, color="black"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("채점 결과")
        msg_box.setText(f"<p style='color:{color}'>{text}</p>")
        msg_box.exec()

    def closeEvent(self, event):
        if self.parents:
            self.parents.show()
        event.accept()
