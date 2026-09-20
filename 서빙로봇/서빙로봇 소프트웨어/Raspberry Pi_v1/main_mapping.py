"""
main_mapping.py
1280 x 960 2D SLAM 격자 지도 & 실시간 7방향 서빙로봇 제어 대시보드

주요 기능:
- 1280 x 960 고해상도 대시보드 GUI (오른쪽: 2D 점유 지도, 왼쪽: 실시간 위치 & 컨트롤)
- 좌측 패널:
  1. 현재 서빙로봇 위치 (X, Y) 실시간 좌표 표시
  2. Target X / Y 목표 좌표 키보드 입력창
  3. 주행 시작 (START), 초기화 (RESET), 비상정지 (EMERGENCY STOP) 버튼
- 주행 시작 시 실시간으로 서빙로봇이 이동하며 좌표값이 지속적으로 갱신됨
"""

import argparse
import time
import sys
import os
import cv2
import numpy as np
import math
from typing import Optional, List

import config
from mapper import OccupancyMap
from path_recommender import PathRecommender, PathRecommendation
from map_visualizer import MapVisualizer
from lidar_processor import LidarProcessor, LidarScan
from oak_processor import OakProcessor, OakFrame, OakObstacle
from object_classifier import ObjectClassifier, ObjectType, ClassifiedObject
from voice_manager import VoiceManager


