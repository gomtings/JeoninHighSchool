import threading
import time

# 계산이 많이 필요한 함수 정의
def print_numbers():
    for i in range(1, 6):
        print(f"숫자: {i}")
        time.sleep(1)  # 1초 대기
    print("print_numbers 함수 완료")

def repeat_function(target, interval):
    while True:
        thread = threading.Thread(target=target)
        thread.start()
        thread.join()  # 함수가 완료될 때까지 대기
        print("다시 실행하기 전 대기 중...")
        time.sleep(interval)  # 일정 시간 대기 후 다시 실행

# 스레드를 이용해 함수 반복 실행
interval = 5  # 5초 간격으로 반복 실행
repeater_thread = threading.Thread(target=repeat_function, args=(print_numbers, interval))
repeater_thread.start()
