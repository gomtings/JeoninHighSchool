"""
calibrate_lidar_front_by_wall.py
평평한 벽을 기준자로 써서 LIDAR_ANGLE_OFFSET_DEG(정면 0도)를 정밀 측정

왜 벽인가:
  손으로 "여기가 정면" 하고 짚는 방식은 점 하나가 기준이라, 0.4m 거리에서 손이
  5cm만 벗어나도 7도 오차가 난다. 벽은 라이다 점이 수백 개 찍히고 그 점들이
  직선을 이루므로, 직선을 맞춰(RANSAC + PCA) 법선을 구하면 개별 점 노이즈가
  상쇄되어 훨씬 정확하다. 로봇을 벽과 직각으로 세우는 것도 로봇의 평평한 앞면을
  쓰면 손보다 정확하게 할 수 있다.

준비 (이 단계가 정확도를 좌우한다):
  1) 평평하고 넓은 벽을 고른다 (걸레받이/몰딩/가구가 없는 깨끗한 면).
  2) 로봇 앞면(ㄷ자 트레이가 열린 쪽)을 벽에 딱 붙인다. 밀착되는 순간 물리적으로
     직각이 보장된다.
  3) 로봇을 '회전시키지 말고' 그대로 뒤로 1~1.5m 밀어낸다.
     (또는 줄자로 로봇 앞쪽 좌우 모서리에서 벽까지 거리를 재서 같게 맞춘다.
      50cm 폭 기준 좌우 차이 5mm 이내면 각도 오차 0.6도 수준)
  4) 이 스크립트를 실행한다.

결과 해석:
  로봇이 벽과 정확히 직각이라면 '벽 법선'이 0.0도로 나와야 한다.
  0이 아니면 그 값이 곧 남아있는 오프셋 오차이며, 스크립트가 보정된
  LIDAR_ANGLE_OFFSET_DEG 값을 직접 계산해서 알려준다.
"""

import math
import time

import cv2
import numpy as np
from rplidar import RPLidar

import config
from lidar_processor import load_self_mask, self_exclusion_threshold

MEASURE_SEC = 8.0        # 측정 수집 시간 (초)
SEARCH_HALF_DEG = 60.0   # 현재 정면 기준 이 각도 안에서만 벽을 찾는다 (옆벽 오인 방지)
WALL_MIN_DIST_M = 0.5    # 이보다 가까운 점은 벽 후보에서 제외 (트레이 구조물 배제)
WALL_MAX_DIST_M = 4.0    # 이보다 먼 점은 제외 (노이즈/다른 방)
RANSAC_ITERS = 200
RANSAC_TOL_M = 0.02      # 직선에서 2cm 이내면 벽 위의 점으로 인정
MIN_INLIERS = 25         # 이보다 적으면 신뢰할 수 없는 측정으로 간주

SELF_MASK = load_self_mask()
SELF_FALLBACK_M = config.LIDAR_SELF_EXCLUSION_M
OFFSET = config.LIDAR_ANGLE_OFFSET_DEG


def normalize(angle: float, offset: float) -> float:
    angle = (angle + offset) % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle


def wrap180(angle: float) -> float:
    angle = angle % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle


def fit_wall(pts: np.ndarray):
    """
    RANSAC 으로 지배적인 직선(벽)을 찾고 PCA 로 다듬는다.
    반환: (법선각도[도], 인라이어 마스크, RMS잔차[m], 벽까지거리[m]) 또는 None
    """
    n = len(pts)
    if n < MIN_INLIERS:
        return None

    rng = np.random.default_rng(0)
    best_inliers = None
    best_count = 0

    for _ in range(RANSAC_ITERS):
        i, j = rng.choice(n, size=2, replace=False)
        p1, p2 = pts[i], pts[j]
        v = p2 - p1
        norm = np.hypot(v[0], v[1])
        if norm < 0.10:          # 너무 가까운 두 점은 방향이 불안정
            continue
        v = v / norm
        # 점-직선 수직거리 = |v × (p - p1)|
        d = np.abs(v[0] * (pts[:, 1] - p1[1]) - v[1] * (pts[:, 0] - p1[0]))
        inliers = d < RANSAC_TOL_M
        cnt = int(inliers.sum())
        if cnt > best_count:
            best_count = cnt
            best_inliers = inliers

    if best_inliers is None or best_count < MIN_INLIERS:
        return None

    # PCA 로 정밀화 (전최소자승 - 수직선/수평선 모두 안전)
    wall = pts[best_inliers]
    centroid = wall.mean(axis=0)
    centered = wall - centroid
    cov = centered.T @ centered
    eigvals, eigvecs = np.linalg.eigh(cov)
    direction = eigvecs[:, np.argmax(eigvals)]      # 벽이 뻗은 방향
    normal = np.array([-direction[1], direction[0]])  # 그에 수직 = 법선

    # 법선이 로봇 -> 벽 쪽을 향하도록 부호 정리
    if np.dot(normal, centroid) < 0:
        normal = -normal

    resid = np.abs(centered @ normal)
    rms = float(np.sqrt((resid ** 2).mean()))

    # x = d*sin(θ), y = d*cos(θ) 규약이므로 θ = atan2(x, y)
    normal_deg = math.degrees(math.atan2(normal[0], normal[1]))
    wall_dist = float(abs(np.dot(centroid, normal)))
    return wrap180(normal_deg), best_inliers, rms, wall_dist


