"""
analyze_map_sources.py
저장된 맵(saved_map.npz)에서 "어느 센서가 장애물/벽 셀을 만들었는가"를 요약하고 그림으로 저장한다.

사용법:  python analyze_map_sources.py [saved_map.npz]
  - 센서별(라이다/뎁스/OAK 장애물/YOLO) hit 는 이 진단 기능을 넣은 뒤 새로 스캔한 맵에만 들어 있다.
    (예전 맵이면 안내만 출력한다)
  - 로봇 주변 거리 구간별로, 벽/장애물로 저장된 셀의 hit 가 어느 센서 몫인지 보여준다.
  - 결과 그림: map_sources.png  (셀 색 = 그 셀의 hit 가 가장 많은 센서)
      파랑 = 뎁스, 하늘 = OAK 장애물, 초록 = YOLO, 주황 = 라이다
"""
import os
import sys

import numpy as np

SOURCES = ("lidar", "depth", "oak", "yolo")
LABEL = {"lidar": "라이다", "depth": "뎁스(update_from_depth)", "oak": "OAK 장애물(update_from_oak)", "yolo": "YOLO"}
COLOR_BGR = {"lidar": (30, 120, 245), "depth": (230, 90, 30), "oak": (230, 200, 60), "yolo": (60, 200, 60)}


def main(path: str):
    d = np.load(path)
    if not all(f"hit_{k}" in d for k in SOURCES):
        print("이 맵에는 센서별 hit 정보가 없습니다. 진단 기능을 넣은 코드로 새로 스캔한 맵이어야 합니다.")
        return
    g = d["grid"]
    src = {k: d[f"hit_{k}"].astype(np.int64) for k in SOURCES}
    total = sum(src.values())
    rc, rr = int(d["robot_col"]), int(d["robot_row"])
    res = float(d["resolution"])
    H, W = g.shape
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - rc, yy - rr) * res

    walls = g == 0.8
    obst = g == 1.0
    print(f"저장된 벽 {int(walls.sum())}셀, 장애물 {int(obst.sum())}셀")
    print("센서별 전체 hit 합:", {LABEL[k]: int(v.sum()) for k, v in src.items()})

    for name, mask in (("벽(갈색)", walls), ("장애물(주황)", obst)):
        if not mask.any():
            continue
        print(f"\n[{name}] 셀의 hit 를 만든 센서 비율")
        tot = total[mask].sum()
        for k in SOURCES:
            print(f"  {LABEL[k]:<28s} {100 * src[k][mask].sum() / max(tot, 1):5.1f}%")
        print("  로봇으로부터의 거리 구간별, 뎁스+OAK(카메라) 몫:")
        cam = src["depth"] + src["oak"] + src["yolo"]
        for lo, hi in ((0, 1), (1, 2), (2, 3), (3, 5), (5, 99)):
            m = mask & (dist >= lo) & (dist < hi)
            if m.any():
                print(f"    {lo}-{hi}m: 셀 {int(m.sum()):5d}  카메라 몫 {100 * cam[m].sum() / max(total[m].sum(), 1):5.1f}%")

    # 그림: 벽/장애물 셀을 가장 많이 만든 센서 색으로
    try:
        import cv2
        stack = np.stack([src[k] for k in SOURCES])
        dom = stack.argmax(axis=0)
        img = np.full((H, W, 3), (18, 22, 28), np.uint8)
        img[g == 0.3] = (90, 95, 100)
        for i, k in enumerate(SOURCES):
            img[(walls | obst) & (dom == i)] = COLOR_BGR[k]
        img = cv2.resize(img, (W * 2, H * 2), interpolation=cv2.INTER_NEAREST)
        cv2.circle(img, (rc * 2, rr * 2), 6, (0, 230, 255), -1)
        out = os.path.join(os.path.dirname(os.path.abspath(path)), "map_sources.png")
        ok, buf = cv2.imencode(".png", img)
        if ok:
            buf.tofile(out)
            print(f"\n그림 저장: {out}")
    except Exception as e:
        print("그림 저장 건너뜀:", e)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_map.npz"))
