from UI_show.UI.grade_manager_ui import Ui_grade_window
from UI_show.Check_grades_window import Check_grades_window
import json
import os
import requests
import ftplib
from PySide6.QtWidgets import (
    QMainWindow,
    QListWidget,
    QTextEdit,
    QDialog,  # 새로운 창을 띄우기 위해 추가
    QVBoxLayout,  # 레이아웃을 위해 추가
    QListWidgetItem,
    QMessageBox,
    QComboBox
)
from PySide6.QtGui import QColor

class grade_manager_Windows(QMainWindow, Ui_grade_window):
    def __init__(self,parent=None,Base_path = None):  # init 공부하기
        super(grade_manager_Windows, self).__init__()
        self.setupUi(self)
        self.parents = parent
        self.Base_path = Base_path
        self.Day = "ALL"
        self.Check_grades_windows = None
        self.setWindowTitle("성적 관리")
        
        # FTP 정보 로드
        FTP_path = os.path.join(self.Base_path, "info", "Report_FTP.json")
        try:
            with open(FTP_path, "r", encoding="UTF-8") as f:
                self.report_dist = json.load(f)
        except Exception as e:
            print(f'FTP.json 데이터가 없습니다. {e},{FTP_path}')

        self.grade_list = self.findChild(QListWidget, "grade_list")
        self.grade_list.itemDoubleClicked.connect(self.clicked_record_list)

        self.Sorting = self.findChild(QComboBox, "Sorting")
        self.Sorting.currentTextChanged.connect(self.Sorting_combobox_text_changed)
        self.subject = self.findChild(QComboBox, "subject")
        self.subject.currentTextChanged.connect(self.subject_combobox_text_changed)

        # 계정목록 가져오기...
        self.result = self.Get_account()
        for directory in self.result['data']:
            name = directory['name']
            self.Sorting.addItem(name)  
        
        # 관리파일 다운로드 
        self.download_Management_file(self.result)
        self.Sorting_combobox_text_changed("정답순")
    
    def subject_combobox_text_changed(self, text):
        self.Day = text
        Sorting = self.Sorting.currentText()

        # 과목 선택을 변경 했다면 순위를 다시 매긴다.
        self.Sorting_combobox_text_changed(Sorting)

    def Sorting_combobox_text_changed(self, text):
        all_data = []
        if text == "정답순":
            for item in self.result['data']:
                name = item['name']
                Management_path = os.path.join(self.Base_path, "Management", name)
                if os.path.isdir(Management_path):
                    for file_name in os.listdir(Management_path):
                        file_path = os.path.join(Management_path, file_name)
                        # file_name에서 DAY2와 snagwoo를 분리합니다.
                        if '_' in file_name:
                            day_part, name_part = file_name.split('_', 1)
                            # self.Day와 day_part를 비교하여 동일한 경우에만 파일을 엽니다.
                            if self.Day == "ALL" or day_part == self.Day:
                                if os.path.isfile(file_path):
                                    with open(file_path, 'r', encoding='utf-8') as file:
                                        try:
                                            # 파일 내용을 모두 읽어서 JSON 객체로 파싱
                                            content = json.load(file)
                                            all_data.append(content)
                                        except json.JSONDecodeError as e:
                                            print(f"{file_name} 파일을 파싱하는 중 오류가 발생했습니다: {str(e)}")
                else:
                    print(f"{Management_path} 디렉토리가 존재하지 않습니다.")
            
            # "맞춘 갯수"로 정렬
            sorted_data = sorted(all_data, key=lambda x: x["맞춘 갯수"], reverse=True)
            # "이름_과제" 리스트 생성
            sorted_names_tasks = [f"{item['과제']}_{item['이름']}_{item['맞춘 갯수']}" for item in sorted_data]
        
        elif text == "오답순":
            for item in self.result['data']:
                name = item['name']
                Management_path = os.path.join(self.Base_path, "Management", name)
                if os.path.isdir(Management_path):
                    for file_name in os.listdir(Management_path):
                        file_path = os.path.join(Management_path, file_name)
                        # file_name에서 DAY2와 snagwoo를 분리합니다.
                        if '_' in file_name:
                            day_part, name_part = file_name.split('_', 1)
                            # self.Day와 day_part를 비교하여 동일한 경우에만 파일을 엽니다.
                            if self.Day == "ALL" or day_part == self.Day:
                                if os.path.isfile(file_path):
                                    with open(file_path, 'r', encoding='utf-8') as file:
                                        try:
                                            # 파일 내용을 모두 읽어서 JSON 객체로 파싱
                                            content = json.load(file)
                                            all_data.append(content)
                                        except json.JSONDecodeError as e:
                                            print(f"{file_name} 파일을 파싱하는 중 오류가 발생했습니다: {str(e)}")
                else:
                    print(f"{Management_path} 디렉토리가 존재하지 않습니다.")
            
            # "틀린 갯수"로 정렬
            sorted_data = sorted(all_data, key=lambda x: x["틀린 갯수"], reverse=True)
            # "이름_과제" 리스트 생성
            sorted_names_tasks = [f"{item['과제']}_{item['이름']}_{item['틀린 갯수']}" for item in sorted_data]
        else:
            name = ""
            for item in self.result['data']:
                if text == item['name']:
                    name = item['name']
            Management_path = os.path.join(self.Base_path, "Management", name)
            if os.path.isdir(Management_path):
                for file_name in os.listdir(Management_path):
                    file_path = os.path.join(Management_path, file_name)
                    # file_name에서 DAY2와 snagwoo를 분리합니다.
                    if '_' in file_name:
                        day_part, name_part = file_name.split('_', 1)
                        # self.Day와 day_part를 비교하여 동일한 경우에만 파일을 엽니다.
                        if self.Day == "ALL" or day_part == self.Day:
                            if os.path.isfile(file_path):
                                with open(file_path, 'r', encoding='utf-8') as file:
                                    try:
                                        # 파일 내용을 모두 읽어서 JSON 객체로 파싱
                                        content = json.load(file)
                                        all_data.append(content)
                                    except json.JSONDecodeError as e:
                                        print(f"{file_name} 파일을 파싱하는 중 오류가 발생했습니다: {str(e)}")
            else:
                print(f"{Management_path} 디렉토리가 존재하지 않습니다.")
            
            # "틀린 갯수"로 정렬
            sorted_data = sorted(all_data, key=lambda x: x["맞춘 갯수"], reverse=True)
            # "이름_과제" 리스트 생성
            sorted_names_tasks = [f"{item['과제']}_{item['이름']}_{item['맞춘 갯수']}" for item in sorted_data]

        self.grade_list.clear()  # 기존 항목을 지우기 위해 추가
        if sorted_names_tasks:  # 리스트가 비어 있지 않을 때만 추가
            for item in sorted_names_tasks:
                self.grade_list.addItem(item)
        else:
            self.popupwindows("기록 없음","테스트 기록이 없습니다.")

    def clicked_record_list(self, item):
        itemtext = item.text()
        change_itemtext = itemtext.strip("\n")
        parts = change_itemtext.split("_")  # "_"를 기준으로 문자열 분리
        file_name = f"{parts[0]}_{parts[1]}"
        path = os.path.join(self.Base_path, "Management",parts[1],file_name)
        if self.Check_grades_windows is None or not self.Check_grades_windows.isVisible(): 
            self.Check_grades_windows = Check_grades_window(self,self.Base_path,path,parts[0]) 
            self.hide()
            self.Check_grades_windows.show()

    def Get_account(self):
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/Get_account.php')
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        return response.json()
    
    def Remove_account(self,name):
        post = {'name': name}
        response = requests.post('http://solimatics.dothome.co.kr/word_test_project/db/Remove_account.php', data=post)
        # 응답이 성공 메시지일 때 팝업 창 띄우기
        return response.json()

    def download_Management_file(self, result):
        SERVER_IP = self.report_dist["SERVER_IP"]
        PORT = self.report_dist["PORT"]
        username = self.report_dist["username"]
        password = self.report_dist["password"]
        session = ftplib.FTP()
        try:
            session.connect(SERVER_IP, PORT, timeout=10)
            session.login(username, password)
            
            for directory in result['data']:
                name = directory['name']
                remote_dir = f"/html/word_test_project/Management/{name}"
                try:
                    session.cwd(remote_dir)
                    print(f"디렉토리 이동 성공: {remote_dir}")

                    files = session.nlst()  # 현재 디렉토리의 모든 파일 목록을 가져옴
                    
                    for file_name in files:
                        Management_path = os.path.join(self.Base_path, "Management", name, file_name)
                        os.makedirs(os.path.dirname(Management_path), exist_ok=True)
                        with open(Management_path, "wb") as keyfile:
                            session.retrbinary("RETR " + file_name, keyfile.write)
                        print(f"다운로드 완료: {os.path.basename(file_name)}")

                except ftplib.error_perm as e:
                    print(f"디렉토리 접근 중 오류가 발생했습니다: {str(e)}")
                    continue

        except ftplib.all_errors as e:
            print(f"성적관리 파일 다운로드 중 오류가 발생했습니다: {str(e)}")
        finally:
            session.quit()

    def popupwindows(self,title,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        self.parents.show()
        event.accept()
