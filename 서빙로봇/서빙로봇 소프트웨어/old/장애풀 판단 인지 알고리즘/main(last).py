import threading
import time
import math
import json
import serial
from adafruit_rplidar import RPLidar, RPLidarException
import traceback

# import concurrent.futures

lidar_data = ((0,), (0,))
sensor_data = (0, 0, 0, 0, 0, 0, 0)
rplidar = None
ser = None
state = "ready"

initial_heading = None

lidar_stop = True   # 스레드 종료 전용
sensor_stop = True  # 스레드 종료 전용
update_stop = True  # 스레드 종료 전용
is_print = True

is_serial_stopped = False  # 센서 동결 확인 전용

position = [0, 0] # 초기 위치

tiltheading = td = None

def get_lidar_data(rplidar) :
    global lidar_data, lidar_stop

    while lidar_stop : 
        try : 
            for scan in rplidar.iter_scans() : 
                for (_, angle, distance) in scan : 
                    lidar_data = angle, distance
        except Exception as e : 
            if is_print : 
                print("error from rplidar :", e)
            traceback.print_exc()


def get_sensor_data(ser):
    global sensor_data, state, sensor_stop, is_serial_stopped, initial_heading

    while sensor_stop:
        try:
            # 우노에서의 데이터 받아오기
            sensor_value = ser.readline().decode('utf-8')  # .rstrip()
            if sensor_value != "" or sensor_value != None:
                # JSON 문자열을 Python 객체로 변환 (파(싱)
                data = json.loads(sensor_value)
                if isinstance(data, str) : 
                    # print("data is string")
                    continue
                new_sensor_data = (
                    data["distance1"],
                    data["distance2"],
                    data["Lidar"],
                    data["heading"],
                    data["tiltheading"],
                    data["TD"],
                    data["averageTD"]
                )
                if initial_heading == None : 
                    initial_heading = data["heading"]
                if new_sensor_data != sensor_data : 
                    sensor_data = new_sensor_data
        except TimeoutError as e:
            if is_print:
                print("JSON parsing timed out:", e)
            is_serial_stopped = True
        # time.sleep(1)
        except json.decoder.JSONDecodeError as e : 
            if is_print : 
                print("error from json :", e)
            # traceback.print_exc()
        except Exception as e:
            if is_print : 
                print("error from sensor :", e)
            traceback.print_exc()

# def update_position(tiltheading, td) : 
#     global position, update_stop
def update_position() :
    global position, update_stop, heading, td
    while update_stop : 
        if td : 
            position[0] = td * math.cos(math.radians(heading))
            position[1] = td * math.sin(math.radians(heading))
            time.sleep(1)

def rplidar_thread_stop() : 
    global lidar_stop
    lidar_stop = False

def sensor_thread_stop() : 
    global sensor_stop
    sensor_stop = False

def update_thread_stop() : 
    global update_stop
    update_stop = False

