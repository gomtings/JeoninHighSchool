import sys
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QThread, Signal, Qt
from rplidar import RPLidar
from collections import defaultdict # 격자별 횟수 계산을 위해 추가

# --- [설정] ---
PORT_NAME = 'COM7'
BAUDRATE = 115200
GRID_SIZE = 20  # 격자 크기를 20mm로 약간 키워 필터링 효율 높임
MAX_DISTANCE_MM = 5000 
CONFIDENCE_THRESHOLD = 5 # 중요: 특정 칸에 5번 이상 찍혀야 "벽"으로 인정 (사람 제외용)

class StaticMappingThread(QThread):
    update_data = Signal(dict)

    def __init__(self):
        super().__init__()
        self.running = True
        self.grid_counts = defaultdict(int) 
        self.global_map_x = []
        self.global_map_y = []

    # --- [추가] 각도 오차를 고려해 가장 가까운 거리 데이터를 찾는 함수 ---
    def get_nearest_dist(self, scan_grids, target_angle):
        # 라이다 데이터는 비어있을 수 있으므로 기본값은 매우 큰 값으로 설정
        # (거리가 멀다고 판단되어야 점을 지우지 않음)
        best_dist = 99999.0
        threshold = 1.5 # 1.5도 이내의 데이터를 검색
        
        # 맵 각도 주변 탐색
        for angle in [target_angle, target_angle-1, target_angle+1, target_angle-2, target_angle+2]:
            a = int(angle % 360)
            if a in scan_grids:
                return scan_grids[a]
        return best_dist

    def run(self):
        try:
            lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE)
            lidar.start_motor()
            lidar.clean_input()

            for scan in lidar.iter_scans(max_buf_meas=1000):
                if not self.running: break
                
                current_scan_grids = {} 
                curr_x, curr_y = [], [] # [보정] 실시간 표시용 리스트 초기화

                for _, angle, dist in scan:
                    if 0 < dist < MAX_DISTANCE_MM:
                        rad = np.deg2rad(angle)
                        wx = dist * np.cos(rad)
                        wy = dist * np.sin(rad)
                        
                        grid_pos = (int(wx / GRID_SIZE), int(wy / GRID_SIZE))
                        # 지우개 로직을 위해 정수 각도별로 거리 저장
                        current_scan_grids[int(angle)] = dist 

                        curr_x.append(wx)
                        curr_y.append(wy)

                        # 1. 지도 누적
                        self.grid_counts[grid_pos] += 1
                        if self.grid_counts[grid_pos] == CONFIDENCE_THRESHOLD:
                            self.global_map_x.append(wx)
                            self.global_map_y.append(wy)

                # --- [지우개 로직] ---
                new_map_x, new_map_y = [], []
                
                # 맵이 커지면 연산량이 많아지므로 0.5초(약 5프레임)마다 한 번씩 지우개 작동 추천
                # 여기서는 매 프레임 작동하도록 작성함
                for i in range(len(self.global_map_x)):
                    mx, my = self.global_map_x[i], self.global_map_y[i]
                    
                    # 지도 점의 각도(0~360)와 거리 계산
                    m_angle = np.rad2deg(np.arctan2(my, mx)) % 360
                    m_dist = np.sqrt(mx**2 + my**2)
                    
                    # 현재 스캔에서 해당 방향의 실시간 거리 확인
                    current_dist = self.get_nearest_dist(current_scan_grids, m_angle)
                    
                    # [지우개 발동 조건]
                    # 현재 측정 거리가 지도 점보다 15cm 이상 더 멀리 찍힌다면?
                    # 그 사이를 가로막던 장애물(사람)이 사라졌다는 뜻!
                    if current_dist > m_dist + 150: 
                         # 카운트 초기화 (나중에 다시 서있으면 새로 그려지게)
                         self.grid_counts[(int(mx/GRID_SIZE), int(my/GRID_SIZE))] = 0
                         continue # new_map에 넣지 않고 버림 (삭제)
                    
                    new_map_x.append(mx)
                    new_map_y.append(my)
                
                self.global_map_x, self.global_map_y = new_map_x, new_map_y

                # UI로 전송
                self.update_data.emit({
                    'map_x': self.global_map_x,
                    'map_y': self.global_map_y,
                    'curr_x': curr_x,
                    'curr_y': curr_y
                })

        except Exception as e:
            print(f"Lidar Error: {e}")
        finally:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()

class MappingVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Static Mapping with Dynamic Object Filtering")
        self.resize(800, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('k')
        layout.addWidget(self.plot_widget)

        # 누적된 지도 (흰색 점)
        self.map_scatter = pg.ScatterPlotItem(size=2, brush=pg.mkBrush(200, 200, 200, 255), pen=None)
        # 현재 실시간 스캔 (빨간색 점)
        self.curr_scatter = pg.ScatterPlotItem(size=4, brush=pg.mkBrush(255, 0, 0, 255), pen=None)
        
        self.plot_widget.addItem(self.map_scatter)
        self.plot_widget.addItem(self.curr_scatter)

        self.robot_marker = pg.ScatterPlotItem(size=15, brush='y', symbol='t')
        self.robot_marker.setData(x=[0], y=[0])
        self.plot_widget.addItem(self.robot_marker)

        self.thread = StaticMappingThread()
        self.thread.update_data.connect(self.update_view)
        self.thread.start()

    def update_view(self, data):
        self.curr_scatter.setData(x=data['curr_x'], y=data['curr_y'])
        self.map_scatter.setData(x=data['map_x'], y=data['map_y'])

    def closeEvent(self, event):
        self.thread.running = False
        self.thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MappingVisualizer()
    window.show()
    sys.exit(app.exec())