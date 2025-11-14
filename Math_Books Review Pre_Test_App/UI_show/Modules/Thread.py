from PySide6.QtCore import QThread,Signal,QMutex, QWaitCondition

class singleThread(QThread):
    result_signal = Signal(object)  # 딕셔너리를 전달할 신호

    def __init__(self, path, get_time_func):
        super().__init__()
        self.path = path
        self.get_time_func = get_time_func  # ⬅️ 함수 전달

    def run(self):
        temp = self.get_time_func(self.path)  # 전달된 함수 실행
        self.result_signal.emit(temp)  # 결과를 메인 스레드로 전달
                   
class Worker(QThread):
    updated = Signal()  # 시그널 정의
    def __init__(self, sleep_time=0):
        super().__init__()
        self.sleep_time = sleep_time
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:  # 플래그가 True인 동안 반복
            self.mutex.lock()
            self.condition.wait(self.mutex, self.sleep_time * 1000)  # 설정된 주기로 대기
            self.mutex.unlock()
            if self.running:
                self.updated.emit()  # 시그널 발생
    
    def state(self):
        return self.running
    
    def stop(self):
        self.running = False  # 쓰레드를 멈추기 위해 플래그를 False로 설정합니다.
        self.condition.wakeAll()  # 대기 중인 스레드 깨우기
        
class AnalysisThread(QThread):
    update_button = Signal(str, bool, str, int)
    update_Calendar = Signal()
    update_Log = Signal(str,str,str)
    update_3DGraph = Signal(str, bool)
    clearFocus = Signal()
    def __init__(self, parent, date, num):
        super().__init__(parent)
        self.date = date
        self.num = num
    
    def is_running(self):
        return self.isRunning()
    
    def run(self):
        self.parent().user_analysis(self.date, self.num)

class ExtractThread(QThread):
    def __init__(self, parent, today, folder_name, thread_id):
        super().__init__(parent)
        self.today = today
        self.folder_name = folder_name
        self.thread_id = thread_id
    
    def is_running(self):
        return self.isRunning()
    
    def run(self):
        self.parent().extract_data(self.today, self.folder_name, self.thread_id)