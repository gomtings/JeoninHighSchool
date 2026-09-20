"""
sensor_fusion.py
OAK-D-Lite + LiDAR 센서 융합 엔진 (핵심 모듈)

융합 전략:
  1. 좌표 정렬: LiDAR 포인트를 OAK 기준 좌표계로 변환
  2. 격자 맵 생성: 두 센서의 장애물 정보를 2D 격자에 투영
  3. 신뢰도 가중 병합:
       - OAK 중앙 영역: 높은 신뢰도
       - OAK 가장자리 / 벽 근처: 낮은 신뢰도 → LiDAR 우선
       - LiDAR 사각지대 포인트: 최고 신뢰도 (OAK 미감지 구역)
  4. 통합 장애물 리스트 반환 (거리, 각도, 신뢰도)
"""

import numpy as np  # 수치 계산 라이브러리
import math  # 수학 함수
import time  # 시간 관련 함수
from dataclasses import dataclass, field  # 데이터 클래스 데코레이터
from typing import List, Optional, Tuple  # 타입 힌트
import config  # 설정 파일 임포트
from oak_processor import OakFrame, OakObstacle  # OAK 처리 모듈 임포트
from lidar_processor import LidarScan, LidarPoint  # LiDAR 처리 모듈 임포트


@dataclass
class FusedObstacle:
    """융합된 단일 장애물 데이터 클래스"""
    distance_m: float           # 최근접 거리 (미터)
    angle_deg: float            # 로봇 정면 기준 수평 각도 (도)
    width_m: float              # 추정 폭 (미터)
    confidence: float           # 종합 신뢰도 0.0~1.0
    source: str                 # 데이터 소스 ("oak", "lidar", "fused")
    is_blind_zone: bool = False # 사각지대에서 감지된 장애물 플래그


@dataclass
class FusionGrid:
    """
    2D 점유 격자 맵 (Occupancy Grid)

    origin은 로봇 위치 (격자 중앙 하단).
    cell 값: 0 = 미지, 1 = 장애물, 신뢰도 0.0~1.0
    """
    resolution: float           # 셀당 해상도 (미터/셀)
    width_cells: int            # 너비 셀 수
    height_cells: int           # 높이 셀 수
    grid: np.ndarray            # (H, W) float32 점유 상태 (0 또는 1)
    confidence: np.ndarray      # (H, W) float32 신뢰도

    @classmethod
    def empty(cls) -> "FusionGrid":
        """빈 격자 맵 생성"""
        res = config.FUSION_GRID_RESOLUTION  # 해상도
        w = int(config.FUSION_GRID_WIDTH_M  / res)   # 너비 셀 수
        h = int(config.FUSION_GRID_HEIGHT_M / res)   # 높이 셀 수
        return cls(
            resolution   = res,
            width_cells  = w,
            height_cells = h,
            grid         = np.zeros((h, w), dtype=np.float32),  # 점유 그리드
            confidence   = np.zeros((h, w), dtype=np.float32),  # 신뢰도 그리드
        )

    @property
    def origin_col(self) -> int:
        """로봇 위치 (격자 중앙 하단)의 열 인덱스"""
        return self.width_cells // 2

    @property
    def origin_row(self) -> int:
        """로봇 위치의 행 인덱스 (하단 10%)"""
        return int(self.height_cells * 0.9)

    def world_to_cell(self, x_m: float, y_m: float) -> Tuple[int, int]:
        """직교 좌표(미터) → 격자 인덱스 (row, col) 변환"""
        col = self.origin_col + int(round(x_m / self.resolution))  # 열 계산
        row = self.origin_row - int(round(y_m / self.resolution))  # 행 계산 (y 증가 방향 반전)
        return row, col

    def set_obstacle(self, x_m: float, y_m: float, conf: float):
        """특정 좌표에 장애물을 설정 (신뢰도가 높을 때만)"""
        row, col = self.world_to_cell(x_m, y_m)  # 좌표 변환
        if 0 <= row < self.height_cells and 0 <= col < self.width_cells:  # 범위 내
            if conf > self.confidence[row, col]:  # 신뢰도 비교
                self.grid[row, col]      = 1.0  # 점유 설정
                self.confidence[row, col] = conf  # 신뢰도 설정

    def reset(self):
        """격자 맵 초기화"""
        self.grid[:] = 0.0       # 점유 초기화
        self.confidence[:] = 0.0  # 신뢰도 초기화


