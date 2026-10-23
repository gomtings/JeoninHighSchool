"""
test.py
YOLO11 모델(.pt)을 받아 ONNX 로 변환한다.

사용법:  python test.py [모델이름]      예) python test.py yolo11m
  - 모델이름을 생략하면 yolo11n. 최초 실행 시 .pt 파일이 자동으로 다운로드된다.
  - 결과 yolo11m.onnx 를 이 폴더에 두고 config.py 의 YOLO_MODEL 을 "yolo11m.onnx" 로 바꾼다.
"""
import sys

from ultralytics import YOLO

name = sys.argv[1] if len(sys.argv) > 1 else "yolo11n"
model = YOLO(f"{name}.pt")

# imgsz: 입력 이미지 크기 (기본값 640)
# dynamic=False: 입력 크기를 고정하여 CPU 추론 속도 향상
model.export(format="onnx", imgsz=640, dynamic=False)

print(f"변환 완료: {name}.onnx 파일이 생성되었습니다.")
