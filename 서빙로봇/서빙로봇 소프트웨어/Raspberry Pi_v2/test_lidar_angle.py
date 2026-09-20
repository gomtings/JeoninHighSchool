"""
test_lidar_angle.py
LiDAR 각도 기준 확인용 테스트

실행 후 로봇 정면에 손을 가져다 대고
콘솔에서 가장 가까운 포인트의 각도를 확인하세요.

정면 = 0도 가 되어야 정상.
만약 다른 각도가 나오면 config.py의
LIDAR_ANGLE_OFFSET_DEG 를 조정하세요.

예시:
  정면에 손 댔는데 180도 → LIDAR_ANGLE_OFFSET_DEG = 180
  정면에 손 댔는데 90도  → LIDAR_ANGLE_OFFSET_DEG = -90
  정면에 손 댔는데 -90도 → LIDAR_ANGLE_OFFSET_DEG = 90
"""

import time
import math
import cv2
import numpy as np
from rplidar import RPLidar
import config
from lidar_processor import load_self_mask, self_exclusion_threshold

PORT      = config.LIDAR_PORT
OFFSET    = config.LIDAR_ANGLE_OFFSET_DEG  # config.py 값을 그대로 사용 (두 곳이 어긋나지 않도록)
SELF_MASK = load_self_mask()  # 각도별 캘리브레이션 프로파일. 없으면 균일 반경으로 자동 폴백
SELF_FALLBACK_M = config.LIDAR_SELF_EXCLUSION_M

def normalize(angle, offset):
    angle = (angle + offset) % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle

lidar = RPLidar(PORT, baudrate=115200, timeout=3)
lidar.connect()
print(f"연결 완료: {lidar.get_info()}")
print("로봇 정면에 손을 가져다 대세요. Ctrl+C 로 종료.")

SIZE = 500
cx, cy = SIZE // 2, SIZE // 2
scale = SIZE / 2 / 5.0  # 5m 범위

try:
    for scan in lidar.iter_scans(max_buf_meas=500):
        canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

        # 거리 눈금
        for d in [1, 2, 3]:
            cv2.circle(canvas, (cx, cy), int(d * scale), (40, 40, 40), 1)
            cv2.putText(canvas, f"{d}m", (cx + int(d*scale) + 2, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80,80,80), 1)

        # 정면 방향 표시
        cv2.line(canvas, (cx, cy), (cx, cy - int(3*scale)), (0, 200, 0), 2)
        cv2.putText(canvas, "FRONT(0deg)", (cx+5, cy - int(2.5*scale)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,200,0), 1)

        min_dist = 99.0
        min_angle = 0.0
        points_info = []

        for quality, angle_raw, dist_mm in scan:
            if quality == 0 or dist_mm == 0:
                continue
            angle  = normalize(float(angle_raw), OFFSET)
            dist_m = dist_mm / 1000.0
            if dist_m > 5.0:
                continue

            rad = math.radians(angle)
            px  = int(cx + dist_m * math.sin(rad) * scale)
            py  = int(cy - dist_m * math.cos(rad) * scale)

            # [자체반사 제외] lidar_processor.py 실전 필터와 동일하게 적용
            # (각도별 캘리브레이션 프로파일이 있으면 그것을, 없으면 균일 반경).
            # 회색으로 표시만 하고 최근접/정상 색상 판정에서는 뺀다 (필터가
            # 자체반사 구간을 실제로 걷어내는지 육안 확인용).
            threshold = self_exclusion_threshold(angle, SELF_MASK, SELF_FALLBACK_M)
            if dist_m < threshold:
                cv2.circle(canvas, (px, py), 2, (70, 70, 70), -1)
                continue

            # 가장 가까운 포인트 추적
            if dist_m < min_dist:
                min_dist  = dist_m
                min_angle = angle

            color = (0, 255, 100) if abs(angle) < 30 else (100, 100, 255)
            cv2.circle(canvas, (px, py), 3, color, -1)

        # 로봇
        cv2.circle(canvas, (cx, cy), 8, (255, 220, 50), -1)

        # 가장 가까운 포인트 정보
        cv2.putText(canvas,
                    f"Nearest: {min_dist:.2f}m  angle: {min_angle:+.1f}deg",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,100), 1)
        # cv2.putText 는 한글을 못 그린다 (Hershey 폰트는 ASCII 전용) -> 반드시 영문으로
        mask_tag = "per-angle profile" if SELF_MASK is not None else f"uniform {SELF_FALLBACK_M:.2f}m (NOT CALIBRATED)"
        cv2.putText(canvas,
                    f"Offset: {OFFSET}deg  SelfExcl: {mask_tag}",
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180,180,180), 1)
        cv2.putText(canvas,
                    "Green = front +-30deg  Blue = other  Gray = self-reflection (excluded)",
                    (10, SIZE-15), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150,150,150), 1)

        win_title = "LiDAR Angle Test (q=quit)"
        cv2.imshow(win_title, canvas)
        if cv2.getWindowProperty(win_title, cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
            break

except KeyboardInterrupt:
    pass
finally:
    lidar.stop()
    lidar.disconnect()
    cv2.destroyAllWindows()
    print("종료")
