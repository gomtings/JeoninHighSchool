"""
oak_worker.py
OAK-D-Lite 프레임 수신과 YOLO 추론을 메인(UI) 루프 밖의 백그라운드 스레드에서 돌린다.

- OAK 스레드: oak_proc.get_frame() 을 계속 호출해 최신 프레임과 그 순간의 로봇 자세를 보관
- YOLO 스레드: OAK 스레드가 보관한 최신 프레임으로 YOLO 를 돌리고, 그 프레임의 뎁스/자세와 함께 결과를 보관
  (YOLO 가 한 번에 약 250ms 걸려도 OAK 스레드는 멈추지 않아 뎁스는 계속 최신으로 유지된다)
- 메인 루프는 get_frame() / get_detections() 로 최신 결과만 가져가고 절대 기다리지 않는다.

스레드여도 효과가 있는 이유: ONNX Runtime(YOLO)과 numpy/OpenCV 는 계산 중 GIL 을 풀어주므로
메인 루프와 실제로 병렬로 돈다.
"""

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import config
from console_utils import safe_print as _safe_print


Pose = Tuple[float, float, float]  # (x_fwd_m, y_left_m, heading_deg) - OccupancyMap.set_robot_pose 입력 형식


@dataclass
class FrameResult:
    frame: object          # OakFrame
    pose: Pose             # 프레임을 받은 순간의 로봇 자세
    seq: int               # 프레임 번호 (같은 프레임을 두 번 맵에 반영하지 않기 위함)


@dataclass
class YoloResult:
    detections: list       # YoloDetector.detect() 결과
    depth_map: object      # YOLO 를 돌린 프레임의 뎁스 (박스와 같은 순간)
    pose: Pose             # 그 프레임을 받은 순간의 로봇 자세
    seq: int               # 결과 번호


class OakYoloWorker:
    def __init__(self, oak_proc, yolo, pose_fn: Callable[[], Pose]):
        self.oak_proc = oak_proc
        self.yolo = yolo
        self.pose_fn = pose_fn

        self._lock = threading.Lock()
        self._frame_cond = threading.Condition(self._lock)  # 새 프레임이 들어오면 YOLO 스레드를 깨운다
        self._stop = threading.Event()
        self._frame: Optional[FrameResult] = None
        self._yolo: Optional[YoloResult] = None
        self._frame_seq = 0
        self._yolo_seq = 0
        self._threads = []
        self._yolo_t_sum, self._yolo_t_n = 0.0, 0   # YOLO 추론 시간 통계 (DEBUG_PROFILE)

    def start(self):
        self._threads = [
            threading.Thread(target=self._oak_loop, name="OakThread", daemon=True),
        ]
        if (self.yolo is not None and getattr(self.yolo, "is_available", False)
                and getattr(config, "YOLO_ENABLED", True)):
            self._threads.append(threading.Thread(target=self._yolo_loop, name="YoloThread", daemon=True))
        for t in self._threads:
            t.start()
        _safe_print(f"[OakYoloWorker] 백그라운드 스레드 시작: {[t.name for t in self._threads]}")

    def stop(self, timeout: float = 2.0):
        self._stop.set()
        with self._frame_cond:
            self._frame_cond.notify_all()
        for t in self._threads:
            t.join(timeout=timeout)

    # ── 메인 루프에서 호출 (기다리지 않음) ──────────────────────────
    def get_frame(self) -> Optional[FrameResult]:
        with self._lock:
            return self._frame

    def get_detections(self) -> Optional[YoloResult]:
        with self._lock:
            return self._yolo

    # ── 백그라운드 스레드 ──────────────────────────────────────────
    def _oak_loop(self):
        while not self._stop.is_set():
            try:
                pose = self.pose_fn()
                frame = self.oak_proc.get_frame()
            except Exception as e:
                _safe_print(f"[OakThread] 프레임 수신 예외: {e}")
                frame = None
            if frame is None:
                time.sleep(0.005)  # 새 뎁스가 아직 없음 (OAK 15FPS)
                continue
            with self._frame_cond:
                self._frame_seq += 1
                self._frame = FrameResult(frame=frame, pose=pose, seq=self._frame_seq)
                self._frame_cond.notify_all()

    def _yolo_loop(self):
        last_seq = 0
        while not self._stop.is_set():
            with self._frame_cond:
                # 직전에 처리한 것보다 새 프레임이 올 때까지 대기
                while not self._stop.is_set() and (self._frame is None or self._frame.seq == last_seq):
                    self._frame_cond.wait(timeout=0.5)
                if self._stop.is_set():
                    break
                fr = self._frame
            last_seq = fr.seq
            rgb = getattr(fr.frame, "rgb_frame", None)
            if rgb is None:
                continue
            t_start = time.time()
            try:
                dets = self.yolo.detect(rgb)
                # [추론 시간 측정] 모델을 바꿔 볼 때 한 번 도는 데 얼마나 걸리는지 10회마다 출력
                if getattr(config, "DEBUG_PROFILE", False):
                    self._yolo_t_sum += time.time() - t_start
                    self._yolo_t_n += 1
                    if self._yolo_t_n >= 10:
                        _safe_print(f"[YOLO PROFILE] 추론 1회 평균 {self._yolo_t_sum / self._yolo_t_n * 1000:.0f}ms "
                                    f"({config.YOLO_MODEL}, 스레드 {getattr(config, 'YOLO_ORT_THREADS', 0)}개, 최대 {getattr(config, 'YOLO_MAX_HZ', 0)}Hz)")
                        self._yolo_t_sum, self._yolo_t_n = 0.0, 0
            except Exception as e:
                _safe_print(f"[YoloThread] 추론 예외: {e}")
                dets = None
            if dets is not None:
                with self._lock:
                    self._yolo_seq += 1
                    self._yolo = YoloResult(detections=dets, depth_map=fr.frame.depth_map,
                                            pose=fr.pose, seq=self._yolo_seq)
            # [주기 제한] 쉬지 않고 돌리면 CPU 를 독차지하므로 YOLO_MAX_HZ 에 맞춰 쉰다
            max_hz = getattr(config, "YOLO_MAX_HZ", 0.0)
            if max_hz > 0:
                rest = 1.0 / max_hz - (time.time() - t_start)
                if rest > 0:
                    self._stop.wait(rest)
