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

import config


def _limit_onnxruntime_threads():
    """
    ONNX Runtime 은 기본값으로 CPU 코어 수만큼 스레드를 띄우고, 일이 없을 때도 코어를 붙잡고
    기다린다(스핀 대기). 그러면 메인 루프와 라이다 프로세스가 CPU 를 못 받는다.
    ultralytics 는 InferenceSession 을 옵션 없이 만들기 때문에, 옵션을 지정하지 않은 세션에
    한해 스레드 수 제한과 스핀 대기 끄기를 끼워 넣는다. (실패해도 기본 동작으로 계속 진행)
    """
    threads = int(getattr(config, "YOLO_ORT_THREADS", 0))
    if threads <= 0:
        return
    try:
        import onnxruntime as ort
        base = ort.InferenceSession
        if getattr(base, "_limited_by_yolo_detector", False):
            return

        class _LimitedSession(base):
            _limited_by_yolo_detector = True

            def __init__(self, path_or_bytes, sess_options=None, *args, **kwargs):
                if sess_options is None:
                    sess_options = ort.SessionOptions()
                    sess_options.intra_op_num_threads = threads
                    sess_options.inter_op_num_threads = 1
                    try:
                        sess_options.add_session_config_entry("session.intra_op.allow_spinning", "0")
                    except Exception:
                        pass
                super().__init__(path_or_bytes, sess_options, *args, **kwargs)

        ort.InferenceSession = _LimitedSession
        print(f"[YOLO] ONNX Runtime 스레드 {threads}개로 제한 (스핀 대기 끔)")
    except Exception as e:
        print(f"[YOLO] ONNX Runtime 스레드 제한 적용 실패 (기본 설정 사용): {e}")


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

                _limit_onnxruntime_threads()
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
