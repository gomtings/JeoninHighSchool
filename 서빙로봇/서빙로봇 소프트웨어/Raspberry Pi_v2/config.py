"""
config.py
서빙 로봇 장애물 회피 시스템 - 전역 설정
OAK-D-Lite + LiDAR 융합
"""

# ─── OAK-D-Lite 설정 ───────────────────────────────────────────────
OAK_DEPTH_MIN_MM = 200  # 유효 깊이 최솟값 (mm)
OAK_DEPTH_MAX_MM = 5000  # 유효 깊이 최댓값 (mm)
OAK_CONFIDENCE_THRESH = 200  # StereoDepth 신뢰도 임계값 (0-255)
OAK_FPS = 15
OAK_RESOLUTION = "400p"  # 400p / 720p

# 벽/평면 필터 파라미터
OAK_WALL_RATIO_THRESH = 0.60  # 화면의 60% 이상 차지하면 벽으로 판단
OAK_EDGE_MARGIN = 0.15  # 화면 가장자리 15% 는 신뢰도 낮음
OAK_DEPTH_STD_THRESH = 80  # 표준편차(mm) 초과 시 노이즈 픽셀

# ─── LiDAR 설정 ────────────────────────────────────────────────────
LIDAR_PORT = "COM7"  # 시리얼 포트
LIDAR_BAUDRATE = 115200
LIDAR_MIN_RANGE_M = 0.15  # 유효 거리 최솟값 (m)
LIDAR_MAX_RANGE_M = 12.0  # 유효 거리 최댓값 (m)
LIDAR_ANGLE_RESOLUTION = 1.0  # 각도 해상도 (도)
# 라이다 장착 각도 보정. test_lidar_angle.py 로 실측한다.
# ★ 기준점 주의: "정면"은 사람이 대충 짚은 방향이 아니라 로봇이 실제로 전진하는
#   방향, 즉 ㄷ자 트레이의 열린 쪽이어야 한다. 이걸 잘못 잡으면 그 오차가 그대로
#   전체 맵 회전 오차가 된다 (실제로 한 번 겪음: 엉뚱한 방향을 정면으로 잡아
#   -95.6도로 설정했다가, ㄷ자 개방부에 손을 대니 +91.5도로 찍혀 약 90도 어긋난
#   것이 드러남).
# 실측: 오프셋 -95.6도 상태에서 ㄷ자 개방부에 손을 대니 +91.3도 / +91.7도로 측정
#       -> 필요한 오프셋 = -(측정값 - (-95.6)) 정규화 = +173.1 / +172.7 -> 평균 172.9도
LIDAR_ANGLE_OFFSET_DEG = 0

# 로봇 자체반사 제외 반경 (m). 라이다 빔이 로봇 몸체(마운트/브래킷/케이블)에
# 맞고 튕겨 돌아오는 근접 반사를 걸러낸다. 실측: 로봇을 제자리에서 90도 돌려도
# 0.23~0.24m 거리의 점 무리가 로봇과 같이 회전 (방 안 물체라면 이렇게 로봇을
# 따라 돌 수 없음) -> 로봇 반경(0.25m)과 일치하는 자체반사로 확인.
# LIDAR_MIN_RANGE_M(센서 자체 최소 측정거리, 0.15m)보다 커야 하며, 그보다
# 짧으면 이 반경이 무의미해진다.
# ★ 이후 실측: 로봇 트레이가 원형이 아니라 ㄷ자(좌/후면 벽 + 위 선반, 앞만 개방)
#   칸막이 구조라, 이 균일 반경 하나로는 가까운 방향(옆벽)에 맞추면 먼 방향
#   (뒤쪽 벽 모서리, 로봇 대각선 반경 0.354m)이 새고, 먼 방향에 맞추면 진짜 앞쪽
#   장애물 감지 거리를 깎아먹는다. calibrate_lidar_self_mask.py 로 각도별
#   프로파일(lidar_self_mask.json)을 만들면 그쪽을 우선 사용하고, 이 값은 그
#   파일이 없을 때(캘리브레이션 전, 또는 로봇 구조 변경 후 재캘리브레이션 전)의
#   폴백 균일 반경으로만 쓰인다.
LIDAR_SELF_EXCLUSION_M = 0.35
# 캘리브레이션 프로파일 파일명 (Raspberry Pi 폴더 기준 상대경로)
LIDAR_SELF_MASK_FILE = "lidar_self_mask.json"
# 캘리브레이션 값 상한(m). 캘리브레이션 중 실수로 벽 옆에 붙여뒀다거나 해서
# 특정 방향 임계값이 과도하게 커지는 걸 방지 (그 이상은 실제 장애물로 간주).
LIDAR_SELF_MASK_MAX_M = 0.45
# config.py 에 추가
LIDAR_FOV_DEG = 180.0  # 사용할 LiDAR 시야각 (정면 기준 ±90도)

