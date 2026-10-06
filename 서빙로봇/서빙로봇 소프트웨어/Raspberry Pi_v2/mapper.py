"""
mapper.py
OAK-D-Lite + LiDAR 데이터를 누적하여 2D 맵을 생성

- LiDAR: 360도 벽/장애물 포인트 → 맵에 누적
- OAK-D-Lite: 정면 깊이 정보 → 맵에 보완
- 로봇이 이동하면 맵도 함께 업데이트 (단순 누적 방식)
"""

import numpy as np  # NumPy 라이브러리 (배열 계산)
import math  # 수학 함수 (삼각함수 등)
import time  # 시간 관련 함수 (타임스탬프)
from dataclasses import dataclass, field  # 데이터 클래스 정의
from typing import List, Tuple, Optional  # 타입 힌트
import config  # 설정 파일에서 상수 가져옴
from console_utils import safe_print as _safe_print


# 셀 상태값 상수 정의
CELL_UNKNOWN    = 0.0  # 미지 영역
CELL_FREE       = 0.3  # 빈 공간
CELL_WALL       = 0.8  # 벽
CELL_OBSTACLE   = 1.0  # 장애물
CELL_GLASS_WALL = 0.6   # 유리벽/투명 장애물


# 맵 셀을 나타내는 데이터 클래스
@dataclass
class MapCell:
    value: float = CELL_UNKNOWN     # 현재 셀 상태 값
    hit_count: int = 0              # 장애물로 감지된 횟수
    free_count: int = 0             # 빈 공간으로 감지된 횟수
    last_updated: float = 0.0       # 마지막 업데이트 시간


