# 아두이노 모터 python으로 제어
import serial
import json

serial_port = 'COM7'
ser = serial.Serial(serial_port, 9600, timeout = 1)

move = False
try : 
    while True : 
        try :
            #우노에서의 데이터 받아오기
            sensor_value = ser.readline().decode('utf-8')#.rstrip()
            #print(sensor_value)
            if sensor_value !="" or sensor_value !=None:
                # JSON 문자열을 Python 객체로 변환 (파(싱)
                data = json.loads(sensor_value)
                # 파싱된 데이터 출력
                distance1 = data["distance1"]
                distance2 = data["distance2"]
                Lidar = data["Lidar"]
                heading = data["heading"]
                tiltheading = data["tiltheading"]
                print(distance1)
                print(distance2)
                print(Lidar)
                print(heading)
                print(tiltheading)
            else :
                print("----")    
        except Exception as e:
            print("error :", e)
            continue
except KeyboardInterrupt : 
    ser.write(b"0\n")
    ser.close()
    print("Serial connection closed")