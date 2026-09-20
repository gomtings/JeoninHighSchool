"""
oak_processor.py
OAK-D-Lite 깊이 데이터 획득 및 전처리

담당 역할:
  - DepthAI 파이프라인 구성 및 스트림 수신
  - 벽/배경 평면 감지 및 필터링 (화면 대부분을 차지하는 평면)
  - 화면 가장자리의 왜곡 신뢰도 처리
  - 노이즈 픽셀 제거
  - 유효 장애물 영역 반환
"""

import numpy as np  # NumPy 라이브러리 (배열 계산)
import cv2  # OpenCV 라이브러리 (이미지 처리)
import time  # 재연결 쿨다운/타임스탬프 계산
import threading  # 재연결을 백그라운드 스레드로 분리해 메인 루프 블로킹 방지
try:
    import depthai as dai  # DepthAI 라이브러리 (OAK 카메라 제어)
except ImportError:
    dai = None
from dataclasses import dataclass, field  # 데이터 클래스 정의
from typing import Optional, Tuple, List  # 타입 힌트
import config  # 설정 파일에서 상수 가져옴
from console_utils import safe_print as _safe_print


# OAK 카메라에서 감지한 단일 장애물 정보를 나타내는 데이터 클래스
@dataclass
class OakObstacle:
    """OAK-D-Lite 에서 감지한 단일 장애물 정보"""
    distance_m: float           # 중심까지의 거리 (미터 단위)
    angle_deg: float            # 로봇 정면 기준 수평 각도 (도 단위, 우측 +)
    bbox_norm: Tuple[float, float, float, float]  # 바운딩 박스 (x1, y1, x2, y2) 정규화 좌표
    confidence: float           # 신뢰도 (0.0 ~ 1.0)
    is_wall: bool = False       # 벽/배경 평면인지 여부


# 한 프레임의 OAK 처리 결과를 나타내는 데이터 클래스
@dataclass
class OakFrame:
    """한 프레임의 처리 결과"""
    depth_map: np.ndarray       # 깊이 맵 ((H, W) float32, 미터 단위)
    rgb_frame: Optional[np.ndarray]  # RGB 프레임 (선택적)
    obstacles: List[OakObstacle] = field(default_factory=list)  # 감지된 장애물 리스트
    valid_mask: np.ndarray = field(default_factory=lambda: np.array([]))  # 유효 마스크
    timestamp: float = 0.0  # 타임스탬프


