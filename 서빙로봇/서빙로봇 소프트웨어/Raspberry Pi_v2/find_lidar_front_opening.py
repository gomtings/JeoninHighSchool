"""
find_lidar_front_opening.py
ㄷ자 트레이의 '열린 방향'을 찾아 LIDAR_ANGLE_OFFSET_DEG 를 결정한다.

원리:
  라이다가 ㄷ자 트레이 안에 들어앉아 있으면, 대부분의 방향은 트레이 벽(0.2~0.45m)에
  막혀 있고 오직 개방부만 멀리 내다볼 수 있다. 따라서 '멀리 보이는 각도 구간'을
  찾으면 그게 곧 로봇의 진짜 정면이다.

  손으로 짚거나 벽에 맞추는 방식과 달리 사람의 판단이 전혀 들어가지 않는다.
  로봇 구조 자체가 기준이 되므로 기준점을 잘못 잡을 여지가 없다.

사용법:
  1) 로봇을 적당히 트인 곳에 둔다 (개방부 앞쪽이 최소 1m 이상 뚫려 있으면 됨).
     벽에 맞출 필요도, 직각으로 세울 필요도 없다.
  2) 이 스크립트를 실행한다 (약 8초).
  3) 출력된 '보정된 오프셋' 값을 config.py 의 LIDAR_ANGLE_OFFSET_DEG 에 넣는다.
  4) 정밀도를 더 원하면, 그 다음 calibrate_lidar_front_by_wall.py 로 다듬는다.
     (이 스크립트는 개방부 중심을 찾는 것이라 보통 ±3도 수준, 벽 측정은 ±1도 수준)

  ★ 오프셋을 바꾼 뒤에는 calibrate_lidar_self_mask.py 를 반드시 다시 실행할 것.
"""

import math
import time

import numpy as np
from rplidar import RPLidar

import config

MEASURE_SEC = 8.0      # 수집 시간 (초)
BUCKET_DEG = 2.0       # 각도 구간 폭
OPEN_DIST_M = 1.0      # 이 거리보다 멀리 보이면 '뚫린 방향'으로 간주
MIN_SAMPLES = 3        # 구간별 최소 샘플 수 (이보다 적으면 판정 보류)


def wrap180(a: float) -> float:
    a = a % 360.0
    return a - 360.0 if a > 180.0 else a


def main():
    n = int(round(360.0 / BUCKET_DEG))
    dists = [[] for _ in range(n)]

    lidar = RPLidar(config.LIDAR_PORT, baudrate=115200, timeout=3)
    lidar.connect()
    print(f"연결 완료: {lidar.get_info()}")
    print(f"현재 LIDAR_ANGLE_OFFSET_DEG = {config.LIDAR_ANGLE_OFFSET_DEG}")
    print(f"\n{MEASURE_SEC:.0f}초간 수집합니다. 로봇을 건드리지 마세요.\n")

    t0 = time.time()
    try:
        for scan in lidar.iter_scans(max_buf_meas=500):
            if time.time() - t0 > MEASURE_SEC:
                break
            for quality, angle_raw, dist_mm in scan:
                if quality == 0 or dist_mm == 0:
                    continue
                d = dist_mm / 1000.0
                if d < config.LIDAR_MIN_RANGE_M or d > config.LIDAR_MAX_RANGE_M:
                    continue
                # 현재 오프셋을 적용한 각도 (지금 코드가 보는 것과 같은 좌표계)
                a = (float(angle_raw) + config.LIDAR_ANGLE_OFFSET_DEG) % 360.0
                dists[int(a / BUCKET_DEG) % n].append(d)
    except KeyboardInterrupt:
        print("중단됨 - 지금까지 모은 데이터로 분석합니다.")
    finally:
        lidar.stop()
        lidar.disconnect()

    med = np.full(n, np.nan)
    for i, v in enumerate(dists):
        if len(v) >= MIN_SAMPLES:
            med[i] = float(np.median(v))

    valid = ~np.isnan(med)
    if valid.sum() < n * 0.3:
        print("데이터가 부족합니다. 라이다가 제대로 도는지 확인 후 다시 실행하세요.")
        return

    # ── 각도별 거리 프로파일 출력 (10도 단위로 요약) ──
    print("=" * 66)
    print("각도별 관측 거리 (현재 오프셋 기준, 0도 = 지금의 '정면')")
    print("=" * 66)
    step = int(round(10.0 / BUCKET_DEG))
    for start in range(0, n, step):
        chunk = med[start:start + step]
        chunk = chunk[~np.isnan(chunk)]
        if len(chunk) == 0:
            continue
        m = float(np.median(chunk))
        ang = wrap180(start * BUCKET_DEG)
        bar = "#" * min(40, int(m * 8))
        mark = "  <= 뚫림" if m > OPEN_DIST_M else ""
        print(f"  {ang:>+5.0f}도  {m:5.2f}m  {bar}{mark}")

    # ── 가장 넓게 뚫린 연속 구간 찾기 (360도 wrap 처리) ──
    is_open = valid & (med > OPEN_DIST_M)
    if not is_open.any():
        print("\n뚫린 방향을 찾지 못했습니다.")
        print(f"모든 방향이 {OPEN_DIST_M}m 안에서 막혀 있습니다. 로봇을 더 트인 곳으로 옮기거나,")
        print("OPEN_DIST_M 을 낮춰서 다시 시도하세요.")
        return

    doubled = np.concatenate([is_open, is_open])   # wrap-around 를 위해 두 바퀴로 이어붙임
    best_len = best_start = 0
    cur_len = 0
    for i, v in enumerate(doubled):
        if v:
            cur_len += 1
            if cur_len > best_len:
                best_len, best_start = cur_len, i - cur_len + 1
        else:
            cur_len = 0
    best_len = min(best_len, n)   # 전방향이 뚫린 경우 방어

    center_idx = (best_start + best_len / 2.0 - 0.5) % n
    center_deg = wrap180(center_idx * BUCKET_DEG)
    width_deg = best_len * BUCKET_DEG
    corrected = wrap180(config.LIDAR_ANGLE_OFFSET_DEG - center_deg)

    print("\n" + "=" * 66)
    print(f"개방부 중심   : {center_deg:+.1f}도  (폭 약 {width_deg:.0f}도)")
    print(f"현재 오프셋   : {config.LIDAR_ANGLE_OFFSET_DEG}도")
    print("-" * 66)
    print(f"보정된 오프셋 : {corrected:.1f}도")
    print("=" * 66)

    if width_deg > 200:
        print("[주의] 뚫린 구간이 200도를 넘습니다. 트레이에 둘러싸인 상태가 아닌 것 같습니다.")
        print("       이 방법은 라이다가 ㄷ자 구조 안에 있을 때만 의미가 있습니다.")
    elif abs(center_deg) < 3.0:
        print("현재 오프셋이 이미 개방부를 정면으로 보고 있습니다.")
    else:
        print(f"config.py 의 LIDAR_ANGLE_OFFSET_DEG 를 {corrected:.1f} 로 바꾸세요.")
        print("★ 그 뒤 calibrate_lidar_self_mask.py 를 반드시 다시 실행하세요.")


if __name__ == "__main__":
    main()
