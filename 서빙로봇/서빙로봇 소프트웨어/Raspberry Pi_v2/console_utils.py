"""
console_utils.py
콘솔 인코딩(예: Windows cp949)이 이모지 등을 인코딩하지 못해 print() 가 예외를
던지는 경우가 있다. 로그 출력 실패가 재연결/에러 처리 같은 실제 로직을 중단시키면
안 되므로, 그런 위험이 있는 print 는 이 헬퍼를 통해 조용히 실패하도록 한다.
"""


def safe_print(msg):
    try:
        print(msg)
    except Exception:
        pass
