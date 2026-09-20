"""
main.py
서빙 로봇 장애물 회피 시스템 메인 루프
lidar_scan = lidar_proc.get_scan()
실행 방법:
    # 실제 하드웨어 (OAK + LiDAR 연결 필요)
    python main.py

    # 시뮬레이션 모드 (하드웨어 없이 테스트)
    python main.py --mock

    # 시각화 없이 실행
    python main.py --mock --no-vis
"""
# python -m venv .venv
# 1. Raspberry Pi 디렉토리로 이동
# cd "c:\GitHub\JeoninHighSchool\서빙로봇\서빙로봇 소프트웨어\Raspberry Pi"
# 2. 가상환경 활성화
# .\.venv\Scripts\Activate.ps1
# 3. 시뮬레이션 대시보드 실행
# python main_mapping.py --mock
# 4. 가상환경 비활성화
# deactivate

import argparse  # 명령줄 인자 파싱을 위한 모듈
import time      # 시간 관련 함수 (타이머, 지연 등)
import sys       # 시스템 관련 함수 (종료 등)
import os        # 완전 프로세스 종료(os._exit) 모듈
import cv2       # OpenCV 라이브러리 (이미지 처리 및 시각화)
import numpy as np  # NumPy 라이브러리 (배열 계산)

# 프로젝트 내 모듈들을 임포트합니다.
import config  # 설정 파일에서 상수들을 가져옴
from oak_processor    import OakProcessor  # OAK 카메라 처리 클래스
from lidar_processor  import LidarProcessor  # LiDAR 데이터 처리 클래스
from sensor_fusion    import SensorFusion  # 센서 융합 클래스
from obstacle_avoidance import ObstacleAvoidance, ZoneLevel  # 장애물 회피 클래스와 존 레벨


