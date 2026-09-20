"""
path_recommender.py
서빙 로봇 19방향 하이브리드 경로 추천 & 4단계 ㄷ자 장애물 회피 시스템

핵심 아키텍처 및 동작 로직:
  1. [19방향 레이마칭 & 50x50cm 풋프린트 스코어링]
     - 로봇 정면 기준 10도 간격(-90° ~ +90°) 19개 방향으로 로봇 차체(50cm x 50cm)의 안전 여유 거리를 레이마칭 측정.
     - 목표 좌표(Target X, Y) 지향성 가중치 및 직진 보너스를 복합 스코어링하여 최적 경로를 추천.

  2. [목표 지향 2단계 순차 자율주행 (X축 정렬 -> Y축 정렬)]
     - 시작 위치 원점 기준 상대 좌표 추적 및 10cm 이내 도달 시 정지 및 목표 도착(GOAL_REACHED) 처리.

  3. [4단계 ㄷ자형 회피 상태 머신 (완료 즉시 목표 지향 주행으로 복귀)]
     - 0단계 (AVOID_BRAKE)       : 전방 장애물(30cm) 감지 시 관성 제동 및 완전 정지
     - 1단계 (AVOID_TURN_90)      : 더 넓게 트인 측면으로 직각 90도 회전
     - 2단계 (AVOID_PASS_WIDTH)   : 실측 장애물 폭에 맞춘 가로 직진 & 측면 초음파 감시
     - 3단계 (AVOID_TURN_FRONT)   : 원래 진행 방향으로 정렬 회전
     - 4단계 (AVOID_PASS_LENGTH)  : 실측 장애물 길이에 맞춘 세로 추월 직진 (초음파 이탈 감지) -> 완료 시 IDLE
     - 원래 지나가던 레인으로 굳이 복귀하지 않고, 장애물을 지나친 "현재 위치"에서 바로 2번(목표 지향 주행)이
       다시 dx/dy를 계산해 목표를 향해 재조준한다. 레인 복귀용 회전+직진 왕복이 없어 더 짧고 빠르다.

  4. [다중 센서 융합 & 에러 세이프가드]
     - 라이다(LiDAR) + 뎁스 카메라(OAK-D) + 좌/우 초음파 센서 융합
     - 초음파 센서 -1/에러 값 수신 시 999.0cm(안전)로 자동 변환 및 3개 중간값(Median) 노이즈 필터링

  5. [BLE JSON 제어 프로토콜 & 400ms 중복 방지]
     - 패킷 규격: {"S-signal": "...", "R-signal": "..."}
     - 정지: {"S-signal": "STOP", "R-signal": ""} / 리셋: {"S-signal": "STOP", "R-signal": "RESET_ODO"}
"""

import math
import re
import json
import time
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import config
from mapper import OccupancyMap, CELL_WALL, CELL_OBSTACLE


@dataclass
class DirectionScore:
    angle_deg: float
    score: float
    clearance_m: float
    has_unknown: bool
    label: str


@dataclass
class PathRecommendation:
    best_angle_deg: float
    best_label: str
    reason: str
    scores: List[DirectionScore]
    is_stuck: bool = False
    target_x: Optional[float] = None
    target_y: Optional[float] = None
    target_name: str = ""
    dist_to_goal_m: Optional[float] = None
    goal_rel_angle_deg: Optional[float] = None
    is_goal_reached: bool = False
    robot_x: float = 0.0
    robot_y: float = 0.0
    robot_heading_deg: float = 0.0
    obs_w: float = 0.0            # 실측 전방 장애물 폭 (m)
    obs_l: float = 0.0            # 실측 전방 장애물 길이 (m)
    target_avoid_w: float = 0.0   # 동적 목표 가로 회피 거리 (m)
    target_avoid_l: float = 0.0   # 동적 목표 세로 추월 거리 (m)
    fault_code: int = 0           # 0=정상 1=모터스톨 2=헤딩포화 3=바퀴편차 4=슬립(라이다)
    fault_reason: str = ""        # 사람이 읽을 수 있는 이상 상태 설명


