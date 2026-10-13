"""
test_oak_rgb_raw.py
OAK-D-Lite RGB 영상이 단색 회색으로 나오는 문제를 가리기 위한 최소 진단 스크립트.
oak_processor 를 거치지 않고 ColorCamera 만 단독으로 연다 (메인 프로그램은 먼저 종료할 것).

사용법:  python test_oak_rgb_raw.py [video|preview|isp|proc]    (기본 video)
  - proc: 메인 프로그램과 똑같이 OakProcessor 로 열어 RGB 를 확인한다
          (단독 모드는 정상인데 proc 만 단색이면 oak_processor 파이프라인 설정 문제)
  - 연결된 센서 이름 / USB 속도를 출력한다.
  - 1초마다 RGB, 왼쪽 흑백 프레임의 mean/std 를 출력한다.
      std 가 거의 0 이면 "무늬 없는 단색 프레임" (영상 자체가 비정상)
  - 화면: 왼쪽 RGB, 오른쪽 흑백(CAM_B). 'q' 종료, 's' 현재 프레임 저장
판정:
  - 흑백은 정상(std 큼)인데 RGB 만 단색  -> RGB 센서/ISP/연결 문제 (하드웨어 가능성)
  - 둘 다 정상                          -> 이 스크립트가 정상이면 oak_processor 파이프라인 설정 문제
  - 센서 목록에 CAM_A 가 없거나 이름이 이상함 -> RGB 센서 인식 실패
"""
import sys
import time

import cv2
import numpy as np
import depthai as dai


def run_processor():
    """메인 프로그램과 같은 OakProcessor 경로로 RGB 를 받아 mean/std 를 출력한다."""
    from oak_processor import OakProcessor
    print("depthai", dai.__version__, "| python", sys.version.split()[0])
    proc = OakProcessor()
    proc.start()
    last_print = 0.0
    try:
        while True:
            frame = proc.get_frame()
            if frame is not None and frame.rgb_frame is not None:
                rgb = frame.rgb_frame
                now = time.time()
                if now - last_print >= 1.0:
                    last_print = now
                    print(f"PROC RGB {rgb.shape} mean={rgb.mean():6.1f} std={rgb.std():6.2f}")
                cv2.imshow("OakProcessor RGB", rgb)
            if (cv2.waitKey(10) & 0xFF) == ord("q"):
                break
    finally:
        proc.stop()
        cv2.destroyAllWindows()


def main(mode: str = "video"):
    if mode == "proc":
        run_processor()
        return

    p = dai.Pipeline()

    cam = p.create(dai.node.ColorCamera)
    cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam.setPreviewSize(640, 360)
    cam.setInterleaved(False)
    cam.setFps(15)
    x_rgb = p.create(dai.node.XLinkOut)
    x_rgb.setStreamName("rgb")
    {"video": cam.video, "preview": cam.preview, "isp": cam.isp}[mode].link(x_rgb.input)

    mono = p.create(dai.node.MonoCamera)
    mono.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    x_mono = p.create(dai.node.XLinkOut)
    x_mono.setStreamName("mono")
    mono.out.link(x_mono.input)

    with dai.Device(p) as dev:
        print("depthai", dai.__version__, "| USB 속도:", dev.getUsbSpeed())
        for f in dev.getConnectedCameraFeatures():
            print("  센서:", f.socket, f.sensorName, f.width, "x", f.height)

        q_rgb = dev.getOutputQueue("rgb", 4, False)
        q_mono = dev.getOutputQueue("mono", 4, False)
        rgb = mono_img = None
        last_print = 0.0
        while True:
            a = q_rgb.tryGet()
            if a is not None:
                rgb = a.getCvFrame()
            b = q_mono.tryGet()
            if b is not None:
                mono_img = b.getCvFrame()

            now = time.time()
            if now - last_print >= 1.0:
                last_print = now
                s = []
                if rgb is not None:
                    s.append(f"RGB  {rgb.shape} mean={rgb.mean():6.1f} std={rgb.std():6.2f}")
                else:
                    s.append("RGB  (프레임 없음)")
                if mono_img is not None:
                    s.append(f"MONO {mono_img.shape} mean={mono_img.mean():6.1f} std={mono_img.std():6.2f}")
                print(" | ".join(s))

            if rgb is not None and mono_img is not None:
                left = cv2.resize(rgb, (640, 360))
                right = cv2.resize(cv2.cvtColor(mono_img, cv2.COLOR_GRAY2BGR) if mono_img.ndim == 2 else mono_img,
                                   (640, 360))
                cv2.imshow("RGB (left) | MONO CAM_B (right)", np.hstack([left, right]))
            key = cv2.waitKey(10) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s") and rgb is not None:
                # cv2.imwrite 는 Windows 한글 경로에서 실패하므로 imencode + tofile 로 저장
                ok, buf = cv2.imencode(".png", rgb)
                if ok:
                    buf.tofile("oak_rgb_raw_test.png")
                    print("saved oak_rgb_raw_test.png")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "video")