def main():
    lidar = RPLidar(config.LIDAR_PORT, baudrate=115200, timeout=3)
    lidar.connect()
    print(f"연결 완료: {lidar.get_info()}")
    print(f"현재 LIDAR_ANGLE_OFFSET_DEG = {OFFSET}")
    print(f"자체반사 필터: {'각도별 프로파일' if SELF_MASK else f'균일 {SELF_FALLBACK_M:.2f}m (미캘리브레이션)'}")
    print(f"\n{MEASURE_SEC:.0f}초간 측정합니다. 로봇을 벽과 직각으로 세워두고 건드리지 마세요.")
    print("(창에서 q 를 누르면 조기 종료)\n")

    SIZE = 560
    cx, cy = SIZE // 2, int(SIZE * 0.72)
    scale = SIZE / 2 / 3.0  # 3m 범위

    normals = []
    stats = []          # 스캔별 단계 통과 개수 (실패 원인 진단용)
    front_dists = []    # 정면 방향에서 실제로 보인 거리들
    best_cand = 0       # 한 스캔에서 나온 최대 후보점 수
    t0 = time.time()

    try:
        for scan in lidar.iter_scans(max_buf_meas=500):
            if time.time() - t0 > MEASURE_SEC:
                break

            canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
            for d in (1, 2, 3):
                cv2.circle(canvas, (cx, cy), int(d * scale), (40, 40, 40), 1)
            cv2.line(canvas, (cx, cy), (cx, cy - int(2.8 * scale)), (0, 200, 0), 2)
            cv2.putText(canvas, "FRONT(0deg)", (cx + 6, cy - int(2.4 * scale)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 0), 1)

            # [진단] 단계별로 점이 몇 개씩 살아남는지 세어, 실패 시 어느 필터가
            # 원인인지 바로 알 수 있게 한다.
            st = dict(raw=0, quality=0, range=0, self_excl=0, window=0, band=0)
            near_front = []   # 정면 ±SEARCH_HALF_DEG 안의 거리들 (거리 조건 진단용)

            candidates = []
            for quality, angle_raw, dist_mm in scan:
                st['raw'] += 1
                if quality == 0 or dist_mm == 0:
                    continue
                st['quality'] += 1
                angle = normalize(float(angle_raw), OFFSET)
                dist_m = dist_mm / 1000.0
                if dist_m < config.LIDAR_MIN_RANGE_M:
                    continue
                st['range'] += 1
                # 실전 파이프라인과 동일한 자체반사 제외
                if dist_m < self_exclusion_threshold(angle, SELF_MASK, SELF_FALLBACK_M):
                    continue
                st['self_excl'] += 1

                rad = math.radians(angle)
                x, y = dist_m * math.sin(rad), dist_m * math.cos(rad)
                px = int(cx + x * scale)
                py = int(cy - y * scale)
                cv2.circle(canvas, (px, py), 2, (90, 90, 90), -1)

                if abs(angle) <= SEARCH_HALF_DEG:
                    st['window'] += 1
                    near_front.append(dist_m)
                    if WALL_MIN_DIST_M <= dist_m <= WALL_MAX_DIST_M:
                        st['band'] += 1
                        candidates.append((x, y))

            stats.append(st)
            if near_front:
                front_dists.extend(near_front)

            result = fit_wall(np.array(candidates)) if len(candidates) >= MIN_INLIERS else None
            best_cand = max(best_cand, len(candidates))

            if result is not None:
                normal_deg, inliers, rms, wall_dist = result
                normals.append(normal_deg)
                pts = np.array(candidates)[inliers]
                for x, y in pts:
                    cv2.circle(canvas, (int(cx + x * scale), int(cy - y * scale)),
                               2, (0, 255, 255), -1)
                nrad = math.radians(normal_deg)
                cv2.arrowedLine(
                    canvas, (cx, cy),
                    (int(cx + wall_dist * math.sin(nrad) * scale),
                     int(cy - wall_dist * math.cos(nrad) * scale)),
                    (0, 165, 255), 2, tipLength=0.06)
                status = (f"wall normal: {normal_deg:+.2f}deg  dist {wall_dist:.2f}m  "
                          f"pts {int(inliers.sum())}  rms {rms*1000:.0f}mm")
            else:
                status = (f"wall NOT found - candidates {len(candidates)} "
                          f"(need {MIN_INLIERS}), in-window {st['window']}")

            cv2.putText(canvas, status, (10, 26), cv2.FONT_HERSHEY_SIMPLEX,
                        0.46, (255, 255, 100), 1)
            cv2.putText(canvas, f"samples: {len(normals)}   offset now: {OFFSET}deg",
                        (10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1)
            cv2.putText(canvas, "Yellow = wall inliers   Orange arrow = wall normal",
                        (10, SIZE - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

            win = "Wall Front Calibration (q=quit)"
            cv2.imshow(win, canvas)
            if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                break
            if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                break
    except KeyboardInterrupt:
        pass
    finally:
        lidar.stop()
        lidar.disconnect()
        cv2.destroyAllWindows()

    print("=" * 62)
    if len(normals) < 3:
        print("측정 실패: 벽을 충분히 잡지 못했습니다.\n")

        if not stats:
            print("라이다에서 스캔을 한 번도 받지 못했습니다.")
            print(f"- 포트({config.LIDAR_PORT})가 맞는지, 다른 프로그램이 점유 중이 아닌지 확인하세요.")
            return

        # 단계별 평균 통과 개수 -> 어느 필터에서 걸렸는지 한눈에 보인다
        keys = [("raw", "스캔 원본"), ("quality", "품질 통과"),
                ("range", f"거리 > {config.LIDAR_MIN_RANGE_M}m"),
                ("self_excl", "자체반사 제외 후"),
                ("window", f"정면 ±{SEARCH_HALF_DEG:.0f}도 안"),
                ("band", f"거리 {WALL_MIN_DIST_M}~{WALL_MAX_DIST_M}m 안 (= 벽 후보)")]
        print(f"[단계별 통과 점 개수] 스캔 {len(stats)}회 평균")
        for k, label in keys:
            avg = sum(s[k] for s in stats) / len(stats)
            print(f"  {label:<32} {avg:7.1f}개")
        print(f"  한 스캔 최대 후보점 수           {best_cand:7d}개  (필요: {MIN_INLIERS}개 이상)")

        print("\n[원인 추정]")
        avg_window = sum(s["window"] for s in stats) / len(stats)
        avg_band = sum(s["band"] for s in stats) / len(stats)
        if avg_window < MIN_INLIERS:
            print(f"  정면 ±{SEARCH_HALF_DEG:.0f}도 방향에 점 자체가 거의 없습니다.")
            print("  -> 지금 오프셋이 가리키는 '정면'이 실제 벽 쪽이 아닐 가능성이 큽니다.")
            print("     SEARCH_HALF_DEG 를 180 으로 올려서 전방향을 훑어보세요.")
        elif avg_band < MIN_INLIERS:
            if front_dists:
                arr = np.array(front_dists)
                print(f"  정면 방향에 점은 있는데({avg_window:.0f}개) 거리 조건에서 걸렸습니다.")
                print(f"  실제 관측 거리: 최소 {arr.min():.2f}m / 중앙값 {np.median(arr):.2f}m / 최대 {arr.max():.2f}m")
                if np.median(arr) < WALL_MIN_DIST_M:
                    print(f"  -> 벽이 너무 가깝습니다. 로봇을 뒤로 더 물리거나 WALL_MIN_DIST_M 을 낮추세요.")
                elif np.median(arr) > WALL_MAX_DIST_M:
                    print(f"  -> 벽이 너무 멉니다. 로봇을 벽 쪽으로 당기거나 WALL_MAX_DIST_M 을 올리세요.")
        else:
            print(f"  후보점은 충분한데({avg_band:.0f}개) 직선을 못 찾았습니다.")
            print("  -> 벽이 평평하지 않거나(굴곡/가구), 잡음이 큽니다.")
            print(f"     RANSAC_TOL_M({RANSAC_TOL_M}m)을 0.04 정도로 올려보세요.")
        return

    arr = np.array(normals)
    mean, std = float(arr.mean()), float(arr.std())
    corrected = wrap180(OFFSET - mean)

    print(f"측정 횟수      : {len(arr)}회")
    print(f"벽 법선 각도   : {mean:+.2f}도 (표준편차 {std:.2f}도)")
    print(f"현재 오프셋    : {OFFSET}도")
    print("-" * 62)
    print(f"보정된 오프셋  : {corrected:.1f}도")
    print("=" * 62)

    if std > 1.0:
        print(f"[주의] 산포가 큽니다({std:.2f}도). 벽이 평평한지, 로봇이 흔들리지 않았는지 확인 후 재측정하세요.")
    if abs(mean) < 0.5:
        print("현재 오프셋이 이미 정확합니다. 수정할 필요 없습니다.")
    else:
        print(f"config.py 의 LIDAR_ANGLE_OFFSET_DEG 를 {corrected:.1f} 로 바꾸세요.")
        print("★ 오프셋을 바꾸면 lidar_self_mask.json 이 무효가 되므로")
        print("  calibrate_lidar_self_mask.py 를 반드시 다시 실행하세요.")


if __name__ == "__main__":
    main()