# OAK 시야각 (OAK-D-Lite 스펙: 수평 73°, 수직 58°)
OAK_HFOV_DEG = 73.0
OAK_VFOV_DEG = 58.0

# ─── 뎁스 → 2D 맵 투영 (mapper.update_from_depth) ───────────────────
# 카메라는 수평(pitch 0)으로 장착되었다고 가정. 실측 후 값을 수정할 것.
OAK_HEIGHT_FROM_FLOOR_M = 1.10  # 카메라 렌즈의 바닥 기준 높이 (m)  ※ 가정값, 실측 필요
# 카메라가 아래로 기울어진 각도 (도, 아래로 + / 수평 0 / 위로 기울면 -).
# 2026-10-16 calibrate_oak_floor.py 결과에서 바닥(높이 약 1.09m)과 책상 윗면(카메라 아래 0.41m)이 둘 다
# 약 -4.3도로 일관되게 나와 위로 약 4도 기울어진 것으로 추정 (프레임 14개 이상, 확정값 아님: 다시 측정 권장)
OAK_PITCH_DEG = -4.3
# 카메라 기반 맵 반영(뎁스/OAK 장애물)을 초당 최대 몇 번 할지.
# 저장 기준(hit 5회 이상 등)은 메인 루프가 2~5FPS 일 때를 기준으로 정해진 "관측 횟수"라서,
# 프레임이 15FPS 로 다 반영되면 0.3초만 스친 사람/노이즈도 영구 벽으로 저장된다(2026-10-16 실측).
MAP_CAMERA_MAX_HZ = 3.0
OAK_OBSTACLE_HEIGHT_FILTER = True  # OAK 장애물 추출(oak_processor)에서도 바닥/천장 높이 범위 밖 픽셀을 제외
DEPTH_OBS_MIN_H_M = 0.10  # 이 높이 미만 점은 바닥으로 간주해 제외 (m)
DEPTH_OBS_MAX_H_M = 0.95  # 이 높이 초과 점은 천장/상부로 간주해 제외 (m)
DEPTH_ROW_STEP = 4  # 뎁스 이미지 행 샘플링 간격 (연산량 절감)
DEPTH_COL_STEP = 2  # 뎁스 이미지 열 샘플링 간격
DEPTH_MIN_PTS_PER_CELL = 3  # 한 셀에 이 개수 이상 점이 모여야 장애물로 인정 (노이즈 제거)
DEPTH_FREE_RAY_COL_STEP = 8  # free 레이캐스팅을 수행할 열 간격
DEPTH_RAYCAST_FREE = True  # 가장 가까운 점까지 free 처리 여부

