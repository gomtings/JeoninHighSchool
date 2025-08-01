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
            self.parent.local.msg("Event/Chat/State/", self.name)  # 닉네임 발송

    def isRunning(self):
        return self.running

    def stop(self):
        self.running = False

class getfriendThread(QThread):
    update_signal = Signal(object)  # 친구 목록 업데이트 시그널
    search_signal = Signal(object)  # 친구 목록 업데이트 시그널

    def __init__(self, parent, name):
        super().__init__(parent)
        self.running = True
        self.parent = parent
        self.name = name
        self.friend = []

    def run(self):
        while self.running:
            self.sleep(1)
            msg = self.parent.local.get_State_message()
            if msg != self.name and msg not in self.friend:
                self.friend.append(msg)
                self.update_signal.emit(self.name)  # 친구 목록 업데이트 시그널 송신
                self.search_signal.emit(self.friend)

    def stop(self):
        self.running = False

class get_ChatMsg_Thread(QThread):
    update_Msg_signal = Signal(object)  # 친구 목록 업데이트 시그널

    def __init__(self, parent, name):
        super().__init__(parent)
        self.running = True
        self.parent = parent
        self.name = name
        self.Chat_msg = {}

    def run(self):
        while self.running:
            self.sleep(1)
            msg = self.parent.local.get_Chat_message()
            self.Chat_msg = msg
            self.update_Msg_signal.emit(self.Chat_msg)  # 친구 목록 업데이트 시그널 송신


    def stop(self):
        self.running = False
