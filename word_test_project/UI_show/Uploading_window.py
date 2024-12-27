from UI_show.UI.wordlist_ui import Ui_uploading_windows
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)
class uploading_window(QMainWindow, Ui_uploading_windows):
    def __init__(self, parent=None, day=None):
        super(wordlist_window, self).__init__(parent)
        self.setupUi(self)
        self.day = day
        self.setWindowTitle(f"uploading for {day}")
        # Initialize other UI elements here if needed

        # Initialize variables and connect signals to slots
        self.word_Widgets = []
        self.Meaning_Widgets = []
        
        self.uploading = self.findChild(QPushButton, "upload")
        self.uploading.clicked.connect(self.uploading)
        
        for i in range(1, 41): 
            text_edit = self.findChild(QLabel, f"Word_{i}") 
            if text_edit: 
                self.word_Widgets.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit Word_{i} not found")  
            text_edit = self.findChild(QLabel, f"Meaning_{i}") 
            if text_edit: 
                self.Meaning_Widgets.append(text_edit) 
            else: 
                print(f"Warning: QTextEdit Meaning_{i} not found")  

    def uploading(self):
        pass
    
"""
app = QApplication(sys.argv)

window = test_Window()
window.show()

try:
    app_exec = app.exec
except AttributeError:
    app_exec = app.exec_
sys.exit(app_exec())
"""