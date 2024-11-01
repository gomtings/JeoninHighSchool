from Day1_wordlist import Ui_Day1_wordlist
from PySide6.QtWidgets import *
import Login


class Main_Windows(QMainWindow,Ui_Day1_wordlist):
    def __init__(self):
        super(Main_Windows, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Integrated_Control_System")

    def Day1_wordlist(self):
        if not hasattr(self, "Day1_wordlist") or not self.login_window.isVisible():
            self.login_window = Login.Login_Windows(self)
            self.login_window.show()