def main():
    global lidar_data, sensor_data, rplidar, ser, state, sensor_stop, heading, td, position, initial_heading

    # # daemon은 프로그램이 종료되면 스레드를 같이 종료하도록 하기 위해 사용
    # lidar_thread = threading.Thread(target=get_lidar_data, args=(rplidar,))
    # lidar_thread.daemon = True
    # lidar_thread.start()

    sensor_thread = threading.Thread(target=get_sensor_data, args=(ser,))
    sensor_thread.daemon = True
    sensor_thread.start()

    # position_thread = threading.Thread(target=update_position, args=(tiltheading, td,))
    position_thread = threading.Thread(target=update_position)
    position_thread.daemon = True
    position_thread.start()

    front = 50  # 정면 거리
    left = 30   # 왼쪽 거리
    right = 30  # 오른쪽 거리
    
    previous_state = None  # 이전 상태를 저장하는 변수
    
    temp_time = time.time()
    
    try:
        while True:
            try : 
                # 라이다 데이터 얻기(코드 수정으로 lidar_data에 자동으로 저장)
                # lidar_data는 (angle, dist) 형식으로, 별다른 주기 없이 계속 업데이트됨

                # 각각 초음파1, 초음파2, 라이다, 지자기 센서, 이동 거리
                dist1, dist2, lidar, heading, tiltheading, _, td = sensor_data
                # try : tiltheading -= initial_heading
                try : heading -= initial_heading
                except : pass
                td *= -0.01
                
                # 초음파 센서(HC-SR04) 감지 범위(5cm~500cm라고 함)
                if dist1 >= 500 : 
                    dist1 = 500
                if dist2 >= 500 : 
                    dist2 = 500
                if 0 < dist1 and dist1 < 5 : 
                    dist1 = 5
                if 0 < dist2 and dist2 < 5 : 
                    dist2 = 5
    
                if is_print : 
                    print(
                            # f"dist1: {dist1 if dist1 is not None else 0:<10}, "
                            # f"dist2: {dist2 if dist2 is not None else 0:<10}, "
                            # f"lidar: {lidar if lidar is not None else 0:<10}, "
                            # f"heading: {heading if heading is not None else 0:<10}, "
                            f"heading: {round(heading, 4) if heading is not None else 0:<10}", end=""
                        )
                    print(f"td : {round(td, 3):<10}", end="")
                    print_position = list(map(round, position))
                    print(f"position : {str(print_position):<10}", end="")
                    print(f"state : {state:<10}")

                if (dist1, dist2, lidar) == (0, 0, 0): 
                    state = 'ready'
                else: 
                    if dist1 <= left and dist2 <= right : 
                        if lidar <= front: 
                            if dist1 > dist2 : 
                                state = 'turn_left'
                            else: 
                                state = 'turn_right'
                        else: 
                            state = 'go_forward'

                    elif dist1 <= left : 
                        state = 'go_right'

                    elif dist2 <= right : 
                        state = 'go_left'

                    else : 
                        if lidar <= front: 
                            if dist1 > dist2 : 
                                state = 'turn_left'
                            else: 
                                state = 'turn_right'
                        else: 
                            state = 'go_forward'

                # state가 이전 상태와 다를 때만 시리얼에 작성
                if state != previous_state:
                    if state == 'turn_right':
                        ser.write(b"turn_right\n")
                    elif state == 'turn_left': 
                        ser.write(b"turn_left\n")
                    elif state == 'go_left': 
                        ser.write(b"go_left\n")
                    elif state == 'go_right':
                        ser.write(b"go_right\n")
                    elif state == 'go_forward':
                        ser.write(b"forward\n")
                    
                    previous_state = state  # 이전 상태 업데이트

                    # print(state)

                # 처음에 ready 없이 바로 forward 입력 시 전송이 안 되는 오류 수정
                if time.time() - temp_time >= 1 and state == 'go_forward' : 
                    ser.write(b"forward\n")
                    temp_time = time.time()

                # 센서값 동결 확인 및 예외 처리
                if is_serial_stopped : 
                    print("Sensor frozed detect. Attempting to reconnect...")
                    if ser : 
                        sensor_thread_stop()
                        sensor_thread.join()
                        ser.close()
                    print("test")
                    break

            except TypeError as e : 
                if is_print: 
                    print("error from main :", e)
                    # traceback.print_exc()

    except KeyboardInterrupt:
        ser.write(b"stop\n")
        sensor_thread_stop()
        # lidar_thread.join()
        sensor_thread.join()
        # rplidar_thread_stop()
        # lidar_thread.join()
        update_thread_stop()
        if ser:
            ser.close()
        if rplidar:
            rplidar.stop()
            rplidar.disconnect()
        traceback.print_exc()
    

if __name__ == "__main__":
    # rplidar_port = 'COM6'
    # rplidar = RPLidar(None, rplidar_port, timeout=3)

    sensor_port = 'COM10'  # 실제 확인 필요
    ser = serial.Serial(sensor_port, 9600, timeout=1)

    print("start")

    main()