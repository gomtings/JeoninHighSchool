"""
calibrate_lidar_self_mask.py
로봇 자체반사(몸체/트레이 칸막이) 각도별 프로파일 캘리브레이션

배경:
  라이다가 완전히 트인 곳이 아니라 트레이 칸막이(좌/후면 벽 + 위 선반, 앞만
  개방된 ㄷ자 구조) 안에 놓여 있으면, 그 벽들이 매 스캔 근접 장애물로 잡힌다.
  이 구조는 원형이 아니므로 균일 반경(config.LIDAR_SELF_EXCLUSION_M) 하나로는
  가까운 방향(옆벽)에 맞추면 먼 방향이 새고, 먼 방향에 맞추면 진짜 정면 장애물
  감지 거리를 깎아먹는다. 이 스크립트는 각도 구간마다 "이 방향에서는 몇 m
  안쪽이 로봇 자기 자신인지"를 실측해 lidar_self_mask.json 으로 저장한다.

사용법:
  1) 로봇을 사방 2m 이상 트인 공간에 정지 상태로 둔다 (사람/벽/물체 없이).
     라이다 자체가 초당 약 5.5회 스스로 회전하므로, 로봇을 돌릴 필요 없이
     한 자리에 가만히 있어도 전 방향이 수집된다.
  2) 이 스크립트를 실행하고 CALIBRATE_SEC 동안 기다린다.
  3) 완료되면 lidar_self_mask.json 이 저장된다. 이후 main_mapping.py/main.py 는
     자동으로 이 파일을 읽어 각도별 자체반사 임계값으로 쓴다 (없으면
     LIDAR_SELF_EXCLUSION_M 균일 반경으로 자동 폴백하므로 이 스크립트는 선택
     사항이지만, 실행해두면 훨씬 정확하다).

주의:
  트인 공간이 아닌 곳에서 캘리브레이션하면(예: 벽에 붙여둠) 그 방향의
  임계값이 실제보다 커져 그쪽 장애물을 못 볼 수 있다. config.py 의
  LIDAR_SELF_MASK_MAX_M 로 상한을 두지만, 가능한 한 넓은 공간에서
  캘리브레이션하는 것이 안전하다.
  로봇 트레이 구조(마운트, 배선 등)를 바꿨다면 반드시 재실행할 것.
"""

import json
import time

import numpy as np
from rplidar import RPLidar

import config
from lidar_processor import SELF_MASK_ANGLE_STEP_DEG, _self_mask_path

CALIBRATE_SEC = 12.0  # 캘리브레이션 수집 시간 (초). 라이다 5.5Hz 기준 약 65회전 분량
MARGIN_M = 0.03       # 측정 잡음 여유 (실측 최소값에 더해서 살짝 넉넉하게)


def normalize(angle: float, offset: float) -> float:
    angle = (angle + offset) % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle


def main():
    n_buckets = int(round(360.0 / SELF_MASK_ANGLE_STEP_DEG))
    min_dist = np.full(n_buckets, np.inf, dtype=np.float64)
    sample_count = np.zeros(n_buckets, dtype=np.int64)

    lidar = RPLidar(config.LIDAR_PORT, baudrate=115200, timeout=3)
    lidar.connect()
    print(f"연결 완료: {lidar.get_info()}")
    print(f"캘리브레이션 시작 - {CALIBRATE_SEC:.0f}초간 로봇을 건드리지 마세요")
    print("사방 2m 이상 트인 공간인지 다시 한 번 확인하세요 (사람/벽/가구 없이).")

    t0 = time.time()
    try:
        for scan in lidar.iter_scans(max_buf_meas=500):
            if time.time() - t0 > CALIBRATE_SEC:
                break
            for quality, angle_raw, dist_mm in scan:
                if quality == 0 or dist_mm == 0:
                    continue
                angle = normalize(float(angle_raw), config.LIDAR_ANGLE_OFFSET_DEG)
                dist_m = dist_mm / 1000.0
                if dist_m < config.LIDAR_MIN_RANGE_M:
                    continue
                idx = int((angle + 180.0) / SELF_MASK_ANGLE_STEP_DEG) % n_buckets
                if dist_m < min_dist[idx]:
                    min_dist[idx] = dist_m
                sample_count[idx] += 1
    except KeyboardInterrupt:
        print("\n중단됨 - 지금까지 모은 데이터로 저장합니다.")
    finally:
        lidar.stop()
        lidar.disconnect()

    empty = sample_count == 0
    if np.any(empty):
        print(f"[경고] {int(empty.sum())}/{n_buckets} 개 각도 구간에서 샘플을 못 모았습니다 "
              f"(라이다 사각지대이거나 수집 시간 부족) - 해당 구간은 균일 반경"
              f"({config.LIDAR_SELF_EXCLUSION_M:.2f}m)으로 유지됩니다.")

    thresholds = np.where(
        empty,
        config.LIDAR_SELF_EXCLUSION_M,
        np.clip(min_dist + MARGIN_M, config.LIDAR_MIN_RANGE_M,
                getattr(config, "LIDAR_SELF_MASK_MAX_M", 0.45)),
    )

    path = _self_mask_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "angle_step_deg": SELF_MASK_ANGLE_STEP_DEG,
            # 이 프로파일은 각도 인덱스로 저장되므로, 캘리브레이션 당시의 각도
            # 오프셋과 짝을 이룰 때만 유효하다. 오프셋이 바뀌면 같은 물리 방향이
            # 다른 각도 라벨을 갖게 되어 프로파일 전체가 엉뚱한 방향에 적용된다.
            # lidar_processor.load_self_mask() 가 이 값을 검사해서 불일치 시 거부한다.
            "angle_offset_deg": config.LIDAR_ANGLE_OFFSET_DEG,
            "thresholds_m": thresholds.tolist(),
            "calibrated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": sample_count.tolist(),
        }, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: {path}")
    print(f"임계값 범위: {thresholds.min():.2f}m ~ {thresholds.max():.2f}m "
          f"(평균 {thresholds.mean():.2f}m, 총 샘플 {int(sample_count.sum())}개)")
    print("main_mapping.py 또는 main.py 를 재시작하면 자동으로 적용됩니다.")


if __name__ == "__main__":
    main()
