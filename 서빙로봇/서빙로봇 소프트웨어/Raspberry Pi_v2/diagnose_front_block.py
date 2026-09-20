"""
diagnose_front_block.py
"앞에 아무것도 없는데 전방 장애물로 뜬다" 의 원인을 가려내는 진단 스크립트

무엇을 보는가:
  전방 차단 판정은 결국 path_recommender._measure_clearance_with_footprint() 안의
  "11x11 셀 풋프린트 안에 grid >= 0.6 인 셀이 3개 이상인가" 한 줄에서 결정된다.
  그 3개가 대체 '무엇'인지를 극좌표(각도/거리)로 되짚어 주면 원인이 바로 갈린다.

    - 차단 셀이 0.25~0.40m 링에 몰려 있다  -> 로봇 자체반사 (트레이 칸막이)
        ROBOT_HALF_M=0.25 이므로 풋프린트 모서리가 정확히 0.354m 에 걸린다.
        균일 반경 폴백(LIDAR_SELF_EXCLUSION_M=0.30)은 ㄷ자 뒤쪽 모서리 0.354m 를
        못 막으므로, 그 사이 구간이 매 스캔 장애물로 등록된다.
        -> calibrate_lidar_self_mask.py 로 lidar_self_mask.json 생성이 해답.

    - 차단 셀이 훨씬 멀리 있거나 뒤쪽 방향에서 온다 -> 각도 오프셋 오류
        LIDAR_ANGLE_OFFSET_DEG 가 틀리면 180도 FOV 필터가 엉뚱한 반원을 정면으로
        잡아 뒤쪽 벽이 전방 장애물이 된다.
        -> find_lidar_front_opening.py 로 재측정이 해답.

사용법:
  로봇을 정면 2m 이상 트인 곳에 세우고 (증상이 나오는 그 상태 그대로),
      python diagnose_front_block.py
  약 10초간 수집 후 판정 결과를 출력한다. 하드웨어만 있으면 되고 아무것도 바꾸지 않는다.
"""

import math
import time
from collections import defaultdict

import numpy as np
from rplidar import RPLidar

import config
from lidar_processor import LidarPoint, LidarScan, load_self_mask, self_exclusion_threshold
from mapper import OccupancyMap


COLLECT_SEC = 10.0
ROBOT_HALF_M = 0.25      # path_recommender.PathRecommender.ROBOT_HALF_M 와 동일해야 함
CELL_THRESHOLD = 0.6     # path_recommender.PathRecommender.CELL_THRESHOLD 와 동일해야 함
MAX_RANGE_M = 3.0        # path_recommender.PathRecommender.MAX_RANGE_M 와 동일해야 함
NEAR_FIELD_M = 0.60      # 자체반사 의심 구간으로 따로 집계할 거리


def normalize_angle(angle: float) -> float:
    """lidar_processor.normalize_angle 과 동일"""
    angle = (angle + getattr(config, "LIDAR_ANGLE_OFFSET_DEG", 0.0)) % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle


def measure_front_clearance(occ_map, half_cells):
    """
    path_recommender._measure_clearance_with_footprint(0.0) 을 그대로 재현하되,
    막힌 지점에서 '어떤 셀이 막았는지'까지 같이 돌려준다. (헤딩 0도 기준)
    """
    grid = occ_map.grid
    height, width = grid.shape
    clearance = 0.0
    dist = 0.05

    while dist <= MAX_RANGE_M:
        row_c, col_c = occ_map.world_to_cell(0.0, dist)  # 정면(0도): x=0, y=dist
        if not (0 <= row_c < height and 0 <= col_c < width):
            return clearance, None, []

        r0, r1 = row_c - half_cells, row_c + half_cells + 1
        c0, c1 = col_c - half_cells, col_c + half_cells + 1

        if r0 < 0 or c0 < 0 or r1 > height or c1 > width:
            return clearance, dist, []  # 맵 경계 = 충돌 취급

        window = grid[r0:r1, c0:c1]
        hits = np.argwhere(window >= CELL_THRESHOLD)
        if len(hits) >= 3:
            blockers = []
            for dr, dc in hits:
                r, c = r0 + int(dr), c0 + int(dc)
                x_m, y_m = occ_map.cell_to_world(r, c)
                blockers.append((
                    math.degrees(math.atan2(x_m, y_m)),   # 로봇 기준 방위각
                    math.hypot(x_m, y_m),                 # 로봇 기준 거리
                    float(grid[r, c]),
                ))
            blockers.sort(key=lambda b: b[1])
            return clearance, dist, blockers

        clearance = dist
        dist += occ_map.resolution

    return clearance, None, []