# 메인 함수: 서빙 로봇의 장애물 회피 시스템을 실행하는 메인 루프
def main(use_mock: bool = False, visualize: bool = True):
    # 프로그램 시작 메시지를 출력합니다.
    print("=" * 55)
    print("  서빙 로봇 장애물 회피 시스템 시작")
    print(f"  모드: {'시뮬레이션(Mock)' if use_mock else '실제 하드웨어'}")  # 모드 표시
    print("=" * 55)

    # ── 모듈 초기화 ───────────────────────────────────────────────
    # 각 모듈 객체들을 생성합니다.
    lidar_proc  = LidarProcessor(use_mock=use_mock)  # LiDAR 처리기 (시뮬레이션 모드 선택)
    fusion      = SensorFusion()  # 센서 융합기
    avoidance   = ObstacleAvoidance()  # 장애물 회피기

    # OAK 프로세서를 초기화합니다 (실제 하드웨어 모드에서만).
    oak_proc: OakProcessor | None = None
    if not use_mock:
        try:
            # OakProcessor() 생성 자체는 dai 라이브러리 설치 여부만 확인하므로 하드웨어가
            # 아직 없어도 실패하지 않는다. 여기서 실패하면 복구 불가능한 상태이므로 완전히 비활성화.
            oak_proc = OakProcessor()
        except Exception as e:
            oak_proc = None
            print(f"[Main] OAK 사용 불가: {e} → OAK 없이 LiDAR 단독 모드")

        if oak_proc is not None:
            try:
                oak_proc.start()  # OAK 카메라 시작 (여기서는 실제 USB 연결을 시도)
                print("[Main] OAK-D-Lite 연결 완료")  # 연결 성공 메시지
            except Exception as e:
                # 초기 연결 실패는 치명적이지 않다 - USB 열거 지연 등 일시적 상황일 수 있으므로
                # oak_proc 는 살려두고, get_frame() 내부의 3초 쿨다운 자동 재연결에 복구를 맡긴다.
                print(f"[Main] OAK 초기 연결 실패: {e} → LiDAR 단독으로 시작, 백그라운드에서 자동 재연결 시도")

    # LiDAR 프로세서를 시작합니다.
    lidar_proc.start()

    # ── FPS 제어 ──────────────────────────────────────────────────
    # FPS 제어를 위한 변수들을 초기화합니다.
    target_dt = 1.0 / config.TARGET_FPS  # 목표 프레임 시간 (초 단위)
    frame_count = 0  # 프레임 카운터
    fps_timer   = time.time()  # FPS 계산용 타이머 시작 시간
    fps_display = 0.0  # 표시할 FPS 값

    print("[Main] 루프 시작 (종료: 'q')")  # 루프 시작 메시지

    try:
        # 메인 루프: 무한 반복하며 센서 데이터 처리, 융합, 회피 판단 수행
        while True:
            t0 = time.time()  # 루프 시작 시간 기록

            # 1. 센서 데이터 수집
            # OAK 카메라 프레임을 가져옵니다 (사용 시).
            oak_frame  = oak_proc.get_frame()   if oak_proc else None
            # LiDAR 스캔 데이터를 가져옵니다.
            lidar_scan = lidar_proc.get_scan()

            # 2. 융합
            # OAK와 LiDAR 데이터를 융합하여 장애물 정보를 생성합니다.
            fused_obstacles = fusion.fuse(oak_frame, lidar_scan)

            # 3. 회피 판단
            # 융합된 장애물 정보를 기반으로 로봇의 이동 명령을 결정합니다.
            cmd = avoidance.decide(fused_obstacles)

            # 4. 콘솔 출력
            # 디버그 모드에서 통계 정보를 출력합니다.
            if config.DEBUG_PRINT_STATS:
                print(f"\r[FPS={fps_display:4.1f}] {cmd}", end="", flush=True)  # FPS와 명령을 실시간 출력

            # 5. 시각화
            # 시각화가 활성화되고 디버그 시각화 설정이 켜져 있으면 디버그 창을 표시합니다.
            if visualize and config.DEBUG_VISUALIZE:
                _show_debug_windows(  # 디버그 창 표시 함수 호출
                    oak_frame, lidar_scan, fusion, avoidance, cmd,
                )

                # 키 입력을 확인합니다.
                key = cv2.waitKey(1) & 0xFF

                win_name = "Obstacle Avoidance - OAK + LiDAR Fusion"
                try:
                    if cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) < 1:
                        break
                except Exception:
                    break

                if key == ord("q") or key == 27:  # 'q' 또는 ESC 키로 종료
                    break

            # 6. 로봇 제어 출력 (실제 구동부 연동 위치)
            # 결정된 명령을 로봇에 전송합니다 (실제 구현은 _send_robot_command 함수에서).
            _send_robot_command(cmd)

            # FPS 계산: 30프레임마다 FPS를 업데이트합니다.
            frame_count += 1
            if frame_count % 30 == 0:
                now = time.time()  # 현재 시간
                fps_display = 30 / max(now - fps_timer, 1e-6)  # FPS 계산 (30프레임에 걸린 시간으로)
                fps_timer   = now  # 타이머 리셋

            # 목표 FPS에 맞게 대기합니다 (프레임 속도 제어).
            elapsed = time.time() - t0  # 경과 시간 계산
            sleep_t = max(0.0, target_dt - elapsed)  # 필요한 대기 시간 계산
            time.sleep(sleep_t)  # 대기

    except KeyboardInterrupt:  # Ctrl+C로 인터럽트 시
        print("\n[Main] 사용자 종료 요청")

    finally:  # 루프 종료 후 정리 작업
        print("\n[Main] 시스템 정리 중...")
        try:
            lidar_proc.stop()  # LiDAR 프로세서 정지
        except Exception:
            pass
        if oak_proc:
            try:
                oak_proc.stop()  # OAK 프로세서 정지
            except Exception:
                pass
        try:
            cv2.destroyAllWindows()  # OpenCV 창 닫기
        except Exception:
            pass

        # 최종 통계 출력
        stats = avoidance.stats()  # 장애물 회피 통계 가져오기
        if stats:
            print("\n[통계]")
            print(f"  DANGER  비율: {stats['danger_ratio']*100:.1f}%")   # 위험 존 비율
            print(f"  WARNING 비율: {stats['warning_ratio']*100:.1f}%")  # 경고 존 비율
            print(f"  SAFE    비율: {stats['safe_ratio']*100:.1f}%")     # 안전 존 비율
            print(f"  평균 근접 거리: {stats['avg_nearest_m']:.2f}m")    # 평균 가장 가까운 장애물 거리
        print("[Main] 모든 시스템 종료 완료.")  # 완료 메시지
        os._exit(0)


