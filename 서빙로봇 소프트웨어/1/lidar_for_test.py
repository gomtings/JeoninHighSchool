# 라이다 센서 처리(임의의 값)

import serial
import time
import json
import time

# serial_port = 'COM6'
# ser = serial.Serial(serial_port, 9600, timeout = 1)

try : 
    while True : 
        lidar_str_value = '{"distance1":20,"distance2":5,"Lidar":44,"Accel_x": 100,"Accel_y":30,"Accel_z":-90}'
        try : 
            lidar_value = json.loads(lidar_str_value)
            # print(lidar_value)
            time.sleep(1)
        except KeyboardInterrupt : 
            print("Serial connection closed")
            break
        except :
            print("비어있거나 잘못된 문자열을 받았습니다")
            time.sleep(1)
            continue
        print(lidar_value['Lidar'])
except KeyboardInterrupt : 
    print("Serial connection closed")