def main(use_mock: bool = False, visualize: bool = True):
    print("=" * 65)
    print("  1280x960 Serving Robot SLAM & Path Recommendation System")
    print(f"  Mode: {'Simulation (Mock)' if use_mock else 'Real Hardware'}")
    print("  Controls: Mouse Click UI | Key Commands: 'q' -> Quit")
    print("=" * 65)

    # ── 1. 핵심 모듈 초기화 ──────────────────────────────────────────
    occ_map = OccupancyMap()
    recommender = PathRecommender(occ_map, use_mock=use_mock)
    map_vis = MapVisualizer(occ_map)
    classifier = ObjectClassifier()
    voice_mgr = VoiceManager()
    classified_objects = []

    # ── [자동 맵 불러오기] 이전에 저장된 맵 파일이 있으면 시작 시 자동 복원 ──
    status_msg = "SYSTEM READY"
    if occ_map.load_map("saved_map.npz"):
        status_msg = "PREVIOUS MAP AUTO-LOADED"
        print("[System] 📂 이전 세션 맵(saved_map.npz) 자동 불러오기 완료!")

    lidar_proc = LidarProcessor(use_mock=use_mock)
    lidar_proc.start()

    oak_proc: Optional[OakProcessor] = None
    if not use_mock:
        try:
            temp_oak = OakProcessor()
            temp_oak.start()
            oak_proc = temp_oak
            print("[System] OAK-D-Lite Camera Initialized.")
        except Exception as e:
            oak_proc = None
            print(f"[System] OAK-D-Lite Init Failed: {e} -> LiDAR Single Mode")

    # ── 2. UI 및 상태 변수 초기화 ────────────────────────────────────
    win_name = "Serving Robot Control Dashboard (1280x960)"
    if visualize:
        cv2.namedWindow(win_name, cv2.WINDOW_AUTOSIZE)

    input_target_x_str = "2.00"
    input_target_y_str = "1.50"
    active_input: Optional[str] = None   # 'x' | 'y' | None

    is_driving = False
    is_emergency = False
    is_exit_requested = False  # UI 종료 버튼 클릭 감지 플래그

    # ── 3. 마우스 클릭 콜백 함수 ────────────────────────────────────
    def on_mouse_click(event, x, y, flags, param):
        nonlocal input_target_x_str, input_target_y_str, active_input, is_driving, is_emergency, is_exit_requested, status_msg

        if event == cv2.EVENT_LBUTTONDOWN:
            # 1) Target X 입력창 클릭
            xx, xy, xw, xh = MapVisualizer.ROI_INPUT_X
            if xx <= x <= xx + xw and xy <= y <= xy + xh:
                active_input = 'x'
                print("[UI] ✏️ Target X 입력창 선택됨")
                return

            # 2) Target Y 입력창 클릭
            yx, yy, yw, yh = MapVisualizer.ROI_INPUT_Y
            if yx <= x <= yx + yw and yy <= y <= yy + yh:
                active_input = 'y'
                print("[UI] ✏️ Target Y 입력창 선택됨")
                return

            # 입력창 외 영역 클릭 시 포커스 해제
            # 2-1) [신규] 테이블 원클릭 프리셋 버튼 클릭 [T1] [T2] [T3] [🏠 HOME]
            preset_clicked = None
            if MapVisualizer.ROI_BTN_T1[0] <= x <= MapVisualizer.ROI_BTN_T1[0] + MapVisualizer.ROI_BTN_T1[2] and \
               MapVisualizer.ROI_BTN_T1[1] <= y <= MapVisualizer.ROI_BTN_T1[1] + MapVisualizer.ROI_BTN_T1[3]:
                preset_clicked = "T1"
            elif MapVisualizer.ROI_BTN_T2[0] <= x <= MapVisualizer.ROI_BTN_T2[0] + MapVisualizer.ROI_BTN_T2[2] and \
                 MapVisualizer.ROI_BTN_T2[1] <= y <= MapVisualizer.ROI_BTN_T2[1] + MapVisualizer.ROI_BTN_T2[3]:
                preset_clicked = "T2"
            elif MapVisualizer.ROI_BTN_T3[0] <= x <= MapVisualizer.ROI_BTN_T3[0] + MapVisualizer.ROI_BTN_T3[2] and \
                 MapVisualizer.ROI_BTN_T3[1] <= y <= MapVisualizer.ROI_BTN_T3[1] + MapVisualizer.ROI_BTN_T3[3]:
                preset_clicked = "T3"
            elif MapVisualizer.ROI_BTN_HOME[0] <= x <= MapVisualizer.ROI_BTN_HOME[0] + MapVisualizer.ROI_BTN_HOME[2] and \
                 MapVisualizer.ROI_BTN_HOME[1] <= y <= MapVisualizer.ROI_BTN_HOME[1] + MapVisualizer.ROI_BTN_HOME[3]:
                preset_clicked = "HOME"

            if preset_clicked:
                if is_driving:
                    status_msg = "DRIVING IN PROGRESS: STOP FIRST TO CHANGE"
                    print(f"[UI] ⚠️ 현재 주행 중입니다. 목표를 바꾸려면 [EMERGENCY STOP] 또는 도착 후 선택하세요.")
                    return

                px_m, py_m, p_name = MapVisualizer.TABLE_PRESETS[preset_clicked]
                input_target_x_str = f"{px_m:.2f}"
                input_target_y_str = f"{py_m:.2f}"
                recommender.start_navigation(px_m, py_m, p_name)
                is_driving = True
                is_emergency = False
                status_msg = f"SERVING TO {p_name} ({px_m:+.1f}, {py_m:+.1f})"
                if preset_clicked == "HOME":
                    voice_mgr.say("주방으로 복귀 주행을 시작합니다.", priority=True)
                else:
                    t_num = preset_clicked.replace("T", "")
                    voice_mgr.say(f"{t_num}번 테이블로 서빙 주행을 시작합니다.", priority=True)
                print(f"[UI] 🍽️ 테이블 프리셋 클릭: {p_name} ({px_m:+.2f}, {py_m:+.2f}) -> 원클릭 서빙 시작!")
                return

            # 3) 커스텀 주행 시작 버튼 클릭
            bx, by, bw, bh = MapVisualizer.ROI_BTN_START
            if bx <= x <= bx + bw and by <= y <= by + bh:
                if is_driving:
                    status_msg = "DRIVING IN PROGRESS: STOP FIRST"
                    return
                try:
                    tx = float(input_target_x_str)
                    ty = float(input_target_y_str)
                    recommender.start_navigation(tx, ty, f"Target({tx:.1f},{ty:.1f})")
                    is_driving = True
                    is_emergency = False
                    status_msg = f"NAVIGATING TO ({tx:.1f}, {ty:.1f})"
                    voice_mgr.say("주행을 시작합니다. 목표 위치로 이동합니다.", cooldown_sec=3.0)
                    print(f"[UI] 🚀 주행 시작: Target ({tx:.2f}, {ty:.2f})")
                except ValueError:
                    status_msg = "ERROR: INVALID NUMERIC INPUT"
                return

            # 4) [신규] 헤딩 정렬 (0°/360°) 버튼 클릭
            ax, ay, aw, ah = MapVisualizer.ROI_BTN_ALIGN_HEAD
            if ax <= x <= ax + aw and ay <= y <= ay + ah:
                recommender.start_heading_alignment()
                status_msg = "ALIGNING HEADING (0° / 360°)..."
                voice_mgr.say("기준 방향을 정렬 중입니다.", cooldown_sec=3.0)
                print("[UI] 🧭 [ALIGN HEADING] 버튼 클릭됨 -> 0°/360° 1도 단위 정렬 시작!")
                return

            # 5) [신규] 맵 저장 버튼 (SAVE MAP) 클릭
            sx, sy, sw, sh = MapVisualizer.ROI_BTN_SAVE_MAP
            if sx <= x <= sx + sw and sy <= y <= sy + sh:
                if occ_map.save_map("saved_map.npz"):
                    status_msg = "MAP SAVED: saved_map.npz & .png"
                    voice_mgr.say("지도가 저장되었습니다.", cooldown_sec=2.0)
                else:
                    status_msg = "ERROR: MAP SAVE FAILED"
                return

            # 6) [신규] 맵 불러오기 버튼 (LOAD MAP) 클릭
            lx, ly, lw, lh = MapVisualizer.ROI_BTN_LOAD_MAP
            if lx <= x <= lx + lw and ly <= y <= ly + lh:
                if occ_map.load_map("saved_map.npz"):
                    status_msg = "MAP LOADED: saved_map.npz"
                    voice_mgr.say("지도를 불러왔습니다.", cooldown_sec=2.0)
                else:
                    status_msg = "ERROR: NO SAVED MAP FOUND"
                return

            # 7) 초기화 버튼 클릭
            rx_b, ry_b, rw_b, rh_b = MapVisualizer.ROI_BTN_RESET
            if rx_b <= x <= rx_b + rw_b and ry_b <= y <= ry_b + rh_b:
                recommender.reset_odometry()
                occ_map.reset()
                is_driving = False
                is_emergency = False
                input_target_x_str = "0.00"
                input_target_y_str = "0.00"
                status_msg = "SYSTEM & MAP RESET COMPLETE (RESET_ODO SENT)"
                voice_mgr.say("시스템과 지도를 초기화했습니다.", cooldown_sec=2.0)
                print("[UI] 🔄 시스템 및 맵 초기화 완료 (BLE 'RESET_ODO' 전송)")
                return

            # 8) 비상정지 버튼 클릭
            ex, ey, ew, eh = MapVisualizer.ROI_BTN_STOP
            if ex <= x <= ex + ew and ey <= y <= ey + eh:
                recommender.stop_navigation()
                is_driving = False
                is_emergency = True
                status_msg = "EMERGENCY STOP ENGAGED!"
                voice_mgr.say("비상 정지가 작동되었습니다.", priority=True)
                print("[UI] 🚨 비상정지 발동!")
                return

            # 9) 시스템 종료 버튼 (QUIT SYSTEM) 클릭
            qx, qy, qw, qh = MapVisualizer.ROI_BTN_QUIT
            if qx <= x <= qx + qw and qy <= y <= qy + qh:
                is_exit_requested = True
                status_msg = "QUIT REQUESTED BY USER"
                voice_mgr.say("시스템을 종료합니다.", priority=True)
                print("[UI] 🛑 UI [QUIT SYSTEM] 종료 버튼 클릭됨 -> 즉시 시스템 종료 중...")
                return

    if visualize:
        cv2.setMouseCallback(win_name, on_mouse_click)

    # ── 4. FPS 및 메인 루프 ──────────────────────────────────────────
    target_dt = 1.0 / config.TARGET_FPS
    frame_count = 0
    fps_timer = time.time()
    fps_display = 0.0

    try:
        while True:
            t0 = time.time()

            # 센서 데이터 수집
            lidar_scan = lidar_proc.get_scan()
            oak_frame = None

            if use_mock:
                t_now = time.time()
                mock_rgb = np.zeros((400, 400, 3), dtype=np.uint8)
                cv2.rectangle(mock_rgb, (0, 0), (400, 240), (120, 100, 90), -1)
                cv2.rectangle(mock_rgb, (0, 240), (400, 400), (60, 60, 60), -1)
                oak_frame = OakFrame(
                    depth_map=np.zeros((400, 400), dtype=np.float32),
                    rgb_frame=mock_rgb,
                    obstacles=[],
                    timestamp=t_now
                )
            else:
                if oak_proc:
                    oak_frame = oak_proc.get_frame()

            # 점유 맵 업데이트 (사전 저장 맵 베이스 위에 실시간 센서 데이터 융합)
            if frame_count % 3 == 0:
                classified_objects = classifier.classify(lidar_scan, oak_frame)

            occ_map.prepare_frame()
            if lidar_scan is not None:
                occ_map.update_from_lidar(lidar_scan)
            if oak_frame:
                occ_map.update_from_oak(oak_frame)
            if classified_objects:
                _update_map_from_classified(occ_map, classified_objects)

            # 경로 추천 및 로봇 이동 시뮬레이션
            recommendation = recommender.recommend()

            # [음성 안내] 장애물 회피 상태 진입 감지
            if recommender.avoid_state in ("AVOID_BRAKE", "AVOID_TURN_90"):
                voice_mgr.say("전방 장애물을 감지하여 우회 주행합니다.", cooldown_sec=6.0)

            # 목표 도착 체크
            if is_driving and recommendation and recommendation.is_goal_reached:
                is_driving = False
                status_msg = "GOAL ARRIVED SUCCESSFULLY!"
                voice_mgr.say("목표 위치에 도착했습니다. 이용해 주셔서 감사합니다.", cooldown_sec=8.0)
                print("[UI] 🎉 목표 지점 도착 완료!")

            # ── 5. 대시보드 시각화 렌더링 ───────────────────────────
            if visualize and config.DEBUG_VISUALIZE:
                dashboard_img = map_vis.render(
                    recommendation=recommendation,
                    fps=fps_display,
                    lidar_points=len(lidar_scan.points) if lidar_scan else 0,
                    input_target_x_str=input_target_x_str,
                    input_target_y_str=input_target_y_str,
                    active_input=active_input,
                    is_driving=is_driving,
                    is_emergency=is_emergency,
                    status_msg=status_msg,
                )

                cv2.imshow(win_name, dashboard_img)

                # ── 6. UI 종료 버튼 클릭, 창 닫기(X), 키보드 초고속 반응성 처리 ─────────────────
                if is_exit_requested:
                    print("[System] UI [QUIT SYSTEM] 클릭 요청에 따른 시스템 종료 중...")
                    break

                # 텍스트 입력 중일 때는 1ms 초고속 반응, 평상시에는 프레임 레이트 유지
                wait_ms = 1 if active_input is not None else max(1, int(target_dt * 1000))
                key = cv2.waitKey(wait_ms) & 0xFF

                # waitKey 호출 이후 OpenCV Window 닫기(X 버튼 클릭) 감지
                try:
                    prop = cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE)
                    if prop == 0 and frame_count > 5:
                        print("[System] GUI 창 닫기(X) 감지 -> 종료 중...")
                        break
                except Exception:
                    pass

                if key == ord('q') or key == 27:  # 'q' 또는 ESC
                    print("[System] 종료 키 입력 -> 종료 중...")
                    break

                # 텍스트 입력창 키 입력 초고속 즉각 처리
                if active_input is not None and key != 255:
                    curr_str = input_target_x_str if active_input == 'x' else input_target_y_str

                    if key in (8, 127):  # Backspace
                        curr_str = curr_str[:-1]
                    elif key in (13, 10):  # Enter
                        active_input = None
                    elif 32 <= key <= 126:
                        ch = chr(key)
                        if ch in "0123456789.-":
                            if len(curr_str) < 7:
                                curr_str += ch

                    if active_input == 'x':
                        input_target_x_str = curr_str
                    elif active_input == 'y':
                        input_target_y_str = curr_str
                elif active_input is None and key != 255:
                    # 단축키: 's' -> 맵 저장, 'l' -> 맵 불러오기
                    if key in (ord('s'), ord('S')):
                        if occ_map.save_map("saved_map.npz"):
                            status_msg = "MAP SAVED: saved_map.npz & .png"
                    elif key in (ord('l'), ord('L')):
                        if occ_map.load_map("saved_map.npz"):
                            status_msg = "MAP LOADED: saved_map.npz"

            # FPS 측정
            frame_count += 1
            if frame_count % 15 == 0:
                now = time.time()
                fps_display = 15 / max(now - fps_timer, 1e-6)
                fps_timer = now

    except KeyboardInterrupt:
        print("\n[System] 사용자 중지 요청 (Ctrl+C)")
    except Exception as e:
        print(f"\n[System] ⚠️ 메인 루프 예외 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n[System] 시스템 정리 및 자원 해제 중...")
        # ── [종료 0순위] 현재까지 스캔된 맵 자동 저장 ──
        try:
            if 'occ_map' in locals() and occ_map:
                print("[System] 💾 [0순위] 현재 맵 자동 저장 중 (saved_map.npz)...")
                occ_map.save_map("saved_map.npz")
        except Exception as e:
            print(f"[System] 맵 자동 저장 중 오류: {e}")

        # ── [종료 1순위] BLE 프로세스를 가장 먼저 안전하게 종료 ──
        try:
            if 'recommender' in locals() and recommender and getattr(recommender, 'ble', None):
                print("[System] [1순위] BLE 프로세스 종료 중...")
                recommender.ble.stop()
                print("[System] BLE 프로세스 정상 종료 완료.")
        except Exception as e:
            print(f"[System] BLE 프로세스 종료 중 예외 (무시): {e}")

        # ── [종료 2순위] LiDAR 프로세스 종료 ──
        try:
            if 'lidar_proc' in locals() and lidar_proc:
                print("[System] [2순위] LiDAR 프로세스 종료 중...")
                lidar_proc.stop()
        except Exception:
            pass

        # ── [종료 3순위] OAK 카메라 프로세스 종료 ──
        try:
            if 'oak_proc' in locals() and oak_proc:
                print("[System] [3순위] OAK 프로세스 종료 중...")
                oak_proc.stop()
        except Exception:
            pass

        # ── [종료 4순위] 음성 안내 독립 프로세스(Process) 종료 ──
        try:
            if 'voice_mgr' in locals() and voice_mgr:
                print("[System] [4순위] VoiceManager 프로세스 종료 중...")
                voice_mgr.stop()
        except Exception:
            pass

        # ── [종료 5순위] OpenCV GUI 창 닫기 ──
        try:
            if visualize:
                cv2.destroyAllWindows()
        except Exception:
            pass

        print("[System] 모든 리소스 해제 완료 -> 완전히 종료됩니다.")
        os._exit(0)


def _update_map_from_classified(occ_map: OccupancyMap, classified_objects: List[ClassifiedObject]): 
    for obj in classified_objects:
        if obj.object_type in (ObjectType.PERSON, ObjectType.OBSTACLE, ObjectType.GLASS_WALL):
            rad = math.radians(obj.angle_deg)
            x_m = obj.distance_m * math.sin(rad)
            y_m = obj.distance_m * math.cos(rad)
            row, col = occ_map.world_to_cell(x_m, y_m)
            val = 0.6 if obj.object_type == ObjectType.GLASS_WALL else 1.0
            occ_map.set_cell(row, col, val)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1280x960 Serving Robot SLAM & Path Recommendation System")
    parser.add_argument("--mock", action="store_true", help="하드웨어 없이 시뮬레이션 테스트 실행")
    parser.add_argument("--no-vis", action="store_true", help="OpenCV GUI 시각화 비활성화")
    args = parser.parse_args()

    main(use_mock=args.mock, visualize=not args.no_vis)
