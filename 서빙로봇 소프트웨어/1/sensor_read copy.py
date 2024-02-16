import serial
import time

# Arduino와 통신할 시리얼 포트 지정
serial_port = 'COM3'  # Windows 예시
# serial_port = '/dev/ttyACM0'  # Linux 예시

# 시리얼 통신 설정
ser = serial.Serial(serial_port, 9600)  # Arduino 코드에서 사용된 보드 속도와 일치시킵니다.


while True:
    time.sleep(0.1)
    # Arduino로부터 데이터 읽기
    print(ser.readline().decode().strip())
