# 아두이노 모터 python으로 제어
import serial

serial_port = 'COM6'
ser = serial.Serial(serial_port, 9600, timeout = 1)

move = False
try : 
    while True : 
        sensor_value = ser.readline().decode('utf-8').rstrip()
        try : sensor_value = int(sensor_value)
        except : 
            print("e :",sensor_value)
            continue
        if sensor_value >= 30 : 
            print(f"sensor value : {sensor_value}", end='\t')
            ser.write(b"1\n")
            print(True)
        elif sensor_value < 30 : 
            print(f"sensor value : {sensor_value}", end='\t')
            ser.write(b"0\n")
            print(False)
except KeyboardInterrupt : 
    ser.write(b"0\n")
    ser.close()
    print("Serial connection closed")