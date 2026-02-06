import sys, math, asyncio
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QThread, Signal
from rplidar import RPLidar
from bleak import BleakScanner, BleakClient

# --- [설정] ---
PORT_NAME = 'COM7'
BAUDRATE = 115200
MAX_DISTANCE_MM = 3000
ROBOT_WIDTH_MM = 600
CLUSTER_THRESHOLD = 400     # 점들을 연결할 최대 거리 (의자 다리 사이가 가까우면 연결됨)

# ---------------- Navigation Thread ----------------
class NavigationThread(QThread):
    update_data = Signal(dict)

    def __init__(self, ble_thread=None):
        super().__init__()
        self.running = True
        self.ble_thread = ble_thread

    def run(self):
        lidar = None
        try:
            lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE)
            lidar.start_motor()
            lidar.clean_input()

            for scan in lidar.iter_scans(max_buf_meas=1000):
                if not self.running: break
                points = []
                for _, angle, dist in scan:
                    if 150 < dist < MAX_DISTANCE_MM:
                        rad = np.deg2rad(angle)
                        points.append({'x': dist * np.sin(rad), 'y': dist * np.cos(rad), 'dist': dist, 'angle': angle})

                if not points: continue
                points.sort(key=lambda p: p['angle'])

                # --- 군집화 (Clustering) ---
                clusters, current_cluster = [], [points[0]]
                for i in range(1, len(points)):
                    p1, p2 = points[i-1], points[i]
                    if math.hypot(p1['x']-p2['x'], p1['y']-p2['y']) < CLUSTER_THRESHOLD:
                        current_cluster.append(p2)
                    else:
                        clusters.append(current_cluster)
                        current_cluster = [p2]
                clusters.append(current_cluster)

                # --- 객체 분석 및 분류 ---
                wall_segments = []  # 연결된 벽 데이터
                obs_x, obs_y = [], []
                people_x, people_y = [], []
                danger_zones = []

                for c in clusters:
                    if len(c) < 2: continue
                    
                    # 군집의 물리적 폭 계산
                    width = math.hypot(c[0]['x']-c[-1]['x'], c[0]['y']-c[-1]['y'])
                    avg_dist = sum(p['dist'] for p in c) / len(c)
                    
                    # 1. 사람 판별 (폭이 20cm~80cm 사이일 때)
                    if 200 < width < 800 and len(c) > 5:
                        people_x.extend([p['x'] for p in c])
                        people_y.extend([p['y'] for p in c])
                    else:
                        # 2. 벽/장애물로 처리 (점으로 표시 + 선으로 연결 데이터 생성)
                        obs_x.extend([p['x'] for p in c])
                        obs_y.extend([p['y'] for p in c])
                        # 시각화를 위해 클러스터의 점들을 순서대로 연결하는 좌표 리스트
                        wall_segments.append({'x': [p['x'] for p in c], 'y': [p['y'] for p in c]})

                    # 위험 구역 계산 (경로 계산용)
                    margin_angle = math.degrees(math.atan2(ROBOT_WIDTH_MM/2 + 100, avg_dist))
                    danger_zones.append(((min(p['angle'] for p in c)-margin_angle)%360, (max(p['angle'] for p in c)+margin_angle)%360))

                # --- 경로 탐색 ---
                best_angle = None
                for a in np.arange(-60, 61, 2):
                    target_a = a if a >= 0 else 360 + a
                    is_safe = True
                    for start, end in danger_zones:
                        if start < end:
                            if start <= target_a <= end: is_safe = False; break
                        else:
                            if target_a >= start or target_a <= end: is_safe = False; break
                    if is_safe:
                        best_angle = a; break

                self.update_data.emit({
                    'obs_x': obs_x, 'obs_y': obs_y,
                    'people_x': people_x, 'people_y': people_y,
                    'wall_segments': wall_segments,
                    'best_angle': best_angle,
                    'decision': "GO" if best_angle is not None else "STOP"
                })

        except Exception as e: print(f"Error: {e}")
        finally:
            if lidar: lidar.stop(); lidar.stop_motor(); lidar.disconnect()

# ---------------- UI (시각화 개선) ----------------
class MappingVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Perception: Walls vs People")
        self.resize(800, 850)
        
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setXRange(-2000, 2000)
        self.plot_widget.setYRange(-500, 3000)
        layout.addWidget(self.plot_widget)

        # 1. 일반 장애물 (점)
        self.obs_scatter = pg.ScatterPlotItem(size=5, brush='r')
        # 2. 사람 (파란색 점으로 구분)
        self.people_scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(0, 191, 255), symbol='d')
        # 3. 벽 연결선들 (여러 개의 선을 관리하기 위한 리스트)
        self.wall_items = []
        # 4. 경로선
        self.path_line = self.plot_widget.plot(pen=pg.mkPen('g', width=5))
        
        self.plot_widget.addItem(self.obs_scatter)
        self.plot_widget.addItem(self.people_scatter)

        self.lidar_thread = NavigationThread()
        self.lidar_thread.update_data.connect(self.update_view)
        self.lidar_thread.start()

    def update_view(self, data):
        # 기존 벽 선들 제거
        for item in self.wall_items:
            self.plot_widget.removeItem(item)
        self.wall_items = []

        # 장애물 및 사람 업데이트
        self.obs_scatter.setData(x=data['obs_x'], y=data['obs_y'])
        self.people_scatter.setData(x=data['people_x'], y=data['people_y'])
        
        # 벽 선 그리기 (클러스터 내부 점 연결)
        for seg in data['wall_segments']:
            line = pg.PlotCurveItem(x=seg['x'], y=seg['y'], pen=pg.mkPen(255, 0, 0, 150, width=2))
            self.plot_widget.addItem(line)
            self.wall_items.append(line)

        self.status_label.setText(f"Decision: {data['decision']} | People Detected: {len(data['people_x']) > 0}")

        if data['best_angle'] is not None:
            angle_rad = np.deg2rad(data['best_angle'])
            self.path_line.setData([0, 1500*np.sin(angle_rad)], [0, 1500*np.cos(angle_rad)])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MappingVisualizer()
    window.show()
    sys.exit(app.exec())