# ── 디버그 창 구성 ────────────────────────────────────────────────
# 디버그를 위한 4분할 시각화 창을 구성하는 함수
def _show_debug_windows(
    oak_frame,  # OAK 카메라 프레임
    lidar_scan,  # LiDAR 스캔 데이터
    fusion: SensorFusion,  # 센서 융합 객체
    avoidance: ObstacleAvoidance,  # 장애물 회피 객체
    cmd,  # 결정된 명령
):
    """4분할 디버그 화면 구성"""
    # 각 패널의 목표 크기 설정
    TARGET_H = 400  # 높이
    TARGET_W = 400  # 너비

    # 패널 1: OAK 깊이맵 시각화
    if oak_frame is not None:
        from oak_processor import OakProcessor
        oak_vis = OakProcessor.__new__(OakProcessor)  # 임시 객체 생성 (시각화용)
        panel_oak = oak_vis.visualize(oak_frame)  # OAK 프레임 시각화
    else:
        # OAK가 없을 때 빈 패널 생성
        panel_oak = np.zeros((TARGET_H, TARGET_W, 3), np.uint8)
        cv2.putText(panel_oak, "OAK: N/A", (10, 40),  # "OAK: N/A" 텍스트 표시
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

    # 패널 2: LiDAR 스캔 시각화
    if lidar_scan is not None:
        from lidar_processor import LidarProcessor
        lidar_vis = LidarProcessor.__new__(LidarProcessor)  # 임시 객체 생성
        panel_lidar = lidar_vis.visualize(lidar_scan, size=TARGET_H)  # LiDAR 스캔 시각화
    else:
        # LiDAR 데이터가 없을 때 빈 패널
        panel_lidar = np.zeros((TARGET_H, TARGET_W, 3), np.uint8)

    # 패널 3: 융합 격자 시각화
    panel_grid = fusion.visualize_grid()  # 융합된 격자 맵 시각화

    # 패널 4: 명령 패널 시각화
    panel_cmd = avoidance.visualize_command(cmd, size=TARGET_H)  # 회피 명령 시각화

    # 모든 패널을 TARGET_H × TARGET_W 크기로 리사이즈
    panels = [panel_oak, panel_lidar, panel_grid, panel_cmd]
    resized = []
    for p in panels:
        r = cv2.resize(p, (TARGET_W, TARGET_H))  # 크기 조정
        resized.append(r)

    # 2×2 그리드로 배치 (상단: OAK, LiDAR / 하단: Fusion, Command)
    top    = np.hstack(resized[:2])  # 상단 행
    bottom = np.hstack(resized[2:])  # 하단 행
    combined = np.vstack([top, bottom])  # 전체 이미지 결합

    # 구분선 그리기
    cv2.line(combined, (TARGET_W, 0), (TARGET_W, TARGET_H * 2), (60, 60, 60), 1)  # 세로선
    cv2.line(combined, (0, TARGET_H), (TARGET_W * 2, TARGET_H), (60, 60, 60), 1)  # 가로선

    # 패널 제목 표시
    labels = ["OAK-D-Lite", "LiDAR", "Fusion Grid", "Command"]  # 제목 리스트
    positions = [  # 제목 위치 리스트
        (6, 16), (TARGET_W + 6, 16),
        (6, TARGET_H + 16), (TARGET_W + 6, TARGET_H + 16),
    ]
    for lbl, pos in zip(labels, positions):
        cv2.putText(combined, lbl, pos,  # 제목 텍스트 그리기
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # 결합된 이미지를 창에 표시
    cv2.imshow("Obstacle Avoidance - OAK + LiDAR Fusion", combined)


# ── 로봇 제어 출력 ────────────────────────────────────────────────
# 결정된 명령을 로봇 구동부에 전송하는 함수 (실제 구현 자리)
def _send_robot_command(cmd):
    """
    실제 로봇 구동부(ROS2, 시리얼 등)와 연동하는 자리.
    여기서는 예시로 아무것도 하지 않는다.

    ROS2 사용 예시:
        from geometry_msgs.msg import Twist
        twist = Twist()
        twist.linear.x  = cmd.linear_speed * MAX_LINEAR_SPEED
        twist.angular.z = cmd.angular_speed * MAX_ANGULAR_SPEED
        cmd_vel_pub.publish(twist)
    """
    # 실제 로봇 제어 코드를 여기에 추가 (현재는 pass로 아무 동작 안 함)
    pass


# ── 진입점 ────────────────────────────────────────────────────────
# 스크립트가 직접 실행될 때 메인 함수를 호출합니다.
if __name__ == "__main__":
    # 명령줄 인자 파서 생성
    parser = argparse.ArgumentParser(description="서빙 로봇 장애물 회피 시스템")
    parser.add_argument("--mock",   action="store_true", help="시뮬레이션 모드")  # 시뮬레이션 모드 옵션
    parser.add_argument("--no-vis", action="store_true", help="시각화 비활성화")  # 시각화 비활성화 옵션
    args = parser.parse_args()  # 인자 파싱

    # 메인 함수 호출 (시뮬레이션 모드와 시각화 설정 전달)
    main(use_mock=args.mock, visualize=not args.no_vis)
