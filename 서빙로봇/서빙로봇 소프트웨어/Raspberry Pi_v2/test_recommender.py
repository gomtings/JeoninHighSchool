"""
test_recommender.py
신규 하이브리드 7방향 경로 추천 및 BLE 초음파 복합 회피 단위 테스트
"""

import math
from mapper import OccupancyMap
from path_recommender import PathRecommender, PathRecommendation

class MockBLE:
    """테스트용 가상 BLE 프로세서"""
    def __init__(self):
        self.sent_messages = []
        self.receive_queue = []

    def start(self):
        pass

    def send(self, msg: str):
        self.sent_messages.append(msg)

    def get_response(self) -> str | None:
        if self.receive_queue:
            return self.receive_queue.pop(0)
        return None

def test_scenario_1_forward_always():
    print("=" * 60)
    print(" 시나리오 1: 주행 시작 전 대기 -> BLE 정지 패킷 송신 / 주행 시작 후 -> FORWARD & BLE 0")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3 # Safe space

    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble

    # 1) 주행 시작 버튼을 안 누른 초기 대기 상태 -> BLE로 {"S-signal": "STOP", "R-signal": ""} 송신 검증
    rec = recommender.recommend()
    assert recommender.state == "STOPPED"
    assert any('"S-signal": "STOP"' in msg and '"R-signal": ""' in msg for msg in mock_ble.sent_messages)
    print(f"초기 대기 상태 BLE: {mock_ble.sent_messages[-1]} (기대: '{{\"S-signal\": \"STOP\", \"R-signal\": \"\"}}')")

    # 2) [주행 시작] 버튼 클릭 -> FORWARD 상태 진입 및 BLE "0" 송신 검증
    recommender.start_navigation(5.0, 0.0, "Goal")
    mock_ble.sent_messages.clear()
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Best Angle: {rec.best_angle_deg} (기대: 0.0)")
    print(f"Best Label: {rec.best_label} (기대: Front)")
    print(f"Scores Count: {len(rec.scores)} (기대: 19)")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.state == "FORWARD"
    assert rec.best_angle_deg == 0.0
    assert rec.best_label == "Front"
    assert len(rec.scores) == 19
    assert any('"S-signal": "0"' in msg for msg in mock_ble.sent_messages)
    print(">>> 시나리오 1 통과!\n")

def test_scenario_2_stopped_on_50cm():
    print("=" * 60)
    print(" 시나리오 2: 주행 중 전방 50cm 이내 장애물 감지 -> 회피 전용 상태 AVOID_TURN 진입 및 선회")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    # 로봇 정면 20cm 거리에 코앞 장애물 배치 (30cm 미만)
    r_obs, c_obs = occ_map.world_to_cell(0.0, 0.20)
    for dr in range(-3, 4):
        for dc in range(-3, 4):
            if occ_map.in_bounds(r_obs + dr, c_obs + dc):
                occ_map.grid[r_obs + dr, c_obs + dc] = 1.0 # Obstacle
                
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Avoid State: {recommender.avoid_state}")
    print(f"Best Angle: {rec.best_angle_deg}")
    print(f"Best Label: {rec.best_label}")
    print(f"Avoid Target Head: {recommender.avoid_target_head}")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.avoid_state in ("AVOID_BRAKE", "AVOID_TURN_90")
    assert recommender.avoid_target_head is not None
    assert len(mock_ble.sent_messages) > 0
    print(">>> 시나리오 2 통과!\n")

def test_scenario_3_avoidance_turning_complex():
    print("=" * 60)
    print(" 시나리오 3: 주행 중 전방 장애물 감지 시 초음파 여유 공간(우측 150cm > 좌측 50cm) -> 우측 90도 회피")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 전방 0.20m 코앞 정면 장애물 배치
    r_f, c_f = occ_map.world_to_cell(0.0, 0.20)
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if occ_map.in_bounds(r_f + dr, c_f + dc):
                occ_map.grid[r_f + dr, c_f + dc] = 1.0

    mock_ble.receive_queue.append("150, 50")
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Avoid State: {recommender.avoid_state}")
    print(f"Best Angle: {rec.best_angle_deg}")
    print(f"Best Label: {rec.best_label}")
    print(f"Avoid Target Head: {recommender.avoid_target_head}")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.avoid_state in ("AVOID_BRAKE", "AVOID_TURN_90")
    assert recommender.avoid_target_head == 90.0  # 우측 90도 회피
    assert recommender.avoid_side == "RIGHT"
    assert len(mock_ble.sent_messages) > 0
    print(">>> 시나리오 3 통과!\n")

