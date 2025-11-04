# cd '.\Integrated_Control_System\'
# cd 'C:/GitHub/JeoninHighSchool/서빙로봇/서빙로봇 소프트웨어/OAK-D-Lite'
# deactivate # 가상 환경에서 빠져 나오기
# python -m venv .venv # 처음 한번 가상환경 생성...
# C:/GitHub/JeoninHighSchool/서빙로봇/서빙로봇 소프트웨어/OAK-D-Lite\.venv\Scripts\Activate.ps1
# pip install depthai
# pip install opencv-python
# pip install --upgrade cmake
# pip install depthai opencv-python blobconverter
# python install_requirements.py
import depthai as dai
import cv2

# 파이프라인 생성
pipeline = dai.Pipeline()

# 카메라 노드 설정 (RGB 카메라)
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(300, 300) # 객체 감지 모델에 맞는 해상도
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

# 객체 감지 모델 로드 (MobileNet SSD)
# 예제에서는 DepthAI 깃허브에서 제공하는 모델을 사용합니다.
# 직접 다운로드하여 사용할 수도 있습니다.
nn = pipeline.create(dai.node.MobileNetDetectionNetwork)
nn.setBlobPath("/path/to/your/mobilenet-ssd.blob") # 이 부분은 실제 모델 경로로 변경해야 합니다.
# 일반적으로 DepthAI 예제 깃허브에서 다운로드 가능:
# https://github.com/luxonis/depthai-model-zoo/blob/main/models/mobilenet-ssd/mobilenet-ssd.blob
# 만약 BlobConverter를 통해 직접 변환했다면 해당 경로를 사용하세요.

nn.setConfidenceThreshold(0.5) # 0.5 이상의 신뢰도만 표시
nn.input.setBlocking(False)

# RGB 카메라 출력을 NN 입력에 연결
cam_rgb.preview.link(nn.input)

# NN 출력 노드 설정
xout_nn = pipeline.create(dai.node.XLinkOut)
xout_nn.setStreamName("nn")
nn.out.link(xout_nn.input)

# 카메라 프리뷰 출력 노드 설정
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# OAK D-Lite 장치에 파이프라인 연결 및 실행
with dai.Device(pipeline) as device:
    # 출력 큐 설정
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    q_nn = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

    frame = None
    detections = []

    # 'MobileNet SSD' 모델의 클래스 레이블 (예시, 실제 모델에 따라 다를 수 있음)
    # 여기서는 'person'만 감지하도록 가정합니다.
    label_map = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
                 "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

    print("OAK D-Lite에서 객체 감지 시작...")
    print("종료하려면 'q' 키를 누르세요.")

    while True:
        in_rgb = q_rgb.tryGet()
        in_nn = q_nn.tryGet()

        if in_rgb is not None:
            # 카메라 프레임을 OpenCV 이미지로 변환
            frame = in_rgb.getCvFrame()

        if in_nn is not None:
            # NN 결과(감지된 객체들) 가져오기
            detections = in_nn.detections

        if frame is not None:
            height = frame.shape[0]
            width = frame.shape[1]

            # 감지된 객체들에 경계 상자 및 레이블 그리기
            for detection in detections:
                try:
                    label = label_map[detection.label]
                except IndexError:
                    label = "Unknown"

                # 'person'만 필터링하여 표시
                if label == "person":
                    # 경계 상자 좌표 계산
                    x1 = int(detection.xmin * width)
                    y1 = int(detection.ymin * height)
                    x2 = int(detection.xmax * width)
                    y2 = int(detection.ymax * height)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) # 초록색 사각형
                    cv2.putText(frame, f"{label}: {int(detection.confidence * 100)}%",
                                (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("OAK D-Lite Object Detection (Person)", frame)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
print("객체 감지 종료.")