# OAK-D-Lite 카메라 데이터를 처리하는 클래스
class OakProcessor:
    """OAK-D-Lite 처리 클래스"""

    def __init__(self):
        if dai is None:
            raise RuntimeError("DepthAI 라이브러리가 설치되지 않았습니다.")
        # 파이프라인과 큐 초기화
        self.pipeline = None  # DepthAI 파이프라인 객체
        self.device = None    # 연결된 디바이스 객체
        self.q_depth = None   # 깊이 데이터 큐
        self.q_rgb = None     # RGB 데이터 큐
        self.latest_rgb = None # 최신 RGB 프레임 캐시 메모리
        self._last_reconnect_time = 0.0  # 재연결 쿨다운 타임스탬프
        self._consecutive_errors = 0     # get_frame() 연속 실패 횟수 (일시적 글리치와 실제 단선 구분용)
        self._reconnect_lock = threading.Lock()  # 재연결 스레드 중복 실행 방지용 (진행 중 표시 겸용)
        self._device_lock = threading.Lock()     # device/q_depth/q_rgb 네이티브 호출 상호배제용
        self._shutdown_requested = threading.Event()  # stop() 이후 백그라운드 재연결이 디바이스를 되살리지 못하게 막는 플래그
        # 파이프라인은 start() 가 호출될 때마다 새로 구성한다 (여기서는 dai 설치 여부만 검증)

    # ── 파이프라인 구성 ────────────────────────────────────────────
    # DepthAI 파이프라인을 구성하는 내부 메서드
    def _setup_pipeline(self):
        self.pipeline = dai.Pipeline()  # 새 파이프라인 생성

        # 왼쪽 모노 카메라 설정
        mono_left  = self.pipeline.create(dai.node.MonoCamera)
        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)  # 해상도 설정
        mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)  # 보드 소켓 설정
        mono_left.setFps(config.OAK_FPS)  # FPS 설정

        # 오른쪽 모노 카메라 설정
        mono_right = self.pipeline.create(dai.node.MonoCamera)
        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
        mono_right.setFps(config.OAK_FPS)

        # 스테레오 깊이 노드 생성 및 설정
        stereo = self.pipeline.create(dai.node.StereoDepth)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)  # 고정밀 모드
        stereo.initialConfig.setConfidenceThreshold(config.OAK_CONFIDENCE_THRESH)  # 신뢰도 임계값
        stereo.setLeftRightCheck(True)  # 좌우 검증 활성화
        stereo.setExtendedDisparity(False)  # 확장 disparity 비활성화
        stereo.setSubpixel(True)  # 서브픽셀 활성화

        # 모노 카메라 출력을 스테레오 깊이에 연결
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)

        # 깊이 데이터를 외부로 출력하는 XLinkOut 노드
        xout_depth = self.pipeline.create(dai.node.XLinkOut)
        xout_depth.setStreamName("depth")  # 스트림 이름 설정
        stereo.depth.link(xout_depth.input)  # 스테레오 깊이 출력을 연결

        # RGB 카메라 설정
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)  # 중앙 RGB 카메라 소켓 설정
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)  # 물리 센서 해상도 강제 설정
        cam_rgb.setPreviewSize(640, 360)  # 미리보기 크기 설정 (16:9 비율 유지)
        cam_rgb.setInterleaved(False)  # 인터리브 비활성화
        cam_rgb.setFps(config.OAK_FPS)  # FPS 설정

        # RGB 데이터를 외부로 출력하는 XLinkOut 노드
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")  # 스트림 이름 설정
        cam_rgb.preview.link(xout_rgb.input)  # RGB 미리보기 출력을 연결

    # OAK 디바이스를 시작하는 메서드
    def start(self):
        self._setup_pipeline()  # 재연결 시에도 항상 새 파이프라인으로 구성 (파이프라인 재사용 불가)
        # 느린 하드웨어 연결(dai.Device())은 락 밖에서 수행해 get_frame() 을 블로킹하지 않는다.
        new_device = dai.Device(self.pipeline)  # 파이프라인으로 디바이스 연결
        try:
            new_q_depth = new_device.getOutputQueue("depth", maxSize=4, blocking=False)  # 깊이 큐 생성
            new_q_rgb   = new_device.getOutputQueue("rgb",   maxSize=4, blocking=False)  # RGB 큐 생성
        except Exception:
            # 큐 생성 중 실패 시 절반만 초기화된 디바이스를 그대로 두지 않고 정리
            try:
                new_device.close()
            except Exception:
                pass
            raise
        # 실제 교체는 짧게 락을 잡고 원자적으로 수행 (get_frame() 의 네이티브 호출과 상호배제).
        # 연결이 진행되는 동안 stop() 이 이미 호출됐다면(_shutdown_requested), 방금 연 디바이스를
        # 되살리지 않고 그대로 닫아 버려 "종료했는데 뒤늦게 재연결되는" 레이스를 막는다.
        with self._device_lock:
            if self._shutdown_requested.is_set():
                try:
                    new_device.close()
                except Exception:
                    pass
                raise RuntimeError("OAK 종료 요청으로 연결을 취소함")
            self.device = new_device
            self.q_depth = new_q_depth
            self.q_rgb = new_q_rgb
            self.latest_rgb = None
            self._consecutive_errors = 0
        _safe_print("[OAK] 디바이스 연결 완료")  # 연결 성공 메시지

    # OAK 디바이스를 정지하는 메서드 (외부에서 호출하는 영구 종료용)
    def stop(self):
        self._shutdown_requested.set()
        self._close_device()
        # 진행 중인 백그라운드 재연결 스레드가 있다면 끝날 때까지 잠시 대기한다.
        # start() 가 dai.Device() 연결에 성공한 직후(=self.device 를 막 채운 뒤) stop() 이
        # 호출됐다면, 위의 _close_device() 는 그 디바이스가 아직 열리기 전이라 아무것도
        # 못 닫았을 수 있다 (닫을 게 없어서 즉시 반환). 재연결 스레드가 마저 끝날 때까지
        # 기다린 뒤 한 번 더 정리하면, 그 사이에 새로 열렸을 수 있는 디바이스까지 확실히 닫힌다.
        if self._reconnect_lock.acquire(timeout=5.0):
            self._reconnect_lock.release()
        self._close_device()

    def _close_device(self):
        """현재 device 를 닫고 참조를 정리 (영구 종료/재연결 전 정리 양쪽에서 공용으로 사용)"""
        # 참조를 락 안에서 떼어낸 뒤, 느릴 수 있는 close() 는 락 밖에서 수행한다.
        # get_frame() 이 q_depth/q_rgb 를 쓰는 구간은 항상 이 락을 잡고 있으므로,
        # 여기서 None 으로 바꾸는 순간 이후로는 옛 device 를 만지는 스레드가 없음이 보장된다.
        with self._device_lock:
            device = self.device
            self.device = None
            self.q_depth = None
            self.q_rgb = None
        if device:
            try:
                device.close()
            except Exception:
                pass

    def _try_reconnect(self):
        """
        연결 끊김 시 3초 쿨다운 후 백그라운드 스레드에서 자동 재연결 시도.
        dai.Device() 연결 자체가 수 초까지 걸릴 수 있는 블로킹 호출이라,
        메인 제어 루프(get_frame() 호출부)를 멈추지 않도록 별도 스레드에서 실행한다.
        """
        if self._shutdown_requested.is_set():
            return
        now = time.time()
        if now - self._last_reconnect_time < 3.0:
            return
        if not self._reconnect_lock.acquire(blocking=False):
            return  # 이미 재연결 스레드가 진행 중
        self._last_reconnect_time = now
        threading.Thread(target=self._reconnect_worker, daemon=True).start()

    def _reconnect_worker(self):
        """백그라운드 스레드에서 실행되는 실제 재연결 작업 (_reconnect_lock 보유 중)"""
        try:
            _safe_print("[OAK] 🔄 카메라 재연결 시도 중... (백그라운드)")
            self._close_device()
            self.start()
            _safe_print("[OAK] ✅ 카메라 자동 재연결 성공!")
        except Exception as e:
            _safe_print(f"[OAK] 재연결 대기 중 ({e})")
        finally:
            self._reconnect_lock.release()

    # ── 프레임 처리 메인 ──────────────────────────────────────────
    # 최신 프레임을 가져와 처리하는 메서드
    def get_frame(self) -> Optional[OakFrame]:
        # device/q_depth/q_rgb 에 대한 네이티브 호출은 전부 이 락 안에서 수행한다.
        # _reconnect_worker 가 백그라운드 스레드에서 stop()/start() 로 같은 객체들을
        # 닫고/새로 여는 것과 동시에 실행되면 DepthAI 네이티브 핸들에 대한 레이스로
        # 프로세스가 죽을 수 있기 때문에, 같은 락으로 상호배제한다.
        with self._device_lock:
            if self.q_depth is None or self.q_rgb is None:
                self._try_reconnect()
                return None

            try:
                in_depth = self.q_depth.tryGet()  # 깊이 큐에서 데이터 가져오기 (비블로킹)
                if in_depth is None:  # 데이터가 없으면
                    return None  # None 반환

                depth_raw = in_depth.getFrame()   # 원시 깊이 프레임 가져오기 (uint16, mm 단위)
                depth_m   = depth_raw.astype(np.float32) / 1000.0  # mm를 m로 변환

                # ── RGB 프레임 획득 및 큐 비우기 ──
                # 최초 기동 시 RGB 데이터가 아직 준비되지 않았다면 최대 1.0초간 대기하며 획득 보장
                t_start = time.time()
                while self.latest_rgb is None and (time.time() - t_start) < 1.0:
                    in_rgb = self.q_rgb.tryGet()
                    if in_rgb is not None:
                        self.latest_rgb = in_rgb.getCvFrame()
                        break
                    time.sleep(0.01)

                # 큐에 쌓여 있는 밀린 RGB 프레임들을 전부 소진하여 가장 최신 프레임으로 캐시 업데이트
                while True:
                    in_rgb = self.q_rgb.tryGet()
                    if in_rgb is None:
                        break
                    self.latest_rgb = in_rgb.getCvFrame()
            except Exception as e:
                # 한두 프레임의 일시적 디코딩 글리치까지 매번 전체 재연결로 처리하지 않도록
                # 연속 실패가 임계치를 넘을 때만 실제 단선으로 간주해 자원 정리 후 재연결 트리거
                self._consecutive_errors += 1
                _safe_print(f"[OAK] 프레임 획득 오류 ({self._consecutive_errors}회 연속): {e}")
                if self._consecutive_errors >= 3:
                    # stop()/start() 는 _try_reconnect() 가 스폰하는 백그라운드 스레드에서 처리 (메인 루프 논블로킹 유지)
                    self._try_reconnect()
                return None

            self._consecutive_errors = 0
            rgb = self.latest_rgb

        # 유효 마스크 생성 (범위 내 + 노이즈 제거)
        valid_mask = self._build_valid_mask(depth_m)

        # 벽/배경 감지 및 필터링
        depth_filtered, wall_mask = self._filter_walls(depth_m, valid_mask)

        # 장애물 후보 추출
        obstacles = self._extract_obstacles(depth_filtered, valid_mask, wall_mask)

        # 처리된 프레임 객체 생성 및 반환
        return OakFrame(
            depth_map  = depth_filtered,  # 필터링된 깊이 맵
            rgb_frame  = rgb,  # RGB 프레임
            obstacles  = obstacles,  # 추출된 장애물
            valid_mask = valid_mask,  # 유효 마스크
            timestamp  = time.time(),  # 현재 시간
        )

    # ── 유효 마스크 생성 ──────────────────────────────────────────
    # 깊이 맵에서 유효한 픽셀을 마스킹하는 메서드
    def _build_valid_mask(self, depth_m: np.ndarray) -> np.ndarray:
        """범위 내 + 노이즈 제거 마스크"""
        # 깊이 범위 마스크 생성 (최소/최대 범위 내)
        range_mask = (
            (depth_m > config.OAK_DEPTH_MIN_MM / 1000.0) &
            (depth_m < config.OAK_DEPTH_MAX_MM / 1000.0)
        )

        # 로컬 표준편차 기반 노이즈 픽셀 제거
        depth_u16 = (depth_m * 1000).astype(np.uint16)  # 다시 uint16으로 변환
        mean  = cv2.blur(depth_u16.astype(np.float32), (5, 5))  # 평균 블러
        mean2 = cv2.blur((depth_u16.astype(np.float32)) ** 2, (5, 5))  # 제곱 평균 블러
        std   = np.sqrt(np.maximum(mean2 - mean ** 2, 0))  # 표준편차 계산
        noise_mask = std < config.OAK_DEPTH_STD_THRESH  # 노이즈 임계값 이하 마스크

        # 가장자리 신뢰도 낮은 영역 마킹 (나중에 가중치 낮춤)
        h, w = depth_m.shape  # 깊이 맵 크기
        edge_h = int(h * config.OAK_EDGE_MARGIN)  # 가장자리 높이 마진
        edge_w = int(w * config.OAK_EDGE_MARGIN)  # 가장자리 너비 마진
        edge_region = np.zeros_like(range_mask, dtype=bool)  # 가장자리 영역 초기화
        edge_region[:edge_h, :]  = True  # 상단 가장자리
        edge_region[-edge_h:, :] = True  # 하단 가장자리
        edge_region[:, :edge_w]  = True  # 좌측 가장자리
        edge_region[:, -edge_w:] = True  # 우측 가장자리

        # 유효 마스크 반환 (범위 + 노이즈 제거)
        return (range_mask & noise_mask).astype(np.uint8)

    # ── 벽 / 배경 평면 필터 ───────────────────────────────────────
    # 깊이 맵에서 벽/배경 평면을 감지하고 필터링하는 메서드
    def _filter_walls(
        self,
        depth_m: np.ndarray,  # 깊이 맵
        valid_mask: np.ndarray,  # 유효 마스크
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        화면의 OAK_WALL_RATIO_THRESH 이상을 차지하는 단일 깊이 평면을
        벽으로 간주하고 제거한다.

        Returns:
            depth_filtered: 벽 픽셀이 0으로 마스킹된 깊이맵
            wall_mask:      벽으로 판단된 픽셀 마스크
        """
        depth_filtered = depth_m.copy()  # 깊이 맵 복사
        wall_mask = np.zeros_like(depth_m, dtype=bool)  # 벽 마스크 초기화

        valid_pixels = depth_m[valid_mask.astype(bool)]  # 유효 픽셀만 추출
        if valid_pixels.size == 0:  # 유효 픽셀이 없으면
            return depth_filtered, wall_mask  # 그대로 반환

        # 깊이 히스토그램으로 지배적인 평면 검출
        hist, bin_edges = np.histogram(  # 히스토그램 생성
            valid_pixels,
            bins=100,
            range=(config.OAK_DEPTH_MIN_MM / 1000.0, config.OAK_DEPTH_MAX_MM / 1000.0),
        )
        dominant_bin = np.argmax(hist)  # 가장 빈도가 높은 빈
        dominant_ratio = hist[dominant_bin] / max(valid_pixels.size, 1)  # 지배 비율 계산

        if dominant_ratio > config.OAK_WALL_RATIO_THRESH:  # 지배 비율이 임계값 초과
            d_low  = bin_edges[dominant_bin]  # 낮은 깊이 경계
            d_high = bin_edges[dominant_bin + 1]  # 높은 깊이 경계
            # ±10% 허용 범위 포함
            margin = (d_high - d_low) * 0.5 + 0.1
            wall_mask = (  # 벽 마스크 생성
                (depth_m >= d_low - margin) &
                (depth_m <= d_high + margin) &
                valid_mask.astype(bool)
            )
            depth_filtered[wall_mask] = 0.0  # 벽 픽셀을 0으로 마스킹

        return depth_filtered, wall_mask  # 필터링된 깊이 맵과 벽 마스크 반환

    # ── 장애물 후보 추출 ──────────────────────────────────────────
    # 필터링된 깊이 맵에서 장애물 후보를 추출하는 메서드
    def _extract_obstacles(
        self,
        depth_filtered: np.ndarray,  # 필터링된 깊이 맵
        valid_mask: np.ndarray,  # 유효 마스크
        wall_mask: np.ndarray,  # 벽 마스크
    ) -> List[OakObstacle]:
        """
        유효한 깊이맵에서 연결 성분(connected component)으로
        장애물 후보를 추출한다.
        """
        h, w = depth_filtered.shape  # 깊이 맵 크기
        hfov_rad = np.deg2rad(config.OAK_HFOV_DEG)  # 수평 시야각을 라디안으로

        # 이진화: 유효 + 비-벽 픽셀
        binary = (
            (depth_filtered > 0) &
            valid_mask.astype(bool) &
            (~wall_mask)
        ).astype(np.uint8) * 255  # 이진 이미지 생성

        # 모폴로지 처리로 파편 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # 타원형 커널
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)  # 닫기 연산
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  kernel)  # 열기 연산

        # 연결 성분 레이블링
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary)
        obstacles: List[OakObstacle] = []  # 장애물 리스트 초기화
        min_area = 400  # 최소 픽셀 면적

        for lbl in range(1, num_labels):  # 각 레이블에 대해 (0은 배경)
            area = stats[lbl, cv2.CC_STAT_AREA]  # 면적
            if area < min_area:  # 최소 면적 미만이면 건너뜀
                continue

            x0 = stats[lbl, cv2.CC_STAT_LEFT]  # 바운딩 박스 좌측
            y0 = stats[lbl, cv2.CC_STAT_TOP]   # 상단
            bw = stats[lbl, cv2.CC_STAT_WIDTH]  # 너비
            bh = stats[lbl, cv2.CC_STAT_HEIGHT]  # 높이
            cx = x0 + bw // 2  # 중심 x
            cy = y0 + bh // 2  # 중심 y

            # 해당 성분의 중위 거리 계산
            region_depth = depth_filtered[labels == lbl]  # 해당 레이블의 깊이 값
            region_depth = region_depth[region_depth > 0]  # 유효 깊이만
            if region_depth.size == 0:  # 유효 깊이가 없으면 건너뜀
                continue
            dist_m = float(np.median(region_depth))  # 중위 거리

            # 수평 각도 계산
            px_from_center = cx - w / 2.0  # 중심으로부터의 픽셀 거리
            angle_deg = float(np.degrees(  # 각도로 변환
                np.arctan(px_from_center / (w / 2.0) * np.tan(hfov_rad / 2.0))
            ))

            # 신뢰도 계산: 가장자리 여부 + 유효 픽셀 비율
            edge_w = int(w * config.OAK_EDGE_MARGIN)  # 가장자리 너비
            edge_h = int(h * config.OAK_EDGE_MARGIN)  # 가장자리 높이
            is_edge = (x0 < edge_w or (x0 + bw) > (w - edge_w) or  # 가장자리에 있는지
                       y0 < edge_h or (y0 + bh) > (h - edge_h))
            valid_ratio = region_depth.size / max(area, 1)  # 유효 픽셀 비율
            confidence = (config.WEIGHT_OAK_EDGE if is_edge else config.WEIGHT_OAK_CENTER) * valid_ratio  # 신뢰도 계산

            # 장애물 객체 생성 및 리스트에 추가
            obstacles.append(OakObstacle(
                distance_m  = dist_m,  # 거리
                angle_deg   = angle_deg,  # 각도
                bbox_norm   = (x0 / w, y0 / h, (x0 + bw) / w, (y0 + bh) / h),  # 정규화 바운딩 박스
                confidence  = float(np.clip(confidence, 0.0, 1.0)),  # 신뢰도 클리핑
                is_wall     = False,  # 벽 아님
            ))

        # 거리 순으로 정렬 (가까운 순)
        obstacles.sort(key=lambda o: o.distance_m)
        return obstacles  # 장애물 리스트 반환

    # ── 디버그 시각화 ─────────────────────────────────────────────
    # 프레임을 시각화하는 메서드
    def visualize(self, frame: OakFrame) -> np.ndarray:
        # RGB 프레임이 있으면 실물 화면(RGB)을 사용하고, 없으면 기존 깊이 맵(Depth)을 사용합니다.
        if frame.rgb_frame is not None:
            vis_img = frame.rgb_frame.copy()
            h, w = vis_img.shape[:2]
            title = "OAK-D-Lite (RGB)"
        else:
            # 깊이 맵을 컬러맵으로 변환
            depth_vis = cv2.normalize(
                frame.depth_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
            )
            vis_img = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)  # JET 컬러맵 적용
            h, w = frame.depth_map.shape
            title = "OAK-D-Lite (Depth)"

        # 각 장애물에 대해 바운딩 박스와 텍스트 표시
        for obs in frame.obstacles:
            x1 = int(obs.bbox_norm[0] * w)  # 바운딩 박스 좌측
            y1 = int(obs.bbox_norm[1] * h)  # 상단
            x2 = int(obs.bbox_norm[2] * w)  # 우측
            y2 = int(obs.bbox_norm[3] * h)  # 하단
            # 거리에 따라 색상 결정
            color = (0, 255, 0) if obs.distance_m > config.ZONE_WARNING_M else (0, 165, 255)  # 초록 또는 주황
            if obs.distance_m < config.ZONE_DANGER_M:
                color = (0, 0, 255)  # 빨강 (위험)
            cv2.rectangle(vis_img, (x1, y1), (x2, y2), color, 2)  # 바운딩 박스 그리기
            cv2.putText(  # 거리와 각도 텍스트 표시
                vis_img,
                f"{obs.distance_m:.2f}m {obs.angle_deg:+.0f}deg",
                (x1, max(y1 - 4, 12)),  # 위치
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1,
            )

        # 제목 표시
        cv2.putText(vis_img, title, (6, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        return vis_img  # 시각화된 이미지 반환
