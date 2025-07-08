from UI_show.UI.Create_question_window_ui import Ui_Create_question_window
import time
import json
import os
import requests
import shutil
import ftplib
import datetime
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
    def __init__(self, parent=None, book=None, Base_path=None, num=0):
        super(Create_question_window, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.book = book
        self.Base_path = Base_path
        self.num = num
        self.Radio_Widgets = []
        self.LineEdit_Widgets = []
        self.selected_image_path = None
        self.report_dist = None
        self.setWindowTitle("객관식 문제 출제")

        # FTP 정보 로드
        try:
            FTP_path = os.path.join(self.Base_path, "info", "Report_FTP.json")
            with open(FTP_path, "r", encoding="UTF-8") as f:
                self.report_dist = json.load(f)
        except Exception as e:
            print(f'Report_FTP.json 데이터가 없습니다. {e}')

        self.picture_view = self.findChild(QLabel, "picture_view")
        self.picture_view.setWordWrap(True)
        self.find_picture = self.findChild(QPushButton, "find_picture")
        self.submit_btn = self.findChild(QPushButton, "submit_btn")

        # ✅ Edit_Description 위젯 찾기 (None 방지 로그 추가)
        self.Edit_Description = self.findChild(QLineEdit, "Edit_Description")
        if self.Edit_Description is None:
            print("❌ 'Edit_Description' QLineEdit을 찾지 못했습니다. UI 파일의 objectName을 확인하세요.")

        self.find_picture.clicked.connect(self.select_image)
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
        file_name, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "Images (*.png *.jpg *.bmp *.gif)"
        )
        if file_name:
            pixmap = QPixmap(file_name)
            self.picture_view.setPixmap(pixmap)
            self.picture_view.setScaledContents(True)
            self.selected_image_path = file_name

    def submit_answer(self):
        selected_answer = None
        for i, radio_button in enumerate(self.Radio_Widgets):
            if radio_button.isChecked():
                selected_answer = f"{i + 1}"
                break

        answer_ex = []
        for LineEdit in self.LineEdit_Widgets:
            text = LineEdit.text()
            answer_ex.append(text)

        # ✅ None 방지 체크
        if self.Edit_Description is None:
            QMessageBox.critical(self, "오류", "Edit_Description 위젯을 찾지 못했습니다. UI 정의를 확인하세요.")
            return

        entered_description = self.Edit_Description.text()

        if not selected_answer or not entered_description or not all(answer_ex):
            QMessageBox.warning(self, "경고", "입력안된 항목이 존재합니다.")
            return

        save_directory = os.path.join(self.Base_path, "Workbook", self.book)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        timestamp = time.strftime("%Y-%m-%d-%H.%M.%S")
        file_name = os.path.join(save_directory, f"{timestamp}_Multiple_{self.num}.json")

        if self.selected_image_path:
            image_ext = os.path.splitext(self.selected_image_path)[1]
            image_name = f"Multiple_image{self.num}{image_ext}"
            image_dest = os.path.join("Workbook", self.book, image_name)
            copy_dest = os.path.join(save_directory, image_name)
        else:
            image_dest = ""
            copy_dest = ""

        submission_data = {
            "answer_ex": answer_ex,
            "selected_answer": selected_answer,
            "entered_description": entered_description,
            "image_path": image_dest
        }

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(submission_data, f, ensure_ascii=False, indent=4)

        if self.selected_image_path and self.selected_image_path != copy_dest:
            shutil.copy(self.selected_image_path, copy_dest)

        version_path = self.Save_version()
        self.upload_folder_to_ftp(save_directory, version_path, self.book)

        QMessageBox.information(self, "성공", "답안과 이미지가 저장되었습니다.")
        self.close()

    def upload_folder_to_ftp(self, local_folder, version_path, book):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]

        session = ftplib.FTP()
        try:
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)

            remote_base_path = f"/html/Math_Books Review Pre_Test_App/Workbook"
            base_local_folder = os.path.abspath(local_folder)

            try:
                session.mkd(remote_base_path)
            except ftplib.error_perm:
                pass

            remote_base_path = f"{remote_base_path}/{book}"
            try:
                session.mkd(remote_base_path)
            except ftplib.error_perm:
                pass

            def upload_recursive(local_path):
                relative_path = os.path.relpath(local_path, base_local_folder)
                remote_path = f"{remote_base_path}/{relative_path.replace(os.sep, '/')}"
                if os.path.isdir(local_path):
                    try:
                        session.mkd(remote_path)
                    except ftplib.error_perm:
                        pass
                    for item in os.listdir(local_path):
                        upload_recursive(os.path.join(local_path, item))
                else:
                    with open(local_path, "rb") as uploadfile:
                        session.encoding = "utf-8"
                        session.storbinary(f"STOR {remote_path}", uploadfile)

            upload_recursive(local_folder)

            if os.path.exists(version_path):
                with open(version_path, "rb") as version_file:
                    remote_version_path = f"/html/Math_Books Review Pre_Test_App/Workbook/version.txt"
                    session.storbinary(f"STOR {remote_version_path}", version_file)

        except ftplib.all_errors as e:
            print(f"⚠️ FTP 업로드 오류: {str(e)}")
        finally:
            session.quit()

    def Save_version(self):
        try:
            now = datetime.datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M")
            version_path = os.path.join(self.Base_path, "Workbook", "version.txt")
            with open(version_path, 'w', encoding='utf-8') as file:
                file.write(formatted_time)
            return version_path
        except Exception as e:
            print(f"⚠️ 버전 저장 실패: {str(e)}")
            return None

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