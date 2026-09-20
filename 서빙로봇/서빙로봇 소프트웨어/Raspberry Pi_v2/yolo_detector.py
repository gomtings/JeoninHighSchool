"""
yolo_detector.py
PC 테스트 및 실시간 추론용 YOLO11 초경량 ONNX 객체 인식 모듈

- yolo11n.onnx 초경량 ONNX 모델 로드 및 실시간 추론
- ultralytics 패키지 미설치 또는 파일 부재 시 에러 없이 기하 필터로 자동 폴백(Fallback) 처리 지원
- 식당/홀 환경의 주 장애물(사람, 의자, 테이블) 선별 감지
"""

import os
import time
import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class YoloDetector:
    """YOLO11 ONNX PC 추론 및 장애물 검출 모듈"""

    def __init__(self, model_name: str = "yolo11n.onnx"):
        self.model = None
        self.is_available = ULTRALYTICS_AVAILABLE
        
        if self.is_available:
            try:
                # 1. 스크립트 디렉토리 기준 yolo11n.onnx 경로 탐색
                base_dir = os.path.dirname(os.path.abspath(__file__))
                local_onnx = os.path.join(base_dir, model_name)
                
                if os.path.exists(local_onnx):
                    model_target = local_onnx
                elif os.path.exists(model_name):
                    model_target = model_name
                else:
                    model_target = "yolo11n.pt"  # 로컬 ONNX 미발견 시 pt 다운로드 로드

                self.model = YOLO(model_target, task="detect")
                print(f"[YOLO] YOLO11 Nano Model ({model_target}) loaded successfully.")
            except Exception as e:
                print(f"[YOLO] Model loading failed: {e} -> Falling back to geometry-only mode.")
                self.is_available = False
        else:
            print("[YOLO] 'ultralytics' library is not found. Running in Geometry-Only Fallback Mode.")

    def detect(self, rgb_frame) -> list:
        """
        RGB 프레임에서 식당 환경 타겟 장애물을 검출합니다.
        
        Returns:
            List[Dict]:
                - 'bbox_norm': (x1, y1, x2, y2) 정규화 바운딩 박스 좌표
                - 'class_id':   클래스 ID (int)
                - 'label':      클래스명 (str)
                - 'confidence': 신뢰도 (float)
        """
        if not self.is_available or self.model is None or rgb_frame is None:
            return []

        try:
            # 추론 수행 (신뢰도 임계치 0.25, 터미널 로그 비활성화)
            results = self.model(rgb_frame, conf=0.25, verbose=False)
            if not results:
                return []

            detected = []
            h, w = rgb_frame.shape[:2]
            
            result = results[0]
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0].item())

                    # 2D 바운딩 박스 정규화 (x1, y1, x2, y2)
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1_norm = float(np.clip(xyxy[0] / w, 0.0, 1.0))
                    y1_norm = float(np.clip(xyxy[1] / h, 0.0, 1.0))
                    x2_norm = float(np.clip(xyxy[2] / w, 0.0, 1.0))
                    y2_norm = float(np.clip(xyxy[3] / h, 0.0, 1.0))

                    conf = float(box.conf[0].item())

                    # 클래스명 매핑 (0: PERSON, 그 외: OBSTACLE)
                    if cls_id == 0:
                        label_name = "PERSON"
                    else:
                        label_name = "OBSTACLE"

                    detected.append({
                        "bbox_norm": (x1_norm, y1_norm, x2_norm, y2_norm),
                        "class_id": cls_id,
                        "label": label_name,
                        "confidence": conf
                    })

            return detected
        except Exception as e:
            print(f"[YOLO] Inference exception: {e}")
            return []
