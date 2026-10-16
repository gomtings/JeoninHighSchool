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


def summarize(results):
    if not results:
        print("바닥 평면을 찾지 못했습니다. 카메라 앞 바닥이 화면 아래쪽에 넓게 보이게 하고 다시 실행하세요.")
        return
    a = np.array(results)
    med = np.median(a, axis=0)
    spread = a.std(axis=0)
    print("\n── 결과 (중앙값) ──")
    print(f"  카메라 높이 : {med[0]:.3f} m   (프레임 간 편차 {spread[0]:.3f})")
    print(f"  pitch       : {med[1]:+.1f}°  (아래로 기울면 +, 편차 {spread[1]:.1f}°)")
    print(f"  roll        : {med[2]:+.1f}°  (좌우 기울기. 코드는 반영하지 않음, 3° 넘으면 알려주세요)")
    print(f"  바닥 인라이어: {100 * med[3]:.0f}%  (낮으면 바닥이 가려졌다는 뜻 - 신뢰하지 말고 다시 측정)")
    print("\nconfig.py 에 이렇게 넣으세요:")
    print(f"  OAK_HEIGHT_FROM_FLOOR_M = {med[0]:.2f}")
    print(f"  OAK_PITCH_DEG = {med[1]:.1f}")
    if med[3] < 0.5:
        print("\n[주의] 인라이어 비율이 50% 미만입니다. 바닥이 충분히 보이지 않아 값이 틀릴 수 있습니다.")


if __name__ == "__main__":
    summarize(capture_and_calibrate(float(sys.argv[1]) if len(sys.argv) > 1 else 5.0))
