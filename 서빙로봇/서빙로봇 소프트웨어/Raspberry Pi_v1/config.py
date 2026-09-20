"""
config.py
서빙 로봇 장애물 회피 시스템 - 전역 설정
OAK-D-Lite + LiDAR 융합
"""

# ─── OAK-D-Lite 설정 ───────────────────────────────────────────────
OAK_DEPTH_MIN_MM       = 200       # 유효 깊이 최솟값 (mm)
OAK_DEPTH_MAX_MM       = 5000      # 유효 깊이 최댓값 (mm)
OAK_CONFIDENCE_THRESH  = 200       # StereoDepth 신뢰도 임계값 (0-255)
OAK_FPS                = 30
OAK_RESOLUTION         = "400p"    # 400p / 720p

# 벽/평면 필터 파라미터
OAK_WALL_RATIO_THRESH  = 0.60      # 화면의 60% 이상 차지하면 벽으로 판단
OAK_EDGE_MARGIN        = 0.15      # 화면 가장자리 15% 는 신뢰도 낮음
OAK_DEPTH_STD_THRESH   = 80        # 표준편차(mm) 초과 시 노이즈 픽셀

# ─── LiDAR 설정 ────────────────────────────────────────────────────
LIDAR_PORT             = "COM7"   # 시리얼 포트
LIDAR_BAUDRATE         = 115200
LIDAR_MIN_RANGE_M      = 0.15      # 유효 거리 최솟값 (m)
LIDAR_MAX_RANGE_M      = 12.0      # 유효 거리 최댓값 (m)
LIDAR_ANGLE_RESOLUTION = 1.0       # 각도 해상도 (도)
# config.py 에 추가
LIDAR_FOV_DEG = 180.0   # 사용할 LiDAR 시야각 (정면 기준 ±90도)

# OAK 시야각 (OAK-D-Lite 스펙: 수평 73°, 수직 58°)
OAK_HFOV_DEG           = 73.0
OAK_VFOV_DEG           = 58.0

# ─── 좌표 변환 (LiDAR → OAK 기준) ─────────────────────────────────
# 로봇에 장착된 물리적 오프셋 (미터 / 도)
# LiDAR 가 OAK 보다 높이 X m, 앞으로 Y m, 오른쪽 Z m 에 위치하면
LIDAR_TO_OAK_OFFSET_X  = 0.0      # 좌우 오프셋 (m)
LIDAR_TO_OAK_OFFSET_Y  = 0.78     # 높이 오프셋 (m) - 라이다 대비 뎁스 카메라 장착 높이 차 (78cm)
LIDAR_TO_OAK_OFFSET_Z  = 0.05     # 전후 오프셋 (m)
LIDAR_TO_OAK_YAW_DEG   = 0.0      # 요(Yaw) 회전 오프셋 (도)

# ─── 융합 설정 ─────────────────────────────────────────────────────
FUSION_GRID_RESOLUTION = 0.05      # 격자 해상도 (m/cell)
FUSION_GRID_WIDTH_M    = 6.0       # 격자 폭 (m)
FUSION_GRID_HEIGHT_M   = 6.0       # 격자 높이 (m)

# 신뢰도 가중치
WEIGHT_OAK_CENTER      = 0.85      # 중앙 영역 OAK 신뢰도
WEIGHT_OAK_EDGE        = 0.35      # 가장자리 OAK 신뢰도
WEIGHT_LIDAR           = 0.90      # LiDAR 신뢰도 (일반적으로 높음)
WEIGHT_LIDAR_BLIND     = 1.00      # LiDAR 사각지대 보완 시 가중치

# ─── 장애물 판단 구역 (로봇 정면 기준, m) ─────────────────────────
ZONE_DANGER_M          = 1.0      # ~50cm : 즉시 정지
ZONE_WARNING_M         = 1.5      # ~120cm : 감속 / 경로 변경
ZONE_SAFE_M            = 2.0      # ~250cm : 정상 주행

# 로봇 폭 (충돌 여유 계산용, m)
ROBOT_WIDTH_M          = 0.5

# ─── 출력 / 디버그 ─────────────────────────────────────────────────
DEBUG_VISUALIZE        = True      # OpenCV 시각화 창 표시
DEBUG_PRINT_STATS      = True      # 콘솔 통계 출력
TARGET_FPS             = 15        # 처리 목표 FPS
Test_message = "서빙로봇 장애물 회피 시스템 - OAK-D-lite + LiDAR 융합"
