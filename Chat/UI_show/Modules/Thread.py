from PySide6.QtCore import QThread,Signal,QMutex, QWaitCondition

class InterestThread(QThread):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.running = True
        self.parent = parent
        self.name = name

    def run(self):
        while self.running:
            self.sleep(1)  # 1초마다 실행
            self.parent.local.msg("Event/State/", self.name)  # 닉네임 발송

    def stop(self):
        self.running = False

class getfriendThread(QThread):
    update_signal = Signal(dict)  # 친구 목록 업데이트 시그널

    def __init__(self, parent, name):
        super().__init__(parent)
        self.running = True
        self.parent = parent
        self.name = name
        self.friend = {}

    def run(self):
        while self.running:
            msg = self.parent.local.get_State_message()
            if msg != self.name:
                self.friend[msg] = msg
                self.update_signal.emit(self.friend)  # 친구 목록 업데이트 시그널 송신

    def stop(self):
        self.running = False