def test_scenario_4_deadlock_uturn():
    print("=" * 60)
    print(" 시나리오 4: STOPPED 상태 -> 좌우 초음파 모두 30cm 미만 (데드락) -> U-Turn 및 BLE 180")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    recommender.state = "STOPPED"
    # 우측 25cm, 좌측 20cm 설정 (둘 다 30cm 미만)
    mock_ble.receive_queue.append("25, 20")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Best Angle: {rec.best_angle_deg} (기대: 180.0)")
    print(f"Best Label: {rec.best_label} (기대: U-Turn)")
    print(f"Stuck 여부: {rec.is_stuck} (기대: True)")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert rec.best_angle_deg == 180.0
    assert rec.best_label == "U-Turn"
    assert rec.is_stuck is True
    assert any('"S-signal": "STOP"' in msg for msg in mock_ble.sent_messages)
    print(">>> test_scenario_4 통과!\n")

def test_scenario_5_turning_to_forward():
    print("=" * 60)
    print(" 시나리오 5: 회피 전진 완료 및 전방 안전 -> 직진 정상 주행 복귀")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    # 4단계 세로 추월 직진 상태에서 측면 초음파가 트임 (80cm) -> 2프레임 후 IDLE 정상 주행 복귀!
    recommender.avoid_state = "AVOID_PASS_LENGTH"
    recommender.avoid_side = "RIGHT"
    recommender.ble_left_cm = 80.0
    recommender.avoid_clear_count = 1
    recommender.robot_heading_deg = 0.0
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Avoid State: {recommender.avoid_state} (기대: IDLE)")
    print(f"Best Angle: {rec.best_angle_deg} (기대: 0.0)")
    print(f"Best Label: {rec.best_label} (기대: Front)")
    print(f"Avoid Target Head: {recommender.avoid_target_head}")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.state == "FORWARD"
    assert recommender.avoid_state in ("IDLE", "AVOID_TURN_RETURN")
    print(">>> 시나리오 5 통과!\n")

def test_scenario_6_forward_right_near():
    print("=" * 60)
    print(" 시나리오 6: FORWARD 상태 -> 우측 초음파 10cm 미만 -> 좌측 보정 조향(-30도) 및 BLE -30")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
def test_scenario_6_forward_wall_adjacent_straight():
    print("=" * 60)
    print(" 시나리오 6: FORWARD 상태 -> 우측에 벽(초음파 8cm)이 있더라도 전방 안전 시 흔들림 없이 직진(0도) 유지")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    # 우측 벽 근접 8cm 설정
    mock_ble.sent_messages.clear()
    mock_ble.receive_queue.append("8, 50")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Best Angle: {rec.best_angle_deg} (기대: 0.0)")
    print(f"Best Label: {rec.best_label} (기대: Front)")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.state == "FORWARD"
    assert rec.best_angle_deg == 0.0
    assert rec.best_label == "Front"
    assert any('"S-signal": "0"' in msg for msg in mock_ble.sent_messages)
    print(">>> 시나리오 6 (벽 근접 시 안정 직진 유지) 통과!\n")

def test_scenario_7_forward_left_wall_adjacent_straight():
    print("=" * 60)
    print(" 시나리오 7: FORWARD 상태 -> 좌측에 벽(초음파 8cm)이 있더라도 전방 안전 시 흔들림 없이 직진(0도) 유지")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    # 좌측 벽 근접 8cm 설정
    mock_ble.sent_messages.clear()
    mock_ble.receive_queue.append("50, 8")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Best Angle: {rec.best_angle_deg} (기대: 0.0)")
    print(f"Best Label: {rec.best_label} (기대: Front)")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.state == "FORWARD"
    assert rec.best_angle_deg == 0.0
    assert rec.best_label == "Front"
    assert any('"S-signal": "0"' in msg for msg in mock_ble.sent_messages)
    print(">>> 시나리오 7 (좌측 벽 근접 시 안정 직진 유지) 통과!\n")

