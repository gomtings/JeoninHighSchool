import serial

serial_port = 'COM6'
ser = serial.Serial(serial_port, 9600, timeout = 1)

try : 
    while True : 
        sensor_value = ser.readline().decode('utf-8').rstrip()
        print(f"sensor value : {sensor_value}")
except KeyboardInterrupt : 
    ser.close()
    print("Serial connection closed")