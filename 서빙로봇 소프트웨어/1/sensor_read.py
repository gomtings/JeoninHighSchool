# 아두이노 센서값 얻기
# *아두이노 초음파 센서값은 보통 2cm~400cm이다.

import serial
import time

py_serial = serial.Serial(
    # 포트 번호(COMx)
    port = 'COM3',
    # 보드 레이트(통신 속도)
    baudrate = 9600 
)

while True : 

    # command = input('start message')
    # py_serial.write(command.encode())

    time.sleep(0.1)

    # 센서값 존재 여부
    if py_serial.readable() : 
        # 센서값 한 줄 읽기 (센서값은 BITE 단위로 들어옴)
        # 예 : b'\xec\x97\x86\xec\x9d\x8c\r\n' ('없음'을 의미)
        # 예 : b'100.00cm\r\n'                 (센서값이 존재할 때)
        response = py_serial.readline()

        # 디코딩 및 출력 ('\n'을 제외함)
        print(response[:len(response)-1].decode())