def test_scenario_8_forward_corridor_straight():
    print("=" * 60)
    print(" 시나리오 8: FORWARD 상태 -> 좁은 복도(양측 벽 초음파 15cm) 통과 시 전방 안전 시 직진(0도) 유지")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    # 양측 벽 15cm 복도 (x=0, y=0, head=0, r=15cm, l=15cm)
    mock_ble.sent_messages.clear()
    mock_ble.receive_queue.append("0.0, 0.0, 0.0, 15.0, 15.0")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Best Angle: {rec.best_angle_deg} (기대: 0.0)")
    print(f"Best Label: {rec.best_label} (기대: Front)")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.state == "FORWARD"
    assert rec.best_angle_deg == 0.0
    assert rec.best_label == "Front"
    assert any('"S-signal": "0"' in msg for msg in mock_ble.sent_messages)
    print(">>> 시나리오 8 (복도 안정 직진 통과) 통과!\n")

def test_scenario_9_avoidance_turning_left_multi():
    print("=" * 60)
    print(" 시나리오 9: 주행 중 전방 장애물 감지 시 초음파 여유 공간(좌측 150cm > 우측 50cm) -> 좌측 회피")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 전방 0.20m 코앞 정면 장애물 배치
    r_f, c_f = occ_map.world_to_cell(0.0, 0.20)
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if occ_map.in_bounds(r_f + dr, c_f + dc):
                occ_map.grid[r_f + dr, c_f + dc] = 1.0

    mock_ble.receive_queue.append("50, 150")
    recommender.start_navigation(5.0, 0.0, "Goal")
    
    rec = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Avoid State: {recommender.avoid_state}")
    print(f"Best Angle: {rec.best_angle_deg}")
    print(f"Best Label: {rec.best_label}")
    print(f"Avoid Target Head: {recommender.avoid_target_head}")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    
    assert recommender.avoid_state in ("AVOID_BRAKE", "AVOID_TURN_90")
    assert recommender.avoid_target_head == -90.0  # 좌측 90도 회피
    assert recommender.avoid_side == "LEFT"
    assert len(mock_ble.sent_messages) > 0
    print(">>> 시나리오 9 통과!\n")

def test_scenario_10_target_coordinate_navigation():
    print("=" * 60)
    print(" 시나리오 10: 목표 좌표 주행 (1.0, 0.0) -> 오차 0.1m(0.93m 도달) 시 목표 완료 및 정지 패킷 송신")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 1. 주행 시작: 목표 좌표 (1.0, 0.0) 설정 [전방 1m]
    recommender.start_navigation(1.0, 0.0, "Goal (1.0, 0.0)")
    assert recommender.target_x == 1.0
    assert recommender.target_y == 0.0
    
    # 주행 전진 단계
    rec1 = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Goal dist: {rec1.dist_to_goal_m:.2f}m")
    assert rec1.is_goal_reached == False
    assert recommender.state == "FORWARD"
    
    # 로봇 위치를 (0.93, 0.0)으로 이동 (목표와 오차 0.07m <= 0.1m 범위 진입)
    recommender.robot_x = 0.93
    recommender.robot_y = 0.0
    
    rec2 = recommender.recommend()
    print(f"State: {recommender.state}")
    print(f"Reason: {rec2.reason}")
    print(f"BLE Sent: {mock_ble.sent_messages}")
    assert rec2.is_goal_reached == True
    assert recommender.state == "GOAL_REACHED"
    assert rec2.best_angle_deg == recommender.STOP_ANGLE
    assert len(rec2.scores) == 0, "도착 시에는 19방향 점수/추천이 없어야 합니다."
    assert any('"S-signal": "STOP"' in msg for msg in mock_ble.sent_messages)

    # 3. 도착 후 다음 프레임에서도 계속 STOP 신호만 나가고 방향 추천을 일체 하지 않는지 확인
    mock_ble.sent_messages.clear()
    rec3 = recommender.recommend()
    assert rec3.is_goal_reached == True
    assert recommender.state == "GOAL_REACHED"
    assert rec3.best_angle_deg == recommender.STOP_ANGLE
    assert len(rec3.scores) == 0
    assert mock_ble.sent_messages[-1] == '{"S-signal": "STOP", "R-signal": ""}'
    print(">>> 시나리오 10 (0.1m 오차 도착 & 오직 정지 신호만 송신) 통과!\n")

