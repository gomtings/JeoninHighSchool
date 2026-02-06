import time
import numpy as np
import matplotlib
# 로컬/데스크톱 환경에서 창을 띄우기 위해 백엔드를 설정합니다.
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from rplidar import RPLidar, RPLidarException

# ⚠️ 시리얼 포트 설정: 실제 Lidar가 연결된 포트로 변경하세요.
PORT_NAME = 'COM7' 

# 📐 인식 및 시각화 임계값 설정
# ----------------------------------------------------
MAX_DISTANCE_CM = 50  # 50cm보다 가까우면 장애물로 간주 
MIN_VALID_DISTANCE_CM = 10 # 10cm 미만은 근거리 노이즈로 무시
ANGLE_MIN = 270       # 정면 180도 범위 시작 (왼쪽 90도)
ANGLE_MAX = 90        # 정면 180도 범위 끝 (오른쪽 90도)
# ----------------------------------------------------

# ⚙️ 연속 감지 로직은 그대로 유지합니다.
REQUIRED_CONSECUTIVE_SCANS = 3 
consecutive_detection_count = 0 

# ----------------------------------------------------------------------------------

def is_within_target_range(angle, distance_mm):
    """
    주어진 각도와 거리가 장애물 인식 범위와 임계값 내에 있는지 확인합니다.
    """
    distance_cm = distance_mm / 10.0 
    
    if distance_cm < MIN_VALID_DISTANCE_CM or distance_cm > MAX_DISTANCE_CM: 
        return False
        
    normalized_angle = angle % 360

    if ANGLE_MIN <= ANGLE_MAX:
        return ANGLE_MIN <= normalized_angle <= ANGLE_MAX
    else:
        return (normalized_angle >= ANGLE_MIN or normalized_angle <= ANGLE_MAX)

# ----------------------------------------------------------------------------------

def run_obstacle_detection_and_visualize():
    global consecutive_detection_count

    lidar = None
    try:
        print(f"Connecting to Lidar on port {PORT_NAME}...")
        lidar = RPLidar(PORT_NAME)
 
        print(f"Lidar Info: {lidar.get_info()}")
        
        # --- Matplotlib 시각화 설정 ---
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location("N") 
        ax.set_theta_direction(-1)     
        ax.set_rlim(0, 500)            
        ax.set_rticks(np.arange(0, 500, 100))
        # 초기 제목 설정
        ax.set_title("Lidar Real-time Scan & Obstacle Highlight", va='bottom')

        # 장애물 인식 영역(180도) 및 임계값(50cm) 시각화
        theta_rad_270 = np.deg2rad(270)
        theta_rad_360 = np.deg2rad(360)
        theta_rad_090 = np.deg2rad(90)

        ax.fill_between(np.linspace(theta_rad_270, theta_rad_360, 50), 0, MAX_DISTANCE_CM, color='red', alpha=0.1)
        ax.fill_between(np.linspace(np.deg2rad(0), theta_rad_090, 50), 0, MAX_DISTANCE_CM, color='red', alpha=0.1)
        ax.plot(np.linspace(theta_rad_090, theta_rad_270, 100), np.full(100, MAX_DISTANCE_CM), color='red', linestyle='--')
        
        # 데이터 포인트 객체 생성 (일반 스캔 데이터 - 검은색 점)
        line, = ax.plot([0], [0], 'ko', markersize=2)
        # 현재 프레임의 장애물 표시용 (파란색 X 마커)
        current_obstacle_line, = ax.plot([], [], 'bx', markersize=5, zorder=3) 

        plt.ion(); plt.show()
        print("\nStarting real-time scan loop...")
        
        for i, scan in enumerate(lidar.iter_scans()):
            
            # 장애물 감지 정보를 저장할 리스트. (거리 cm, 각도 deg) 쌍 저장
            current_scan_obstacles_polar_deg = []
            angles_rad = []
            distances_cm = []
            
            # 1. 현재 스캔 데이터 처리
            for quality, angle_deg, distance_mm in scan:
                
                distance_cm_current = distance_mm / 10.0
                
                if distance_mm > 0:
                    angles_rad.append(np.deg2rad(angle_deg))
                    distances_cm.append(distance_cm_current)
                
                # 인식 로직
                if is_within_target_range(angle_deg, distance_mm):
                    # 장애물로 인식된 점의 (거리, 각도)를 저장합니다.
                    current_scan_obstacles_polar_deg.append((distance_cm_current, angle_deg))

            # 2. 연속 감지 횟수 업데이트 및 최종 판단
            is_obstacle_in_current_scan = len(current_scan_obstacles_polar_deg) > 0
            
            # 잔상이 남지 않도록 이전 프레임의 장애물 마커를 초기화합니다.
            current_obstacle_line.set_xdata([])
            current_obstacle_line.set_ydata([])

            # 📌 가장 가까운 장애물 초기값 설정
            min_distance = 500 # 최대 측정 거리보다 큰 값으로 초기화
            closest_angle = -1.0 
            
            
            if is_obstacle_in_current_scan:
                consecutive_detection_count += 1
                
                if consecutive_detection_count >= REQUIRED_CONSECUTIVE_SCANS:
                    
                    # 3. 가장 가까운 장애물 찾기
                    for r, theta in current_scan_obstacles_polar_deg:
                        if r < min_distance:
                            min_distance = r
                            closest_angle = theta
                            
                    print(f"🚨 OBSTACLE DETECTED! Closest: {min_distance:.1f}cm @ {closest_angle:.1f}°")
                    
                    # 📌 잔상 없이 현재 감지된 장애물만 파란색 X로 표시
                    obs_r = [r for r, theta in current_scan_obstacles_polar_deg]
                    obs_theta = [np.deg2rad(theta) for r, theta in current_scan_obstacles_polar_deg]
                    
                    current_obstacle_line.set_xdata(obs_theta)
                    current_obstacle_line.set_ydata(obs_r)
                    
                    # 📌 Matplotlib 제목 업데이트
                    ax.set_title(f"Closest Obstacle: {min_distance:.1f}cm @ {closest_angle:.1f}°", va='bottom')
                    
                else:
                    print(f"⚠️ Potential Obstacle. (Count: {consecutive_detection_count}/{REQUIRED_CONSECUTIVE_SCANS})")
                    ax.set_title("Lidar Real-time Scan & Obstacle Highlight", va='bottom')
            else:
                consecutive_detection_count = 0
                print("✅ Path Clear.")
                # 📌 Matplotlib 제목 초기화
                ax.set_title("Lidar Real-time Scan & Obstacle Highlight", va='bottom')
            
            # 4. 일반 스캔 시각화 업데이트
            line.set_xdata(angles_rad)
            line.set_ydata(distances_cm)
            
            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            
            time.sleep(0.01) 

    except RPLidarException as e:
        print(f"RPLidar Error: {e}. Check power/cable or try a different port.")
    except KeyboardInterrupt:
        print("Visualization stopped by user.")
    finally:
        if lidar:
            print("Stopping motor and disconnecting.")
            lidar.stop()
            lidar.disconnect()

if __name__ == '__main__':
    run_obstacle_detection_and_visualize()
