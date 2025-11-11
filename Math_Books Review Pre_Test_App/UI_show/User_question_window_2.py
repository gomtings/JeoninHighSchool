from UI_show.UI.user_question_window2_ui import Ui_Create_question_window
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import json
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtGui import QPixmap


class Create_question_window(QMainWindow, Ui_Create_question_window):
    def __init__(self, parent=None, Base_path=None, file_path=None, book=None, point=None):
        super().__init__()
        self.setupUi(self)
        self.parents = parent
        self.file_path = file_path
        self.Base_path = Base_path
        self.book = book
        self.point = point
        self.name = name
        self.setWindowTitle("주관식 문제 출제")

        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                self.data = json.load(json_file)
        except Exception as e:
            QMessageBox.critical(self, "에러", f"JSON 파일을 열 수 없습니다:\n{e}")
            self.close()
            return

        self.correct_answer_edit = self.correc_answer_Edit
        self.submitbtn = self.submitbtn
        self.picture_view = self.picture_view
        self.input_Description = self.input_Description
        self.submitbtn.clicked.connect(self.chk_answer)
        self.point['이름'] = self.name
        self.point['과제'] = self.book
        self.load_question()

    def detect_language_with_threshold(self, text, threshold=0.7):
        korean_chars = len(re.findall(r'[가-힣]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = korean_chars + english_chars
        if total_chars == 0:
            return "Unknown"
        korean_ratio = korean_chars / total_chars
        english_ratio = english_chars / total_chars
        if korean_ratio >= threshold:
            return "Korean"
        elif english_ratio >= threshold:
            return "English"
        else:
            return "Mixed"

    def get_model_for_language(self, text):
        language = self.detect_language_with_threshold(text)
        model_dict = {
            "Korean": "snunlp/KR-SBERT-V40K-klueNLI-augSTS",
            "English": "all-mpnet-base-v2",
            "Mixed": "paraphrase-MiniLM-L6-v2"
        }
        model_name = model_dict.get(language, "all-mpnet-base-v2")
        if model_name not in self.model_cache:
            self.model_cache[model_name] = SentenceTransformer(model_name)
        return self.model_cache[model_name], language

    def load_question(self):
        question_text = self.data.get("entered_description", "")
        self.input_Description.setText(f"문제: {question_text}")
        image_path_str = self.data.get("image_path", "")
        image_path_str = os.path.join(self.Base_path, image_path_str)
        image_path = Path(image_path_str)
        if not image_path.is_absolute():
            image_path = Path(self.file_path).parent / image_path
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            self.picture_view.setPixmap(pixmap)
            self.picture_view.setScaledContents(True)

    def check_entailment(self, premise, hypothesis):
        inputs = self.nli_tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.nli_model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        labels = ["entailment", "neutral", "contradiction"]
        pred_label = labels[probs.argmax()]
        return pred_label

    def chk_answer(self):
        user_answer = self.correct_answer_edit.toPlainText().strip().lower()
        correct_answer = self.data.get("entered_correct_answer", "").strip().lower()
        model, detected_lang = self.get_model_for_language(correct_answer)
        language = self.detect_language_with_threshold(user_answer)

        if not user_answer:
            self.show_message("답안을 입력해주세요.", "orange")
            return

        embedding1 = model.encode(user_answer, convert_to_tensor=True)
        embedding2 = model.encode(correct_answer, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embedding1, embedding2)
        point = similarity.item()
        # ✅ 5. 결과 출력
        print(f"문장 유사도 (코사인 유사도): {similarity.item():.4f}")
        
        if language == detected_lang:
            if point >= 0.8:
                self.point['맞춘 갯수'] = self.point.get('맞춘 갯수',0) + 1
                self.show_message("✅ 정답입니다!", "green")
            else:
                self.point['틀린 갯수'] = self.point.get('틀린 갯수',0) + 1
                self.show_message(f"❌ 오답입니다!","red")
        else:
            self.point['틀린 갯수'] = self.point.get('틀린 갯수',0) + 1
            self.show_message(f"❌ 오답입니다!","red") 

        self.correct_answer_edit.clear()
        self.close()
        self.parents.show_next_question(self.book, self.point)
    
    def show_message(self, text, color="black"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("채점 결과")
        msg_box.setText(f"<p style='color:{color}'>{text}</p>")
        msg_box.exec()




    def closeEvent(self, event):
        if self.parents:
            self.parents.show()
        event.accept()