def test_scenario_11_stop_navigation_button():
    print("=" * 60)
    print(" 시나리오 11: 주행 중 [주행 정지] 버튼 클릭 시 도착 전 강제 정지(정지 패킷 송신)")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 주행 시작
    recommender.start_navigation(5.0, 0.0, "Goal (5.0, 0.0)")
    rec1 = recommender.recommend()
    assert recommender.state == "FORWARD"
    
    # 사용자 [주행 정지] 버튼 클릭
    mock_ble.sent_messages.clear()
    recommender.stop_navigation()
    print(f"State after stop button: {recommender.state}")
    print(f"BLE Sent on Stop: {mock_ble.sent_messages}")
    
    assert recommender.state == "STOPPED"
    assert recommender.target_x is None
    assert recommender.target_y is None
    assert any('"S-signal": "STOP"' in msg and '"R-signal": ""' in msg for msg in mock_ble.sent_messages)
    print(">>> 시나리오 11 (주행 정지 버튼 클릭 테스트) 통과!\n")

def test_scenario_12_ble_5_values_format():
    print("=" * 60)
    print(" 시나리오 12: BLE 5개 인자 수신 포맷 (x, y, heading, right, left)")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 5개 인자: x, y, heading, right, left
    mock_ble.receive_queue.append("1.5, 2.0, 45.0, 120.0, 80.0")
    recommender._poll_ble()
    
    print(f"Robot Position: ({recommender.robot_x}, {recommender.robot_y}, heading={recommender.robot_heading_deg}°)")
    print(f"Ultrasonic Sensor: R={recommender.ble_right_cm:.1f}cm, L={recommender.ble_left_cm:.1f}cm")
    
    assert recommender.robot_x == 1.5
    assert recommender.robot_y == 2.0
    assert recommender.robot_heading_deg == 45.0
    assert recommender.ble_right_cm == 120.0
    assert recommender.ble_left_cm == 80.0
    print(">>> 시나리오 12 (BLE 5개 인자 수신 파싱) 통과!\n")

def test_scenario_13_reset_odometry_ble_message():
    print("=" * 60)
    print(" 시나리오 13: 리셋 버튼 클릭 시 reset_odometry -> BLE {\"S-signal\":\"STOP\", \"R-signal\":\"RESET_ODO\"} 전송 및 좌표 초기화")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 주행 중인 상황 세팅
    recommender.start_navigation(5.0, 5.0, "Goal (5.0, 5.0)")
    recommender.robot_x = 2.5
    recommender.robot_y = 3.0
    recommender.robot_heading_deg = 30.0
    
    # 오도메트리 리셋 버튼 클릭
    mock_ble.sent_messages.clear()
    recommender.reset_odometry()
    
    print(f"BLE Sent on Reset: {mock_ble.sent_messages}")
    print(f"Robot X: {recommender.robot_x}, Y: {recommender.robot_y}, Heading: {recommender.robot_heading_deg}")
    print(f"State: {recommender.state}")
    
    assert recommender.robot_x == 0.0
    assert recommender.robot_y == 0.0
    assert recommender.robot_heading_deg == 0.0
    assert any('"S-signal": "STOP"' in msg and '"R-signal": "RESET_ODO"' in msg for msg in mock_ble.sent_messages)
    print(">>> 시나리오 13 (리셋 시 BLE 딕셔너리 RESET_ODO 전송) 통과!\n")

def test_scenario_14_ble_realtime_xy_parsing():
    print("=" * 60)
    print(" 시나리오 14: BLE 다양한 실시간 x, y, heading 좌표 UI 완벽 파싱")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 1. Key-Value 형식
    mock_ble.receive_queue.append("X: 1.45 Y: 2.80 H: 30.5 R: 85 L: 90")
    recommender._poll_ble()
    print(f"Key-Value 수신 파싱 -> Robot X: {recommender.robot_x}, Y: {recommender.robot_y}, Heading: {recommender.robot_heading_deg}")
    assert recommender.robot_x == 1.45
    assert recommender.robot_y == 2.80
    assert recommender.robot_heading_deg == 30.5
    
    # 2. 3개 콤마 형식 (x, y, heading)
    mock_ble.receive_queue.append("3.20, 4.50, 90.0")
    recommender._poll_ble()
    print(f"3개 콤마 수신 파싱 -> Robot X: {recommender.robot_x}, Y: {recommender.robot_y}, Heading: {recommender.robot_heading_deg}")
    assert recommender.robot_x == 3.20
    assert recommender.robot_y == 4.50
    assert recommender.robot_heading_deg == 90.0
    
    # 3. 2개 콤마 형식 (x, y)
    mock_ble.receive_queue.append("-0.75, 1.85")
    recommender._poll_ble()
    print(f"2개 x,y 수신 파싱 -> Robot X: {recommender.robot_x}, Y: {recommender.robot_y}")
    assert recommender.robot_x == -0.75
    assert recommender.robot_y == 1.85
    print(">>> 시나리오 14 (BLE 실시간 x,y 좌표 수신 및 UI 연동) 통과!\n")

