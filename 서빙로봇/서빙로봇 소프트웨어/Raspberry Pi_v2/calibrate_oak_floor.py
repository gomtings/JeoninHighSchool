"""
calibrate_oak_floor.py
OAK-D-Lite 깊이 영상에서 바닥 평면을 찾아 카메라의 "바닥 기준 높이"와 "아래로 기울어진 각도(pitch)"를 측정한다.

왜 필요한가:
  mapper.update_from_depth 는 카메라 높이(OAK_HEIGHT_FROM_FLOOR_M)와 기울기(OAK_PITCH_DEG)로 각 픽셀의
  바닥 기준 높이를 계산해 바닥/천장을 걸러낸다. 이 값이 실제와 다르면 바닥이 "장애물"로 맵에 쌓인다.

사용법 (메인 프로그램은 먼저 종료):
  python calibrate_oak_floor.py            # 카메라가 보는 바닥으로 측정
  - 로봇을 평평한 곳에 두고, 카메라 앞쪽 2~4m 바닥이 화면 아래쪽에 넓게 보이게 한다 (물건/사람 치우기).
  - 약 5초간 여러 프레임을 모아 중앙값으로 결과를 낸다.
  - 마지막에 config.py 에 넣을 값을 출력한다.

원리: 화면 아래쪽 픽셀들의 3D 점(카메라 좌표 X 우, Y 아래, Z 광축)에 RANSAC 으로 평면을 맞춘다.
  바닥의 윗방향 단위벡터는 카메라 좌표에서 (0, -cos p, -sin p) 이므로
  pitch p = atan2(-nz, -ny),  카메라 높이 H = -(n · P)
"""
import math
import sys
import time

import numpy as np

import config


def fit_floor(depth_m: np.ndarray, rng: np.random.Generator, hfov_deg: float = None,
              row_start: float = 0.45, thresh: float = 0.03, iters: int = 300):
    """
    깊이 영상(m) 하나에서 바닥 평면을 찾는다.
    반환: (height_m, pitch_deg, roll_deg, inlier_ratio) 또는 None
    """
    hfov_deg = hfov_deg or config.OAK_HFOV_DEG
    h, w = depth_m.shape
    fx = (w / 2.0) / math.tan(math.radians(hfov_deg) / 2.0)
    r0 = int(h * row_start)
    rows = np.arange(r0, h, 3)
    cols = np.arange(0, w, 3)
    z = depth_m[np.ix_(rows, cols)]
    v = (rows - h / 2.0)[:, None]
    u = (cols - w / 2.0)[None, :]
    ok = (z > 0.4) & (z < 4.5)
    Z = z[ok]
    if Z.size < 500:
        return None
    X = (u * z / fx)[ok]
    Y = (v * z / fx)[ok]
    P = np.stack([X, Y, Z], axis=1)

    best_n, best_d, best_cnt = None, 0.0, 0
    n_pts = P.shape[0]
    for _ in range(iters):
        i = rng.choice(n_pts, 3, replace=False)
        a, b, c = P[i]
        nrm = np.cross(b - a, c - a)
        L = np.linalg.norm(nrm)
        if L < 1e-9:
            continue
        nrm /= L
        if nrm[1] > 0:           # 윗방향(카메라 좌표에서 Y 음수 쪽)을 향하게 통일
            nrm = -nrm
        d = float(nrm @ a)       # n·P = d  (바닥이면 d = -H)
        cnt = int((np.abs(P @ nrm - d) < thresh).sum())
        if cnt > best_cnt:
            best_n, best_d, best_cnt = nrm, d, cnt
    if best_n is None:
        return None

    # 인라이어로 최소제곱 재맞춤
    inl = np.abs(P @ best_n - best_d) < thresh
    Q = P[inl]
    mean = Q.mean(axis=0)
    _, _, vt = np.linalg.svd(Q - mean, full_matrices=False)
    n = vt[2]
    if n[1] > 0:
        n = -n
    d = float(n @ mean)
    height = -d
    pitch = math.degrees(math.atan2(-n[2], -n[1]))   # 아래로 기울면 +
    roll = math.degrees(math.asin(np.clip(n[0], -1, 1)))
    return height, pitch, roll, float(inl.mean())