# 2D 점유 격자 맵을 관리하는 클래스
class OccupancyMap:
    """
    2D 점유 격자 맵.
    맵 자체는 월드 좌표계에 고정되고, 로봇은 set_robot_pose()로 전달받은
    오도메트리를 따라 맵 위를 이동하며, 센서 데이터가 그 위치 기준으로 누적된다.
    """

    def __init__(self):
        # 맵 해상도 설정 (미터/셀)
        self.resolution = config.FUSION_GRID_RESOLUTION
        # 맵 크기 설정 (미터)
        self.width_m    = config.FUSION_GRID_WIDTH_M   # 맵 가로 크기 (m)
        self.height_m   = config.FUSION_GRID_HEIGHT_M  # 맵 세로 크기 (m)

        # 셀 단위 크기 계산
        self.width_cells  = int(self.width_m  / self.resolution)
        self.height_cells = int(self.height_m / self.resolution)

        # 맵 그리드 초기화: 0=미지, 0.3=빈공간, 0.8=벽, 1.0=장애물
        self.grid = np.full(
            (self.height_cells, self.width_cells),
            CELL_UNKNOWN,
            dtype=np.float32,
        )
        # [정적 맵 원본 보관] 불러온 사전 맵과 실시간 감지 센서 맵의 색상 구분을 위한 배열
        self.static_grid    = np.full_like(self.grid, CELL_UNKNOWN)
        # 신뢰도 카운터 및 장애물 메모리 타임스탬프 초기화
        self.hit_count      = np.zeros_like(self.grid, dtype=np.int32)    # 장애물 감지 카운트
        self.free_count     = np.zeros_like(self.grid, dtype=np.int32)    # 빈 공간 감지 카운트
        self.last_hit_time  = np.zeros_like(self.grid, dtype=np.float64)  # 장애물이 마지막으로 감지된 시간 (s)
        self.first_hit_time = np.zeros_like(self.grid, dtype=np.float64)  # 현재 관측 구간이 시작된 시간 (s)
        # 사람으로 분류된 셀 등, 이 시각까지는 영구 지도로 승격시키지 않는다
        self.no_promote_until = np.zeros_like(self.grid, dtype=np.float64)
        # 이 셀을 마지막으로 OAK 화각 안에서 장애물로 관측한 시각 (s)
        self.oak_seen_time    = np.zeros_like(self.grid, dtype=np.float64)
        # [확률 기반 셀 갱신] log-odds. 셀 하나가 0(미지)을 기준으로 hit 면 +, free 면 -로
        # 움직이고 [LOGODDS_MIN, LOGODDS_MAX] 로 clip 된다. 상한이 있어서 오래 쌓인
        # 장애물도 free 관측 몇 번(약 LOGODDS_MAX/|L_FREE|)이면 뒤집힌다
        # (hit/free 비율 방식은 hit 가 수십 개 쌓이면 수백 번의 free 가 필요했다).
        # 영구 승격/사람 차단/메모리 보호는 기존 hit_count 로직을 그대로 쓰고,
        # 이 값은 _update_cell 의 장애물/빈공간 판정에만 사용한다.
        self.logodds = np.zeros_like(self.grid, dtype=np.float32)
        self.L_HIT = 0.85            # 장애물 관측 1회의 증가량 (확률 약 0.70 에 해당)
        self.L_FREE = -0.40          # 빈 공간 관측 1회의 변화량 (확률 약 0.40 에 해당)
        self.LOGODDS_MIN = -4.0
        self.LOGODDS_MAX = 4.0
        self.L_OCC_THRESH = 0.40     # 이 값 초과면 장애물 (hit 1회로 바로 넘는 민감도 유지)
        self.L_FREE_THRESH = -0.30   # 이 값 미만이면 빈 공간
        self.L_OAK_FLOOR = 2.0       # OAK 가 직접 확인한 장애물의 최소 log-odds (라이다 free 몇 번에 안 지워지게)
        self.OBSTACLE_MEMORY_SEC = 5.0  # 장애물 메모리 보존 시간 (5초 동안 책상 상판을 라이다가 지우지 못하도록 보호)

        # [영구 승격 기준]
        # 이전 값(8회)은 실측상 사람이 0.2초만 서 있어도 통과했다. 원인은 두 가지였다.
        #  - get_scan() 이 새 스캔이 없으면 캐시된 직전 스캔을 그대로 반환해 같은 관측이
        #    프레임마다 중복 계수됨 (라이다 5.5Hz vs 루프 15FPS -> 약 2.7배)
        #  - 한 스캔 안에서 여러 광선이 같은 셀을 때려 스캔 1회에 +3 씩 오름
        # 아래 update_from_lidar 에서 두 중복을 모두 제거했고, 그 위에 기준을 세웠다.
        self.STATIC_PROMOTE_HIT_COUNT = 25  # 중복 제거 기준 약 25회 (5.5Hz 에서 약 4.5초)
        self.STATIC_PROMOTE_MIN_SEC = 3.0   # 관측 시작~최근 관측이 이 시간 이상 벌어져야 함
        # 사람으로 분류된 셀의 hit_count 상한. 장애물 메모리 유지에 필요한 최소값(2)의
        # 두 배로 두어, 회피는 정상 동작하되 승격 조건(hit > 25)에는 못 닿게 한다.
        self.PERSON_HIT_CAP = 4

        # [벽/장애물 구분] 저장 시 벽으로 분류된 덩어리의 긴 변이 이 길이 미만이면 장애물로 본다
        self.WALL_MIN_LENGTH_M = 2.0
        self.WALL_FRAGMENT_MIN_CELLS = 8

        # [승격 자격] 분류기가 검증할 수 있는 방위에서 본 관측인가
        # 위 PERSON_HIT_CAP 은 block_promotion() 이 불려야 걸리고, 그건 분류기가
        # PERSON 라벨을 붙여줘야 열린다. 그런데 PERSON 은 OAK 융합 분류에서만
        # 나온다 - object_classifier 는 lidar_only 클러스터를 무조건 OBSTACLE 로
        # 내린다. 라이다는 ±90도를 보는데 OAK 는 ±36.5도뿐이라, 그 바깥 측면에 선
        # 사람은 구조적으로 PERSON 이 될 수 없고 캡도 안 걸린다.
        # (실측: 측면 60도에 10초 서 있으면 5초 만에 영구 지도에 벽으로 박혔다)
        # 그래서 OAK 화각 밖에서만 본 셀은 "검증받지 못한 관측"으로 보고 시간 조건을
        # 훨씬 길게 요구한다. 사람은 버티기 어렵고 벽은 버티는 길이다.
        # 측면을 아예 막지 않는 이유: 로봇이 나란히 지나가는 복도 벽은 끝까지 정면에
        # 안 들어오므로, 완전히 막으면 영구 지도에 정면으로 마주친 것만 남는다.
        self.OAK_VERIFY_HALF_FOV_DEG = getattr(config, "OAK_HFOV_DEG", 73.0) / 2.0
        self.STATIC_PROMOTE_SIDE_MIN_SEC = 15.0

        # 로봇 현재 위치 (맵 중앙에서 시작하며, set_robot_pose 호출 시 실제 이동을 따라 갱신됨)
        self.robot_col = self.width_cells  // 2
        self.robot_row = self.height_cells // 2

        # 월드 좌표 원점(오도메트리 0,0 지점)에 해당하는 셀 - 최초 1회 고정
        self._origin_col = self.robot_col
        self._origin_row = self.robot_row

        # 로봇 현재 자세 (맵 좌표계: x=우측+, y=전방+ / 헤딩: 전방 0도, 우측 +90도)
        self.robot_world_x    = 0.0
        self.robot_world_y    = 0.0
        self.robot_heading_deg = 0.0

        # 마지막 업데이트 시간
        self.last_update = time.time()
        # 직전에 반영한 스캔의 타임스탬프 (같은 스캔의 중복 반영을 막는다)
        self._last_scan_ts = None
        # free_count 감쇠용 스캔 카운터 (update_from_lidar 가 스캔마다 증가)
        self._free_tick = 0

    # ── 로봇 자세(오도메트리) 반영 ────────────────────────────────
    def set_robot_pose(self, x_fwd_m: float, y_left_m: float, heading_deg: float):
        """
        BLE 오도메트리로 받은 로봇의 현재 자세를 맵에 반영한다.

        입력 좌표계(PathRecommender/BLE): 전방=+X, 좌측=+Y, 헤딩 0도=전방 / +90도=우측
        맵 좌표계: x=우측+, y=전방+ (world_to_cell 이 이 축을 기준으로 동작)
        """
        self.robot_world_x     = -y_left_m   # 좌측(+Y) → 맵의 우측(+x) 기준으로 부호 반전
        self.robot_world_y     = x_fwd_m     # 전방(+X) → 맵의 전방(+y)
        self.robot_heading_deg = heading_deg

        # 고정 원점 셀로부터의 변위로 현재 로봇 셀 위치를 갱신
        self.robot_col = self._origin_col + int(round(self.robot_world_x / self.resolution))
        self.robot_row = self._origin_row - int(round(self.robot_world_y / self.resolution))

    # ── 장애물 관측 1회 등록 ──────────────────────────────────────
    def _register_hit(self, row: int, col: int, now: float, weight: int = 1):
        """
        장애물 감지를 기록하고, 관측 구간의 시작 시각(first_hit_time)을 관리한다.
        관측이 OBSTACLE_MEMORY_SEC 이상 끊겼다가 다시 시작되면 새 구간으로 본다
        (오래 전 잠깐 스쳤던 기록이 시간 폭 조건을 거저 통과하지 못하도록).
        """
        prev = self.last_hit_time[row, col]
        if prev == 0.0 or (now - prev) > self.OBSTACLE_MEMORY_SEC:
            self.first_hit_time[row, col] = now
        self.hit_count[row, col] += weight
        self.last_hit_time[row, col] = now
        self.logodds[row, col] = min(self.logodds[row, col] + self.L_HIT, self.LOGODDS_MAX)

    def _register_free(self, row: int, col: int):
        """
        빈 공간 관측 1회를 기록한다 (free_count 와 log-odds 를 함께 갱신).
        hit 가 여러 번 쌓인 셀(책상/의자 다리 등)은 빔이 다리 사이를 지나갈 때마다
        free_count 가 부풀어 저장 때 장애물에서 탈락하므로, free_count 는 4번에 1번만
        올린다. log-odds 는 그대로 갱신하므로 실시간 맵에서 사라진 장애물은 똑같이 지워진다.
        """
        if self.hit_count[row, col] < 3 or (self._free_tick & 3) == 0:
            self.free_count[row, col] += 1
        self.logodds[row, col] = max(self.logodds[row, col] + self.L_FREE, self.LOGODDS_MIN)

    def block_promotion(self, row: int, col: int, now: float,
                        radius_cells: int = 3, sec: float = 10.0):
        """
        이 셀 주변을 사람으로 간주해 영구 지도(static_grid) 승격에서 제외한다.

        ★ 승격 차단 표시만으로는 부족하다.
          hit_count 는 어디서도 줄지 않으므로, 사람이 4초만 서 있어도 수백까지
          쌓인다. 그 상태로 사람이 떠나면 5초간은 장애물 메모리가 free 광선을
          막아 free_count 도 안 오르고, no_promote_until 이 만료되는 순간
          hit/total 이 여전히 0.6~0.9 라 그대로 승격돼 버린다.
          (실측: 4초 서 있으면 14초에, 20초 서 있으면 30초에 유령 벽 발생)
          결국 차단이 아니라 sec 초 지연에 불과했다.

          그래서 hit_count 자체에 상한을 건다. 5초 장애물 메모리와 prepare_frame
          보호는 hit >= 2 만 요구하므로(PERSON_HIT_CAP = 4 는 그 두 배),
          회피 대상으로는 그대로 잡히면서 승격 조건(hit > 25)에는 도달할 수 없다.
          사람이 떠나면 free 광선 몇 번에 비율이 무너져 자연 소멸한다.
        """
        until = now + sec
        for dr in range(-radius_cells, radius_cells + 1):
            for dc in range(-radius_cells, radius_cells + 1):
                r, c = row + dr, col + dc
                if self.in_bounds(r, c):
                    self.no_promote_until[r, c] = until
                    if self.hit_count[r, c] > self.PERSON_HIT_CAP:
                        self.hit_count[r, c] = self.PERSON_HIT_CAP

    # ── 좌표 변환 ─────────────────────────────────────────────────
    # 월드 좌표(미터)를 맵 셀 인덱스로 변환하는 메서드
    def world_to_cell(self, x_m: float, y_m: float) -> Tuple[int, int]:
        """직교 좌표(m) → 격자 인덱스 (row, col). 로봇의 현재 위치 기준."""
        # 로봇 위치를 기준으로 셀 인덱스 계산
        col = self.robot_col + int(round(x_m / self.resolution))  # x → col
        row = self.robot_row - int(round(y_m / self.resolution))  # y → row (y축 반전)
        return row, col

    # 맵 셀 인덱스를 월드 좌표(미터)로 변환하는 메서드
    def cell_to_world(self, row: int, col: int) -> Tuple[float, float]:
        """격자 인덱스 → 직교 좌표(m)"""
        # 셀 인덱스를 로봇 기준 월드 좌표로 변환
        x_m = (col - self.robot_col) * self.resolution  # col → x
        y_m = (self.robot_row - row) * self.resolution  # row → y (y축 반전)
        return x_m, y_m

    # 주어진 셀 인덱스가 맵 범위 내인지 확인하는 메서드
    def in_bounds(self, row: int, col: int) -> bool:
        # 행과 열이 맵 크기 내에 있는지 체크
        return 0 <= row < self.height_cells and 0 <= col < self.width_cells

    # ── LiDAR 스캔 업데이트 ───────────────────────────────────────
    # LiDAR 스캔 데이터를 맵에 반영하는 메서드
    def update_from_lidar(self, scan) -> int:
        """
        LiDAR 스캔 포인트를 맵에 반영.
        레이 캐스팅으로 포인트까지의 경로를 빈 공간으로 마킹하되,
        카메라 등으로 최근 등록된 장애물(책상 등)은 강제로 지워지지 않도록 보호.
        """
        if scan is None or not scan.points:  # 스캔 데이터가 없으면
            return 0  # 업데이트 없음

        # [중복 스캔 차단] LidarProcessor.get_scan() 은 새 스캔이 없으면 캐시된 직전
        # 스캔을 그대로 반환한다. 라이다는 약 5.5Hz 인데 메인 루프는 15FPS 라, 그대로
        # 두면 같은 관측이 약 2.7배 중복 계수되어 신뢰도 카운트가 부풀려진다.
        scan_ts = getattr(scan, "timestamp", None)
        if scan_ts is not None and scan_ts == self._last_scan_ts:
            return 0
        self._last_scan_ts = scan_ts
        self._free_tick += 1

        now = time.time()

        # [셀 중복 제거] 한 스캔 안에서 여러 광선이 같은 셀을 때리면(사람 폭이 8도만
        # 돼도 광선 17개가 5cm 셀 하나에 수렴) 스캔 1회에 카운트가 +3씩 올랐다.
        # 스캔 1회당 셀 1회로 정규화한다.
        hit_cells = set()
        free_cells = set()
        verified_cells = set()  # 그 중 OAK 화각 안에서 본 끝점 (분류기가 걸러줄 수 있는 셀)

        for point in scan.points:  # 각 포인트에 대해
            if point.distance_m <= 0:  # 거리가 유효하지 않으면
                continue  # 건너뜀

            # 포인트의 극좌표를 직교좌표로 변환 (로봇 헤딩만큼 회전시켜 월드 방향으로 정렬)
            rad   = math.radians(point.angle_deg + self.robot_heading_deg)  # 로봇 헤딩 보정 후 라디안 변환
            x_end = point.distance_m * math.sin(rad)  # 끝점 x (로봇 현재 위치 기준 상대 좌표)
            y_end = point.distance_m * math.cos(rad)  # 끝점 y (로봇 현재 위치 기준 상대 좌표)

            # 끝점을 셀 인덱스로 변환
            end_row, end_col = self.world_to_cell(x_end, y_end)

            # 레이 캐스팅: 로봇 위치에서 포인트까지의 경로를 빈 공간으로 마킹
            ray_cells = self._bresenham(  # Bresenham 알고리즘으로 경로 셀 계산
                self.robot_row, self.robot_col,  # 시작점: 로봇
                end_row, end_col,  # 끝점
            )
            for r, c in ray_cells[:-1]:  # 끝점 제외한 경로 셀들
                if self.in_bounds(r, c):  # 맵 범위 내이면
                    free_cells.add((r, c))

            if self.in_bounds(end_row, end_col):  # 범위 내이면
                hit_cells.add((end_row, end_col))
                # OAK 화각 안의 끝점만 분류기가 사람/벽을 판별해줄 수 있다
                if abs(point.angle_deg) <= self.OAK_VERIFY_HALF_FOV_DEG:
                    verified_cells.add((end_row, end_col))

        # 같은 스캔에서 끝점이기도 한 셀은 빈 공간으로 치지 않는다 (끝점 우선)
        free_cells -= hit_cells

        for r, c in free_cells:
            # [장애물 메모리 보호] 최근 5초 이내에 감지된 장애물 셀은 라이다 빈 공간 광선이 지우지 못하도록 보호!
            if (now - self.last_hit_time[r, c] < self.OBSTACLE_MEMORY_SEC) and (self.grid[r, c] >= CELL_WALL):
                continue
            self._register_free(r, c)  # 빈 공간 카운트 + log-odds 갱신
            self._update_cell(r, c, now)  # 셀 상태 업데이트

        # 승격 자격 판정에 쓰이므로 _update_cell 보다 먼저 찍는다
        for r, c in verified_cells:
            self.oak_seen_time[r, c] = now

        # 끝점은 장애물로 마킹
        updated = 0  # 업데이트된 셀 수
        for r, c in hit_cells:
            self._register_hit(r, c, now)  # 장애물 카운트 + 관측 구간 시작 시각 관리
            self._update_cell(r, c, now)   # 셀 상태 업데이트
            updated += 1  # 업데이트 수 증가

        # 마지막 업데이트 시간 기록
        self.last_update = now
        return updated  # 업데이트된 셀 수 반환

    # ── OAK 깊이맵 업데이트 ───────────────────────────────────────
    # OAK 카메라 데이터를 맵에 반영하는 메서드
    def update_from_oak(self, oak_frame) -> int:
        """
        OAK-D-Lite 장애물 정보를 맵에 반영 (책상 상판 등).
        정면 시야각 내 장애물을 메모리 보호와 함께 등록.
        """
        if oak_frame is None or not oak_frame.obstacles:  # OAK 데이터가 없으면
            return 0  # 업데이트 없음

        now = time.time()
        updated = 0  # 업데이트된 셀 수
        for obs in oak_frame.obstacles:  # 각 장애물에 대해
            if obs.is_wall:  # 벽이면 건너뜀
                continue

            # 장애물의 극좌표를 직교좌표로 변환 (로봇 헤딩만큼 회전시켜 월드 방향으로 정렬)
            rad   = math.radians(obs.angle_deg + self.robot_heading_deg)
            x_end = obs.distance_m * math.sin(rad)
            y_end = obs.distance_m * math.cos(rad)

            # 끝점을 셀 인덱스로 변환
            end_row, end_col = self.world_to_cell(x_end, y_end)

            if self.in_bounds(end_row, end_col):  # 범위 내이면
                # 신뢰도에 따라 가중치 적용
                weight = int(obs.confidence * 4) + 2
                self._register_hit(end_row, end_col, now, weight)  # 카운트 + 관측 구간 시작 시각
                self.oak_seen_time[end_row, end_col] = now  # OAK 가 직접 본 셀 (검증 가능)
                self.free_count[end_row, end_col] = 0       # 기존 free 카운트 리셋 (확실한 장애물 선언)
                self.logodds[end_row, end_col] = max(self.logodds[end_row, end_col], self.L_OAK_FLOOR)
                self.grid[end_row, end_col] = CELL_OBSTACLE # 즉시 장애물 부여

                # [책상 상판 두께 팽창] 장애물 주변 3x3 반경도 함께 메모리 보호 등록
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = end_row + dr, end_col + dc
                        if self.in_bounds(nr, nc):
                            self._register_hit(nr, nc, now)
                            self.oak_seen_time[nr, nc] = now
                            self._update_cell(nr, nc, now)

                updated += 1  # 업데이트 수 증가

        return updated  # 업데이트된 셀 수 반환

    # ── OAK 뎁스 이미지 → 2D 맵 투영 ───────────────────────────────
    def update_from_depth(self, depth_m: np.ndarray) -> int:
        """
        뎁스 이미지(미터)의 픽셀을 높이 필터로 걸러 2D 격자에 투영한다.
        - 로봇 높이 범위(바닥/천장 제외)에 있는 모든 점을 장애물 후보로 기록
        - 셀당 점 개수가 DEPTH_MIN_PTS_PER_CELL 이상일 때만 장애물로 인정 (노이즈 제거)
        - 한 프레임에서 셀당 관측은 1회로 정규화 (update_from_lidar 와 동일한 중복 방지)
        - free 레이캐스팅은 열별 최솟값(가장 가까운 점)까지만 수행
        카메라는 수평 장착(pitch 0)으로 가정한다.
        """
        if depth_m is None or depth_m.ndim != 2 or depth_m.size == 0:
            return 0

        h, w = depth_m.shape
        rows = np.arange(0, h, config.DEPTH_ROW_STEP)
        cols = np.arange(0, w, config.DEPTH_COL_STEP)
        z = depth_m[np.ix_(rows, cols)].astype(np.float32)  # (R, C) 전방 거리(Z)

        # 핀홀 모델 (정사각 픽셀: fx = fy)
        fx = (w / 2.0) / math.tan(math.radians(config.OAK_HFOV_DEG) / 2.0)
        u = (cols - w / 2.0)[None, :]
        v = (rows - h / 2.0)[:, None]

        x_cam = u * z / fx                                        # 카메라 기준 우측 +
        height = config.OAK_HEIGHT_FROM_FLOOR_M - v * z / fx      # 바닥 기준 높이

        valid = (
            (z > config.OAK_DEPTH_MIN_MM / 1000.0) &
            (z < config.OAK_DEPTH_MAX_MM / 1000.0) &
            (height >= config.DEPTH_OBS_MIN_H_M) &
            (height <= config.DEPTH_OBS_MAX_H_M)
        )
        if not valid.any():
            return 0

        # 로봇 헤딩만큼 회전시켜 월드 방향으로 정렬 (update_from_oak 의 angle+heading 과 동일)
        hd = math.radians(self.robot_heading_deg)
        sin_h, cos_h = math.sin(hd), math.cos(hd)
        x_w = x_cam * cos_h + z * sin_h
        y_w = z * cos_h - x_cam * sin_h

        now = time.time()

        # 필터를 통과한 모든 점을 셀 인덱스로 변환
        col_idx = self.robot_col + np.rint(x_w[valid] / self.resolution).astype(np.int64)
        row_idx = self.robot_row - np.rint(y_w[valid] / self.resolution).astype(np.int64)
        inb = (row_idx >= 0) & (row_idx < self.height_cells) & (col_idx >= 0) & (col_idx < self.width_cells)
        flat = row_idx[inb] * self.width_cells + col_idx[inb]
        if flat.size == 0:
            return 0

        # 셀별 점 개수 집계 → 최소 개수 이상인 셀만 장애물
        cells, counts = np.unique(flat, return_counts=True)
        cells = cells[counts >= config.DEPTH_MIN_PTS_PER_CELL]
        r_hit, c_hit = np.divmod(cells, self.width_cells)
        hit_set = set(zip(r_hit.tolist(), c_hit.tolist()))

        # free 레이캐스팅: 열별 최솟값(가장 가까운 점)까지만
        if config.DEPTH_RAYCAST_FREE:
            free_set = set()
            z_masked = np.where(valid, z, np.inf)
            nearest_idx = np.argmin(z_masked, axis=0)
            step = max(1, config.DEPTH_FREE_RAY_COL_STEP // config.DEPTH_COL_STEP)
            for j in range(0, len(cols), step):
                i = nearest_idx[j]
                if not valid[i, j]:
                    continue
                er = self.robot_row - int(round(y_w[i, j] / self.resolution))
                ec = self.robot_col + int(round(x_w[i, j] / self.resolution))
                for r, c in self._bresenham(self.robot_row, self.robot_col, er, ec)[:-1]:
                    if self.in_bounds(r, c):
                        free_set.add((r, c))
            free_set -= hit_set  # 같은 프레임에서 끝점인 셀은 빈 공간으로 치지 않는다
            for r, c in free_set:
                # 라이다/카메라가 최근 장애물로 본 셀은 지우지 않음 (높이가 다른 물체 보호)
                if now - self.last_hit_time[r, c] < self.OBSTACLE_MEMORY_SEC:
                    continue
                self._register_free(r, c)
                self._update_cell(r, c, now)

        # 장애물 셀 갱신. 카메라 화각 안의 관측이므로 oak_seen_time 도 찍는다.
        # 승격 자격 판정에 쓰이므로 _update_cell 보다 먼저 찍는다.
        for r, c in hit_set:
            self.oak_seen_time[r, c] = now
            self._register_hit(r, c, now)
            self.free_count[r, c] = 0
            self.grid[r, c] = CELL_OBSTACLE
            self._update_cell(r, c, now)
        return len(hit_set)

    # ── YOLO 가구 감지 → 2D 맵 투영 ────────────────────────────────
    def update_from_yolo(self, detections, depth_m: np.ndarray) -> int:
        """
        YOLO 가 의자/소파/테이블로 확인한 박스를 맵의 장애물로 투영한다.

        update_from_depth 는 셀당 점 3개 이상이라는 잡음 필터 때문에 멀거나 무늬 없는 상판을
        놓친다. YOLO 박스는 "여기 가구가 있다"는 의미 정보가 있으므로 그 박스 안에서는
        필터를 완화한다.
        - 박스의 열마다, 높이 범위 안(바닥/천장 제외)의 가장 가까운 뎁스를 가구 앞면 거리로 쓴다.
        - 박스 안에 유효 뎁스가 거의 없으면(무늬 없는 상판 등) 박스 하단(바닥 접점)의
          위치로 거리를 추정한다. 카메라 높이/수평 장착 가정(config.OAK_HEIGHT_FROM_FLOOR_M)에 의존한다.
        - 투영된 셀은 hit_count 를 올려 영구 지도 후보가 된다 (set_cell 은 임시 표시일 뿐이었다).
        """
        if not detections or depth_m is None or depth_m.ndim != 2 or depth_m.size == 0:
            return 0

        h, w = depth_m.shape
        fx = (w / 2.0) / math.tan(math.radians(config.OAK_HFOV_DEG) / 2.0)
        z_min = config.OAK_DEPTH_MIN_MM / 1000.0
        z_max = config.OAK_DEPTH_MAX_MM / 1000.0
        hd = math.radians(self.robot_heading_deg)
        sin_h, cos_h = math.sin(hd), math.cos(hd)
        now = time.time()

        hit_set = set()
        for det in detections:
            if det.get("class_id") not in config.YOLO_MAP_CLASS_IDS:
                continue
            if det.get("confidence", 0.0) < config.YOLO_MAP_MIN_CONF:
                continue

            bx1, by1, bx2, by2 = det["bbox_norm"]
            x1, x2 = int(bx1 * w), int(bx2 * w)
            y1, y2 = int(by1 * h), int(by2 * h)
            if x2 - x1 < 4 or y2 - y1 < 4:
                continue

            cols = np.arange(x1, x2, 2)
            rows = np.arange(y1, y2)
            sub = depth_m[np.ix_(rows, cols)].astype(np.float32)          # (R, C)
            height = config.OAK_HEIGHT_FROM_FLOOR_M - (rows - h / 2.0)[:, None] * sub / fx
            ok = (
                (sub > z_min) & (sub < z_max) &
                (height >= config.DEPTH_OBS_MIN_H_M) & (height <= config.DEPTH_OBS_MAX_H_M)
            )
            enough = ok.sum(axis=0) >= config.YOLO_MAP_MIN_COL_PTS         # 열별 뎁스 신뢰 여부

            if enough.mean() >= 0.3:
                # 열별 가장 가까운 유효 뎁스 = 가구 앞면
                z = np.where(ok, sub, np.inf).min(axis=0)
                use = enough
                z, cols_used = z[use], cols[use]
            else:
                # 뎁스 부족: 박스 하단 = 바닥 접점. 수평 카메라의 바닥점 거리 z = H * fx / (y - cy)
                v = y2 - h / 2.0
                if v <= 2.0:
                    continue
                z_floor = config.OAK_HEIGHT_FROM_FLOOR_M * fx / v
                if not (z_min < z_floor < min(config.YOLO_FLOOR_MAX_M, 99.0)):
                    continue
                z = np.full(cols.shape, z_floor, dtype=np.float32)
                cols_used = cols

            x_cam = (cols_used - w / 2.0) * z / fx
            x_w = x_cam * cos_h + z * sin_h
            y_w = z * cos_h - x_cam * sin_h
            c_idx = self.robot_col + np.rint(x_w / self.resolution).astype(np.int64)
            r_idx = self.robot_row - np.rint(y_w / self.resolution).astype(np.int64)
            for r, c in zip(r_idx.tolist(), c_idx.tolist()):
                if self.in_bounds(r, c):
                    hit_set.add((r, c))

        for r, c in hit_set:
            self._register_hit(r, c, now, config.YOLO_MAP_HIT_WEIGHT)
            self.oak_seen_time[r, c] = now          # 카메라 화각 안의 관측
            self.free_count[r, c] = 0
            self.logodds[r, c] = max(self.logodds[r, c], self.L_OAK_FLOOR)
            self.grid[r, c] = CELL_OBSTACLE
            self._update_cell(r, c, now)
        return len(hit_set)

    # ── 셀 상태 갱신 ──────────────────────────────────────────────
    # 셀의 상태를 hit/free 카운트 비율 및 장애물 메모리로 결정하는 내부 메서드
    def _update_cell(self, row: int, col: int, now: Optional[float] = None):
        """hit/free 카운트 비율, 5초 장애물 메모리 보호, 영구 승격 여부로 셀 상태 결정"""
        if now is None:
            now = time.time()

        hit  = self.hit_count[row, col]  # 장애물 감지 횟수
        free = self.free_count[row, col]  # 빈 공간 감지 횟수
        total = hit + free  # 총 감지 횟수

        # [영구 승격] 충분히 여러 번(STATIC_PROMOTE_HIT_COUNT회 초과), 일관되게(비율 0.40 초과)
        # 장애물로 확인된 셀은 static_grid(영구 지도)에 편입시킨다.
        # 이후엔 센서 시야를 벗어나거나 다음 세션에 다시 켜도 계속 기억된다.
        # (사람처럼 움직이는 대상은 한 셀에서 hit_count가 이 정도까지 쌓이기 전에 자리를 벗어나므로
        #  자연히 승격되지 않는다.)
        # 관측이 얼마나 긴 시간에 걸쳐 일관됐는지 (카운트만으로는 프레임률에 좌우된다)
        observed_span = self.last_hit_time[row, col] - self.first_hit_time[row, col]
        # 이번 관측 구간 안에 OAK 화각 관측이 섞여 있으면 분류기가 사람 여부를 걸러줄
        # 수 있다 -> 정상 기준. 측면에서만 본 셀은 그 검증을 못 받았으므로 사람이
        # 버티기 어려운 길이(STATIC_PROMOTE_SIDE_MIN_SEC)를 요구한다.
        oak_verified = (now - self.oak_seen_time[row, col]) <= self.OBSTACLE_MEMORY_SEC
        min_span = (self.STATIC_PROMOTE_MIN_SEC if oak_verified
                    else self.STATIC_PROMOTE_SIDE_MIN_SEC)
        if (hit > self.STATIC_PROMOTE_HIT_COUNT
                and total > 0 and (hit / total) > 0.40
                and observed_span >= min_span
                and now >= self.no_promote_until[row, col]):
            self.static_grid[row, col] = CELL_WALL
            self.grid[row, col] = CELL_WALL
            return

        # [핵심] 최근 5초 이내에 카메라/라이다가 장애물로 등록한 셀은 강제로 장애물 유지!
        if (now - self.last_hit_time[row, col] < self.OBSTACLE_MEMORY_SEC) and (hit >= 2):
            self.grid[row, col] = CELL_OBSTACLE
            return

        if total == 0:  # 감지 기록이 없으면
            return  # 상태 유지

        # [확률 기반 판정] log-odds 로 장애물/빈 공간을 가른다 (그 사이는 현재 상태 유지)
        lo = self.logodds[row, col]

        if lo > self.L_OCC_THRESH:
            # 위의 영구 승격 분기에서 이미 hit > STATIC_PROMOTE_HIT_COUNT 인 경우를 처리했으므로
            # 여기 도달하는 건 항상 승격 기준에 못 미치는(아직 확신이 약한) 일반 장애물이다.
            self.grid[row, col] = CELL_OBSTACLE
        elif lo < self.L_FREE_THRESH:
            self.grid[row, col] = CELL_FREE  # 빈 공간으로 설정
            # [영구 지도 반영] 빈 공간으로 여러 번(5회 이상) 확인된 셀은 static_grid에도 빈 공간으로 편입
            if free >= 5 and self.static_grid[row, col] != CELL_WALL:
                self.static_grid[row, col] = CELL_FREE
        # 그 사이는 현재 상태 유지 (불확실 영역)

    def set_cell(self, row: int, col: int, value: float):
        """특정 셀의 점유 상태 값을 직접 설정 (범위 내부일 때)"""
        if self.in_bounds(row, col):
            self.grid[row, col] = value

    # ── Bresenham 레이 캐스팅 ─────────────────────────────────────
    # 두 셀 사이의 선분을 따라 모든 셀을 반환하는 정적 메서드 (Bresenham 알고리즘)
    @staticmethod
    def _bresenham(r0: int, c0: int, r1: int, c1: int) -> List[Tuple[int, int]]:
        """두 격자 좌표 사이의 셀 목록 반환 (Bresenham 선분 알고리즘)"""
        cells = []  # 셀 리스트
        dr = abs(r1 - r0)  # 행 차이
        dc = abs(c1 - c0)  # 열 차이
        sr = 1 if r1 > r0 else -1  # 행 방향
        sc = 1 if c1 > c0 else -1  # 열 방향
        err = dr - dc  # 오류 값 초기화

        r, c = r0, c0  # 시작점
        max_steps = max(dr, dc) + 1  # 최대 스텝 수

        for _ in range(max_steps):  # 최대 스텝까지 반복
            cells.append((r, c))  # 현재 셀 추가
            if r == r1 and c == c1:  # 끝점에 도달하면
                break  # 종료
            e2 = 2 * err  # 오류 값 계산
            if e2 > -dc:  # 행 방향 조정 필요
                err -= dc
                r   += sr
            if e2 < dr:  # 열 방향 조정 필요
                err += dr
                c   += sc

        return cells  # 셀 리스트 반환

    # ── 맵 통계 ───────────────────────────────────────────────────
    # 맵의 통계 정보를 반환하는 메서드
    def stats(self) -> dict:
        total = self.width_cells * self.height_cells  # 총 셀 수
        obstacle_cells = np.sum(self.grid >= CELL_OBSTACLE)  # 장애물 셀 수
        wall_cells     = np.sum((self.grid >= CELL_WALL) & (self.grid < CELL_OBSTACLE))  # 벽 셀 수
        free_cells     = np.sum((self.grid > 0) & (self.grid < CELL_WALL))  # 빈 공간 셀 수
        unknown_cells  = np.sum(self.grid == CELL_UNKNOWN)  # 미지 셀 수
        return {  # 통계 딕셔너리 반환
            "total": total,  # 총 셀 수
            "obstacle": int(obstacle_cells),  # 장애물 셀 수
            "wall":     int(wall_cells),     # 벽 셀 수
            "free":     int(free_cells),     # 빈 공간 셀 수
            "unknown":  int(unknown_cells),  # 미지 셀 수
            "explored_pct": round((1 - unknown_cells / total) * 100, 1),  # 탐색된 비율 (%)
        }

    # ── 전방 장애물 크기(폭, 길이) 측정 ──────────────────────────────
    def get_front_obstacle_dimensions(
        self,
        max_dist_m: float = 1.5,
        half_width_m: float = 0.8
    ) -> Tuple[float, float, float]:
        """
        로봇 전방 관심 영역(ROI, 로봇의 현재 헤딩 기준) 내 장애물 클러스터의
        실제 물리적 크기(가로 폭, 세로 깊이, 최근접 거리)를 측정.

        맵 격자 자체는 회전하지 않으므로, 로봇 주변을 넉넉히 포함하는
        월드좌표 정사각형 윈도우를 먼저 자른 뒤 각 셀을 로봇 헤딩만큼
        역회전시켜 "로봇 로컬 전방/좌우" 기준으로 판정한다.

        Returns:
            (width_m, length_m, nearest_dist_m)
        """
        y_min, y_max = 0.05, max_dist_m

        # 회전된 ROI(사각형)를 항상 포함할 수 있는 정사각형 탐색 반경
        search_radius_m = math.hypot(half_width_m, max_dist_m)
        r_span = int(math.ceil(search_radius_m / self.resolution)) + 1

        r_start = max(0, self.robot_row - r_span)
        r_end   = min(self.height_cells, self.robot_row + r_span + 1)
        c_start = max(0, self.robot_col - r_span)
        c_end   = min(self.width_cells, self.robot_col + r_span + 1)

        window = self.grid[r_start:r_end, c_start:c_end]
        obs_rows, obs_cols = np.where(window >= CELL_WALL)

        if obs_rows.size == 0:
            return 0.40, 0.45, 999.0  # 장애물 감지 안 됨 (기본값)

        global_rows = obs_rows + r_start
        global_cols = obs_cols + c_start

        # 로봇 기준 월드 좌표 (x=우측+, y=전방+, 헤딩 회전 미반영)
        x_world = (global_cols - self.robot_col) * self.resolution
        y_world = (self.robot_row - global_rows) * self.resolution

        # 로봇 헤딩만큼 역회전 -> 로봇 로컬 좌표(x=로봇 우측+, y=로봇 전방+)
        h = math.radians(self.robot_heading_deg)
        cos_h, sin_h = math.cos(h), math.sin(h)
        x_local = x_world * cos_h - y_world * sin_h
        y_local = x_world * sin_h + y_world * cos_h

        # 로봇 로컬 기준 전방 ROI(가로 ±half_width_m, 세로 y_min~y_max) 안의 셀만 채택
        in_roi = (
            (x_local >= -half_width_m) & (x_local <= half_width_m) &
            (y_local >= y_min) & (y_local <= y_max)
        )
        if not np.any(in_roi):
            return 0.40, 0.45, 999.0  # 장애물 감지 안 됨 (기본값)

        xs = x_local[in_roi]
        ys = y_local[in_roi]

        width_m  = float(np.max(xs) - np.min(xs) + self.resolution)
        length_m = float(np.max(ys) - np.min(ys) + self.resolution)
        nearest_m = float(np.min(ys))

        # 최소 물리 크기 보정 (단일 픽셀 노이즈 방어: 최소 0.20m)
        width_m  = max(0.25, width_m)
        length_m = max(0.25, length_m)

        return width_m, length_m, nearest_m

    # ── 맵 저장 및 불러오기 (File I/O) ──────────────────────────────
    def _resolve_path(self, filepath: str) -> str:
        """상대 경로 입력 시 mapper.py가 위치한 폴더 기준으로 절대 경로 변환"""
        import os
        if not os.path.isabs(filepath):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(base_dir, filepath)
        return filepath

    def save_map(self, filepath: str = "saved_map.npz") -> bool:
        """
        누적된 영구 지도(static_grid)를 압축 파일(.npz)과 시각화 이미지(.png)로 저장.
        static_grid는 사전에 불러온 지도 + 이번 세션에서 충분히 반복 확인되어
        영구 승격된 셀들로 구성된다.
        """
        filepath = self._resolve_path(filepath)

        # 저장 전, 라이다 끝점(벽/장애물)과 빈 공간을 균형 있게 static_grid에 확실하게 동기화
        total_counts = self.hit_count + self.free_count
        hit_ratio = self.hit_count / np.maximum(total_counts, 1)

        # 유효 감지 끝점 (벽 또는 장애물)
        # 라이다가 책상/의자 다리 사이를 통과하면 그 셀에 free 가 훨씬 많이 쌓여 hit 비율이
        # 0.25 에 못 미친다. 그래서 hit 가 충분히 반복된 셀은 비율 조건을 크게 완화한다.
        # 최소 hit 5 는 사람 셀의 상한(PERSON_HIT_CAP=4)보다 커서, 사람 흔적은 저장되지 않는다.
        valid_hits = (self.hit_count >= 2) & (
            (self.hit_count >= self.free_count * 0.25) |
            ((self.hit_count >= 5) & (self.hit_count >= self.free_count * 0.05))
        )
        # 유효 빈 공간
        valid_free = (self.free_count >= 3) & (hit_ratio < 0.20) & (~valid_hits)
        self.static_grid[valid_free] = CELL_FREE

        # [외곽 벽 vs 실내 장애물 기하학적 분리]
        # 미탐색 영역(Unknown)과 맞닿은 60cm 경계면 및 연결된 모든 벽체는 외곽 벽(CELL_WALL),
        # 실내 빈 공간 한가운데 완전히 고립된 독립 점들만 실내 장애물(CELL_OBSTACLE)로 분류
        try:
            import cv2
            unknown_mask = (self.static_grid == CELL_UNKNOWN) & (~valid_hits) & (~valid_free)
            # 미탐색 영역 60cm 마진 팽창 (5x5 커널 5회 반복 = 10셀 = 50~60cm)
            kernel = np.ones((5, 5), np.uint8)
            unknown_dilated = cv2.dilate(unknown_mask.astype(np.uint8), kernel, iterations=5)
            is_outer = (unknown_dilated > 0)

            # 벽면 연결 요소(Connected Components) 분석:
            # 틈새/유리/몰딩 등으로 끊긴 벽면을 3x3 클로징으로 묶은 후, 외곽 마진과 연결된 모든 벽체는 CELL_WALL로 승격
            k_conn = np.ones((3, 3), np.uint8)
            hits_closed = cv2.morphologyEx(valid_hits.astype(np.uint8), cv2.MORPH_CLOSE, k_conn)
            num_labels, labels, _, _ = cv2.connectedComponentsWithStats(hits_closed, connectivity=8)

            wall_mask = np.zeros_like(valid_hits, dtype=bool)
            obs_mask  = np.zeros_like(valid_hits, dtype=bool)

            for i in range(1, num_labels):
                cluster_mask = (labels == i) & valid_hits
                if not np.any(cluster_mask):
                    continue
                # 해당 클러스터의 일부분이라도 외곽 미탐색 마진과 닿아 있으면 외곽 벽체로 판정
                if np.any(is_outer & (labels == i)):
                    wall_mask[cluster_mask] = True
                else:
                    obs_mask[cluster_mask] = True

            self.static_grid[wall_mask] = CELL_WALL
            self.static_grid[obs_mask]  = CELL_OBSTACLE

            # [짧은 벽 조각 재분류] 벽 근처에 놓인 박스/탁자는 위 판정에서 벽과 이어져 벽으로
            # 분류된다. 실제 벽은 길고 연속적이므로, 벽으로 분류된 덩어리 중 긴 변이
            # WALL_MIN_LENGTH_M 미만이고 WALL_FRAGMENT_MIN_CELLS 이상인 것은 장애물로 되돌린다.
            # (그보다 작은 조각은 잡음으로 보고 그대로 둔다)
            wall_u8 = (self.static_grid == CELL_WALL).astype(np.uint8)
            n_w, lab_w, st_w, _ = cv2.connectedComponentsWithStats(wall_u8, connectivity=8)
            max_len_cells = self.WALL_MIN_LENGTH_M / self.resolution
            for i in range(1, n_w):
                longest = max(st_w[i, cv2.CC_STAT_WIDTH], st_w[i, cv2.CC_STAT_HEIGHT])
                if st_w[i, cv2.CC_STAT_AREA] >= self.WALL_FRAGMENT_MIN_CELLS and longest < max_len_cells:
                    self.static_grid[lab_w == i] = CELL_OBSTACLE
        except Exception:
            self.static_grid[valid_hits] = CELL_WALL

        try:
            np.savez_compressed(
                filepath,
                grid=self.static_grid,
                hit_count=self.hit_count,
                free_count=self.free_count,
                logodds=self.logodds,
                resolution=self.resolution,
                width_m=self.width_m,
                height_m=self.height_m,
                robot_col=self.robot_col,
                robot_row=self.robot_row,
                robot_heading=float(self.robot_heading_deg),
                timestamp=time.time(),
            )
        except Exception as e:
            _safe_print(f"[OccupancyMap] ❌ 맵 저장 실패: {e}")
            return False

        # 사람이 열어볼 수 있는 고대비 컬러 PNG 이미지로도 함께 저장.
        img_path = filepath.rsplit(".", 1)[0] + ".png"
        try:
            import cv2
            H, W = self.static_grid.shape
            scale = 2
            rendered = np.zeros((H * scale, W * scale, 3), dtype=np.uint8)

            # 1. 배경 (미지/미탐색 영역): 딥 다크 차콜 (18, 22, 28)
            rendered[:] = (18, 22, 28)

            # 2. 실제 탐색된 주행 가능 맵 (빈 공간): 밝고 깨끗한 세라믹 화이트 (240, 242, 245)
            free_mask = (self.static_grid == CELL_FREE)
            free_img = np.zeros((H, W), dtype=np.uint8)
            free_img[free_mask] = 255
            free_scaled = cv2.resize(free_img, (W * scale, H * scale), interpolation=cv2.INTER_NEAREST)
            rendered[free_scaled > 0] = (240, 242, 245)

            # 3. 외곽 벽 (Outer Wall Boundary): 또렷한 짙은 슬레이트 흑청색 (35, 40, 60)
            wall_mask = (self.static_grid == CELL_WALL)
            wall_img = np.zeros((H, W), dtype=np.uint8)
            wall_img[wall_mask] = 255
            k_wall = np.ones((2, 2), np.uint8)
            wall_dilated = cv2.dilate(wall_img, k_wall, iterations=1)
            wall_scaled = cv2.resize(wall_dilated, (W * scale, H * scale), interpolation=cv2.INTER_NEAREST)
            rendered[wall_scaled > 0] = (35, 40, 60)

            # 4. 실내 장애물 (Obstacles - 테이블/의자/가구): 선명한 네온 코랄 오렌지/레드 (30, 80, 245)
            obs_mask = (self.static_grid >= CELL_OBSTACLE)
            obs_img = np.zeros((H, W), dtype=np.uint8)
            obs_img[obs_mask] = 255
            k_obs = np.ones((3, 3), np.uint8)
            obs_dilated = cv2.dilate(obs_img, k_obs, iterations=1)
            obs_scaled = cv2.resize(obs_dilated, (W * scale, H * scale), interpolation=cv2.INTER_NEAREST)
            rendered[obs_scaled > 0] = (30, 80, 245)

            # [거리 보조 링] 로봇 원점 기준 1m, 2m, 3m 거리 가이드 링 (연한 보조선)
            rc_x = int(self.robot_col * scale)
            rc_y = int(self.robot_row * scale)
            px_per_m = int(round(1.0 / self.resolution * scale))
            if 0 <= rc_x < rendered.shape[1] and 0 <= rc_y < rendered.shape[0]:
                for dist_m in [1.0, 2.0, 3.0]:
                    r_px = int(round(dist_m * px_per_m))
                    cv2.circle(rendered, (rc_x, rc_y), r_px, (42, 50, 64), 1, cv2.LINE_AA)
                    # 링 상단에 거리 텍스트 살짝 표기
                    if rc_y - r_px > 10:
                        cv2.putText(rendered, f"{dist_m:.0f}m", (rc_x + 3, rc_y - r_px - 2),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.28, (90, 105, 125), 1, cv2.LINE_AA)

            # 5. 로봇 위치 및 진행 방향(헤딩) 표시
            if 0 <= rc_x < rendered.shape[1] and 0 <= rc_y < rendered.shape[0]:
                # 로봇 반경 (약 25cm) 가이드 원
                body_r = max(4, int(round(0.25 * px_per_m)))
                cv2.circle(rendered, (rc_x, rc_y), body_r, (100, 180, 240), 1, cv2.LINE_AA)
                cv2.circle(rendered, (rc_x, rc_y), 4, (240, 200, 30), -1)  # 네온 옐로우 코어
                cv2.circle(rendered, (rc_x, rc_y), 6, (255, 255, 255), 1)

                # 로봇 헤딩 화살표 (0도=전방/-Y, +90도=우측/+X)
                rad = math.radians(self.robot_heading_deg)
                arrow_len = max(24, int(round(0.6 * px_per_m)))  # 약 60cm 길이 화살표
                tip_x = int(round(rc_x + arrow_len * math.sin(rad)))
                tip_y = int(round(rc_y - arrow_len * math.cos(rad)))
                cv2.arrowedLine(rendered, (rc_x, rc_y), (tip_x, tip_y),
                                (0, 230, 255), 2, tipLength=0.35, line_type=cv2.LINE_AA)

            # 6. 범례(Legend) 추가 (좌측 상단)
            legend_x, legend_y = 15, 15
            cv2.rectangle(rendered, (legend_x - 5, legend_y - 5), (legend_x + 205, legend_y + 135), (10, 12, 16), -1)
            cv2.rectangle(rendered, (legend_x - 5, legend_y - 5), (legend_x + 205, legend_y + 135), (50, 60, 80), 1)

            heading_str = f"{self.robot_heading_deg:+.0f} deg"
            items = [
                ("Free Space (Walkable)", (240, 242, 245)),
                ("Outer Wall Boundary", (35, 40, 60)),
                ("Obstacle (Table/Chair)", (30, 80, 245)),
                ("Unknown Background", (18, 22, 28)),
                (f"Robot & Head ({heading_str})", (0, 230, 255)),
            ]
            for i, (label, col) in enumerate(items):
                iy = legend_y + i * 24 + 14
                cv2.rectangle(rendered, (legend_x + 6, iy - 8), (legend_x + 22, iy + 5), col, -1)
                cv2.rectangle(rendered, (legend_x + 6, iy - 8), (legend_x + 22, iy + 5), (140, 150, 160), 1)
                cv2.putText(rendered, label, (legend_x + 28, iy + 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (220, 225, 235), 1, cv2.LINE_AA)

            # 7. 맵 좌표축 인디케이터 (우측 상단: 로봇 주행 좌표계 기준 ▲ Front +X, ▶ Right -Y)
            ax_box_w, ax_box_h = 115, 82
            ax_x0 = rendered.shape[1] - ax_box_w - 15
            ax_y0 = 15
            cv2.rectangle(rendered, (ax_x0, ax_y0), (ax_x0 + ax_box_w, ax_y0 + ax_box_h), (10, 12, 16), -1)
            cv2.rectangle(rendered, (ax_x0, ax_y0), (ax_x0 + ax_box_w, ax_y0 + ax_box_h), (50, 60, 80), 1)

            origin_ax = (ax_x0 + 26, ax_y0 + ax_box_h - 22)
            # 전방 (직진 / Robot +X) 축
            cv2.arrowedLine(rendered, origin_ax, (origin_ax[0], origin_ax[1] - 38),
                            (80, 220, 130), 2, tipLength=0.3, line_type=cv2.LINE_AA)
            cv2.putText(rendered, "Front (+X)", (origin_ax[0] - 22, origin_ax[1] - 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 235, 200), 1, cv2.LINE_AA)
            # 우측 (Robot -Y) 축
            cv2.arrowedLine(rendered, origin_ax, (origin_ax[0] + 38, origin_ax[1]),
                            (80, 170, 255), 2, tipLength=0.3, line_type=cv2.LINE_AA)
            cv2.putText(rendered, "Right (-Y)", (origin_ax[0] + 42, origin_ax[1] + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 210, 255), 1, cv2.LINE_AA)

            # 8. 거리 스케일 바 (우측 하단: 1.0m 또는 2.0m 축척 바)
            scale_bar_m = 2.0 if (px_per_m * 2 <= 160) else 1.0
            bar_len_px = int(scale_bar_m * px_per_m)
            sb_w, sb_h = bar_len_px + 36, 44
            sb_x0 = rendered.shape[1] - sb_w - 15
            sb_y0 = rendered.shape[0] - sb_h - 15
            cv2.rectangle(rendered, (sb_x0, sb_y0), (sb_x0 + sb_w, sb_y0 + sb_h), (10, 12, 16), -1)
            cv2.rectangle(rendered, (sb_x0, sb_y0), (sb_x0 + sb_w, sb_y0 + sb_h), (50, 60, 80), 1)

            bx1 = sb_x0 + 18
            bx2 = bx1 + bar_len_px
            by = sb_y0 + 28
            # 스케일 바 라인 및 눈금 틱
            cv2.line(rendered, (bx1, by), (bx2, by), (230, 235, 245), 2, cv2.LINE_AA)
            cv2.line(rendered, (bx1, by - 5), (bx1, by + 5), (230, 235, 245), 2, cv2.LINE_AA)
            cv2.line(rendered, (bx2, by - 5), (bx2, by + 5), (230, 235, 245), 2, cv2.LINE_AA)
            cv2.line(rendered, ((bx1 + bx2) // 2, by - 3), ((bx1 + bx2) // 2, by + 3), (160, 175, 190), 1, cv2.LINE_AA)
            cv2.putText(rendered, f"Scale: {scale_bar_m:.1f}m", (bx1, sb_y0 + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (230, 235, 245), 1, cv2.LINE_AA)

            # 9. 실제 탐색 영역 바운딩 박스 및 하단 상세 정보
            explored_mask = (self.static_grid != CELL_UNKNOWN)
            if np.any(explored_mask):
                rows, cols = np.where(explored_mask)
                w_m = (np.max(cols) - np.min(cols) + 1) * self.resolution
                h_m = (np.max(rows) - np.min(rows) + 1) * self.resolution
                exp_txt = f" | Explored: {w_m:.1f}m x {h_m:.1f}m"
            else:
                exp_txt = ""

            info_txt = f"Map: {self.width_m:.1f}m x {self.height_m:.1f}m (Res: {self.resolution*100:.0f}cm){exp_txt}"
            cv2.putText(rendered, info_txt, (15, rendered.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 175, 195), 1, cv2.LINE_AA)

            # Windows 한글 경로 호환을 위해 imencode 후 tofile 로 저장
            is_ok, buf = cv2.imencode(".png", rendered)
            if is_ok:
                buf.tofile(img_path)
            _safe_print(f"[OccupancyMap] 💾 맵 저장 완료: {filepath} & 고대비 컬러 {img_path}")
        except Exception as e:
            _safe_print(f"[OccupancyMap] 💾 맵 저장 완료: {filepath} (PNG 미리보기는 건너뜀: {e})")
        return True

    def load_map(self, filepath: str = "saved_map.npz") -> bool:
        """저장된 .npz 맵 파일을 불러와 현재 맵 및 static_grid로 복원"""
        import os
        filepath = self._resolve_path(filepath)
        if not os.path.exists(filepath):
            _safe_print(f"[OccupancyMap] ⚠️ 저장된 맵 파일이 존재하지 않습니다: {filepath}")
            return False

        try:
            data = np.load(filepath)
            loaded_grid = data["grid"]
            if loaded_grid.shape == self.grid.shape:
                self.grid[:]        = loaded_grid
                self.static_grid[:] = loaded_grid  # 사전 정적 지도 기준점으로 보관
                if "hit_count" in data:
                    self.hit_count[:] = data["hit_count"]
                if "free_count" in data:
                    self.free_count[:] = data["free_count"]
                if "logodds" in data:
                    self.logodds[:] = data["logodds"]
                else:
                    # 이전 형식의 맵: 저장된 카운트로 log-odds 를 근사 복원
                    self.logodds[:] = np.clip(
                        self.hit_count * self.L_HIT + self.free_count * self.L_FREE,
                        self.LOGODDS_MIN, self.LOGODDS_MAX,
                    )
                if "robot_col" in data and "robot_row" in data:
                    self.robot_col = int(data["robot_col"])
                    self.robot_row = int(data["robot_row"])
                if "robot_heading" in data:
                    self.robot_heading_deg = float(data["robot_heading"])
                loaded_now = time.time()
                self.last_hit_time[:] = loaded_now   # 메모리 보호 시간 갱신
                self.first_hit_time[:] = loaded_now  # 불러온 셀이 시간 폭 조건을 거저 통과하지 않도록
                _safe_print(f"[OccupancyMap] 📂 맵 불러오기 성공: {filepath} (크기: {self.grid.shape}, 로봇 헤딩: {self.robot_heading_deg:+.1f} deg)")
                return True
            else:
                _safe_print(f"[OccupancyMap] ⚠️ 맵 격자 해상도/크기 불일치 (현재: {self.grid.shape}, 로드: {loaded_grid.shape})")
                return False
        except Exception as e:
            _safe_print(f"[OccupancyMap] ❌ 맵 불러오기 오류: {e}")
            return False

    def prepare_frame(self):
        """
        매 프레임 센서 업데이트 전 호출: 사전 저장된 정적 맵(static_grid)을 베이스로 유지하되,
        최근 OBSTACLE_MEMORY_SEC(기본 5초) 이내에 확인된 장애물 셀은 이번 프레임에 센서
        시야를 벗어났더라도 그대로 유지한다 (OAK처럼 시야각이 좁은 센서가 잠깐 다른 곳을
        보는 사이 장애물이 지도에서 사라지는 것을 방지).
        """
        now = time.time()
        protected = (self.hit_count >= 2) & ((now - self.last_hit_time) < self.OBSTACLE_MEMORY_SEC)
        self.grid[:] = np.where(protected, CELL_OBSTACLE, self.static_grid)

    # 맵 전체를 초기화하는 메서드 (사용자 초기화 버튼 클릭 시)
    def reset(self):
        self.grid[:]          = CELL_UNKNOWN  # 그리드 초기화
        self.static_grid[:]   = CELL_UNKNOWN  # 정적 맵 초기화
        self.hit_count[:]     = 0             # 히트 카운트 초기화
        self.free_count[:]    = 0             # 프리 카운트 초기화
        self.logodds[:]       = 0.0           # log-odds 초기화
        self.last_hit_time[:] = 0.0           # 장애물 메모리 초기화
        self.first_hit_time[:] = 0.0          # 관측 구간 시작 시각 초기화
        self.no_promote_until[:] = 0.0        # 승격 차단 표시 초기화
        self.oak_seen_time[:] = 0.0           # OAK 검증 관측 시각 초기화
        self._last_scan_ts = None             # 중복 스캔 판별 상태 초기화