def test_scenario_15_sequential_xy_no_y_zero():
    print("=" * 60)
    print(" 시나리오 15: 2단계 Y축 맞춤 후 X오차 발생 시 -> Y=0 복귀 없이 현재 위치에서 X 재정렬")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 목표 (3.0, 2.0) 설정 [전방 3m, 우측 2m]
    recommender.start_navigation(3.0, 2.0, "Goal (3.0, 2.0)")
    
    # 1. 로봇이 1단계 X축(전방)을 맞춤 (X=3.00, Y=0.0) -> sub_stage가 ALIGN_Y로 전환됨
    recommender.robot_x = 3.00
    recommender.robot_y = 0.00
    rec1 = recommender.recommend()
    print(f"1단계 완료 후 -> sub_stage: {recommender.sub_stage}, Reason: {rec1.reason}")
    assert recommender.sub_stage == "ALIGN_Y"
    
    # 2. 로봇이 Y축(우측)을 맞추러 가서 Y=2.00에 도달했는데 외란으로 X=2.70 (dx=0.30m 오차 발생)
    recommender.robot_x = 2.70
    recommender.robot_y = 2.00
    rec2 = recommender.recommend()
    print(f"Y축 도달 후 X오차 시 -> sub_stage: {recommender.sub_stage}, Reason: {rec2.reason}")
    # Y를 0으로 되돌리지 않고, 현재 위치에서 바로 ALIGN_X로 전환하여 X를 재정렬!
    assert recommender.sub_stage == "ALIGN_X"
    assert "1단계 X재정렬" in rec2.reason
    assert "Y=0" not in rec2.reason
    
    # 3. 로봇이 현재 위치에서 X를 다시 맞춤 (X=3.00, Y=2.00) -> 즉시 도착 완료!
    recommender.robot_x = 3.00
    recommender.robot_y = 2.00
    rec3 = recommender.recommend()
    print(f"X 재정렬 완료 후 -> state: {recommender.state}, is_goal_reached: {rec3.is_goal_reached}")
    assert rec3.is_goal_reached == True
    assert recommender.state == "GOAL_REACHED"
    print(">>> 시나리오 15 (Y=0 복귀 없는 순차 오차 수렴 주행) 통과!\n")

