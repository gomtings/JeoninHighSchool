# python测试代码：通过串口发送数据至arduino开发板
import threading
import serial
import time  
import struct

def read_from_serial(ser):
    try:
        while True:
            if ser.in_waiting > 0:
                data_bytes = ser.readline()
                espLog = data_bytes.decode('utf-8').rstrip()
                print(espLog)
            time.sleep(0.01)
    except serial.SerialException as e:
        print(f"cmdSer error: {e}")

if __name__ == "__main__":
    ser = serial.Serial('COM6', 115200)     # 请更改为你的串口号
    if ser.isOpen():  
        print("串口已打开")  
    else:  
        print("串口打开失败")  
        exit()  

    reader_thread = threading.Thread(target=read_from_serial, args=[ser])
    reader_thread.daemon = True 
    reader_thread.start()
    
    try:  
        while True:  
            checksum_bytes = b'\x01\xff' 
            motor1 = struct.pack('>h', 0)       # 电机1停止
            motor2 = struct.pack('>h', 123)     # 电机2转动，速度为123
            motor3 = struct.pack('>h', 255)     # 电机3全速转动，速度为255
            motor4 = struct.pack('>h', -255)    # 电机4全速反转，速度为-255
            svo1 =b'\x00'       # 舵机1角度为0度
            svo2 =b'\x3C'       # 舵机2角度为60度
            svo3 =b'\x5A'       # 舵机3角度为90度
            svo4 =b'\xB4'       # 舵机4角度为180度
            data_to_send = checksum_bytes + motor1 + motor2+ motor3 + motor4 + svo1 + svo2 + svo3 + svo4
            ser.write(data_to_send) 
            time.sleep(0.5)  
    except KeyboardInterrupt:  
        print("程序被用户中断")  
    finally:  
        ser.close()  