def main():
    self_mask = load_self_mask()
    print("=" * 72)
    print(" 전방 오검출 진단")
    print("=" * 72)
    print(f"  LIDAR_ANGLE_OFFSET_DEG  = {getattr(config, 'LIDAR_ANGLE_OFFSET_DEG', 0.0)}")
    print(f"  LIDAR_FOV_DEG           = {getattr(config, 'LIDAR_FOV_DEG', 360.0)}")
    print(f"  LIDAR_SELF_EXCLUSION_M  = {config.LIDAR_SELF_EXCLUSION_M}  (균일 폴백)")
    print(f"  자체반사 프로파일        = {'로드됨 (각도별)' if self_mask else '없음 -> 균일 폴백 사용'}")
    print(f"  풋프린트 모서리 거리     = {ROBOT_HALF_M * math.sqrt(2.0):.3f} m  "
          f"(이 안쪽 반사는 전부 전방 차단 요인)")
    print("=" * 72)

    half_fov = getattr(config, "LIDAR_FOV_DEG", 360.0) / 2.0
    half_cells = int(math.ceil(ROBOT_HALF_M / config.FUSION_GRID_RESOLUTION))

    occ_map = OccupancyMap()
    occ_map.set_robot_pose(0.0, 0.0, 0.0)

    n_raw = n_fov_cut = n_range_cut = n_self_cut = n_kept = 0
    near_by_bucket = defaultdict(list)   # 10도 버킷 -> 최종 통과한 근거리 점들
    cut_by_bucket = defaultdict(list)    # 10도 버킷 -> 자체반사로 잘린 점들
    n_scans = 0

    lidar = RPLidar(config.LIDAR_PORT, baudrate=config.LIDAR_BAUDRATE, timeout=3)
    try:
        lidar.connect()
        print(f"[LiDAR] 연결: {config.LIDAR_PORT} - {COLLECT_SEC:.0f}초 수집 시작 "
              f"(로봇을 움직이지 마세요)\n")
        t_end = time.time() + COLLECT_SEC

        for scan_raw in lidar.iter_scans(max_buf_meas=500):
            points = []
            for quality, angle_raw, dist_mm in scan_raw:
                if quality == 0:
                    continue
                n_raw += 1
                angle = normalize_angle(float(angle_raw))
                dist_m = float(dist_mm) / 1000.0

                if abs(angle) > half_fov:
                    n_fov_cut += 1
                    continue
                if dist_m < config.LIDAR_MIN_RANGE_M or dist_m > config.LIDAR_MAX_RANGE_M:
                    n_range_cut += 1
                    continue

                threshold = self_exclusion_threshold(angle, self_mask, config.LIDAR_SELF_EXCLUSION_M)
                bucket = int(math.floor(angle / 10.0)) * 10
                if dist_m < threshold:
                    n_self_cut += 1
                    cut_by_bucket[bucket].append(dist_m)
                    continue

                n_kept += 1
                if dist_m < NEAR_FIELD_M:
                    near_by_bucket[bucket].append(dist_m)
                points.append(LidarPoint(angle_deg=angle, distance_m=dist_m, is_blind_zone=False))

            if points:
                n_scans += 1
                occ_map.prepare_frame()
                occ_map.set_robot_pose(0.0, 0.0, 0.0)
                occ_map.update_from_lidar(
                    LidarScan(points=points, blind_zone_points=[], timestamp=time.time())
                )

            if time.time() >= t_end:
                break
    finally:
        try:
            lidar.stop()
            lidar.disconnect()
        except Exception:
            pass

    # ── [1] 필터 통계 ────────────────────────────────────────────────
    print("[1] 포인트 필터 통계")
    print(f"    원시 {n_raw}  ->  FOV컷 {n_fov_cut} / 거리컷 {n_range_cut} / "
          f"자체반사컷 {n_self_cut}  ->  최종 {n_kept}   (스캔 {n_scans}회)")

    # ── [2] 근거리 생존 포인트 (자체반사 의심) ───────────────────────
    print(f"\n[2] 자체반사 필터를 '통과한' 근거리(<{NEAR_FIELD_M}m) 포인트")
    if not near_by_bucket:
        print("    없음 -> 자체반사는 깨끗하게 걸러지고 있습니다.")
    else:
        print("    각도버킷 |  개수 | 최소   | 중앙값 | 적용임계 | 판정")
        for bucket in sorted(near_by_bucket):
            ds = sorted(near_by_bucket[bucket])
            thr = self_exclusion_threshold(bucket + 5.0, self_mask, config.LIDAR_SELF_EXCLUSION_M)
            med = ds[len(ds) // 2]
            verdict = "★자체반사 의심" if med < ROBOT_HALF_M * math.sqrt(2.0) else "실제 물체로 보임"
            print(f"    {bucket:+4d}~{bucket+10:+4d} | {len(ds):5d} | {ds[0]:.3f} | "
                  f"{med:.3f} | {thr:.3f}   | {verdict}")

    # ── [3] 전방 클리어런스 재현 ─────────────────────────────────────
    clearance, block_dist, blockers = measure_front_clearance(occ_map, half_cells)
    print(f"\n[3] 전방(0도) 클리어런스 재현: {clearance:.2f} m   "
          f"(FRONT_STOP_DIST_M = {config.ZONE_DANGER_M} m)")
    if clearance < config.ZONE_DANGER_M:
        print("    => 전방 장애물로 판정되는 상태입니다. 차단한 셀은 다음과 같습니다:")
        for ang, d, val in blockers[:12]:
            print(f"       방위 {ang:+7.1f}도   거리 {d:.3f} m   grid={val:.2f}")
    else:
        print("    => 이 시점에는 전방이 트여 있습니다. (증상 재현 안 됨)")

    # ── [4] 판정 ─────────────────────────────────────────────────────
    print("\n[4] 판정")
    ring = [b for b in blockers if 0.20 <= b[1] <= 0.40]
    if blockers and len(ring) >= max(3, len(blockers) * 0.5):
        print("    ★ 자체반사(트레이 칸막이)가 원인입니다.")
        print("      차단 셀이 로봇 반경(0.25~0.354m) 링에 몰려 있습니다.")
        print("      -> calibrate_lidar_self_mask.py 를 실행해 lidar_self_mask.json 을 만드세요.")
        print(f"      -> 임시 대응: config.LIDAR_SELF_EXCLUSION_M 을 "
              f"{config.LIDAR_SELF_EXCLUSION_M} -> 0.40 으로 상향")
    elif blockers:
        print("    ★ 자체반사 링이 아닙니다. 각도 오프셋 오류일 가능성이 큽니다.")
        print("      (뒤쪽 벽이 전방으로 접혀 들어오는 경우 이렇게 나옵니다)")
        print("      -> find_lidar_front_opening.py 로 LIDAR_ANGLE_OFFSET_DEG 를 재측정하세요.")
        print("      -> 참고: config.py 주석의 실측값은 172.9도인데 현재 설정은 "
              f"{getattr(config, 'LIDAR_ANGLE_OFFSET_DEG', 0.0)}도 입니다.")
    else:
        print("    이번 수집에서는 전방 차단이 재현되지 않았습니다.")
        print("    증상이 나타나는 상태에서 다시 실행해 주세요.")
    print()


if __name__ == "__main__":
    main()