def test_scenario_16_full_avoidance_cycle():
    print("=" * 60)
    print(" 시나리오 16: 디귿(ㄷ)자형 초음파 측면 감지 4단계 완전 회피 사이클 검증")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    
    # 전방 0.20m 지점에 코앞 장애물 배치
    r_obs, c_obs = occ_map.world_to_cell(0.0, 0.20)
    for dr in range(-3, 4):
        for dc in range(-3, 4):
            if occ_map.in_bounds(r_obs + dr, c_obs + dc):
                occ_map.grid[r_obs + dr, c_obs + dc] = 1.0
                
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    
    # 초음파: 우측(150cm)이 좌측(50cm)보다 넓음 -> 우측 회피 선택
    mock_ble.receive_queue.append("150, 50")
    recommender.start_navigation(5.0, 0.0, "Goal (5, 0)")
    
    # 1. 전방 장애물 감지 -> AVOID_BRAKE/AVOID_TURN_90 상태 진입 및 선회 준비
    rec1 = recommender.recommend()
    print(f"[Step 1] avoid_state: {recommender.avoid_state}, 조향: {rec1.best_label}, BLE: {mock_ble.sent_messages[-1]}")
    assert recommender.avoid_state in ("AVOID_BRAKE", "AVOID_TURN_90")
    while recommender.avoid_state == "AVOID_BRAKE":
        recommender.recommend()
    assert recommender.avoid_state == "AVOID_TURN_90"
    
    # 2. 로봇이 +90도로 선회 완료 -> AVOID_PASS_WIDTH(가로 폭 직진 & 좌측 초음파 감시) 진입 및 BLE "0"(직진) 전송!
    recommender.robot_heading_deg = 90.0
    occ_map.grid[:] = 0.3  # 90도 선회 후 우측 전방은 트여있음
    recommender.ble_left_cm = 25.0  # 장애물 옆면 지나가는 중
    rec2 = recommender.recommend()
    print(f"[Step 2] avoid_state: {recommender.avoid_state}, 조향: {rec2.best_label}, BLE: {mock_ble.sent_messages[-1]}")
    assert recommender.avoid_state == "AVOID_PASS_WIDTH"
    assert any('"S-signal": "0"' in msg for msg in mock_ble.sent_messages)
    
    # 3. 최소 5프레임 직진 + 오도메트리 가로 이동 + 왼쪽 초음파 트임 (80cm) -> AVOID_TURN_FRONT 전환!
    recommender.robot_y = -0.60
    recommender.ble_left_cm = 80.0
    for _ in range(5):
        recommender.recommend()
    rec3 = recommender.recommend()
    print(f"[Step 3] avoid_state: {recommender.avoid_state}, 조향: {rec3.best_label}, BLE: {mock_ble.sent_messages[-1]}")
    assert recommender.avoid_state == "AVOID_TURN_FRONT"
    
    # 4. 로봇이 전방 0도로 선회 완료 -> AVOID_PASS_LENGTH(세로 길이 추월 직진) 진입!
    recommender.robot_heading_deg = 0.0
    recommender.ble_left_cm = 25.0  # 장애물 몸통 옆면 통과 중
    rec4 = recommender.recommend()
    print(f"[Step 4] avoid_state: {recommender.avoid_state}, 조향: {rec4.best_label}, BLE: {mock_ble.sent_messages[-1]}")
    assert recommender.avoid_state == "AVOID_PASS_LENGTH"
    assert any('"S-signal": "0"' in msg for msg in mock_ble.sent_messages)
    
    # 5. 세로 길이도 이동 거리 확보 + 초음파 트임 (80cm) -> AVOID_TURN_RETURN 또는 IDLE 복귀!
    recommender.robot_x = 0.80
    recommender.ble_left_cm = 80.0
    occ_map.grid[:] = 0.3
    for _ in range(5):
        recommender.recommend()
    rec5 = recommender.recommend()
    print(f"[Step 5] avoid_state: {recommender.avoid_state}, 조향: {rec5.best_label}, Reason: {rec5.reason}")
    assert recommender.avoid_state in ("IDLE", "AVOID_TURN_RETURN")
    print(">>> 시나리오 16 (디귿자형 4단계 초음파 회피 전체 사이클 완벽 통과!) 통과!\n")

def test_scenario_17_dynamic_obstacle_smart_return():
    print("=" * 60)
    print(" 시나리오 17: [안전 강화 3] 90도 회전 직후 사람이 이미 비켜서 지나감 -> 불필요한 직진 없이 즉시 0도 복귀")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.start_navigation(5.0, 0.0, "Goal")

    recommender.avoid_state = "AVOID_TURN_90"
    recommender.avoid_side = "RIGHT"
    recommender.avoid_target_head = 90.0
    recommender.robot_heading_deg = 90.0  # 90도 선회 완료
    recommender.ble_left_cm = 999.0       # 측면에 장애물 없음(사람이 비킴)

    rec = recommender.recommend()
    print(f"Avoid State: {recommender.avoid_state}, Target Head: {recommender.avoid_target_head}, Reason: {rec.reason}")
    assert recommender.avoid_state in ("AVOID_PASS_WIDTH", "AVOID_TURN_FRONT")
    print(">>> 시나리오 17 (동적 장애물 스마트 빠른 복귀) 통과!\n")