class PathRecommender:
    # ── 설정 ─────────────────────────────────────────────────────
    FRONT_STOP_DIST_M = config.ZONE_DANGER_M  # 전방 장애물 감지 기준 거리 (config의 즉시정지 거리와 통일)
    ROBOT_HALF_M      = 0.25   # 로봇 몸체 절반 (50cm / 2 = 25cm)
    SAFE_MARGIN_M     = 0.30   # 몸체 반폭 + 안전 여유 (25cm + 5cm)
    MAX_RANGE_M       = 3.0    # 센서 최대 탐색 거리 (m)
    CELL_THRESHOLD    = 0.6    # 충돌 감지 임계점
    STOP_ANGLE        = -1.0   # 정지 신호
    UTURN_ANGLE       = 180.0  # 유턴 신호
    ARRIVE_MARGIN_M   = 0.10   # 목표 도착 판단 오차 거리 (0.10m = 10cm 주변 도달 시 정지)
    AXIS_ALIGN_DONE_M      = 0.10  # X/Y 축 정렬 완료로 볼 오차 (히스테리시스 하한)
    AXIS_REALIGN_TRIGGER_M = 0.15  # 정렬 완료 후 다시 재정렬로 들어갈 오차 (히스테리시스 상한, 경계 근처 진동 방지)
    HEADING_ALIGN_DONE_DEG      = 15.0  # 헤딩 정렬 완료로 볼 오차 (히스테리시스 하한)
    HEADING_REALIGN_TRIGGER_DEG = 20.0  # 정렬 완료 후 다시 턴을 시작할 오차 (히스테리시스 상한, 경계 근처 진동 방지)

    # ㄷ자 회피 거리 상수 (m)
    MIN_AVOID_WIDTH_M  = 0.40   # 90도 회전 후 가로 폭 최소 직진 보장 거리 (40cm)
    MAX_AVOID_WIDTH_M  = 0.65   # 가로 폭 최대 직진 거리 (65cm)
    MIN_AVOID_LENGTH_M = 0.45   # 0도 정렬 후 세로 길이 최소 직진 보장 거리 (45cm)
    MAX_AVOID_LENGTH_M = 0.70   # 세로 길이 최대 직진 거리 (70cm)
    MAX_AVOID_RETRY    = 3      # 회피 직진 중 전방이 다시 막혀 회피를 재시작할 수 있는 최대 횟수

    # ── 라이다 기반 슬립 감지 ────────────────────────────────────
    # 오도메트리는 엔코더에서 나오므로 바퀴가 헛돌면 같이 속는다. 라이다는 바퀴와
    # 무관한 유일한 관측 수단이라, "오도메트리는 갔다는데 세상은 그대로"를 잡아낸다.
    SLIP_WINDOW_SEC       = 2.0   # 현재 스캔과 비교할 과거 시점
    SLIP_MIN_ODO_M        = 0.25  # 이만큼 이동했다고 오도메트리가 주장하는데
    SLIP_MAX_SCAN_DELTA_M = 0.05  # 라이다가 본 세상이 이만큼도 안 변했으면 슬립
    SLIP_STRUCT_RATIO     = 0.30  # 0.2~4m 유효 포인트 비율. 미만이면 판정 보류
    SLIP_MIN_MATCHED      = 30    # 두 스캔 사이에 각도가 매칭된 최소 포인트 수
    # [오검출 방지] 오도메트리 좌표가 물리적으로 불가능한 속도로 튀면 그건 "이동"이
    # 아니라 데이터 불연속(PC 재시작으로 메가의 누적 좌표를 뒤늦게 받음, BLE 재연결,
    # 패킷 오파싱)이다. 실측 주행 속도는 0.35~0.39m/s 이므로 1.0m/s 를 넘는 변화는
    # 전부 불연속으로 간주하고 비교 창을 통째로 버린다.
    SLIP_MAX_PLAUSIBLE_MPS = 1.0

    # ── 이상 상태 탈출 (REVERSE 명령) ────────────────────────────
    # 로봇 후방에는 센서가 하나도 없다 (라이다 FOV 180도, 초음파는 좌/우, OAK 는 전방).
    # 후방 판정은 "방금 지나온 자리"라는 맵 메모리에만 의존하므로, 뒤에서 걸어온
    # 사람은 볼 수 없다. 그래서 후진은 반드시 짧아야 하고 1회로 제한한다.
    FAULT_REVERSE_TIMEOUT_SEC = 2.5   # 메가는 1.5초/25cm 에 자체 종료. 여유를 둔 상한
    FAULT_REAR_CLEAR_M        = 0.45  # 후진 25cm + 여유. 이보다 좁으면 후진 포기
    MAX_FAULT_RETRY           = 1     # 자동 탈출 시도 횟수

    # ── 180도 선회 탈출 ──────────────────────────────────────────
    # 후진보다 나은 이유: 180도 돌면 라이다가 탈출 방향을 보게 되므로,
    # "눈 감은 후진"이 "눈 뜬 전진"으로 바뀐다.
    # 단 제자리 회전은 코너가 원을 그리며 스윕한다. 50x50cm 로봇의 반대각선은
    # 0.354m 라, 전방 면 기준으로 최소 10cm 여유가 없으면 코너가 벽을 파고든다.
    ROT_SWEEP_MARGIN_M       = 0.05  # 스윕 반경(0.354m)에 더할 안전 여유
    ESCAPE_FWD_DIST_M        = 0.40  # 회전 후 벽에서 물러날 거리
    ESCAPE_FWD_TIMEOUT_SEC   = 3.0   # 슬립이면 오도메트리가 안 늘어나므로 시간으로도 끊는다
    ESCAPE_TURN_TIMEOUT_SEC  = 8.0   # 180도 선회가 끝나지 않을 때의 상한

    # fault 코드 (메가와 동일한 번호 체계)
    FAULT_NONE, FAULT_STALL, FAULT_HEADING, FAULT_WHEEL, FAULT_SLIP = 0, 1, 2, 3, 4
    FAULT_NAMES = {
        1: "모터 스톨 (바퀴가 물리적으로 멈춤)",
        2: "헤딩 보정 포화 (한쪽이 걸려 방향이 틀어짐)",
        3: "바퀴 편차 (한 바퀴가 들리거나 걸림)",
        4: "슬립 (바퀴는 도는데 로봇이 안 움직임)",
    }

    # 검사할 10도 단위 세분화 19방향 (각도, 레이블)
    DIRECTIONS = [
        (0,    "Front"),       # 전방
        (10,   "Right-10"),    # 우측 10도
        (20,   "Right-20"),    # 우측 20도
        (30,   "Right-30"),    # 우측 30도
        (40,   "Right-40"),    # 우측 40도
        (50,   "Right-50"),    # 우측 50도
        (60,   "Right-60"),    # 우측 60도
        (70,   "Right-70"),    # 우측 70도
        (80,   "Right-80"),    # 우측 80도
        (90,   "Right-90"),    # 우측 90도 (직각 우회)
        (-10,  "Left-10"),     # 좌측 10도
        (-20,  "Left-20"),     # 좌측 20도
        (-30,  "Left-30"),     # 좌측 30도
        (-40,  "Left-40"),     # 좌측 40도
        (-50,  "Left-50"),     # 좌측 50도
        (-60,  "Left-60"),     # 좌측 60도
        (-70,  "Left-70"),     # 좌측 70도
        (-80,  "Left-80"),     # 좌측 80도
        (-90,  "Left-90"),     # 좌측 90도 (직각 좌회)
    ]

    # BLE 메시지 파싱 정규식: "right, left" 2개 또는 "x, y, heading, right, left" 5개 포맷 통합 지원
    BLE_PATTERN = re.compile(
        r"(?:(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*)?(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)",
    )

    def __init__(self, occ_map: OccupancyMap, use_mock: bool = False):
        self.occ_map = occ_map

        # 로봇 몸체 풋프린트 (50cm x 50cm 사각형) 격자 오프셋 사전 계산
        self.footprint_offsets: List[Tuple[int, int]] = []
        self._precompute_footprint()

        # 회피 전용 디귿(ㄷ)자형 초음파 측면 감지 상태 머신
        # ("IDLE" | "AVOID_TURN_90" | "AVOID_PASS_WIDTH" | "AVOID_TURN_FRONT" | "AVOID_PASS_LENGTH")
        self.avoid_state: str = "IDLE"
        self.avoid_side: str = "RIGHT"          # "RIGHT" (+90도 우회전 후 좌측초음파 감시) | "LEFT" (-90도 좌회전 후 우측초음파 감시)
        self.avoid_base_head: float = 0.0       # 장애물 감지 시점의 원래 진행 목표 각도 (0, 90, -90, 180)
        self.avoid_target_head: Optional[float] = None
        self.target_avoid_width_m: float = 0.40   # 장애물 크기 기반 동적 목표 가로 회피 거리
        self.target_avoid_length_m: float = 0.45  # 장애물 크기 기반 동적 목표 세로 추월 거리
        self.obs_measured_w: float = 0.0        # 실측 장애물 가로 폭 (m)
        self.obs_measured_l: float = 0.0        # 실측 장애물 세로 길이 (m)
        self.avoid_brake_timer: int = 0         # 회피 전 관성 제동(긴급 브레이크) 프레임 타이머
        self.avoid_start_x: float = 0.0         # 회피 각 단계 시작 시점의 로봇 X 좌표
        self.avoid_start_y: float = 0.0         # 회피 각 단계 시작 시점의 로봇 Y 좌표
        self.avoid_clear_count: int = 0         # 측면 초음파 값 급증(장애물 이탈) 연속 감지 카운트
        self.avoid_step_timeout: int = 0        # 무한 직진 방지 안전 타임아웃
        self.avoid_min_steps: int = 0           # 최소 직진 보장 카운터
        self.avoid_forward_timer: int = 0
        self.avoid_retry_count: int = 0         # 회피 직진 중 전방 재차단으로 회피를 다시 시작한 횟수

        # BLE 중복 전송 억제 및 통신 락 변수
        self.last_sent_payload: str = ""
        self.last_sent_time: float = 0.0

        # 상태 머신 (기본 대기 상태: STOPPED -> [주행 시작] 클릭 시 FORWARD 전환)
        self.state = "STOPPED"   # "STOPPED" | "FORWARD" | "TURNING" | "GOAL_REACHED"
        self.aligning_heading: bool = False  # 버튼 클릭 시 0도/360도 1도 단위 정렬 활성화 플래그
        self.turn_angle = 0.0    # 회피 방향 각도
        self.turn_label = ""     # 회피 방향 라벨
        self.turn_timer = 0      # 회피 유지 프레임
        self._heading_turning = False  # 직전 프레임에 헤딩 턴 중이었는지 (히스테리시스용)

        # 목표 좌표 관련 변수
        self.target_x: Optional[float] = None
        self.target_y: Optional[float] = None
        self.target_name: str = ""

        # 주행 시작 시점의 기준 원점 (로봇 전방=+X, 좌측=+Y, 우측=-Y)
        self.origin_x: float = 0.0
        self.origin_y: float = 0.0
        self.origin_heading: float = 0.0

        # 로봇 현재 추적 오도메트리 위치
        self.robot_x: float = 0.0
        self.robot_y: float = 0.0
        self.robot_heading_deg: float = 0.0

        # 이상 상태 (메가에서 BLE 6번째 필드로 오거나, PC가 라이다로 직접 판정)
        self.mega_fault: int = 0        # 메가가 보고한 코드 (원시값)
        self.fault_code: int = 0        # 확정된 이상 상태 (래치됨)
        self.fault_reason: str = ""
        # "NONE" | "REVERSING" | "ESCAPE_TURN" | "ESCAPE_FWD" | "DONE"
        self.fault_stage: str = "NONE"
        self.fault_reverse_start: float = 0.0
        self.fault_retry_count: int = 0
        self.fault_escape_head: float = 0.0   # 180도 선회 목표 헤딩
        self.fault_escape_x: float = 0.0      # 탈출 전진 시작 좌표
        self.fault_escape_y: float = 0.0
        self._scan_history: List[Tuple[float, dict, float, float, float]] = []
        self._last_scan_ts: float = -1.0   # 같은 스캔을 두 번 넣지 않기 위한 신선도 검사용

        # BLE 수신 데이터 저장 (초기 시작 시 오인 정지/회피 방지를 위해 999.0cm로 초기화)
        self.ble_right_cm = 999.0
        self.ble_left_cm  = 999.0
        self.ble_right_history = []
        self.ble_left_history = []

        # BLE 프로세서 연결
        self.use_mock = use_mock
        self.ble = None
        if not use_mock:
            try:
                from BLE_processor import ble_processor
                self.ble = ble_processor()
                self.ble.start()
                print("[PathRecommender] BLE 연결 완료")
            except Exception as e:
                print(f"[PathRecommender] BLE 연결 실패 (단독 모드): {e}")
        else:
            print("[PathRecommender] Simulation Mock Mode: BLE 무선 연결 건너뜀 (가상 오도메트리)")

    # ── 풋프린트 사전 계산 (50cm x 50cm 사각형) ──────────────────
    def _precompute_footprint(self):
        """로봇 50cm x 50cm 사각형 몸체의 격자 오프셋 계산"""
        res = self.occ_map.resolution
        half_cells = int(math.ceil(self.ROBOT_HALF_M / res))
        # 레이마칭은 이 반경으로 numpy 슬라이스를 잘라 쓴다.
        # footprint_offsets 자체는 외부(test_run.py 등) 호환을 위해 그대로 유지한다.
        self.footprint_half_cells = half_cells
        for dr in range(-half_cells, half_cells + 1):
            for dc in range(-half_cells, half_cells + 1):
                self.footprint_offsets.append((dr, dc))

    # ── "주행 시작" 및 "주행 정지", "헤딩 정렬" 메소드 ───────────────────────
    def start_heading_alignment(self):
        """'헤딩 정렬' 버튼 클릭 시: 0도 또는 360도 중 더 가까운 쪽에 1도 단위로 정렬 시작"""
        self._poll_ble()
        self.aligning_heading = True
        print(f"\n[PathRecommender] [ALIGN] 헤딩 0°/360° 정렬 시작! (현재 헤딩: {self.robot_heading_deg:.1f}°)")

    def start_navigation(self, x_m: float, y_m: float, name: str = "Goal"):
        """'주행 시작': 목표 좌표(글로벌 절대 좌표계)로 주행 개시"""
        self._poll_ble()
        self.aligning_heading = False
        self.avoid_state = "IDLE"
        self.avoid_target_head = None
        self.avoid_forward_timer = 0
        self.avoid_retry_count = 0
        self.fault_code = 0
        self.fault_reason = ""
        self.mega_fault = 0   # 낡은 보고값으로 즉시 재래치되는 것을 막는다
        self.fault_stage = "NONE"
        self.fault_retry_count = 0
        self._scan_history.clear()

        self.target_x = float(x_m)
        self.target_y = float(y_m)
        self.target_name = name
        self.state = "FORWARD"
        self.sub_stage = "ALIGN_X"  # 1단계 X축 정렬 -> 2단계 Y축 정렬 순차 주행
        print(f"\n[PathRecommender] [START] 주행 시작! 목표 좌표: ({x_m:.2f}, {y_m:.2f}) [전방=+X, 좌측=+Y, 우측=-Y] (현재 로봇: ({self.robot_x:.2f}, {self.robot_y:.2f}))")

    def _send_stop_packet(self, reset_odo: bool = False):
        """
        정지 신호를 딕셔너리(JSON) 형태로 BLE 송신합니다.
        - 평상시 (구동 전 / 대기 / 정지): {"S-signal": "STOP", "R-signal": ""}
        - 좌표 초기화 버튼 클릭 시: {"S-signal": "STOP", "R-signal": "RESET_ODO"}
        """
        self._send_ble("STOP", "RESET_ODO" if reset_odo else "", force=True)

    def stop_navigation(self):
        """'주행 정지': 즉시 주행을 취소하고 정지 신호 {"S-signal":"STOP", "R-signal":""} 전송 및 STOPPED 상태 전환"""
        self.target_x = None
        self.target_y = None
        self.target_name = ""
        self.avoid_state = "IDLE"
        self.avoid_target_head = None
        self.avoid_forward_timer = 0
        self.avoid_retry_count = 0
        self.fault_code = 0
        self.fault_reason = ""
        self.mega_fault = 0   # 낡은 보고값으로 즉시 재래치되는 것을 막는다
        self.fault_stage = "NONE"
        self.fault_retry_count = 0
        self._scan_history.clear()
        self.aligning_heading = False
        self.state = "STOPPED"
        self._send_stop_packet(reset_odo=False)
        print("\n[PathRecommender] [STOP] 주행 정지! (사용자 정지 요청 -> 정지 패킷 {\"S-signal\":\"STOP\", \"R-signal\":\"\"} 전송)")

    def reset_odometry(self):
        """'오도메트리 초기화': 로봇 내부 좌표를 0.0으로 리셋하고 BLE를 통해 {"S-signal":"STOP", "R-signal":"RESET_ODO"} 전송"""
        self.stop_navigation()
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_heading_deg = 0.0
        self.origin_x = 0.0
        self.origin_y = 0.0
        self.origin_heading = 0.0
        self.avoid_state = "IDLE"
        self.avoid_target_head = None
        self.avoid_forward_timer = 0
        self.aligning_heading = False
        self._send_stop_packet(reset_odo=True)
        print("\n[PathRecommender] [RESET] 오도메트리 리셋 신호 {\"S-signal\":\"STOP\", \"R-signal\":\"RESET_ODO\"} BLE 전송 완료")

    def set_target(self, x_m: float, y_m: float, name: str = "Goal"):
        """목표 좌표 설정 호환용 래퍼"""
        self.start_navigation(x_m, y_m, name)

    def clear_target(self):
        """목표 좌표 해제 호환용 래퍼"""
        self.stop_navigation()

    def set_target_goal(self, x_m: float, y_m: float, name: str = "Target"):
        """목표 좌표 호환용 래퍼"""
        self.start_navigation(x_m, y_m, name)

    def clear_target_goal(self):
        """목표 좌표 해제 호환용 래퍼"""
        self.stop_navigation()

    def _compute_goal_vector(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        글로벌 절대 좌표계 기준 로봇 현재 위치에서 목표 (target_x, target_y)까지의
        (남은거리m, 로봇 상대 목표 각도deg, 목표 절대 각도deg) 계산.
        축 정의: 전방=+X(0도), 좌측=+Y(-90도), 우측=-Y(+90도), 후방=-X(180도)
        """
        if self.target_x is None or self.target_y is None:
            return None, None, None

        # 글로벌 절대 좌표 기준 목표와의 오차 벡터 (전방=+X, 좌측=+Y, 우측=-Y)
        dx = self.target_x - self.robot_x
        dy = self.target_y - self.robot_y
        dist_m = math.hypot(dx, dy)

        # dx:전방(+X), dy:좌측(+Y)/우측(-Y) -> atan2(-dy, dx) => 전방=0도, 우측=+90도, 좌측=-90도, 후방=180도
        goal_global_deg = math.degrees(math.atan2(-dy, dx))

        # 로봇 헤딩 차이 보정 (0도 기준)
        rel_angle_deg = goal_global_deg - self.robot_heading_deg
        rel_angle_deg = (rel_angle_deg + 180.0) % 360.0 - 180.0

        return dist_m, rel_angle_deg, goal_global_deg

    def _is_still_turning(self, target_heading_deg: float) -> Tuple[bool, float]:
        """
        목표 절대 헤딩(target_heading_deg)과 현재 헤딩의 오차를 계산하고,
        히스테리시스를 적용해 "아직 턴 중인지"를 판정한다.
        - 직전 프레임에 턴 중이었다면 HEADING_ALIGN_DONE_DEG(15도)까지 좁혀져야 정렬 완료로 본다.
        - 직전 프레임에 턴 중이 아니었다면(직진 중) HEADING_REALIGN_TRIGGER_DEG(20도)를
          넘어야 다시 턴을 시작한다.
        오차가 15~20도 경계 근처에서 노이즈로 흔들려도 턴↔직진을 계속 왔다갔다하지 않도록 함.

        Returns: (is_turning, head_err)
        """
        current_head = (self.robot_heading_deg - self.origin_heading + 180.0) % 360.0 - 180.0
        head_err = (target_heading_deg - current_head + 180.0) % 360.0 - 180.0
        threshold = self.HEADING_ALIGN_DONE_DEG if self._heading_turning else self.HEADING_REALIGN_TRIGGER_DEG
        self._heading_turning = abs(head_err) > threshold
        return self._heading_turning, head_err

    def _get_heading_alignment_steering(self, target_heading_deg: float) -> Tuple[float, str]:
        """
        목표 절대 헤딩 각도(target_heading_deg, 전방 기준 0도, 우측 +90, 좌측 -90, 후방 180)와
        현재 로봇 헤딩(self.robot_heading_deg) 간의 오차를 계산하여
        15도 이내로 정렬되면 직진(0.0, 'Front'),
        15도 초과 오차 시 부드러운 10도 단위 회전 명령을 반환합니다.
        """
        current_head = (self.robot_heading_deg - self.origin_heading + 180.0) % 360.0 - 180.0
        head_err = (target_heading_deg - current_head + 180.0) % 360.0 - 180.0

        # 헤딩 오차가 15도 이내이면 정렬 완료 -> 시원하게 직진!
        if abs(head_err) <= 15.0:
            return 0.0, "Front"

        # 헤딩 오차가 클 때는 10도 단위로 부드럽게 회전 (20도 ~ 90도 범위 클리핑)
        if head_err > 0:
            turn_deg = min(90.0, max(20.0, round(head_err / 10.0) * 10.0))
            return turn_deg, f"Right-{int(turn_deg)}"
        else:
            turn_deg = max(-90.0, min(-20.0, round(head_err / 10.0) * 10.0))
            return turn_deg, f"Left-{int(abs(turn_deg))}"

    def _get_zero_alignment_steering_1deg(self) -> Tuple[float, str, float, bool]:
        """
        '헤딩 정렬' 버튼 클릭 시, BLE를 통해 들어오는 현재 헤딩값을
        0과 360 중 더 가까운 쪽에 1도 단위 정밀 각도로 맞춥니다.

        반환값:
            (chosen_angle, chosen_label, target_head, is_aligned)
        """
        curr_head = (self.robot_heading_deg % 360.0 + 360.0) % 360.0  # 0.0 ~ 360.0 정규화

        diff_0 = abs(curr_head - 0.0)
        diff_360 = abs(curr_head - 360.0)

        if diff_0 <= diff_360:
            target_head = 0.0
            head_err = (0.0 - curr_head + 180.0) % 360.0 - 180.0
        else:
            target_head = 360.0
            head_err = (360.0 - curr_head + 180.0) % 360.0 - 180.0

        # 오차 1도 이내이면 정렬 완료!
        if abs(head_err) <= 1.0:
            return 0.0, "Front", target_head, True

        # 1도 단위 정밀 조향 (오차 각도를 1도 단위로 정수 클리핑 송신)
        turn_deg = float(max(-90, min(90, int(round(head_err)))))
        label = f"Right-{int(turn_deg)}" if turn_deg > 0 else f"Left-{int(abs(turn_deg))}"
        return turn_deg, label, target_head, False

    # ── BLE 메시지 수신 및 파싱 (실시간 x, y, heading 수신) ──────────────────
    def _poll_ble(self):
        """
        BLE 수신 데이터를 파싱하여 실시간 x, y, heading 좌표 및 초음파 센서값을 갱신합니다.
        지원 포맷:
        1. 5개 인자: "x, y, heading, right, left" (예: "0.25, 1.10, 0.0, 100, 80")
        2. 3개 인자: "x, y, heading" (예: "0.25, 1.10, 15.0")
        3. 2개 인자: "x, y" (예: "0.25, 1.10")
        4. Key-Value 형식: "X:0.25 Y:1.10 H:0.0" 또는 "x=0.25, y=1.10"
        5. 초음파 전용: "RIGHT: 50 LEFT: 80"
        """
        if self.ble is None:
            return

        # 큐에 쌓인 메시지를 모두 읽어서 가장 최신 값만 사용
        latest = None
        while True:
            msg = self.ble.get_response()
            if msg is None:
                break
            latest = msg

        if latest is None:
            return

        try:
            if latest.startswith("__"):
                return

            text = latest.strip()

            # 1. Key-Value 형태 파싱 (X:, Y:, H:, R:, L:)
            kx = re.search(r"[xX]\s*[:=]\s*(-?\d+(?:\.\d+)?)", text)
            ky = re.search(r"[yY]\s*[:=]\s*(-?\d+(?:\.\d+)?)", text)
            kh = re.search(r"(?:[hH]|heading)\s*[:=]\s*(-?\d+(?:\.\d+)?)", text, re.IGNORECASE)
            kr = re.search(r"(?:[rR]|right)\s*[:=]\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
            kl = re.search(r"(?:[lL]|left)\s*[:=]\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)

            if kx and ky:
                self.robot_x = float(kx.group(1))
                self.robot_y = float(ky.group(1))
                if kh:
                    self.robot_heading_deg = float(kh.group(1))
                if kr and kl:
                    self._update_ultrasonic(float(kr.group(1)), float(kl.group(1)))
                print(f"[BLE 수신] 원본: '{text}' -> 파싱: (X:{self.robot_x:+.2f}m, Y:{self.robot_y:+.2f}m, Head:{self.robot_heading_deg:+.1f}deg)")
                return

            # 2. 쉼표(,) 및 공백 기반 숫자 분리 파싱
            parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
            nums = []
            for p in parts:
                try:
                    nums.append(float(p))
                except ValueError:
                    pass

            if len(nums) >= 5:
                # [x값, y값, 헤딩, 오른쪽초음파, 왼쪽초음파, (선택)이상상태코드]
                self.robot_x = nums[0]
                self.robot_y = nums[1]
                self.robot_heading_deg = nums[2]
                self._update_ultrasonic(nums[3], nums[4])
                if len(nums) >= 6:
                    code = int(nums[5])
                    if code != self.mega_fault:
                        print(f"[BLE] 메가 이상 상태 코드 변경: {self.mega_fault} -> {code}")
                    self.mega_fault = code
            elif len(nums) == 4:
                # [x, y, right, left]
                self.robot_x = nums[0]
                self.robot_y = nums[1]
                self._update_ultrasonic(nums[2], nums[3])
            elif len(nums) == 3:
                # [x값, y값, 헤딩]
                self.robot_x = nums[0]
                self.robot_y = nums[1]
                self.robot_heading_deg = nums[2]
            elif len(nums) == 2:
                # 2개 인자: 값이 둘 다 20 미만이면 x, y 우선 판정
                if abs(nums[0]) <= 20.0 and abs(nums[1]) <= 20.0 and (isinstance(nums[0], float) or isinstance(nums[1], float)):
                    self.robot_x = nums[0]
                    self.robot_y = nums[1]
                else:
                    self._update_ultrasonic(nums[0], nums[1])
            
            print(f"[BLE 수신] 원본: '{text}' -> 파싱: (X:{self.robot_x:+.2f}m, Y:{self.robot_y:+.2f}m, Head:{self.robot_heading_deg:+.1f}deg, R:{self.ble_right_cm:.1f}cm, L:{self.ble_left_cm:.1f}cm)")
        except Exception as e:
            print(f"[PathRecommender] BLE 파싱 예외 발생 ({latest}): {e}")

    def _update_ultrasonic(self, raw_right: float, raw_left: float):
        """
        초음파 노이즈 및 고장 에러(-1) 필터링
        - -1 또는 0 이하(측정 실패/타임아웃): 장애물 없음(999.0cm)으로 안전 처리하여 오작동 방지
        - 최근 3개 값의 중간값(Median) 필터로 튀는 노이즈 제거
        """
        # 에러 값(-1, <=0) 또는 비정상 큰 값(>400cm) 필터링
        valid_r = raw_right if (raw_right > 0.0 and raw_right < 400.0) else 999.0
        valid_l = raw_left if (raw_left > 0.0 and raw_left < 400.0) else 999.0

        self.ble_right_history.append(valid_r)
        self.ble_left_history.append(valid_l)
        if len(self.ble_right_history) > 3:
            self.ble_right_history.pop(0)
        if len(self.ble_left_history) > 3:
            self.ble_left_history.pop(0)

        self.ble_right_cm = sorted(self.ble_right_history)[len(self.ble_right_history) // 2]
        self.ble_left_cm  = sorted(self.ble_left_history)[len(self.ble_left_history) // 2]

    # ── BLE 전송 헬퍼 ────────────────────────────────────────────
    def _send_ble(self, s_signal: str, r_signal: str = "", force: bool = False):
        """
        BLE를 통해 JSON 딕셔너리 패킷 {"S-signal": ..., "R-signal": ...} 형태로 Arduino에 전송
        - [명령 락] 명령이 변경되었을 때 즉시 송신, 동일 명령은 400ms 주기 하트비트 전송
        - 주행 중 추천 방향: {"S-signal": "0", "R-signal": ""} / {"S-signal": "90", "R-signal": ""} 등
        - 정지/도착/대기: {"S-signal": "STOP", "R-signal": ""}
        - 좌표 초기화: {"S-signal": "STOP", "R-signal": "RESET_ODO"}
        """
        if self.ble is not None:
            now = time.time()
            payload_key = f"{s_signal}|{r_signal}"

            # 직전 명령과 동일하고 force가 아니며 400ms 미경과 시 스킵 (버퍼 렉 및 중복 전송 방지)
            if not force and payload_key == getattr(self, "last_sent_payload", ""):
                if now - getattr(self, "last_sent_time", 0.0) < 0.4:
                    return

            try:
                payload = {
                    "S-signal": str(s_signal),
                    "R-signal": str(r_signal)
                }
                self.ble.send(json.dumps(payload))
                self.last_sent_payload = payload_key
                self.last_sent_time = now
            except Exception as e:
                print(f"[BLE] 전송 오류: {e}")

    # ── 50cm x 50cm 사각형 풋프린트를 고려한 여유 거리 측정 ───
    def _measure_clearance_with_footprint(self, angle_deg: float) -> float:
        """
        로봇의 현재 헤딩(robot_heading_deg)을 반영하여
        특정 로컬 방향 각도로 로봇 몸체(50cm x 50cm)를 고려한 안전 거리를 레이 마칭으로 측정합니다.
        """
        curr_rel_head = getattr(self, "robot_heading_deg", 0.0) - getattr(self, "origin_heading", 0.0)
        global_deg = angle_deg + curr_rel_head
        rad = math.radians(global_deg)
        step_m = self.occ_map.resolution
        clearance = 0.0

        # 루프 바깥으로 뺄 수 있는 것은 전부 빼둔다 (매 스텝 재계산 방지)
        sin_r = math.sin(rad)
        cos_r = math.cos(rad)
        grid = self.occ_map.grid
        height, width = grid.shape
        half = self.footprint_half_cells
        threshold = self.CELL_THRESHOLD

        dist = 0.05
        while dist <= self.MAX_RANGE_M:
            row_c, col_c = self.occ_map.world_to_cell(dist * sin_r, dist * cos_r)

            if not (0 <= row_c < height and 0 <= col_c < width):
                break

            # 로봇 몸체가 놓일 11x11 셀 영역을 numpy 슬라이스로 한 번에 잘라
            # 임계값 이상인 셀 수를 센다. 셀을 하나씩 파이썬으로 훑던 기존 방식과
            # 결과는 완전히 동일하고(19방향 대조 오차 0.000000m), 인터프리터 오버헤드가
            # 사라져 13배 빠르다. 라즈베리파이에서는 이 차이가 제어 주기를 좌우한다.
            r0, r1 = row_c - half, row_c + half + 1
            c0, c1 = col_c - half, col_c + half + 1

            if r0 < 0 or c0 < 0 or r1 > height or c1 > width:
                # 풋프린트가 맵 밖으로 나가면 기존 코드와 동일하게 충돌로 본다.
                # (슬라이스는 범위를 넘으면 조용히 짧아지므로 반드시 먼저 걸러야 한다)
                hit = True
            else:
                hit = int(np.count_nonzero(grid[r0:r1, c0:c1] >= threshold)) >= 3

            if hit:
                if dist <= 0.05:
                    clearance = 0.0
                break

            clearance = dist
            dist += step_m

        return clearance

    # ── 경고 구역 완만한 조향 (정지 없이 살짝 피해가기) ─────────────
    NUDGE_ANGLES_DEG = (-20.0, -10.0, 10.0, 20.0)  # 완만한 회피 시 후보로 고려할 작은 각도들
    NUDGE_MARGIN_M   = 0.15  # 직진(0도)보다 이만큼 더 트여 있어야 옆으로 살짝 트는 걸 채택

    def _compute_gentle_steering(self, front_clearance: float, scores: List["DirectionScore"]) -> Tuple[float, str]:
        """
        전방이 ZONE_WARNING_M(경고 구역) 안으로 들어왔지만 아직 FRONT_STOP_DIST_M(즉시정지 구역)
        만큼 가깝진 않을 때, 완전히 멈추고 90도 ㄷ자 회피를 시작하는 대신 작은 각도(±10/±20도)로
        살짝 조향해서 부드럽게 피해가도록 한다. 상용 로봇의 DWA류 로컬 플래너를 이산적 명령
        인터페이스 안에서 흉내낸 것 — 매 프레임 재계산되며 상태를 남기지 않는다.
        """
        if front_clearance >= config.ZONE_WARNING_M:
            return 0.0, "Front"  # 충분히 트여 있음 -> 직진

        by_angle = {s.angle_deg: s.clearance_m for s in scores}
        best_angle, best_clearance = 0.0, front_clearance

        for angle_deg in self.NUDGE_ANGLES_DEG:
            clearance = by_angle.get(angle_deg)
            # 직진보다 확실히(NUDGE_MARGIN_M 이상) 더 트인 방향만 채택 (미세한 차이로 인한 좌우 흔들림 방지)
            if clearance is not None and clearance > best_clearance + self.NUDGE_MARGIN_M:
                best_angle, best_clearance = angle_deg, clearance

        if best_angle == 0.0:
            return 0.0, "Front"
        label = f"Right-{int(best_angle)}" if best_angle > 0 else f"Left-{int(abs(best_angle))}"
        return best_angle, label

    # ── 라이다 기반 슬립 감지 ────────────────────────────────────
    def feed_lidar_scan(self, scan):
        """
        매 프레임 최신 라이다 스캔을 넣어준다 (main_mapping 루프에서 호출).
        슬립 판정용으로 최근 스캔을 1도 단위로 비닝해 보관한다.
        """
        if scan is None or not getattr(scan, "points", None):
            return

        # [가드 1 - 스캔 신선도] LidarProcessor.get_scan() 은 큐가 비면 직전 스캔을
        # 그대로 다시 돌려준다. 라이다는 5~10Hz 인데 메인 루프는 15FPS 를 노리므로
        # "같은 스캔"이 반복해서 들어오는 게 정상이다. 이걸 그냥 쌓으면 비교 대상이
        # 자기 자신이 되어 scan_delta 가 항상 0 -> "세상이 안 변했다"가 무조건 참이
        # 되고, 슬립 판정이 오도메트리 하나에만 의존하게 된다. 새 스캔만 받는다.
        scan_ts = float(getattr(scan, "timestamp", 0.0) or 0.0)
        if scan_ts > 0.0 and scan_ts == self._last_scan_ts:
            return
        self._last_scan_ts = scan_ts

        now = time.time()

        # [가드 2 - 오도메트리 연속성] 좌표가 물리적으로 불가능한 속도로 튀었다면
        # 실제 이동이 아니라 데이터 불연속이다. 비교 창이 그 점프를 가로지르면
        # "오도메트리는 갔는데 세상은 그대로" 가 성립해 정지 중에도 슬립으로 오판한다.
        # 점프를 관측하면 히스토리를 비워 창이 점프를 포함하지 못하게 한다.
        if self._scan_history:
            p_t, _, _, px, py = self._scan_history[-1]
            dt = now - p_t
            if dt > 0.0:
                jump = math.hypot(self.robot_x - px, self.robot_y - py)
                if jump / dt > self.SLIP_MAX_PLAUSIBLE_MPS:
                    print(f"[PathRecommender] [SLIP GUARD] 오도메트리 불연속 감지 "
                          f"({jump:.2f}m / {dt:.2f}s = {jump/dt:.1f}m/s) -> 슬립 비교 창 초기화")
                    self._scan_history.clear()

        binned = {}
        close_pts = 0
        for p in scan.points:
            d = p.distance_m
            if d <= 0.0:
                continue
            b = int(round(p.angle_deg))
            # 같은 각도 빈에 여러 포인트가 있으면 더 가까운 값을 채택
            if b not in binned or d < binned[b]:
                binned[b] = d
            if 0.2 <= d <= 4.0:
                close_pts += 1

        struct_ratio = close_pts / float(len(scan.points))
        self._scan_history.append((now, binned, struct_ratio, self.robot_x, self.robot_y))

        # 비교 창의 2배까지만 보관 (메모리 무한 증가 방지)
        while len(self._scan_history) > 2 and (now - self._scan_history[0][0]) > self.SLIP_WINDOW_SEC * 2.0:
            self._scan_history.pop(0)

    def _check_slip(self) -> Optional[Tuple[float, float, int]]:
        """
        "오도메트리는 움직였다는데 라이다가 본 세상은 그대로"인지 검사.

        오도메트리는 엔코더에서 파생되므로 바퀴가 헛돌면 함께 속는다. 라이다는
        바퀴와 무관한 유일한 관측 수단이라 이 대조가 성립한다.

        Returns: 슬립이면 (오도메트리 이동거리, 스캔 변화 중앙값, 매칭 포인트 수), 아니면 None
        """
        if len(self._scan_history) < 2:
            return None

        now_t, now_bins, now_ratio, nx, ny = self._scan_history[-1]

        # 비교 창(SLIP_WINDOW_SEC) 이상 떨어진 가장 최신 과거 샘플을 기준으로 삼는다
        ref = None
        for s in self._scan_history:
            if (now_t - s[0]) >= self.SLIP_WINDOW_SEC:
                ref = s
            else:
                break
        if ref is None:
            return None

        ref_t, ref_bins, ref_ratio, rx, ry = ref

        # [필수 가드] 텅 빈 공간에서는 실제로 움직여도 거리값이 안 변한다.
        # 주변에 구조물이 충분히 보일 때만 판정하고, 아니면 조용히 보류한다
        # (오검출로 멀쩡한 주행을 멈추는 것보다 미검출이 낫다).
        if now_ratio < self.SLIP_STRUCT_RATIO or ref_ratio < self.SLIP_STRUCT_RATIO:
            return None

        common = [b for b in now_bins if b in ref_bins]
        if len(common) < self.SLIP_MIN_MATCHED:
            return None

        # 중앙값을 쓰면 지나가는 사람 몇 명 때문에 판정이 흔들리지 않는다
        deltas = sorted(abs(now_bins[b] - ref_bins[b]) for b in common)
        scan_delta = deltas[len(deltas) // 2]

        moved_odo = math.hypot(nx - rx, ny - ry)
        if moved_odo >= self.SLIP_MIN_ODO_M and scan_delta <= self.SLIP_MAX_SCAN_DELTA_M:
            return (moved_odo, scan_delta, len(common))
        return None

    def _evaluate_fault(self) -> int:
        """
        메가가 보고한 이상 상태와 PC가 라이다로 직접 판정한 슬립을 합쳐
        확정 fault 코드를 결정하고 래치한다. 한 번 걸리면 주행 시작/정지로만 풀린다.
        """
        if self.fault_code != 0:
            return self.fault_code  # 이미 래치됨

        # 1) 메가 보고 (모터 스톨 / 헤딩 포화 / 바퀴 편차)
        if self.mega_fault != 0:
            self.fault_code = self.mega_fault
            self.fault_reason = self.FAULT_NAMES.get(self.mega_fault, f"메가 이상 코드 {self.mega_fault}")
            print(f"\n[PathRecommender] [FAULT {self.fault_code}] {self.fault_reason} (메가 보고)")
            return self.fault_code

        # 2) PC 자체 판정 (슬립) - 실제로 직진 주행 중일 때만
        # [가드 3] 정지 명령을 보내고 있는 동안은 판정하지 않는다. 로봇이 서 있으면
        # 라이다도 당연히 안 변하므로 "세상이 안 변했다" 조건이 무조건 참이 되고,
        # 판정이 오도메트리 신뢰성 하나에만 걸리게 된다 - 그런데 오도메트리를 못
        # 믿는 상황을 잡으려는 게 이 검사의 목적이라 자기모순이다.
        commanding_drive = not str(getattr(self, "last_sent_payload", "")).startswith("STOP")
        if (commanding_drive and self.state == "FORWARD"
                and self.avoid_state in ("IDLE", "AVOID_PASS_WIDTH", "AVOID_PASS_LENGTH")):
            slip = self._check_slip()
            if slip is not None:
                moved, delta, matched = slip
                self.fault_code = self.FAULT_SLIP
                self.fault_reason = (
                    f"슬립 (오도메트리 {moved:.2f}m 이동 주장, 라이다 변화 {delta*100:.1f}cm, "
                    f"매칭 {matched}점) - 오도메트리 좌표를 신뢰할 수 없음"
                )
                print(f"\n[PathRecommender] [FAULT 4] {self.fault_reason}")
                return self.fault_code

        return 0

    def _rotation_clearance_ok(self) -> Tuple[bool, int]:
        """
        제자리 180도 회전이 가능한지 판정.

        로봇이 중심을 축으로 돌면 네 코너가 반대각선 반경(50x50cm -> 0.354m)의
        원을 그린다. 정지 상태의 전방 면(0.25m)보다 10cm 더 나가므로, 벽에
        완전히 밀착한 상태에서 돌리면 코너가 벽을 파고들며 갈린다.
        중심 주변 원형 영역에 장애물 셀이 있는지 직접 확인한다.

        Returns: (회전 가능 여부, 막힌 셀 수)
        """
        res = self.occ_map.resolution
        radius_m = self.ROBOT_HALF_M * math.sqrt(2.0) + self.ROT_SWEEP_MARGIN_M
        rad_cells = int(math.ceil(radius_m / res))
        r0, c0 = self.occ_map.robot_row, self.occ_map.robot_col

        blocked = 0
        for dr in range(-rad_cells, rad_cells + 1):
            for dc in range(-rad_cells, rad_cells + 1):
                if dr * dr + dc * dc > rad_cells * rad_cells:
                    continue
                r, c = r0 + dr, c0 + dc
                if not self.occ_map.in_bounds(r, c):
                    blocked += 1
                    continue
                if float(self.occ_map.grid[r, c]) >= self.CELL_THRESHOLD:
                    blocked += 1
        # 레이마칭과 같은 기준(3셀)으로 단일 픽셀 노이즈를 견딘다
        return (blocked < 3), blocked

    # ── 이상 상태 탈출 시퀀스 (후진 -> 재개 또는 정지) ───────────
    def _handle_fault(self, fault: int, dist_m, goal_rel_angle) -> PathRecommendation:
        """
        이상 상태가 확정됐을 때의 처리.

        1) 후방이 트여 있으면 REVERSE 를 보내 짧게(25cm/1.5초) 물러난다.
           벽이나 턱에 밀착한 채로 방치하지 않기 위함이다.
        2) 후진이 끝나면:
           - fault 1~3 (스톨/헤딩/바퀴): 오도메트리는 대체로 살아 있으므로 목표 주행 재개
           - fault 4 (슬립): 엔코더가 헛돌며 없는 거리를 누적했으므로 현재 좌표를
             신뢰할 수 없다. 재개하면 엉뚱한 곳으로 간다 -> 정지하고 사람 판단을 기다린다.
        """
        now = time.time()
        self.avoid_state = "IDLE"
        self.aligning_heading = False

        def pack(angle, label, reason, stuck):
            return PathRecommendation(
                best_angle_deg=angle, best_label=label, reason=reason, scores=[],
                is_stuck=stuck,
                target_x=self.target_x, target_y=self.target_y, target_name=self.target_name,
                dist_to_goal_m=dist_m, goal_rel_angle_deg=goal_rel_angle,
                is_goal_reached=False,
                robot_x=self.robot_x, robot_y=self.robot_y,
                robot_heading_deg=self.robot_heading_deg,
                fault_code=fault, fault_reason=self.fault_reason,
            )

        # ── 1단계: 탈출 방법 결정 ──
        # 회전을 후진보다 우선한다. 180도 돌고 나면 라이다가 탈출 방향을 보게 되므로
        # 그 다음 전진은 전방 감시가 살아 있는 "눈 뜬 이동"이 된다.
        if self.fault_stage == "NONE":
            if self.fault_retry_count >= self.MAX_FAULT_RETRY:
                self.fault_stage = "DONE"
            else:
                rot_ok, blocked = self._rotation_clearance_ok()
                if rot_ok:
                    self.fault_retry_count += 1
                    self._start_escape_turn(now)
                else:
                    # 회전 스윕 공간이 없다 -> 짧은 후진으로 공간부터 만든다
                    rear_clear = self._measure_clearance_with_footprint(180.0)
                    if rear_clear >= self.FAULT_REAR_CLEAR_M:
                        self.fault_stage = "REVERSING"
                        self.fault_reverse_start = now
                        self.fault_retry_count += 1
                        print(f"\n[PathRecommender] [FAULT] 회전 공간 부족(장애물 셀 {blocked}개) - "
                              f"후방 {rear_clear:.2f}m 로 먼저 물러난 뒤 선회 재시도")
                    else:
                        self.fault_stage = "DONE"
                        print(f"\n[PathRecommender] [FAULT] 회전 공간 부족(셀 {blocked}개) + "
                              f"후방 {rear_clear:.2f}m - 자력 탈출 불가, 정지 유지")

        # ── 2단계: 후진으로 회전 공간 확보 ──
        if self.fault_stage == "REVERSING":
            elapsed = now - self.fault_reverse_start
            if elapsed < self.FAULT_REVERSE_TIMEOUT_SEC:
                self._send_ble("REVERSE")
                return pack(self.STOP_ANGLE, "REVERSE",
                            f"[이상 상태 {fault}] {self.fault_reason} -> 선회 공간 확보용 후진 중 ({elapsed:.1f}s)",
                            True)
            rot_ok, blocked = self._rotation_clearance_ok()
            if rot_ok:
                self._start_escape_turn(now)
            else:
                self.fault_stage = "DONE"
                print(f"\n[PathRecommender] [FAULT] 후진 후에도 회전 공간 부족(셀 {blocked}개) - 정지 유지")

        # ── 3단계: 180도 선회 (라이다가 탈출 방향을 보도록) ──
        if self.fault_stage == "ESCAPE_TURN":
            is_turning, head_err = self._is_still_turning(self.fault_escape_head)
            if is_turning and (now - self.fault_reverse_start) < self.ESCAPE_TURN_TIMEOUT_SEC:
                angle, label = self._get_heading_alignment_steering(self.fault_escape_head)
                self._send_ble(str(int(angle)))
                return pack(angle, label,
                            f"[이상 상태 {fault}] 180도 선회 중 (목표 {self.fault_escape_head:+.0f}°, 오차 {head_err:+.1f}°)",
                            True)
            self.fault_stage = "ESCAPE_FWD"
            self.fault_escape_x = self.robot_x
            self.fault_escape_y = self.robot_y
            self.fault_reverse_start = now
            print(f"\n[PathRecommender] [FAULT] 선회 완료 -> 전방 감시하며 {self.ESCAPE_FWD_DIST_M:.2f}m 이탈 전진")

        # ── 4단계: 벽에서 물러나는 전진 (이제 전방이 보인다) ──
        # 회전 직후 곧바로 목표 주행을 재개하면, 목표가 벽 너머라 다시 벽 쪽으로
        # 돌아서 버린다. 물리적으로 떨어진 뒤에 재개해야 한다.
        if self.fault_stage == "ESCAPE_FWD":
            elapsed = now - self.fault_reverse_start
            moved = math.hypot(self.robot_x - self.fault_escape_x,
                               self.robot_y - self.fault_escape_y)
            front = self.forward_clearance()
            if front < self.FRONT_STOP_DIST_M:
                self.fault_stage = "DONE"
                print(f"\n[PathRecommender] [FAULT] 이탈 전진 중 전방도 막힘({front:.2f}m) - 정지 유지")
            elif moved < self.ESCAPE_FWD_DIST_M and elapsed < self.ESCAPE_FWD_TIMEOUT_SEC:
                self._send_ble("0")
                return pack(0.0, "Front",
                            f"[이상 상태 {fault}] 벽에서 이탈 전진 중 ({moved:.2f}/{self.ESCAPE_FWD_DIST_M:.2f}m, 전방 {front:.2f}m)",
                            True)
            else:
                # 이탈 완료
                if fault == self.FAULT_SLIP:
                    self.fault_stage = "DONE"
                    print(f"\n[PathRecommender] [FAULT 4] 이탈 완료. 슬립으로 오도메트리가 오염되어 "
                          f"목표 좌표를 신뢰할 수 없음 -> 정지 유지")
                else:
                    self.fault_stage = "NONE"
                    self.fault_code = 0
                    self.fault_reason = ""
                    self.mega_fault = 0
                    self._scan_history.clear()
                    if self.target_x is not None:
                        self.state = "FORWARD"
                        self.sub_stage = "ALIGN_X"
                    print(f"\n[PathRecommender] [FAULT] 탈출 완료 (이동 {moved:.2f}m) -> 목표 주행 재개")
                    self._send_stop_packet(reset_odo=False)
                    return pack(self.STOP_ANGLE, "STOP", "탈출 완료 -> 목표 주행 재개", False)

        # ── 5단계: 정지 유지 ──
        self.state = "STOPPED"
        self._send_stop_packet(reset_odo=False)
        return pack(self.STOP_ANGLE, "FAULT",
                    f"[이상 상태 {fault}] {self.fault_reason} -> 주행 중단. 확인 후 [주행 시작]으로 재개하세요.",
                    True)

    def _start_escape_turn(self, now: float):
        """현재 헤딩의 반대 방향(180도)을 목표로 선회 단계에 진입"""
        current_rel = (self.robot_heading_deg - self.origin_heading + 180.0) % 360.0 - 180.0
        self.fault_escape_head = (current_rel + 180.0 + 180.0) % 360.0 - 180.0
        self.fault_stage = "ESCAPE_TURN"
        self.fault_reverse_start = now
        self._heading_turning = True  # 히스테리시스를 "턴 중"으로 시작
        print(f"\n[PathRecommender] [FAULT] 회전 공간 확보됨 -> 180도 선회 시작 "
              f"(현재 {current_rel:+.0f}° -> 목표 {self.fault_escape_head:+.0f}°)")

    # ── 회피 직진 단계 중 전방 재차단 시 비상 처리 ────────────────
    def _abort_avoid_on_front_block(
        self,
        stage_label: str,
        front_clearance: float,
        scores: List["DirectionScore"],
        dist_m: Optional[float],
        goal_rel_angle: Optional[float],
    ) -> PathRecommendation:
        """
        ㄷ자 회피의 직진 단계(2단계 가로 폭 통과 / 4단계 세로 길이 추월) 도중
        진행 방향 전방에 새로운 장애물이 나타났을 때의 비상 정지 처리.

        이 단계들은 원래 오도메트리 이동거리 / 측면 초음파 / 타임아웃만 보고
        무조건 직진("0")을 내보내기 때문에, 회피 경로 위에 벽이나 사람이 있으면
        그대로 충돌한다. 여기서 즉시 STOP 을 보내고 회피 상태 머신을 IDLE 로
        되돌리면, 다음 프레임에 일반 목표 지향 주행 로직이 같은 전방 장애물을
        다시 감지해 "현재 위치와 현재 센서 값" 기준으로 회피 방향을 새로 고른다.

        좌우로 계속 왔다갔다하며 갇히는 것을 막기 위해 재시작 횟수를
        MAX_AVOID_RETRY 로 제한하고, 초과하면 정지(STOPPED) 상태로 전환한다.
        """
        self.avoid_state = "IDLE"
        self.avoid_target_head = None
        self.avoid_clear_count = 0
        self.avoid_step_timeout = 0
        self.avoid_retry_count += 1
        self._send_stop_packet(reset_odo=False)

        if self.avoid_retry_count > self.MAX_AVOID_RETRY:
            self.state = "STOPPED"
            self.avoid_retry_count = 0
            is_stuck = True
            reason_msg = (
                f"[회피 실패] {stage_label} 중 전방 재차단(전방 {front_clearance:.2f}m) - "
                f"회피 재시도 {self.MAX_AVOID_RETRY}회 초과 -> 주행 중단 및 정지"
            )
        else:
            is_stuck = False
            reason_msg = (
                f"[회피 비상 정지] {stage_label} 중 전방 장애물 감지 (전방 {front_clearance:.2f}m "
                f"< {self.FRONT_STOP_DIST_M:.2f}m) -> 회피 중단, 현재 위치에서 재탐색 "
                f"({self.avoid_retry_count}/{self.MAX_AVOID_RETRY}회)"
            )

        return PathRecommendation(
            best_angle_deg=self.STOP_ANGLE,
            best_label="Stop",
            reason=reason_msg,
            scores=scores,
            is_stuck=is_stuck,
            target_x=self.target_x,
            target_y=self.target_y,
            target_name=self.target_name,
            dist_to_goal_m=dist_m,
            goal_rel_angle_deg=goal_rel_angle,
            is_goal_reached=False,
            robot_x=self.robot_x,
            robot_y=self.robot_y,
            robot_heading_deg=self.robot_heading_deg,
        )

    # ── 메인 추천 엔진 ───────────────────────────────────────────
    def recommend(self) -> PathRecommendation:
        """
        경로 추천 결과를 반환한다.

        실제 판단 로직은 _recommend_impl() 에 있고, 여기서는 그 결과에 실측
        장애물 치수/동적 회피 목표치를 한 번에 채워 넣는다. _recommend_impl()
        안에는 return 지점이 15곳이 넘어서, 각 지점마다 이 필드들을 넘기면
        반드시 빠뜨리는 곳이 생기기 때문이다 (실제로 전부 빠져 있어서
        대시보드의 장애물 크기 표시가 통째로 동작하지 않았다).
        """
        rec = self._recommend_impl()
        rec.fault_code = self.fault_code
        rec.fault_reason = self.fault_reason

        # 목표 도착 상태에서는 직전 장애물 정보를 그대로 남겨두지 않고 비운다.
        if not rec.is_goal_reached:
            rec.obs_w = self.obs_measured_w
            rec.obs_l = self.obs_measured_l
            rec.target_avoid_w = self.target_avoid_width_m
            rec.target_avoid_l = self.target_avoid_length_m
        return rec

    def _recommend_impl(self) -> PathRecommendation:
        """
        하이브리드 동작 로직:
        1. 목표 좌표가 지정된 경우 목표 지향성 스코어링 및 거리 계산 연동.
        2. 목표지점 25cm 이내 도달 시 정지 신호 및 GOAL_REACHED 상태 전환.
        3. 평상시(FORWARD)에는 목표 방향 또는 안전 방향으로 주행.
        4. 전방 80cm 이내 장애물 감지 시 정지(STOPPED) 및 초음파+맵 복합 회피.
        """
        # BLE 최신 수신 값 및 위치 파싱
        self._poll_ble()

        # 목표 좌표 벡터 계산
        dist_m, goal_rel_angle, goal_global_angle = self._compute_goal_vector()
        has_goal = (dist_m is not None and goal_rel_angle is not None)

        # ─────────────────────────────────────────────────────────
        # [최우선] 이상 상태(메가 fault / 라이다 슬립) 확인
        #
        # ★ 이 검사는 반드시 아래 도착 판정보다 앞에 있어야 한다.
        #   슬립 중에는 엔코더가 계속 거리를 누적하므로 오도메트리상으로는
        #   목표에 "도착"해 버린다. 도착 판정이 먼저 걸리면 로봇이 제자리에
        #   선 채로 "목표 위치에 도착했습니다"를 선언하게 된다.
        # ─────────────────────────────────────────────────────────
        fault = self._evaluate_fault()
        if fault != 0:
            return self._handle_fault(fault, dist_m, goal_rel_angle)

        # ── 0. 목표 도착 상태 최우선 처리 (방향 추천 일체 없이 오직 정지 신호만 전송) ──
        if self.state == "GOAL_REACHED" or (has_goal and dist_m <= self.ARRIVE_MARGIN_M):
            self.state = "GOAL_REACHED"
            self.avoid_state = "IDLE"
            self.aligning_heading = False
            self._send_stop_packet(reset_odo=False)
            return PathRecommendation(
                best_angle_deg=self.STOP_ANGLE,
                best_label="STOP",
                reason=f"목표 {self.target_name or 'Goal'} 도착 완료! 정지 상태 유지 (BLE: STOP 신호 송신)",
                scores=[],  # 방향 추천 없음
                is_stuck=False,
                target_x=self.target_x,
                target_y=self.target_y,
                target_name=self.target_name,
                dist_to_goal_m=dist_m,
                goal_rel_angle_deg=goal_rel_angle,
                is_goal_reached=True,
                robot_x=self.robot_x,
                robot_y=self.robot_y,
                robot_heading_deg=self.robot_heading_deg,
            )

        # 1. 19방향 스코어링 수행 (직진 우대 가중치 및 목표 지향성 반영)
        scores: List[DirectionScore] = []
        for angle_deg, label in self.DIRECTIONS:
            clearance = self._measure_clearance_with_footprint(angle_deg)
            if has_goal:
                angle_diff = abs((angle_deg - goal_rel_angle + 180.0) % 360.0 - 180.0)
                # 남은 거리가 가까울수록(0.8m 이내) 목표 지향 가중치를 대폭 상향하여 도착지로 확실히 빨려들어가 안착
                dist_weight = 6.0 if (dist_m and dist_m < 0.8) else 4.0
                goal_alignment_bonus = max(0.0, 1.0 - angle_diff / 180.0) * dist_weight
                straight_bonus = 2.0 if angle_deg == 0 else 0.0
                score = clearance * 2.0 + goal_alignment_bonus + straight_bonus
            else:
                forward_bonus = max(0.0, 1.0 - abs(angle_deg) / 180.0) * 1.5
                straight_bonus = 2.5 if angle_deg == 0 else 0.0
                score = clearance * 2.0 + forward_bonus + straight_bonus

            scores.append(DirectionScore(
                angle_deg   = angle_deg,
                score       = score,
                clearance_m = clearance,
                has_unknown = False,
                label       = label,
            ))

        # 전방 장애물 크기 실시간 측정 (디버깅 및 동적 회피용)
        obs_w, obs_l, obs_near = self.occ_map.get_front_obstacle_dimensions(max_dist_m=1.5, half_width_m=0.8)
        if obs_near < 1.5:
            self.obs_measured_w = obs_w
            self.obs_measured_l = obs_l
        elif self.avoid_state == "IDLE":
            self.obs_measured_w = 0.0
            self.obs_measured_l = 0.0

        # 전방 0도 안전 거리
        front_clearance = scores[0].clearance_m

        # ── 1. FORWARD 상태 ──
        if self.state == "FORWARD":
            if has_goal:
                dx = self.target_x - self.robot_x
                dy = self.target_y - self.robot_y

                # 최종 도착 체크 (X, Y 종합 거리 오차 0.10m 이내)
                dist_to_goal = math.hypot(dx, dy)
                if dist_to_goal <= self.ARRIVE_MARGIN_M:
                    self.state = "GOAL_REACHED"
                    self.avoid_state = "IDLE"
                    self.aligning_heading = False
                    self._send_stop_packet(reset_odo=False)
                    return PathRecommendation(
                        best_angle_deg=self.STOP_ANGLE,
                        best_label="STOP",
                        reason=f"목표 {self.target_name or 'Goal'} 도착 완료! (오차 {dist_to_goal:.2f}m) 정지 상태 유지 (BLE: STOP 신호 송신)",
                        scores=[],
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_to_goal,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=True,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # ─────────────────────────────────────────────────────────
                # [회피 1순위] 디귿(ㄷ)자형 초음파+오도메트리 기반 4단계 완전 회피 머신 (긴급 제동 + 상대 각도 보정)
                # ─────────────────────────────────────────────────────────
                # 0단계: 초근접 장애물 긴급 제동 (차체 완전 정지 후 회전 개시)
                if getattr(self, "avoid_state", "IDLE") == "AVOID_BRAKE":
                    self.avoid_brake_timer -= 1
                    self._send_stop_packet(reset_odo=False)

                    if self.avoid_brake_timer <= 0:
                        self.avoid_state = "AVOID_TURN_90"
                        self.avoid_start_x = self.robot_x
                        self.avoid_start_y = self.robot_y
                        self.avoid_clear_count = 0
                        self.avoid_step_timeout = 100
                        chosen_angle, chosen_label = self._get_heading_alignment_steering(self.avoid_target_head)
                        reason_msg = f"[회피 1단계: 90도 선회] 긴급 제동 완료 -> {self.avoid_side} 90도({self.avoid_target_head:+.0f}°) 회전 시작"
                    else:
                        chosen_angle = self.STOP_ANGLE
                        chosen_label = "Stop"
                        reason_msg = f"[회피 긴급 제동] 장애물 근접 감지 -> 회전 전 관성 감속 정지 중 (잔여 {self.avoid_brake_timer}프레임)"

                    return PathRecommendation(
                        best_angle_deg=chosen_angle,
                        best_label=chosen_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # 1단계: 직각 90도 선회 (현재 진행 방향 기준 상대적 90도)
                elif getattr(self, "avoid_state", "IDLE") == "AVOID_TURN_90":
                    is_turning_avoid, head_err = self._is_still_turning(self.avoid_target_head)

                    if is_turning_avoid:
                        chosen_angle, chosen_label = self._get_heading_alignment_steering(self.avoid_target_head)
                        reason_msg = f"[회피 1단계: 90도 선회] {self.avoid_side} 90도({self.avoid_target_head:+.0f}°) 회전 중 (오차:{head_err:+.1f}°, 조향:{chosen_label})"
                    else:
                        # 90도 선회 완료 시점 -> 2단계(가로 폭 직진 이동) 진입 (기준 좌표 기록)
                        self.avoid_state = "AVOID_PASS_WIDTH"
                        self.avoid_start_x = self.robot_x
                        self.avoid_start_y = self.robot_y
                        self.avoid_clear_count = 0
                        self.avoid_step_timeout = 100
                        chosen_angle = 0.0
                        chosen_label = "Front"
                        reason_msg = f"[회피 2단계: 가로 폭 통과] {self.avoid_side} 90도 선회 완료 -> 직진 시작 (목표 이동: {self.MIN_AVOID_WIDTH_M:.2f}m)"

                    self._send_ble(str(int(chosen_angle)))
                    return PathRecommendation(
                        best_angle_deg=chosen_angle,
                        best_label=chosen_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # 2단계: 가로 폭 직진 & 오도메트리 이동 거리 검증 & 측면 초음파 감시
                elif getattr(self, "avoid_state", "IDLE") == "AVOID_PASS_WIDTH":
                    # [안전] 이 단계는 무조건 직진을 내보내므로, 진행 방향(현재 헤딩 기준 0도)
                    # 전방이 막히면 다른 조건을 보기 전에 먼저 멈춘다.
                    if front_clearance < self.FRONT_STOP_DIST_M:
                        return self._abort_avoid_on_front_block(
                            "회피 2단계(가로 폭 통과)", front_clearance, scores, dist_m, goal_rel_angle
                        )

                    chosen_angle = 0.0
                    chosen_label = "Front"
                    self.avoid_step_timeout -= 1

                    moved_dist = math.hypot(self.robot_x - self.avoid_start_x, self.robot_y - self.avoid_start_y)
                    side_dist = self.ble_left_cm if self.avoid_side == "RIGHT" else self.ble_right_cm

                    # 측면 초음파 트임 여부 확인 (45cm 이상)
                    if side_dist >= 45.0:
                        self.avoid_clear_count += 1
                    else:
                        self.avoid_clear_count = 0

                    # [동적 회피 거리 적용] 실측 장애물 크기 기반 목표 가로 거리(target_avoid_width_m) 도달 여부 검증
                    target_w = getattr(self, "target_avoid_width_m", self.MIN_AVOID_WIDTH_M)
                    can_turn_front = (moved_dist >= target_w and self.avoid_clear_count >= 2) or \
                                     (moved_dist >= target_w + 0.20) or \
                                     (self.avoid_step_timeout <= 0)

                    if can_turn_front:
                        self.avoid_state = "AVOID_TURN_FRONT"
                        self.avoid_target_head = self.avoid_base_head
                        self.avoid_clear_count = 0
                        self.avoid_step_timeout = 100
                        chosen_angle, chosen_label = self._get_heading_alignment_steering(self.avoid_base_head)
                        reason_msg = f"[회피 3단계: 진행 방향 정렬] 가로 폭 통과 완료 (이동:{moved_dist:.2f}m/{target_w:.2f}m, 측면:{side_dist:.1f}cm) -> 원래 진행각({self.avoid_base_head:+.0f}°) 복귀 회전 시작"
                    else:
                        reason_msg = f"[회피 2단계: 가로 폭 통과] 장애물 옆 직진 중 (이동:{moved_dist:.2f}m/{target_w:.2f}m, 측면:{side_dist:.1f}cm)"

                    self._send_ble(str(int(chosen_angle)))
                    return PathRecommendation(
                        best_angle_deg=chosen_angle,
                        best_label=chosen_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # 3단계: 원래 진행 방향(avoid_base_head)으로 선회
                elif getattr(self, "avoid_state", "IDLE") == "AVOID_TURN_FRONT":
                    is_turning_avoid, head_err = self._is_still_turning(self.avoid_base_head)

                    if is_turning_avoid:
                        chosen_angle, chosen_label = self._get_heading_alignment_steering(self.avoid_base_head)
                        reason_msg = f"[회피 3단계: 진행 방향 정렬] 원래 진행각({self.avoid_base_head:+.0f}°) 정렬 중 (오차:{head_err:+.1f}°, 조향:{chosen_label})"
                    else:
                        # 원래 진행각 선회 완료 시점 -> 4단계(세로 길이 추월 직진) 진입 (기준 좌표 기록)
                        self.avoid_state = "AVOID_PASS_LENGTH"
                        self.avoid_start_x = self.robot_x
                        self.avoid_start_y = self.robot_y
                        self.avoid_clear_count = 0
                        self.avoid_step_timeout = 100
                        chosen_angle = 0.0
                        chosen_label = "Front"
                        target_l = getattr(self, "target_avoid_length_m", self.MIN_AVOID_LENGTH_M)
                        reason_msg = f"[회피 4단계: 세로 길이 추월] 진행 방향 정렬 완료 -> 직진 시작 (목표 추월 이동: {target_l:.2f}m)"

                    self._send_ble(str(int(chosen_angle)))
                    return PathRecommendation(
                        best_angle_deg=chosen_angle,
                        best_label=chosen_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # 4단계: 세로 길이 직진 & 오도메트리 이동 거리 검증 & 측면 초음파 감시 (장애물 완전 추월)
                elif getattr(self, "avoid_state", "IDLE") == "AVOID_PASS_LENGTH":
                    # [안전] 2단계와 동일하게, 맹목 직진 전에 전방을 먼저 확인한다.
                    if front_clearance < self.FRONT_STOP_DIST_M:
                        return self._abort_avoid_on_front_block(
                            "회피 4단계(세로 길이 추월)", front_clearance, scores, dist_m, goal_rel_angle
                        )

                    chosen_angle = 0.0
                    chosen_label = "Front"
                    self.avoid_step_timeout -= 1

                    moved_dist = math.hypot(self.robot_x - self.avoid_start_x, self.robot_y - self.avoid_start_y)
                    side_dist = self.ble_left_cm if self.avoid_side == "RIGHT" else self.ble_right_cm

                    if side_dist >= 45.0:
                        self.avoid_clear_count += 1
                    else:
                        self.avoid_clear_count = 0

                    # [동적 추월 거리 적용] 실측 장애물 길이 기반 목표 추월 거리(target_avoid_length_m) 도달 여부 검증
                    target_l = getattr(self, "target_avoid_length_m", self.MIN_AVOID_LENGTH_M)
                    can_start_return = (moved_dist >= target_l and self.avoid_clear_count >= 2) or \
                                       (moved_dist >= target_l + 0.25) or \
                                       (self.avoid_step_timeout <= 0)

                    if can_start_return:
                        # 장애물을 완전히 지나침 -> 회피 종료. 원래 레인으로 복귀하지 않고,
                        # 현재 위치에서 바로 목표 지향 주행(ALIGN_X/ALIGN_Y)이 dx/dy를 새로 계산해 재조준한다.
                        self.avoid_state = "IDLE"
                        self.avoid_target_head = None
                        self.avoid_clear_count = 0
                        self.avoid_retry_count = 0
                        chosen_angle = 0.0
                        chosen_label = "Front"
                        reason_msg = f"[ㄷ자 회피 완료] 장애물 추월 완료 (이동:{moved_dist:.2f}m/{target_l:.2f}m) -> 원래 레인 복귀 없이 목표 방향으로 바로 재조준"
                    else:
                        reason_msg = f"[회피 4단계: 세로 길이 추월] 장애물 몸통 추월 직진 중 (이동:{moved_dist:.2f}m/{target_l:.2f}m, 측면:{side_dist:.1f}cm)"

                    self._send_ble(str(int(chosen_angle)))
                    return PathRecommendation(
                        best_angle_deg=chosen_angle,
                        best_label=chosen_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # ─────────────────────────────────────────────────────────
                # [일반 주행] 목표 지향 2단계 순차 이동 (X -> Y)
                # ─────────────────────────────────────────────────────────
                if not hasattr(self, "sub_stage") or self.sub_stage is None:
                    self.sub_stage = "ALIGN_X"

                # 1단계 vs 2단계 목표 헤딩 결정 (전방=+X(0도), 좌측=+Y(-90도), 우측=-Y(+90도), 후방=-X(180도))
                if self.sub_stage == "ALIGN_X":
                    if abs(dx) > self.AXIS_ALIGN_DONE_M:
                        target_head = 0.0 if dx > 0 else 180.0
                        stage_name = "1단계 X정렬"
                    else:
                        self.sub_stage = "ALIGN_Y"
                        target_head = -90.0 if dy >= 0 else 90.0
                        stage_name = "2단계 Y정렬 전환"
                elif self.sub_stage == "ALIGN_Y":
                    if abs(dy) > self.AXIS_ALIGN_DONE_M:
                        target_head = -90.0 if dy >= 0 else 90.0
                        stage_name = "2단계 Y정렬"
                    else:
                        # 재정렬 진입은 완료 기준(0.10m)보다 넉넉한 히스테리시스 기준(0.15m)을 써서,
                        # dx가 0.10m 경계 근처에서 노이즈로 흔들려도 X<->Y 사이를 계속 왔다갔다하지 않도록 함.
                        if abs(dx) > self.AXIS_REALIGN_TRIGGER_M:
                            self.sub_stage = "ALIGN_X"
                            target_head = 0.0 if dx > 0 else 180.0
                            stage_name = "1단계 X재정렬"
                        else:
                            # Y는 0.10m 이내, X는 재정렬을 걸 정도(0.15m)는 아님 -> 도착 처리
                            self.state = "GOAL_REACHED"
                            self.avoid_state = "IDLE"
                            self.aligning_heading = False
                            self._send_stop_packet(reset_odo=False)
                            return PathRecommendation(
                                best_angle_deg=self.STOP_ANGLE,
                                best_label="STOP",
                                reason=f"목표 {self.target_name or 'Goal'} 도착 완료! (오차 {dist_to_goal:.2f}m) 정지 상태 유지 (BLE: STOP 신호 송신)",
                                scores=[],
                                is_stuck=False,
                                target_x=self.target_x,
                                target_y=self.target_y,
                                target_name=self.target_name,
                                dist_to_goal_m=dist_to_goal,
                                goal_rel_angle_deg=goal_rel_angle,
                                is_goal_reached=True,
                                robot_x=self.robot_x,
                                robot_y=self.robot_y,
                                robot_heading_deg=self.robot_heading_deg,
                            )

                # 현재 로봇 헤딩과 목표 각도 간의 오차 계산 (히스테리시스 적용)
                is_turning, head_err = self._is_still_turning(target_head)

                # ─────────────────────────────────────────────────────────
                # [규칙] 제자리에서 턴을 할 때는 장애물 인식을 통한 방향 추천을 하지 않음!
                # ─────────────────────────────────────────────────────────
                if is_turning:
                    chosen_angle, chosen_label = self._get_heading_alignment_steering(target_head)
                    reason_msg = f"[{stage_name} 턴 중] 목표각({target_head:+.0f}°) 회전 정렬 중 (오차:{head_err:+.1f}°, 조향:{chosen_label})"
                    self._send_ble(str(int(chosen_angle)))
                    return PathRecommendation(
                        best_angle_deg=chosen_angle,
                        best_label=chosen_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # ─────────────────────────────────────────────────────────
                # [직진 전진 상태] 턴이 완료되어 직진할 때 전방 장애물이 있는 경우에만 턴 방향 검사 및 회피!
                # ─────────────────────────────────────────────────────────
                if front_clearance < self.FRONT_STOP_DIST_M:
                    # 턴하려는 방향(우측 vs 좌측)에 장애물/벽이 있는지 확인하여 더 넓게 트인 쪽으로 턴!
                    # 초음파 거리(cm) 및 라이다 측면 여유 거리(m) 종합 비교
                    right_scores = [s for s in scores if s.angle_deg > 0]
                    left_scores  = [s for s in scores if s.angle_deg < 0]
                    right_lidar_clearance = max([s.clearance_m for s in right_scores], default=0.0)
                    left_lidar_clearance  = max([s.clearance_m for s in left_scores], default=0.0)

                    # 초음파 센서 차이가 뚜렷하면 초음파 우선, 비슷하면 라이다 공간 기준 판정
                    if abs(self.ble_right_cm - self.ble_left_cm) >= 10.0:
                        prefer_right = self.ble_right_cm > self.ble_left_cm
                    else:
                        prefer_right = right_lidar_clearance >= left_lidar_clearance

                    self.avoid_side = "RIGHT" if prefer_right else "LEFT"

                    # 진행 방향 기준 상대적 90도 회피각 계산
                    self.avoid_base_head = target_head
                    rel_turn_deg = 90.0 if prefer_right else -90.0
                    self.avoid_target_head = (self.avoid_base_head + rel_turn_deg + 180.0) % 360.0 - 180.0

                    self.avoid_start_x = self.robot_x
                    self.avoid_start_y = self.robot_y
                    self.avoid_clear_count = 0
                    self.avoid_step_timeout = 100

                    # 장애물 크기 측정 및 동적 회피 거리 계산
                    obs_w, obs_l, _ = self.occ_map.get_front_obstacle_dimensions(max_dist_m=1.2, half_width_m=0.8)
                    self.obs_measured_w = obs_w
                    self.obs_measured_l = obs_l

                    # 동적 가로 회피 거리 = (장애물폭 / 2) + 로봇반폭(0.25m) + 안전여유(0.12m)
                    self.target_avoid_width_m = max(self.MIN_AVOID_WIDTH_M, min(self.MAX_AVOID_WIDTH_M, (obs_w / 2.0) + self.ROBOT_HALF_M + 0.12))
                    # 동적 세로 추월 거리 = 장애물길이 + 로봇전장(0.50m) + 안전여유(0.15m)
                    self.target_avoid_length_m = max(self.MIN_AVOID_LENGTH_M, min(self.MAX_AVOID_LENGTH_M, obs_l + (self.ROBOT_HALF_M * 2.0) + 0.15))

                    # 긴급 제동(Emergency Brake) 우선 적용
                    self.avoid_state = "AVOID_BRAKE"
                    self.avoid_brake_timer = 3
                    self._send_stop_packet(reset_odo=False)

                    return PathRecommendation(
                        best_angle_deg=self.STOP_ANGLE,
                        best_label="Stop",
                        reason=f"전방 장애물(폭:{obs_w:.2f}m, 깊이:{obs_l:.2f}m) 감지 -> 트인 {self.avoid_side} 90도 회피 (목표가로:{self.target_avoid_width_m:.2f}m, 세로:{self.target_avoid_length_m:.2f}m)",
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )

                # ─────────────────────────────────────────────────────────
                # [직진/완만한 회피 주행] 전방이 충분히 트였으면 직진, 경고 구역(ZONE_WARNING_M)
                # 안이면 완전히 멈추지 않고 작은 각도로 살짝 조향해 부드럽게 피해감
                # ─────────────────────────────────────────────────────────
                chosen_angle, chosen_label = self._compute_gentle_steering(front_clearance, scores)
                if chosen_angle == 0.0:
                    reason_msg = f"[{stage_name}] 직진 전진 주행 중 (전방 {front_clearance:.2f}m 확보)"
                else:
                    reason_msg = f"[{stage_name}] 경고 구역 완만한 회피 조향({chosen_label}) 중 (전방 {front_clearance:.2f}m)"
                self._send_ble(str(int(chosen_angle)))
                return PathRecommendation(
                    best_angle_deg=chosen_angle,
                    best_label=chosen_label,
                    reason=reason_msg,
                    scores=scores,
                    is_stuck=False,
                    target_x=self.target_x,
                    target_y=self.target_y,
                    target_name=self.target_name,
                    dist_to_goal_m=dist_m,
                    goal_rel_angle_deg=goal_rel_angle,
                    is_goal_reached=False,
                    robot_x=self.robot_x,
                    robot_y=self.robot_y,
                    robot_heading_deg=self.robot_heading_deg,
                )
            else:
                # 목표가 없는 일반 직진 (경고 구역이면 완만한 회피 조향)
                chosen_angle, chosen_label = self._compute_gentle_steering(front_clearance, scores)
                reason_msg = (
                    f"직진 주행 중 (전방 {front_clearance:.2f}m 확보)" if chosen_angle == 0.0
                    else f"경고 구역 완만한 회피 조향({chosen_label}) 중 (전방 {front_clearance:.2f}m)"
                )
                self._send_ble(str(int(chosen_angle)))
                return PathRecommendation(
                    best_angle_deg=chosen_angle,
                    best_label=chosen_label,
                    reason=reason_msg,
                    scores=scores,
                    is_stuck=False,
                    target_x=self.target_x,
                    target_y=self.target_y,
                    target_name=self.target_name,
                    dist_to_goal_m=dist_m,
                    goal_rel_angle_deg=goal_rel_angle,
                    is_goal_reached=False,
                    robot_x=self.robot_x,
                    robot_y=self.robot_y,
                    robot_heading_deg=self.robot_heading_deg,
                )

        # ── 2. STOPPED 상태: 주행 시작 버튼을 누르지 않은 대기 상태 또는 정지 버튼 클릭 상태 ──
        elif self.state == "STOPPED":
            # [버튼 트리거 헤딩 정렬] 사용자가 '헤딩 정렬' 버튼을 클릭한 경우에만 1도 단위 정밀 정렬 수행
            if getattr(self, "aligning_heading", False):
                align_angle, align_label, target_zero_head, is_zero_aligned = self._get_zero_alignment_steering_1deg()

                if not is_zero_aligned:
                    # 1도 단위 정밀 각도 문자열 송신 (예: "12", "-5")
                    self._send_ble(str(int(align_angle)))
                    reason_msg = f"[헤딩 정렬 중 (1° 정밀)] 현재 헤딩({self.robot_heading_deg:.1f}°) -> 목표 {target_zero_head:.0f}° 정렬 중 (조향: {align_label})"
                    return PathRecommendation(
                        best_angle_deg=align_angle,
                        best_label=align_label,
                        reason=reason_msg,
                        scores=scores,
                        is_stuck=False,
                        target_x=self.target_x,
                        target_y=self.target_y,
                        target_name=self.target_name,
                        dist_to_goal_m=dist_m,
                        goal_rel_angle_deg=goal_rel_angle,
                        is_goal_reached=False,
                        robot_x=self.robot_x,
                        robot_y=self.robot_y,
                        robot_heading_deg=self.robot_heading_deg,
                    )
                else:
                    # 1도 이내 정렬 완료 시 플래그 해제 및 정지 신호 패킷 송신
                    self.aligning_heading = False
                    self._send_stop_packet(reset_odo=False)
                    print(f"\n[PathRecommender] [ALIGN COMPLETE] 헤딩 {target_zero_head:.0f}° 정렬 완료! -> STOP 대기")

            # 평상시 대기 상태에서는 BLE로 {"S-signal":"STOP", "R-signal":""} 패킷 전송
            self._send_stop_packet(reset_odo=False)

            # 양측 초음파 및 공간이 모두 30cm 미만으로 꽉 막힌 경우 유턴(180) 레이블 세팅
            if self.ble_right_cm < 30.0 and self.ble_left_cm < 30.0:
                return PathRecommendation(
                    best_angle_deg=self.UTURN_ANGLE,
                    best_label="U-Turn",
                    reason=f"좌우 공간 모두 협소 (R:{self.ble_right_cm:.1f}cm L:{self.ble_left_cm:.1f}cm) -> BLE 정지(STOP) 및 유턴 대기",
                    scores=scores,
                    is_stuck=True,
                    target_x=self.target_x,
                    target_y=self.target_y,
                    target_name=self.target_name,
                    dist_to_goal_m=dist_m,
                    goal_rel_angle_deg=goal_rel_angle,
                    is_goal_reached=False,
                    robot_x=self.robot_x,
                    robot_y=self.robot_y,
                    robot_heading_deg=self.robot_heading_deg,
                )

            # 대시보드 UI 시각화용 10도 단위 추천 각도 계산
            right_scores = [s for s in scores if s.angle_deg > 0]
            left_scores  = [s for s in scores if s.angle_deg < 0]

            right_lidar_clearance = max([s.clearance_m for s in right_scores], default=0.0)
            left_lidar_clearance  = max([s.clearance_m for s in left_scores], default=0.0)

            right_sensor_space = right_lidar_clearance * 0.6 + (self.ble_right_cm / 100.0) * 0.4
            left_sensor_space  = left_lidar_clearance * 0.6 + (self.ble_left_cm / 100.0) * 0.4

            prefer_right = right_sensor_space >= left_sensor_space

            candidate_angles = [a for a in range(10, 91, 10)] if prefer_right else [a for a in range(-10, -91, -10)]
            fallback_angles  = [a for a in range(-10, -91, -10)] if prefer_right else [a for a in range(10, 91, 10)]

            best_angle = None
            best_score = -999.0
            best_label = ""

            for angle_deg in candidate_angles:
                clearance = self._measure_clearance_with_footprint(float(angle_deg))
                if clearance >= self.ROBOT_HALF_M * 2.0:
                    score = clearance * 2.0
                    if score > best_score:
                        best_score = score
                        best_angle = float(angle_deg)
                        best_label = f"Right-{int(angle_deg)}" if angle_deg > 0 else f"Left-{int(abs(angle_deg))}"

            if best_angle is None:
                for angle_deg in fallback_angles:
                    clearance = self._measure_clearance_with_footprint(float(angle_deg))
                    if clearance >= self.ROBOT_HALF_M * 2.0:
                        score = clearance * 1.5
                        if score > best_score:
                            best_score = score
                            best_angle = float(angle_deg)
                            best_label = f"Right-{int(angle_deg)}" if angle_deg > 0 else f"Left-{int(abs(angle_deg))}"

            if best_angle is None:
                all_candidates = candidate_angles + fallback_angles
                for angle_deg in all_candidates:
                    clearance = self._measure_clearance_with_footprint(float(angle_deg))
                    if clearance > best_score:
                        best_score = clearance
                        best_angle = float(angle_deg)
                        best_label = f"Right-{int(angle_deg)}" if angle_deg > 0 else f"Left-{int(abs(angle_deg))}"

            if best_angle is None:
                best_angle = 90.0 if prefer_right else -90.0
                best_label = "Right-90" if prefer_right else "Left-90"

            self.turn_angle = best_angle
            self.turn_label = best_label

            return PathRecommendation(
                best_angle_deg=self.turn_angle,
                best_label=self.turn_label,
                reason=f"주행 시작 대기 / 정지 상태 (BLE: STOP 신호 송신) -> 방향 추천: {self.turn_label}",
                scores=scores,
                is_stuck=False,
                target_x=self.target_x,
                target_y=self.target_y,
                target_name=self.target_name,
                dist_to_goal_m=dist_m,
                goal_rel_angle_deg=goal_rel_angle,
                is_goal_reached=False,
                robot_x=self.robot_x,
                robot_y=self.robot_y,
                robot_heading_deg=self.robot_heading_deg,
            )

        # ── 3. TURNING 상태: 회피 조향 중 ──
        elif self.state == "TURNING":
            self.turn_timer -= 1

            # 회피 프레임 완료 및 전방 안전 -> 직진 상태로 평화롭게 복귀
            if self.turn_timer <= 0 and front_clearance >= self.FRONT_STOP_DIST_M:
                self.state = "FORWARD"
                self._send_ble("0")
                return PathRecommendation(
                    best_angle_deg=0.0,
                    best_label="Front",
                    reason=f"회피 완료 (전방 {front_clearance:.2f}m 확보) -> 직진 복귀",
                    scores=scores,
                    is_stuck=False,
                    target_x=self.target_x,
                    target_y=self.target_y,
                    target_name=self.target_name,
                    dist_to_goal_m=dist_m,
                    goal_rel_angle_deg=goal_rel_angle,
                    is_goal_reached=False,
                    robot_x=self.robot_x,
                    robot_y=self.robot_y,
                    robot_heading_deg=self.robot_heading_deg,
                )

            # 회피 프레임 완료했으나 전방이 여전히 막힘 -> 멈추지 않고 추가 회피 각도 지속 전송
            if self.turn_timer <= 0 and front_clearance < self.FRONT_STOP_DIST_M:
                best_s = max(scores, key=lambda s: s.clearance_m)
                self.turn_angle = best_s.angle_deg if best_s.clearance_m > 0.2 else 90.0
                self.turn_label = f"Avoid-{int(self.turn_angle)}"
                self.turn_timer = 6
                self._send_ble(str(int(self.turn_angle)))
                return PathRecommendation(
                    best_angle_deg=self.turn_angle,
                    best_label=self.turn_label,
                    reason=f"전방 재차 장애물 감지 ({front_clearance:.2f}m) -> 멈춤 없이 지속 회피 조향({self.turn_angle:+.0f}°)",
                    scores=scores,
                    is_stuck=False,
                    target_x=self.target_x,
                    target_y=self.target_y,
                    target_name=self.target_name,
                    dist_to_goal_m=dist_m,
                    goal_rel_angle_deg=goal_rel_angle,
                    is_goal_reached=False,
                    robot_x=self.robot_x,
                    robot_y=self.robot_y,
                    robot_heading_deg=self.robot_heading_deg,
                )

            # 회피 방향 송신 유지
            self._send_ble(str(int(self.turn_angle)))
            return PathRecommendation(
                best_angle_deg=self.turn_angle,
                best_label=self.turn_label,
                reason=f"{self.turn_label} 회피 주행 중 (잔여 {self.turn_timer}프레임)",
                scores=scores,
                is_stuck=False,
                target_x=self.target_x,
                target_y=self.target_y,
                target_name=self.target_name,
                dist_to_goal_m=dist_m,
                goal_rel_angle_deg=goal_rel_angle,
                is_goal_reached=False,
                robot_x=self.robot_x,
                robot_y=self.robot_y,
                robot_heading_deg=self.robot_heading_deg,
            )

        # 안전장치 폴백
        self.state = "FORWARD"
        return PathRecommendation(
            best_angle_deg=0.0,
            best_label="Front",
            reason="예외 상태 감지 -> 직진 복구",
            scores=scores,
            is_stuck=False,
            target_x=self.target_x,
            target_y=self.target_y,
            target_name=self.target_name,
            dist_to_goal_m=dist_m,
            goal_rel_angle_deg=goal_rel_angle,
            is_goal_reached=False,
            robot_x=self.robot_x,
            robot_y=self.robot_y,
            robot_heading_deg=self.robot_heading_deg,
        )

    def forward_clearance(self) -> float:
        """외부 호출용 전방 안전 거리 측정"""
        return self._measure_clearance_with_footprint(0.0)