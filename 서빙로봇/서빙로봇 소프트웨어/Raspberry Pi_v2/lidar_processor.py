"""
lidar_processor.py
LiDAR 멀티프로세싱 버전

- 독립 프로세스에서 LiDAR 스캔 수행
- 스캔 결과를 Queue로 메인 프로세스에 전달
- 스레드 대신 프로세스 분리로 GIL 우회 및 과부하 방지
"""

import json
import math
import os
import time
import multiprocessing
from multiprocessing import Process, Queue
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import config


# ── 각도별 자체반사 프로파일 (calibrate_lidar_self_mask.py 로 생성) ──────
# 로봇 몸체/트레이 칸막이는 원형이 아니므로, 균일 반경 하나로는 가까운 방향에
# 맞추면 먼 방향(예: ㄷ자 칸막이의 안쪽 모서리)이 새고, 먼 방향에 맞추면
# 가까운 방향에서 실제 장애물 감지 거리를 깎아먹는다. 각도 구간마다 캘리브레이션된
# 임계값을 쓰면 이 트레이드오프가 없다. 캘리브레이션 파일이 없으면(아직 실행 전,
# 혹은 로봇 구조 변경 후 재생성 전) config.LIDAR_SELF_EXCLUSION_M 균일 반경으로
# 자동 폴백한다.
SELF_MASK_ANGLE_STEP_DEG = 2.0


def _self_mask_path() -> str:
    filename = getattr(config, "LIDAR_SELF_MASK_FILE", "lidar_self_mask.json")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def load_self_mask() -> Optional[Tuple[float, List[float]]]:
    """각도별 자체반사 제외 거리(m) 프로파일을 불러온다. 없거나 손상되면 None."""
    path = _self_mask_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        step = float(data["angle_step_deg"])
        values = [float(v) for v in data["thresholds_m"]]
        if step <= 0 or not values:
            return None

        # [각도 오프셋 일치 검사] 프로파일은 각도 인덱스로 저장되므로 캘리브레이션
        # 당시의 오프셋과 짝을 이룰 때만 유효하다. 오프셋을 바꾼 뒤 재캘리브레이션을
        # 잊으면 같은 물리 방향이 다른 각도 라벨을 갖게 되어, 프로파일이 엉뚱한 방향에
        # 적용되면서 실제 장애물을 자체반사로 오인해 지워버릴 수 있다. 조용히 넘어가면
        # 원인 찾기가 매우 어려우므로 명시적으로 거부하고 균일 반경으로 폴백한다.
        saved_offset = data.get("angle_offset_deg")
        current_offset = getattr(config, "LIDAR_ANGLE_OFFSET_DEG", 0.0)
        if saved_offset is None or abs(float(saved_offset) - current_offset) > 0.5:
            print(f"[LiDAR] 자체반사 프로파일이 현재 각도 오프셋과 맞지 않습니다 "
                  f"(프로파일: {saved_offset}, 현재: {current_offset}) - 무시하고 균일 반경으로 폴백. "
                  f"calibrate_lidar_self_mask.py 를 다시 실행하세요.")
            return None

        return step, values
    except Exception as e:
        print(f"[LiDAR] 자체반사 프로파일 로드 실패({path}): {e} - 균일 반경으로 폴백")
        return None


def self_exclusion_threshold(
    angle_deg: float,
    mask: Optional[Tuple[float, List[float]]],
    fallback_m: float,
) -> float:
    """
    지정 각도(오프셋 보정 완료된 로봇 기준 각도)에서 적용할 자체반사 제외 거리(m).
    mask 가 없으면 균일 반경(fallback_m)을 그대로 쓴다.
    캘리브레이션 오염(캘리브레이션 중 실제 장애물이 끼어든 경우) 방어를 위해
    센서 최소 측정거리 ~ LIDAR_SELF_MASK_MAX_M 범위로 항상 클리핑한다.
    """
    lo = config.LIDAR_MIN_RANGE_M
    hi = getattr(config, "LIDAR_SELF_MASK_MAX_M", 0.45)
    if mask is None:
        return min(max(fallback_m, lo), hi)
    step, values = mask
    n = len(values)
    idx = int(((angle_deg + 180.0) % 360.0) / step) % n
    return min(max(values[idx], lo), hi)


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
        # LIDAR_ANGLE_OFFSET_DEG: 라이다 장착 각도 보정 (test_lidar_angle.py 로 실측)
        # 라이다 원점(0도)이 로봇 정면과 어긋나 있으면, 이 보정 없이는
        # LIDAR_FOV_DEG(180도) 필터가 엉뚱한 반원(예: 뒤쪽)을 정면으로 오인해
        # 뒤쪽 벽이 맵의 전방 장애물로 나타난다.
        angle = (angle + getattr(config, "LIDAR_ANGLE_OFFSET_DEG", 0.0)) % 360.0
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
    self_mask = load_self_mask()
    if self_mask is not None:
        print(f"[LiDAR] 자체반사 프로파일 로드: {_self_mask_path()}")
    else:
        print(f"[LiDAR] 자체반사 프로파일 없음 - 균일 반경 {config.LIDAR_SELF_EXCLUSION_M:.2f}m 로 폴백 "
              f"(calibrate_lidar_self_mask.py 실행 권장)")

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
                        # [자체반사 제외] 로봇 몸체/트레이 칸막이(마운트, 브래킷, 측면 벽
                        # 등)에 라이다 빔이 맞고 튕겨 돌아오는 반사. 실측: 로봇을 제자리에서
                        # 돌려도 점 무리가 로봇과 같이 회전 -> 방 안 물체가 아니라 몸체 자체.
                        # 이 구조가 원형이 아니라 ㄷ자(트레이 칸막이)라 방향마다 거리가
                        # 다르므로, 균일 반경 대신 각도별 캘리브레이션 프로파일을 쓴다
                        # (self_mask 가 없으면 LIDAR_SELF_EXCLUSION_M 균일 반경으로 폴백).
                        if dist_m < self_exclusion_threshold(angle, self_mask, config.LIDAR_SELF_EXCLUSION_M):
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
