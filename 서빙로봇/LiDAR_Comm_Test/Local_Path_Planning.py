import sys
import numpy as np
import pyqtgraph as pg
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QThread, Signal, Qt
from rplidar import RPLidar

# --- [설정] ---
PORT_NAME = 'COM7'
BAUDRATE = 115200
MAX_DISTANCE_MM = 3000   # 3미터 이내 데이터만 사용
ROBOT_WIDTH_MM = 500     # 로봇의 실제 폭 (여유값 포함)
CLUSTER_THRESHOLD = 150  # 점들 사이의 거리가 150mm 이내면 하나의 물체로 판단

class NavigationThread(QThread):
    update_data = Signal(dict)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        lidar = None
        try:
            print(f"Connecting to Lidar on {PORT_NAME}...")
            lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE)
            lidar.start_motor()
            lidar.clean_input()
            print("Lidar motor started. Waiting for scans...")

            for scan in lidar.iter_scans(max_buf_meas=1000):
                if not self.running: break
                
                # print(f"Scan received: {len(scan)} points") # 주석 해제하면 데이터 수신 확인 가능

                points = []
                for _, angle, dist in scan:
                    if 0 < dist < MAX_DISTANCE_MM:
                        rad = np.deg2rad(angle)
                        # 좌표 변환 (0도 = 정면 위쪽)
                        x = dist * np.sin(rad)
                        y = dist * np.cos(rad)
                        points.append({'x': x, 'y': y, 'dist': dist, 'angle': angle})

                if not points:
                    continue

                # 1. 군집화 (Clustering)
                points.sort(key=lambda p: p['angle'])
                clusters = []
                current_cluster = [points[0]]
                for i in range(1, len(points)):
                    p1 = points[i-1]
                    p2 = points[i]
                    dist_diff = math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)
                    if dist_diff < CLUSTER_THRESHOLD:
                        current_cluster.append(p2)
                    else:
                        clusters.append(current_cluster)
                        current_cluster = [p2]
                clusters.append(current_cluster)

                # 2. 객체 분석 및 장애물 분류
                obstacles_x, obstacles_y = [], []
                people_x, people_y = [], []
                danger_zones = []

                for c in clusters:
                    if len(c) < 2: continue
                    width = math.sqrt((c[0]['x']-c[-1]['x'])**2 + (c[0]['y']-c[-1]['y'])**2)
                    avg_dist = sum(p['dist'] for p in c) / len(c)
                    angles = [p['angle'] for p in c]
                    min_a, max_a = min(angles), max(angles)
                    
                    if 200 < width < 800 and len(c) > 10: # 점이 최소 10개는 모여야 사람으로 의심
                        people_x.extend([p['x'] for p in c])
                        people_y.extend([p['y'] for p in c])
                    else:
                        # [버그 수정] append -> extend
                        obstacles_x.extend([p['x'] for p in c])
                        obstacles_y.extend([p['y'] for p in c])
                    
                    buffer_angle = math.degrees(math.atan2(ROBOT_WIDTH_MM/2, avg_dist))
                    danger_zones.append((min_a - buffer_angle, max_a + buffer_angle))

                # 3. 경로 탐색 (Gap Finding)
                best_angle = None
                possible_angles = np.arange(-45, 46, 1)
                
                for a in possible_angles:
                    norm_a = a if a >= 0 else 360 + a
                    is_safe = True
                    for start, end in danger_zones:
                        if start <= norm_a <= end:
                            is_safe = False
                            break
                    if is_safe:
                        best_angle = a
                        break

                decision = "GO STRAIGHT" if best_angle == 0 else f"TURN {best_angle}" if best_angle else "STOP/SEARCH"

                # UI 전송
                self.update_data.emit({
                    'obs_x': obstacles_x, 'obs_y': obstacles_y,
                    'peo_x': people_x, 'peo_y': people_y,
                    'best_angle': best_angle,
                    'decision': decision
                })

        except Exception as e:
            print(f"Lidar Error: {e}")
        finally:
            if lidar:
                lidar.stop()
                lidar.stop_motor()
                lidar.disconnect()
            print("Lidar disconnected.")

class MappingVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Perception & Navigation")
        self.resize(800, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 상태 표시 라벨
        self.status_label = QLabel("Waiting for Lidar...")
        self.status_label.setStyleSheet("font-size: 20px; color: yellow; background-color: black; padding: 10px;")
        layout.addWidget(self.status_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('k')
        self.plot_widget.setXRange(-2000, 2000)
        self.plot_widget.setYRange(-500, 3000)
        layout.addWidget(self.plot_widget)

        # 일반 장애물 (회색 점)
        self.obs_scatter = pg.ScatterPlotItem(size=4, brush=pg.mkBrush(150, 150, 150, 255))
        # 사람 추정 (빨간색 점)
        self.peo_scatter = pg.ScatterPlotItem(size=6, brush=pg.mkBrush(255, 0, 0, 255))
        # 추천 경로 (초록색 선)
        self.path_line = self.plot_widget.plot(pen=pg.mkPen('g', width=5))
        
        self.plot_widget.addItem(self.obs_scatter)
        self.plot_widget.addItem(self.peo_scatter)

        # 로봇 마커
        self.robot_marker = pg.ScatterPlotItem(size=20, brush='y', symbol='t')
        self.robot_marker.setData(x=[0], y=[0])
        self.plot_widget.addItem(self.robot_marker)

        self.thread = NavigationThread()
        self.thread.update_data.connect(self.update_view)
        self.thread.start()

    def update_view(self, data):
        self.obs_scatter.setData(x=data['obs_x'], y=data['obs_y'])
        self.peo_scatter.setData(x=data['peo_x'], y=data['peo_y'])
        self.status_label.setText(f"Decision: {data['decision']}")

        # 추천 경로 그리기
        if data['best_angle'] is not None:
            angle_rad = np.deg2rad(data['best_angle'])
            # 1미터 길이의 추천 방향 선
            lx = [0, 1000 * np.sin(angle_rad)]
            ly = [0, 1000 * np.cos(angle_rad)]
            self.path_line.setData(lx, ly)
            self.path_line.setPen(pg.mkPen('g', width=5))
        else:
            self.path_line.setData([], []) # 갈 곳이 없으면 선을 지움

    def closeEvent(self, event):
        self.thread.running = False
        self.thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MappingVisualizer()
    window.show()
    sys.exit(app.exec())