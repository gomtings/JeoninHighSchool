# 아두이노 센서값 얻기

import serial
import time

py_serial = serial.Serial(
    port = 'COM3',
    baudrate = 9600 
)

while True : 

    time.sleep(0.1)

    if py_serial.readable() : 
        response = py_serial.readline()

        print(response[:len(response)-1].decode())