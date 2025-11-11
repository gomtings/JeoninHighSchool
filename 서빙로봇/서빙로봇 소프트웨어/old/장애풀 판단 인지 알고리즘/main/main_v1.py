import threading
import time
import math
import json
import serial
from adafruit_rplidar import RPLidar, RPLidarException
from lidar_to_grid_map import lidar_to_grid_map
import traceback

lidar_data = ((0,), (0,))
sensor_data = (0, 0, 0, 0, 0)
rplidar = None
ser = None
state = "ready"

sensor_stop = True
is_print = True

def get_lidar_data(rplidar) :
    global lidar_data

    while True:
        try:
            scan_data = []
            t = 0
            for scan in rplidar.iter_scans():
                for (_, angle, distance) in scan:
                    if t > 0:
                        processed_angle = math.radians(float(angle - 90))
                        processed_dist = float(distance) / 1000
                        if angle:  # 각도 범위, 이후에 실제로 장착해서 범위 지정
                            scan_data.append((processed_angle, processed_dist))
                            # 가려진 각도 확인하기 위해서 로봇 회전시키기
                            # 라이다 값 얻을때마다 회전해야 하기에 딜레이를 주는 것도 고려
                t += 1
                if t == 3:
                    scan_data.sort(key=lambda x: x[0])
                    angle, dist = zip(*scan_data)
                    lidar_data = angle, dist
                    break
            # time.sleep(1)
        except RPLidarException as error:  # get_lidar_data에서 발생하는 오류
            if is_print: 
                print(f"error from rplidar : {error}")
            rplidar.stop()
            rplidar.disconnect()
            # rplidar = RPLidar(None, rplidar_port, timeout=3)

def get_sensor_data(ser):
    global sensor_data, state, sensor_stop

    while sensor_stop:
        try:
            # 우노에서의 데이터 받아오기
            sensor_value = ser.readline().decode('utf-8')  # .rstrip()
            if sensor_value != "" or sensor_value != None:
                # JSON 문자열을 Python 객체로 변환 (파(싱)
                data = json.loads(sensor_value)
                sensor_data = (
                    data["distance1"],
                    data["distance2"],
                    data["Lidar"],
                    data["heading"],
                    data["tiltheading"]
                )
        except Exception as e:
            if is_print : 
                print("error from sensor :", e)
            # traceback.print_exc()
        # time.sleep(1)

def sensor_thread_stop() : 
    global sensor_stop
    sensor_stop = False

def main():
    global lidar_data, sensor_data, rplidar, ser, state, sensor_stop


    # lidar_thread = threading.Thread(target=get_lidar_data, args=(rplidar,))
    # # daemon은 프로그램이 종료되면 스레드를 같이 종료하도록 하기 위해 사용
    # lidar_thread.daemon = True
    # lidar_thread.start()

    sensor_thread = threading.Thread(target=get_sensor_data, args=(ser,))
    sensor_thread.daemon = True
    sensor_thread.start()


    front = 50  # 정면 거리
    left = 30   # 왼쪽 거리
    right = 30  # 오른쪽 거리
    
    previous_state = None  # 이전 상태를 저장하는 변수
    
    last_print_time = time.time()
    temp_time = time.time()

    try:
        while True:
            try : 
                # 라이다 데이터 얻기(라이다 연결 필요)
                angle, dist = lidar_data
                # map = lidar_to_grid_map(angle, dist, is_show=False)
                # map 기준 위쪽이 라이다 앞방향

                # 각각 초음파1, 초음파2, 라이다, 지자기 센서
                dist1, dist2, lidar, heading, tiltheading = sensor_data
                if (dist1, dist2, lidar, heading, tiltheading) == (0, 0, 0, 0, 0):
                    pass  # 센서값이 모두 0이면 에러 발생 >>> 예외 처리

                # heading과 tiltheading은 동일한 값을 가짐. 입맛따라 사용
                # print(f"dist1 : {dist1:<10}, dist2 : {dist2:<10},lidar : {lidar:<10}, heading : {heading:<10}, tiltheading : {tiltheading:<10}", end="")
                
                # if (is_print) and (time.time() - last_print_time >= 0.2) :
                if is_print :
                    print(f"dist1 : {dist1 if dist1 is not None else 0:<10}, dist2 : {dist2 if dist2 is not None else 0:<10}, lidar : {lidar if lidar is not None else 0:<10}, heading : {heading if heading is not None else 0:<10}, tiltheading : {tiltheading if tiltheading is not None else 0:<10}", end="")
                    print(f"rplidar : {round(angle[0], 4):<10}", end="")
                    print(f"state : {state:<10}")
                    last_print_time = time.time()

                # 센서값 동결 에러 해결. 실제로 작동하는지 확인 필요
                if not ser : 
                    # COM7 나중에 수정해야 할지도
                    ser = serial.Serial('COM7', 9600, timeout=1)
                    print("test")
                    break


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

                    print(state)

                # 처음에 ready 없이 바로 forward 입력 시 전송이 안 되는 오류 수정
                if time.time() - temp_time >= 1 and state == 'go_forward' : 
                    ser.write(b"forward\n")
                    temp_time = time.time()

            except TypeError as e : 
                if is_print: 
                    print("error from main :", e)
                    traceback.print_exc()

    except KeyboardInterrupt:
        ser.write(b"stop\n")
        if ser:
            ser.close()
        if rplidar:
            rplidar.stop()
            rplidar.disconnect()
        sensor_thread_stop()
        # lidar_thread.join()
        sensor_thread.join()
    

if __name__ == "__main__":
    # rplidar_port = 'COM3'
    # rplidar = RPLidar(None, rplidar_port, timeout=3)

    sensor_port = 'COM7'  # 실제 확인 필요
    ser = serial.Serial(sensor_port, 9600, timeout=1)

    print("start")

    main()




# 센서값 이전과 같은 예외 처리하기(센서 오작동 방지용)


"""
(딜레이 없을 때)
딜레이 없이는 회전 각도가 지나치게 큼. - 파이썬에서 명령 전달하는 데 딜레이가 있어서?, 정면 인식 거리가 길어서


(딜레이 주어졌을 때)
딜레이 시간이 명확하지 않음.
그닥 유동적이지 않음


"""

# 20240618 주행 어느 정도 완성되었고, 반응속도 높이기 위해 arduino sendtime을 500에서 100으로 수정
# 모터 연결 부분에 문제가 있어서 실행은 못해봄. 이후에 해봐야 함.