# ─── YOLO 가구 → 2D 맵 투영 (mapper.update_from_yolo) ───────────────
YOLO_ENABLED = True  # False 면 YOLO 스레드를 띄우지 않음 (CPU 부하 비교 테스트용)
# YOLO 를 초당 최대 몇 번 돌릴지. ONNX Runtime 은 도는 동안 CPU 코어를 거의 다 쓰므로
# 쉬지 않고 돌리면 메인 루프와 라이다 프로세스가 CPU 를 못 받는다. 맵에는 정적 가구만 반영하므로 낮게 둔다.
YOLO_MAX_HZ = 2.0
YOLO_ORT_THREADS = 2  # ONNX Runtime 이 YOLO 추론에 쓸 CPU 스레드 수 (0 이면 기본값 = 코어 전부)
# COCO 클래스 id: 56=chair, 57=couch, 60=dining table
YOLO_MAP_CLASS_IDS = (56, 57, 60)
YOLO_MAP_MIN_CONF = 0.35  # 이 신뢰도 미만 감지는 맵에 반영하지 않음
YOLO_MAP_HIT_WEIGHT = 2  # 감지 1회당 셀 hit 가중치
YOLO_MAP_MIN_COL_PTS = 2  # 박스 한 열에서 유효 뎁스가 이 개수 이상이어야 그 열의 뎁스를 신뢰
YOLO_FLOOR_MAX_M = 6.0  # 뎁스가 없을 때 박스 하단(바닥 접점)으로 추정하는 최대 거리 (m)

# ─── 좌표 변환 (LiDAR → OAK 기준) ─────────────────────────────────
# 로봇에 장착된 물리적 오프셋 (미터 / 도)
# LiDAR 가 OAK 보다 높이 X m, 앞으로 Y m, 오른쪽 Z m 에 위치하면
LIDAR_TO_OAK_OFFSET_X = 0.0  # 좌우 오프셋 (m)
LIDAR_TO_OAK_OFFSET_Y = (
    0.78  # 높이 오프셋 (m) - 라이다 대비 뎁스 카메라 장착 높이 차 (78cm)
)
LIDAR_TO_OAK_OFFSET_Z = 0.05  # 전후 오프셋 (m)
LIDAR_TO_OAK_YAW_DEG = 0.0  # 요(Yaw) 회전 오프셋 (도)

# ─── 융합 설정 ─────────────────────────────────────────────────────
FUSION_GRID_RESOLUTION = 0.05  # 격자 해상도 (m/cell)
FUSION_GRID_WIDTH_M = 20.0  # 격자 폭 (m)
FUSION_GRID_HEIGHT_M = 20.0  # 격자 높이 (m)

# 신뢰도 가중치
WEIGHT_OAK_CENTER = 0.85  # 중앙 영역 OAK 신뢰도
WEIGHT_OAK_EDGE = 0.35  # 가장자리 OAK 신뢰도
WEIGHT_LIDAR = 0.90  # LiDAR 신뢰도 (일반적으로 높음)
WEIGHT_LIDAR_BLIND = 1.00  # LiDAR 사각지대 보완 시 가중치

# ─── 장애물 판단 구역 (로봇 정면 기준, m) ─────────────────────────
ZONE_DANGER_M = 0.5  # ~50cm : 즉시 정지
ZONE_WARNING_M = 1.0  # ~100cm : 감속 / 경로 변경
ZONE_SAFE_M = 1.5  # ~150cm : 정상 주행
OBS_BOX_MAX_DIST_M = ZONE_WARNING_M  # 맵에 Obs 장애물 박스를 표시할 근접 위험 거리 (m)

# 로봇 폭 (충돌 여유 계산용, m)
ROBOT_WIDTH_M = 0.5
# 로봇이 서 있는/지나간 자리(반폭 ROBOT_WIDTH_M/2 이내)를 매 프레임 '확실한 바닥'으로 확정
ROBOT_FOOTPRINT_FREE = True

# ─── 출력 / 디버그 ─────────────────────────────────────────────────
DEBUG_VISUALIZE = True  # OpenCV 시각화 창 표시
DEBUG_PRINT_STATS = True  # 콘솔 통계 출력
DEBUG_PROFILE = True  # 메인 루프 단계별 소요 시간(ms)을 30프레임마다 콘솔에 출력
TARGET_FPS = 15  # 처리 목표 FPS
Test_message = "서빙로봇 장애물 회피 시스템 - OAK-D-lite + LiDAR 융합"
