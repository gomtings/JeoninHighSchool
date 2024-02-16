# 라이다 센서 값 처리

import serial
import time
import json

serial_port = 'COM6'
ser = serial.Serial(serial_port, 9600, timeout = 1)

while True : 
    try : 
        sensor_str_value = ser.readline().decode('utf-8').rstrip()
        sensor_value = json.loads(sensor_str_value)
        print(sensor_value['Accel_x'], end='\t')
        print(sensor_value['Accel_y'], end='\t')
        print(sensor_value['Accel_z'])
    except KeyboardInterrupt : 
        print("Serial connection closed")
        break
    except :
        print("비어있거나 잘못된 문자열을 받았습니다")
        continue