def capture_and_calibrate(seconds: float = 5.0):
    import depthai as dai
    p = dai.Pipeline()
    left = p.create(dai.node.MonoCamera)
    left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    right = p.create(dai.node.MonoCamera)
    right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
    stereo = p.create(dai.node.StereoDepth)
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)
    stereo.initialConfig.setConfidenceThreshold(config.OAK_CONFIDENCE_THRESH)
    stereo.setLeftRightCheck(True)
    stereo.setSubpixel(True)
    left.out.link(stereo.left)
    right.out.link(stereo.right)
    xo = p.create(dai.node.XLinkOut)
    xo.setStreamName("depth")
    stereo.depth.link(xo.input)

    rng = np.random.default_rng(0)
    results = []
    with dai.Device(p) as dev:
        q = dev.getOutputQueue("depth", 4, False)
        t0 = time.time()
        while time.time() - t0 < seconds:
            f = q.tryGet()
            if f is None:
                time.sleep(0.01)
                continue
            depth_m = f.getFrame().astype(np.float32) / 1000.0
            r = fit_floor(depth_m, rng)
            if r:
                results.append(r)
                print(f"  프레임 {len(results):2d}: 높이 {r[0]:.3f}m  pitch {r[1]:+.1f}°  roll {r[2]:+.1f}°  (바닥 인라이어 {100 * r[3]:.0f}%)")
    return results


def summarize(results, cam_height_hint: float = None):
    """
    프레임별 결과에서 "바닥"을 골라 요약한다. 바닥으로 인정하는 조건:
      - 수평면(기울기 ±25° 이내), 카메라 높이 0.5~1.6m, 인라이어 비율 30% 이상
    조건을 못 채우면(벽/책상 윗면을 맞춘 경우 등) config 값은 출력하지 않고 어떤 수평면이 보였는지만 알려준다.
    """
    cam_height_hint = cam_height_hint or config.OAK_HEIGHT_FROM_FLOOR_M
    if not results:
        print("평면을 하나도 찾지 못했습니다. 카메라 앞 바닥이 화면 아래쪽에 넓게 보이게 하고 다시 실행하세요.")
        return
    a = np.array(results)
    good = (np.abs(a[:, 1]) < 25) & (a[:, 0] > 0.5) & (a[:, 0] < 1.6) & (a[:, 3] >= 0.30)
    print(f"\n프레임 {len(a)}개 중 바닥으로 쓸 수 있는 것: {int(good.sum())}개")

    # 수평에 가까운 평면(바닥, 책상 윗면 등)이 어느 높이에 몇 번 보였는지 (카메라 아래 몇 m 인지)
    horiz = a[np.abs(a[:, 1]) < 15]
    if len(horiz):
        print("관측된 수평면 (카메라로부터 아래로 떨어진 거리 / 횟수 / 평균 기울기):")
        bins = np.round(horiz[:, 0] / 0.05) * 0.05
        for hb in sorted(set(bins), key=lambda x: -(bins == x).sum())[:4]:
            m = bins == hb
            tag = "  <- 카메라 높이와 비슷: 바닥일 가능성" if abs(hb - cam_height_hint) < 0.12 else ""
            print(f"  {hb:.2f}m  {int(m.sum()):3d}회  기울기 {horiz[m, 1].mean():+.1f}°{tag}")

    if good.sum() < 5:
        print("\n[측정 실패] 바닥 평면이 충분히 잡히지 않았습니다. config.py 에 넣을 값을 출력하지 않습니다.")
        print("  - 카메라 앞 2~4m 바닥이 화면 아래쪽에 넓게 보이고, 벽에서 2m 이상 떨어지게 하세요.")
        print("  - 책상/의자/사람 다리가 화면 아래쪽을 채우고 있으면 바닥 대신 그 윗면을 맞춥니다.")
        print("  - 바닥에 무늬가 없으면 스테레오 깊이가 비어서 측정이 어렵습니다(바닥에 신문지나 매트를 깔아 보세요).")
        return

    g = a[good]
    med = np.median(g, axis=0)
    spread = g.std(axis=0)
    print("\n── 결과 (바닥으로 인정된 프레임의 중앙값) ──")
    print(f"  카메라 높이 : {med[0]:.3f} m   (편차 {spread[0]:.3f})")
    print(f"  pitch       : {med[1]:+.1f}°  (아래로 기울면 +, 위로 기울면 -, 편차 {spread[1]:.1f}°)")
    print(f"  roll        : {med[2]:+.1f}°  (좌우 기울기. 코드는 반영하지 않음, 3° 넘으면 알려주세요)")
    print(f"  바닥 인라이어: {100 * med[3]:.0f}%")
    print("\nconfig.py 에 이렇게 넣으세요:")
    print(f"  OAK_HEIGHT_FROM_FLOOR_M = {med[0]:.2f}")
    print(f"  OAK_PITCH_DEG = {med[1]:.1f}")


if __name__ == "__main__":
    summarize(capture_and_calibrate(float(sys.argv[1]) if len(sys.argv) > 1 else 5.0))
