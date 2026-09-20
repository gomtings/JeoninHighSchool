"""
lidar_processor.py
LiDAR 멀티프로세싱 버전

- 독립 프로세스에서 LiDAR 스캔 수행
- 스캔 결과를 Queue로 메인 프로세스에 전달
- 스레드 대신 프로세스 분리로 GIL 우회 및 과부하 방지
"""

import math
import time
import multiprocessing
from multiprocessing import Process, Queue
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
import config


# ── 데이터 클래스 (프로세스 간 공유 가능해야 하므로 단순 구조 유지) ──
@dataclass
class LidarPoint:
    angle_deg: float
    distance_m: float
    is_blind_zone: bool


@dataclass
class LidarScan:
    points: List[LidarPoint] = field(default_factory=list)
    blind_zone_points: List[LidarPoint] = field(default_factory=list)
    timestamp: float = 0.0

    @property
    def front_points(self) -> List[LidarPoint]:
        half = config.OAK_HFOV_DEG / 2.0
        return [p for p in self.points
                if -half <= p.angle_deg <= half and not p.is_blind_zone]


# ── LiDAR 워커 함수 (독립 프로세스에서 실행) ──────────────────────
def _lidar_worker(scan_queue: Queue, stop_event, use_mock: bool):
    """
    독립 프로세스에서 실행.
    스캔 결과를 scan_queue 에 넣음.
    stop_event 가 set 되면 종료.
    """

    def is_blind_zone(angle_deg: float) -> bool:
        half_fov = config.OAK_HFOV_DEG / 2.0
        # 180도 시야각 제한 적용
        half_lidar_fov = getattr(config, 'LIDAR_FOV_DEG', 360.0) / 2.0
        if abs(angle_deg) > half_lidar_fov:
            return True
        return abs(angle_deg) > half_fov

    def normalize_angle(angle: float) -> float:
        angle = angle % 360.0
        if angle > 180.0:
            angle -= 360.0
        return angle

    def put_scan(scan: LidarScan):
        # 큐가 가득 차면 오래된 것 버리고 최신 것만 유지 (qsize 호환성 방어)
        try:
            while scan_queue.qsize() > 2:
                try:
                    scan_queue.get_nowait()
                except Exception:
                    break
        except Exception:
            pass

        try:
            scan_queue.put_nowait(scan)
        except Exception:
            pass

    # ── Mock 루프 ─────────────────────────────────────────────────
    if use_mock:
        angle_step = config.LIDAR_ANGLE_RESOLUTION
        angles = np.arange(-180.0, 180.0, angle_step)
        half_lidar_fov = getattr(config, 'LIDAR_FOV_DEG', 360.0) / 2.0

        while not stop_event.is_set():
            t = time.time()
            points: List[LidarPoint] = []

            for angle in angles:
                # 시야각 필터
                if abs(angle) > half_lidar_fov:
                    continue

                dist = 4.0
                if -10 <= angle <= 10:
                    dist = 1.5 + 0.05 * math.sin(t * 2)
                elif -120 <= angle <= -110:
                    dist = 0.8 + 0.03 * math.sin(t * 3)
                elif 160 <= angle <= 180 or -180 <= angle <= -160:
                    dist = 2.0

                dist += float(np.random.normal(0, 0.01))
                dist = float(np.clip(dist, config.LIDAR_MIN_RANGE_M, config.LIDAR_MAX_RANGE_M))

                points.append(LidarPoint(
                    angle_deg     = float(angle),
                    distance_m    = dist,
                    is_blind_zone = is_blind_zone(float(angle)),
                ))

            scan = LidarScan(
                points            = points,
                blind_zone_points = [p for p in points if p.is_blind_zone],
                timestamp         = t,
            )
            put_scan(scan)
            time.sleep(0.1)
        return

    # ── 실제 하드웨어 루프 ────────────────────────────────────────
    lidar_hw = None
    half_lidar_fov = getattr(config, 'LIDAR_FOV_DEG', 360.0) / 2.0

    try:
        from rplidar import RPLidar
        lidar_hw = RPLidar(config.LIDAR_PORT, baudrate=115200, timeout=3)
        lidar_hw.connect()
        print(f"[LiDAR 프로세스] 연결: {config.LIDAR_PORT}")

        while not stop_event.is_set():
            try:
                for scan_raw in lidar_hw.iter_scans(max_buf_meas=500):
                    if stop_event.is_set():
                        break
                    points: List[LidarPoint] = []

                    for quality, angle_raw, dist_mm in scan_raw:
                        if quality == 0:
                            continue
                        angle  = normalize_angle(float(angle_raw))
                        dist_m = float(dist_mm) / 1000.0

                        # 시야각 + 거리 필터
                        if abs(angle) > half_lidar_fov:
                            continue
                        if dist_m < config.LIDAR_MIN_RANGE_M or dist_m > config.LIDAR_MAX_RANGE_M:
                            continue

                        points.append(LidarPoint(
                            angle_deg     = angle,
                            distance_m    = dist_m,
                            is_blind_zone = is_blind_zone(angle),
                        ))

                    if points:
                        scan = LidarScan(
                            points            = points,
                            blind_zone_points = [p for p in points if p.is_blind_zone],
                            timestamp         = time.time(),
                        )
                        put_scan(scan)

            except Exception as e:
                print(f"[LiDAR 프로세스] 스캔 오류: {e} → 재연결...")
                time.sleep(2.0)
                try:
                    lidar_hw.stop()
                    lidar_hw.disconnect()
                    time.sleep(1.0)
                    lidar_hw.connect()
                except Exception:
                    pass

    except Exception as e:
        print(f"[LiDAR 프로세스] 초기화 실패: {e}")
    finally:
        if lidar_hw:
            try:
                lidar_hw.stop()
                lidar_hw.disconnect()
            except Exception:
                pass
        print("[LiDAR 프로세스] 종료")


