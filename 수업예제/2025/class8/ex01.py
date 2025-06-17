import threading
import time
from mqtt_module import MQTTClient
#pip install paho-mqtt

class Chat:
    def __init__(self):
        self.local = MQTTClient(False)  # 관리 프로그램과 통신 할 MQTT 로컬연결..
        self.local.localconnect()  # MQTT 서버 연결
        self.local.loop_start()  # MQTT 시작
        self.local.subscribe("Event/State/")
        self.name = None
        self.friend = {}
        self.subscribe = {}
        self.interest_thread = None
        self.running = False  # 쓰레드 실행 상태 관리
        
    def Change_name(self):
        owner = input("사용자의 이름을 입력해 주세요.")
        self.name = owner
        print(f"사용자 이름을 변경 하였습니다.{self.name}")

    def ChatMsg(self):
        owner = input("체팅할 사용자의 이름을 입력해 주세요.")
        friend = self.friend.get(owner,None)
        if friend:
            subscribe = self.subscribe.get(friend,None)
            if not subscribe:
                msg = f"Event/Chat/{friend}"
                self.subscribe[friend] = msg 
                self.local.subscribe(msg)
        else:
            print(f"{owner} 검색된 사용자가 없습니다.")

    def CloseChat(self):
        owner = input("체팅할 사용자의 이름을 입력해 주세요.")
        friend = self.friend.get(owner,None)
        if friend:
            subscribe = self.subscribe.get(friend,None)
            if not subscribe:
                msg = f"Event/Chat/{friend}"
                del self.subscribe[friend]
                self.local.unsubscribe(msg)
        else:
            print(f"{owner} 검색된 사용자가 없습니다.")
                
    def interest_loop(self):
        while self.running:
            time.sleep(10)  # 1분마다 실행
            self.local.msg("Event/State/", self.name)  # 주변에 내 닉네임을 발송함.
            
            msg = self.local.get_State_message()
            if msg !=self.name:
                self.friend[msg] = msg
                self.local.update_friend(self.friend)
                
    def start_interest_system(self):
        # 실행 중이면 중단
        if self.interest_thread and self.interest_thread.is_alive():
            self.running = False
            self.interest_thread.join()  # 기존 쓰레드 종료
            print("쓰레드가 중단되었습니다.")

        # 새로운 쓰레드 실행
        self.running = True
        self.interest_thread = threading.Thread(target=self.interest_loop, daemon=True)
        self.interest_thread.start()
        print("새로운 쓰레드가 시작되었습니다.")

    def run(self):
        while True:
            print("\n=== 은행 시스템 메뉴 ===")
            print("1. 사용자 이름 변경")
            print("2. 사용자 검색 하용/차단")
            print("3. 채팅 하기")
            print("4. 채팅 종료")
            
            choice = input("원하는 기능을 선택하세요: ")
            if choice == "1":
                self.Change_name()
            elif choice == "2":
                self.start_interest_system()
            elif choice == "3":
                self.ChatMsg()                
            elif choice == "4":
                self.CloseChat()                  
# 시스템 실행
bank_system = Chat()
bank_system.Change_name()
bank_system.run()