class SensorFusion:
    """센서 융합 엔진 클래스"""

    def __init__(self):
        """초기화 메서드"""
        self.grid = FusionGrid.empty()  # 융합 격자 맵
        self._last_fused: List[FusedObstacle] = []  # 마지막 융합 결과

    # ── 메인 융합 함수 ────────────────────────────────────────────
    def fuse(
        self,
        oak_frame: Optional[OakFrame],
        lidar_scan: Optional[LidarScan],
    ) -> List[FusedObstacle]:
        """
        OAK 프레임과 LiDAR 스캔을 받아 융합된 장애물 리스트를 반환한다.

        우선순위:
          - LiDAR 사각지대 포인트 → 최우선 (OAK 미감지)
          - OAK 중앙 영역 + LiDAR 일치 → 높은 신뢰도
          - OAK 가장자리 단독 → 낮은 신뢰도, LiDAR 로 보정
          - LiDAR 전방 단독 → OAK 보완
        """
        self.grid.reset()  # 격자 초기화

        # 1. LiDAR 데이터를 격자에 투영
        if lidar_scan is not None:
            self._project_lidar(lidar_scan)

        # 2. OAK 데이터를 격자에 투영
        if oak_frame is not None:
            self._project_oak(oak_frame)

        # 3. 격자 스무딩 (작은 노이즈 제거)
        self._smooth_grid()

        # 4. 격자 → 장애물 객체 추출
        fused = self._extract_obstacles_from_grid(lidar_scan)

        self._last_fused = fused  # 결과 저장
        return fused

    # ── LiDAR → 격자 투영 ─────────────────────────────────────────
    def _project_lidar(self, scan: LidarScan):
        """
        LiDAR 포인트를 격자에 투영.
        사각지대 포인트는 가중치 1.0, 일반 포인트는 0.9.
        """
        for p in scan.points:
            if p.distance_m <= 0:
                continue  # 유효하지 않은 포인트 제외
            rad = math.radians(p.angle_deg)  # 각도를 라디안으로
            x_m = p.distance_m * math.sin(rad)   # 우측 + (x 좌표)
            y_m = p.distance_m * math.cos(rad)   # 전방 + (y 좌표)

            # 좌표 변환 적용 (물리적 장착 오프셋)
            x_m += config.LIDAR_TO_OAK_OFFSET_X
            y_m += config.LIDAR_TO_OAK_OFFSET_Z

            # 신뢰도 설정 (사각지대 우선)
            conf = config.WEIGHT_LIDAR_BLIND if p.is_blind_zone else config.WEIGHT_LIDAR
            self.grid.set_obstacle(x_m, y_m, conf)  # 격자에 설정

    # ── OAK → 격자 투영 ──────────────────────────────────────────
    def _project_oak(self, frame: OakFrame):
        """
        OAK 장애물을 격자에 투영.
        이미 LiDAR 가 해당 셀에 높은 신뢰도를 기록한 경우 덮어쓰지 않는다.
        """
        for obs in frame.obstacles:
            if obs.is_wall:
                continue  # 벽 제외
            
            # OAK 장착 높이(45cm) 오프셋 보정 적용 (빗변 거리 -> 지면 수평 평면 거리)
            h_diff = config.LIDAR_TO_OAK_OFFSET_Y
            flat_dist = math.sqrt(max(0.01, obs.distance_m**2 - h_diff**2))
            
            rad = math.radians(obs.angle_deg)  # 각도를 라디안으로
            x_m = flat_dist * math.sin(rad)  # x 좌표
            y_m = flat_dist * math.cos(rad)  # y 좌표
            self.grid.set_obstacle(x_m, y_m, obs.confidence)  # 격자에 설정

    # ── 격자 스무딩 ───────────────────────────────────────────────
    def _smooth_grid(self):
        """
        3×3 최대 풀링으로 인접 셀 팽창 (로봇 폭 여유).
        이후 신뢰도가 낮은 단독 셀 제거.
        """
        from scipy.ndimage import maximum_filter, uniform_filter  # 필터 임포트
        robot_cells = max(1, int(config.ROBOT_WIDTH_M / 2 / config.FUSION_GRID_RESOLUTION))  # 로봇 반폭 셀 수
        size = robot_cells * 2 + 1  # 필터 크기

        # 최대 필터로 팽창
        self.grid.grid      = maximum_filter(self.grid.grid,      size=size)
        self.grid.confidence = maximum_filter(self.grid.confidence, size=size)

        # 고립된 단일 셀 (노이즈) 제거
        neighbor_sum = uniform_filter(self.grid.grid.astype(float), size=3) * 9  # 이웃 합
        isolated = (self.grid.grid > 0) & (neighbor_sum < 2)  # 고립 셀 마스크
        self.grid.grid[isolated] = 0.0       # 제거
        self.grid.confidence[isolated] = 0.0

    # ── 격자 → 장애물 객체 ───────────────────────────────────────
    def _extract_obstacles_from_grid(
        self,
        lidar_scan: Optional[LidarScan],
    ) -> List[FusedObstacle]:
        """
        점유 격자에서 연속된 장애물 덩어리를 추출하여
        FusedObstacle 리스트로 반환한다.
        """
        import cv2  # OpenCV 임포트

        binary = (self.grid.grid > 0.1).astype(np.uint8) * 255  # 이진화
        if binary.sum() == 0:
            return []  # 장애물 없음

        # 연결 성분 분석
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary)
        obstacles: List[FusedObstacle] = []

        # 사각지대 각도 집합 (LiDAR 기준)
        blind_angles = set()
        if lidar_scan:
            half_fov = config.OAK_HFOV_DEG / 2.0  # OAK 시야각 절반
            for p in lidar_scan.points:
                if abs(p.angle_deg) > half_fov:
                    blind_angles.add(round(p.angle_deg))  # 사각지대 각도 추가

        res = self.grid.resolution  # 해상도
        orig_row = self.grid.origin_row  # 원점 행
        orig_col = self.grid.origin_col  # 원점 열

        for lbl in range(1, num_labels):
            area = stats[lbl, cv2.CC_STAT_AREA]  # 영역 크기
            if area < 4:
                continue  # 너무 작음 제외

            mask = labels == lbl  # 마스크
            rows, cols = np.where(mask)  # 마스크 위치

            # 격자 → 직교 좌표 변환
            ys = (orig_row - rows) * res    # 전방 거리
            xs = (cols - orig_col) * res    # 좌우

            # 가장 가까운 점 찾기
            dists = np.sqrt(xs ** 2 + ys ** 2)  # 거리 계산
            nearest_idx = np.argmin(dists)  # 최소 거리 인덱스
            dist_m = float(dists[nearest_idx])  # 최소 거리

            # 각도 계산 (중심 기준)
            cx = float(np.mean(xs))  # 중심 x
            cy = float(np.mean(ys))  # 중심 y
            angle_deg = float(math.degrees(math.atan2(cx, max(cy, 0.01))))  # 각도

            # 폭 추정
            width_m = float(np.max(xs) - np.min(xs) + res)  # 폭

            # 신뢰도: 해당 셀들의 평균
            conf = float(np.mean(self.grid.confidence[mask]))  # 평균 신뢰도

            # 사각지대 여부 판단
            is_blind = any(
                abs(round(angle_deg) - ba) < 5 for ba in blind_angles
            )

            # 소스 판별
            if conf >= 0.88:
                source = "fused" if not is_blind else "lidar"  # 융합 또는 LiDAR
            elif is_blind:
                source = "lidar"  # LiDAR
            else:
                source = "oak"  # OAK

            obstacles.append(FusedObstacle(
                distance_m   = dist_m,
                angle_deg    = angle_deg,
                width_m      = width_m,
                confidence   = float(np.clip(conf, 0.0, 1.0)),  # 신뢰도 클리핑
                source       = source,
                is_blind_zone = is_blind,
            ))

        obstacles.sort(key=lambda o: o.distance_m)  # 거리 기준 정렬
        return obstacles

    # ── 디버그 시각화 ─────────────────────────────────────────────
    def visualize_grid(self) -> "np.ndarray":
        """융합 격자 맵을 BGR 이미지로 반환"""
        import cv2  # OpenCV 임포트

        vis_size = 400  # 시각화 크기
        h, w = self.grid.height_cells, self.grid.width_cells  # 격자 크기
        scale_x = vis_size / w  # x 스케일
        scale_y = vis_size / h  # y 스케일
        canvas = np.zeros((vis_size, vis_size, 3), dtype=np.uint8)  # 캔버스 생성

        # 장애물 셀 채색
        for row in range(h):
            for col in range(w):
                if self.grid.grid[row, col] > 0.1:  # 점유 셀
                    px = int(col * scale_x)  # 픽셀 x
                    py = int(row * scale_y)  # 픽셀 y
                    conf = self.grid.confidence[row, col]  # 신뢰도
                    # 신뢰도에 따라 색상: 높으면 밝은 빨강, 낮으면 어두운 주황
                    intensity = int(conf * 220 + 35)
                    cv2.rectangle(
                        canvas,
                        (px, py),
                        (px + max(1, int(scale_x)), py + max(1, int(scale_y))),  # 사각형
                        (0, int(intensity * 0.4), intensity),  # 색상
                        -1,  # 채우기
                    )

        # 로봇 위치 표시
        rx = int(self.grid.origin_col * scale_x)  # 로봇 x
        ry = int(self.grid.origin_row * scale_y)  # 로봇 y
        cv2.circle(canvas, (rx, ry), 6, (255, 255, 255), -1)  # 흰색 원

        # 구역 경계선 그리기
        for zone_m, color in [
            (config.ZONE_DANGER_M,  (0, 0, 200)),    # 위험 구역 (빨강)
            (config.ZONE_WARNING_M, (0, 140, 255)),  # 경고 구역 (주황)
            (config.ZONE_SAFE_M,    (0, 200, 0)),    # 안전 구역 (녹색)
        ]:
            r_cells = int(zone_m / self.grid.resolution * scale_y)  # 반지름 픽셀
            cv2.circle(canvas, (rx, ry), r_cells, color, 1)  # 원 그리기

        # 장애물 레이블 표시
        for obs in self._last_fused:
            rad = math.radians(obs.angle_deg)  # 각도를 라디안으로
            ox = int(rx + obs.distance_m / self.grid.resolution * math.sin(rad) * scale_x)  # 장애물 x
            oy = int(ry - obs.distance_m / self.grid.resolution * math.cos(rad) * scale_y)  # 장애물 y
            col_pt = (0, 80, 255) if obs.is_blind_zone else (255, 200, 0)  # 색상 (사각지대 파랑, 일반 노랑)
            cv2.circle(canvas, (ox, oy), 5, col_pt, -1)  # 점 표시
            cv2.putText(
                canvas,
                f"{obs.distance_m:.1f}m",  # 거리 텍스트
                (ox + 4, oy - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, col_pt, 1,
            )

        # 제목 표시
        cv2.putText(canvas, "Fusion Grid", (6, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        return canvas