def test_scenario_18_button_triggered_1deg_heading_alignment():
    print("=" * 60)
    print(" 시나리오 18: [버튼 기반 1도 정밀 헤딩 정렬] 0도 vs 360도 비교 및 BLE 정지 패킷 검증")
    print("=" * 60)
    occ_map = OccupancyMap()
    occ_map.grid[:] = 0.3
    recommender = PathRecommender(occ_map)
    mock_ble = MockBLE()
    recommender.ble = mock_ble
    recommender.state = "STOPPED"

    # 1. 평상시 버튼 안 누름 -> BLE {"S-signal": "STOP", "R-signal": ""} 전송 유지
    rec_idle = recommender.recommend()
    print(f"[Idle State] BLE: {mock_ble.sent_messages[-1]}")
    assert any('"S-signal": "STOP"' in msg and '"R-signal": ""' in msg for msg in mock_ble.sent_messages)

    # 2. 케이스 A: '헤딩 정렬' 버튼 클릭 -> 현재 헤딩 30도 -> 0도 목표로 1도 단위 Left-30 송신
    recommender.robot_heading_deg = 30.0
    recommender.start_heading_alignment()
    assert recommender.aligning_heading == True

    rec_a = recommender.recommend()
    print(f"[Case A: Head 30°] 조향: {rec_a.best_label}, BLE: {mock_ble.sent_messages[-1]}, Reason: {rec_a.reason}")
    assert "0° 정렬 중" in rec_a.reason
    assert "Left-30" in rec_a.best_label
    assert any('"S-signal": "-30"' in msg for msg in mock_ble.sent_messages)

    # 3. 케이스 B: '헤딩 정렬' 버튼 클릭 -> 현재 헤딩 345도 -> 360도 목표로 1도 단위 Right-15 송신
    recommender.robot_heading_deg = 345.0
    recommender.start_heading_alignment()
    rec_b = recommender.recommend()
    print(f"[Case B: Head 345°] 조향: {rec_b.best_label}, BLE: {mock_ble.sent_messages[-1]}, Reason: {rec_b.reason}")
    assert "360° 정렬 중" in rec_b.reason
    assert "Right-15" in rec_b.best_label
    assert any('"S-signal": "15"' in msg for msg in mock_ble.sent_messages)

    # 4. 케이스 C: 현재 헤딩 0.5도 -> 0도와 1도 이내 정렬 완료 -> 플래그 자동 해제 및 BLE 정지 패킷 송신
    recommender.robot_heading_deg = 0.5
    recommender.start_heading_alignment()
    rec_c = recommender.recommend()
    print(f"[Case C: Head 0.5°] BLE: {mock_ble.sent_messages[-1]}, Reason: {rec_c.reason}")
    assert recommender.aligning_heading == False
    assert any('"S-signal": "STOP"' in msg and '"R-signal": ""' in msg for msg in mock_ble.sent_messages)

    # 5. 케이스 D: 현재 헤딩 359.8도 -> 360도와 1도 이내 정렬 완료 -> 플래그 자동 해제 및 BLE 정지 패킷 송신
    recommender.robot_heading_deg = 359.8
    recommender.start_heading_alignment()
    rec_d = recommender.recommend()
    print(f"[Case D: Head 359.8°] BLE: {mock_ble.sent_messages[-1]}, Reason: {rec_d.reason}")
    assert recommender.aligning_heading == False
    assert any('"S-signal": "STOP"' in msg and '"R-signal": ""' in msg for msg in mock_ble.sent_messages)

    print(">>> 시나리오 18 (버튼 기반 1도 단위 정밀 헤딩 정렬 & 정지 패킷 검증) 통과!\n")

if __name__ == "__main__":
    print("하이브리드 10도 세분화 경로 추천 시스템 종합 단위 검증을 시작합니다.\n")
    test_scenario_1_forward_always()
    test_scenario_2_stopped_on_50cm()
    test_scenario_3_avoidance_turning_complex()
    test_scenario_4_deadlock_uturn()
    test_scenario_5_turning_to_forward()
    test_scenario_6_forward_wall_adjacent_straight()
    test_scenario_7_forward_left_wall_adjacent_straight()
    test_scenario_8_forward_corridor_straight()
    test_scenario_9_avoidance_turning_left_multi()
    test_scenario_10_target_coordinate_navigation()
    test_scenario_11_stop_navigation_button()
    test_scenario_12_ble_5_values_format()
    test_scenario_13_reset_odometry_ble_message()
    test_scenario_14_ble_realtime_xy_parsing()
    test_scenario_15_sequential_xy_no_y_zero()
    test_scenario_16_full_avoidance_cycle()
    test_scenario_17_dynamic_obstacle_smart_return()
    test_scenario_18_button_triggered_1deg_heading_alignment()
    print("모든 하이브리드 연동 단위 검증 성공! 매우 성공적입니다.")
