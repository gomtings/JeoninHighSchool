from ultralytics import YOLO

# 1. YOLO11 Nano 모델 로드 (최초 실행 시 자동 다운로드)
model = YOLO("yolo11n.pt")

# 2. ONNX 포맷으로 변환
# imgsz: 입력 이미지 크기 (기본값 640)
# dynamic=False: 입력 크기를 고정하여 CPU 추론 속도 향상
model.export(format="onnx", imgsz=640, dynamic=False)

print("변환 완료: yolo11n.onnx 파일이 생성되었습니다.")