# ── 메인 프로세스에서 사용하는 클래스 ────────────────────────────
class LidarProcessor:

    def __init__(self, use_mock: bool = False):
        self.use_mock         = use_mock
        self._scan_queue      = multiprocessing.Queue()
        self._stop_event      = multiprocessing.Event()
        self._process: Process = None
        self._latest_scan: Optional[LidarScan] = None

    def start(self):
        if self._process and self._process.is_alive():
            return
        self._stop_event.clear()
        self._process = Process(
            target = _lidar_worker,
            args   = (self._scan_queue, self._stop_event, self.use_mock),
            daemon = True,
        )
        self._process.start()
        print("[LiDAR] 프로세스 시작")

    def stop(self):
        self._stop_event.set()
        if self._process and self._process.is_alive():
            self._process.join(timeout=3.0)
            if self._process.is_alive():
                self._process.terminate()
        print("[LiDAR] 프로세스 종료")

    def get_scan(self) -> Optional[LidarScan]:
        """최신 스캔 반환 (큐에서 모두 꺼내 가장 최신 것만 사용)"""
        latest = None
        while True:
            try:
                latest = self._scan_queue.get_nowait()
            except Exception:
                break
        if latest is not None:
            self._latest_scan = latest
        return self._latest_scan

    # 시각화는 메인 프로세스에서 scan 객체를 받아 직접 수행
    def visualize(self, scan: LidarScan, size: int = 400):
        import cv2
        canvas = np.zeros((size, size, 3), dtype=np.uint8)
        if scan is None:
            return canvas
        cx, cy = size // 2, size // 2
        scale  = size / 2 / config.LIDAR_MAX_RANGE_M

        for d in [1, 2, 3, 4]:
            r = int(d * scale)
            cv2.circle(canvas, (cx, cy), r, (40, 40, 40), 1)
            cv2.putText(canvas, f"{d}m", (cx + r + 2, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80, 80, 80), 1)

        for p in scan.points:
            rad = math.radians(p.angle_deg)
            px  = int(cx + p.distance_m * math.sin(rad) * scale)
            py  = int(cy - p.distance_m * math.cos(rad) * scale)
            color = (0, 100, 255) if p.is_blind_zone else (0, 220, 120)
            cv2.circle(canvas, (px, py), 2, color, -1)

        half_fov = math.radians(config.OAK_HFOV_DEG / 2.0)
        for sign in [-1, 1]:
            ex = int(cx + 3 * scale * math.sin(sign * half_fov))
            ey = int(cy - 3 * scale * math.cos(sign * half_fov))
            cv2.line(canvas, (cx, cy), (ex, ey), (200, 200, 0), 1)

        cv2.circle(canvas, (cx, cy), 6, (255, 255, 255), -1)
        cv2.putText(canvas, "LiDAR", (6, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(canvas, "Blind zone", (6, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 100, 255), 1)
        return canvas

    @staticmethod
    def to_cartesian(points: List[LidarPoint]) -> np.ndarray:
        if not points:
            return np.empty((0, 2), dtype=np.float32)
        angles = np.array([p.angle_deg  for p in points], dtype=np.float32)
        dists  = np.array([p.distance_m for p in points], dtype=np.float32)
        rad    = np.deg2rad(angles)
        return np.stack([dists * np.sin(rad), dists * np.cos(rad)], axis=1)
