"""
object_classifier.py
식당/홀 환경 최적화 버전

환경별 개선:
  [넓은 홀/식당]
    - 감지 범위 6m로 확대 (기존 ZONE_SAFE + 1.5m)
    - 넓은 공간 기준으로 클러스터 병합 각도 완화
    - 원거리 벽 판단 시 표준편차 임계값 완화

  [사람이 자주 지나다님]
    - 사람 감지 점수 임계값 하향 (0.55 → 0.45)
    - 프레임 간 이동 감지 거리 임계값 완화 (0.05 → 0.03m)
    - 사람 폭 범위 확대 (최대 0.90m - 옷/짐 포함)
    - 이동 감지 시 가중치 상향

  [유리벽/투명 장애물]
    - LiDAR 포인트 없는데 OAK 깊이가 불안정한 구역 → GLASS_WALL 판단
    - OAK 깊이값이 튀거나 NaN 비율 높으면 유리 의심
    - 유리벽은 맵에 특수 마킹
"""

import numpy as np  # 수치 계산 라이브러리
import cv2  # OpenCV 컴퓨터 비전 라이브러리
import math  # 수학 함수
from collections import deque  # 양방향 큐 자료구조
from dataclasses import dataclass, field  # 데이터 클래스 데코레이터
from typing import List, Optional, Tuple, Dict  # 타입 힌트
from enum import Enum, auto  # 열거형
import config  # 설정 파일 임포트
from yolo_detector import YoloDetector


class ObjectType(Enum):
    """객체 타입 열거형"""
    UNKNOWN    = auto()  # 알 수 없는 객체
    WALL       = auto()  # 벽
    OBSTACLE   = auto()  # 장애물
    PERSON     = auto()  # 사람
    GLASS_WALL = auto()  # 유리벽/투명 장애물
    DENIED     = auto()  # LiDAR 감지 → OAK 부정 → 맵에서 제거 대상


@dataclass
class LidarCluster:
    """LiDAR 클러스터 데이터 클래스"""
    center_angle_deg: float  # 클러스터 중심 각도 (도)
    min_angle_deg: float     # 최소 각도 (도)
    max_angle_deg: float     # 최대 각도 (도)
    distance_m: float        # 거리 (미터)
    point_count: int         # 포인트 수
    is_blind_zone: bool      # OAK 시야각 밖인지 여부
    dist_std: float = 0.0    # 거리 표준편차


@dataclass
class ClassifiedObject:
    """분류된 객체 데이터 클래스"""
    object_type: ObjectType      # 객체 타입
    distance_m: float            # 거리 (미터)
    angle_deg: float             # 각도 (도)
    width_m: float               # 폭 (미터)
    height_ratio: float          # 높이 비율 (0-1)
    confidence: float            # 신뢰도 (0-1)
    bbox_norm: Tuple[float, float, float, float]  # 정규화된 바운딩 박스 (x1,y1,x2,y2)
    lidar_confirmed: bool        # LiDAR로 확인되었는지 여부
    source: str                  # 데이터 소스 ("lidar_only", "fused", "oak_only", "oak_glass", "oak_denied")
    wall_score: float   = 0.0    # 벽 점수
    person_score: float = 0.0    # 사람 점수
    glass_score: float  = 0.0    # 유리벽 점수


# ── 시간적 스무딩 트래커 ──────────────────────────────────────────
class ObjectTracker:
    """객체 추적 클래스 - 누적 없이 현재 데이터 즉시 반영"""
    ANGLE_BIN = 10.0 
    MOVE_THRESH_M = 0.03 

    def __init__(self):
        """초기화: 히스토리 큐를 제거하고 이전 거리값만 관리"""
        self._prev_positions: Dict[int, float] = {} 

    def _bin(self, angle_deg: float) -> int:
        return int(round(angle_deg / self.ANGLE_BIN)) * int(self.ANGLE_BIN)

    def update(self, obj: ClassifiedObject) -> ObjectType:
        """
        [수정] 누적 히스토리를 거치지 않고 계산된 타입을 즉시 반환함.
        """
        return obj.object_type

    def is_moving(self, angle_deg: float, distance_m: float) -> bool:
        """이전 프레임 대비 현재 변화만 측정하여 즉시 이동 여부 판단"""
        b = self._bin(angle_deg)
        prev = self._prev_positions.get(b)
        self._prev_positions[b] = distance_m
        
        if prev is None:
            return False
        return abs(distance_m - prev) > self.MOVE_THRESH_M

# ── LiDAR 클러스터 추출 ───────────────────────────────────────────
class LidarClusterer:
    """LiDAR 데이터에서 클러스터를 추출하는 클래스"""
    # 넓은 홀: 병합 각도 완화, 감지 범위 확대
    GAP_ANGLE_DEG = 8.0     # 클러스터 간 각도 갭 (도)
    GAP_DIST_M    = 0.40    # 클러스터 간 거리 갭 (미터) - 넓은 공간: 0.35 → 0.40
    MIN_POINTS    = 3       # 최소 포인트 수
    NOISE_STD_MAX = 0.25    # 노이즈 표준편차 최대값 - 넓은 공간에서 반사 노이즈 허용 완화
    MERGE_ANGLE   = 15.0    # 클러스터 병합 각도 (도) - 넓은 홀: 12 → 15도
    MAX_RANGE_M   = 6.0     # 최대 감지 범위 (미터) - 넓은 홀: ZONE_SAFE+1.5 → 6m

    def extract_clusters(self, scan) -> List[LidarCluster]:
        """LiDAR 스캔에서 클러스터 추출"""
        if scan is None or not scan.points:
            return []  # 스캔 데이터 없음

        # 유효 포인트 필터링 및 정렬
        points = [p for p in scan.points
                  if 0 < p.distance_m <= self.MAX_RANGE_M]  # 범위 내 포인트
        points.sort(key=lambda p: p.angle_deg)  # 각도 기준 정렬

        raw: List[LidarCluster] = []  # 원시 클러스터 리스트
        current: List = []  # 현재 클러스터 포인트

        for pt in points:
            if not current:
                current.append(pt)  # 첫 포인트
                continue
            prev      = current[-1]  # 이전 포인트
            angle_gap = abs(pt.angle_deg  - prev.angle_deg)  # 각도 갭
            dist_gap  = abs(pt.distance_m - prev.distance_m)  # 거리 갭

            if angle_gap > self.GAP_ANGLE_DEG or dist_gap > self.GAP_DIST_M:
                # 갭이 크면 새 클러스터 시작
                if len(current) >= self.MIN_POINTS:
                    c = self._build(current)  # 클러스터 빌드
                    if c:
                        raw.append(c)  # 추가
                current = [pt]  # 새 클러스터 시작
            else:
                current.append(pt)  # 현재 클러스터에 추가

        # 마지막 클러스터 처리
        if len(current) >= self.MIN_POINTS:
            c = self._build(current)
            if c:
                raw.append(c)

        merged = self._merge(raw)  # 클러스터 병합
        merged.sort(key=lambda c: c.distance_m)  # 거리 기준 정렬
        return merged

    def _build(self, points) -> Optional[LidarCluster]:
        """포인트 리스트에서 클러스터 생성"""
        angles   = [p.angle_deg  for p in points]  # 각도 리스트
        dists    = [p.distance_m for p in points]  # 거리 리스트
        dist_std = float(np.std(dists))  # 거리 표준편차
        if dist_std > self.NOISE_STD_MAX and len(points) < 6:
            return None  # 노이즈 클러스터 제외
        center_angle = float(np.mean(angles))  # 중심 각도
        half_fov     = config.OAK_HFOV_DEG / 2.0  # OAK 시야각 절반
        return LidarCluster(
            center_angle_deg = center_angle,
            min_angle_deg    = float(min(angles)),
            max_angle_deg    = float(max(angles)),
            distance_m       = float(np.median(dists)),  # 중앙값 거리
            point_count      = len(points),
            is_blind_zone    = abs(center_angle) > half_fov,  # 시야각 밖
            dist_std         = dist_std,
        )

    def _merge(self, clusters: List[LidarCluster]) -> List[LidarCluster]:
        """유사한 클러스터 병합"""
        if len(clusters) < 2:
            return clusters  # 병합 필요 없음
        merged = []  # 병합 결과
        used   = [False] * len(clusters)  # 사용 여부 플래그
        for i, ci in enumerate(clusters):
            if used[i]:
                continue  # 이미 사용됨
            group = [ci]  # 그룹 시작
            for j, cj in enumerate(clusters[i + 1:], i + 1):
                if used[j]:
                    continue
                # 병합 조건: 각도와 거리 차이
                if (abs(ci.center_angle_deg - cj.center_angle_deg) < self.MERGE_ANGLE
                        and abs(ci.distance_m - cj.distance_m) < 0.35):
                    group.append(cj)  # 그룹에 추가
                    used[j] = True  # 사용 표시
            if len(group) == 1:
                merged.append(ci)  # 단일 클러스터
            else:
                # 그룹 평균 계산
                total = sum(g.point_count for g in group)
                avg_a = sum(g.center_angle_deg * g.point_count for g in group) / total
                avg_d = sum(g.distance_m       * g.point_count for g in group) / total
                hf    = config.OAK_HFOV_DEG / 2.0
                merged.append(LidarCluster(
                    center_angle_deg = avg_a,
                    min_angle_deg    = min(g.min_angle_deg for g in group),
                    max_angle_deg    = max(g.max_angle_deg for g in group),
                    distance_m       = avg_d,
                    point_count      = total,
                    is_blind_zone    = abs(avg_a) > hf,
                    dist_std         = float(np.mean([g.dist_std for g in group])),
                ))
            used[i] = True  # 사용 표시
        return merged


# ── 핵심 분류기 ───────────────────────────────────────────────────
class ObjectClassifier:
    # 임계값 설정 (식당/홀 최적화 유지)
    WALL_SCORE_THRESH   = 0.60
    PERSON_SCORE_THRESH = 0.45
    GLASS_SCORE_THRESH  = 0.55
    WALL_STD_THRESH_NEAR = 0.12
    WALL_STD_THRESH_FAR  = 0.22

    def __init__(self):
        self.clusterer = LidarClusterer()
        self.tracker   = ObjectTracker()
        self.yolo      = YoloDetector()  # YOLOv8 감지기 초기화

    def classify(self, lidar_scan, oak_frame) -> List[ClassifiedObject]:
        """메인 분류 메서드 - 3D 기하 분석과 PC용 YOLOv8 AI 분석의 하이브리드 공간 융합"""
        clusters = self.clusterer.extract_clusters(lidar_scan)
        results: List[ClassifiedObject] = []

        # 1단계: OAK 프레임이 수신되었고, RGB 스트림과 YOLO가 유효하게 구동 가능한 경우 YOLO 추론 가동
        yolo_objects: List[ClassifiedObject] = []
        if oak_frame is not None and oak_frame.rgb_frame is not None and self.yolo.is_available:
            yolo_results = self.yolo.detect(oak_frame.rgb_frame)
            depth_map = oak_frame.depth_map
            
            if depth_map is not None and depth_map.size > 0:
                h, w = depth_map.shape[:2]
                hfov = config.OAK_HFOV_DEG
                
                for det in yolo_results:
                    bbox = det["bbox_norm"]
                    # 2D 바운딩 박스 정규화 영역을 깊이 맵 해상도에 매칭하여 슬라이싱
                    x1 = int(bbox[0] * w)
                    y1 = int(bbox[1] * h)
                    x2 = int(bbox[2] * w)
                    y2 = int(bbox[3] * h)
                    
                    # 2D 박스 영역 내 뎁스 맵 데이터 슬라이스 추출
                    region = depth_map[y1:y2, x1:x2]
                    valid = region[(region > 0.1) & (region < config.OAK_DEPTH_MAX_MM / 1000.0)]
                    
                    # 뎁스 픽셀이 일정 수 이상 유효한 경우 중위값(median)을 사물 거리로 채택
                    if valid.size > 10:
                        raw_dist_m = float(np.median(valid))
                        # OAK 장착 높이(45cm) 보정 적용된 수평 거리 계산
                        h_diff = config.LIDAR_TO_OAK_OFFSET_Y
                        dist_m = math.sqrt(max(0.01, raw_dist_m**2 - h_diff**2))
                    else:
                        # 뎁스 정보가 없거나 시뮬레이션 환경(0)인 경우 기본 1.5m 부여하여 매핑 지원
                        dist_m = 1.5
                        
                    # 수평 각도 계산 (2D 박스 중심 좌표 기준 HFOV 아크탄젠트 프로젝션)
                    cx = (x1 + x2) / 2.0
                    px_from_center = cx - w / 2.0
                    hfov_rad = np.deg2rad(hfov)
                    angle_deg = float(np.degrees(
                        np.arctan(px_from_center / (w / 2.0) * np.tan(hfov_rad / 2.0))
                    ))
                    
                    # ClassifiedObject 패키징 (YOLO 전용 소스 마킹)
                    obj_type = ObjectType.PERSON if det["label"] == "PERSON" else ObjectType.OBSTACLE
                    yolo_objects.append(ClassifiedObject(
                        object_type     = obj_type,
                        distance_m      = dist_m,
                        angle_deg       = angle_deg,
                        width_m         = (x2 - x1) / w * dist_m * math.tan(math.radians(hfov / 2)) * 2,
                        height_ratio    = (y2 - y1) / h,
                        confidence      = det["confidence"],
                        bbox_norm       = bbox,
                        lidar_confirmed = False,
                        source          = "oak_only",  # OAK(YOLO) 단독 검출 임시 마킹
                    ))

        # 2단계: LiDAR 클러스터 분석 수행 및 근접한 YOLO 감지 데이터 공간 융합
        for cluster in clusters:
            if cluster.is_blind_zone or oak_frame is None:
                # OAK 시야 밖은 LiDAR 데이터 단독으로 장애물 생성
                obj = ClassifiedObject(
                    object_type     = ObjectType.OBSTACLE,
                    distance_m      = cluster.distance_m,
                    angle_deg       = cluster.center_angle_deg,
                    width_m         = self._estimate_width(cluster),
                    height_ratio    = 0.0,
                    confidence      = 0.75,
                    bbox_norm       = (0, 0, 0, 0),
                    lidar_confirmed = True,
                    source          = "lidar_only",
                )
                results.append(obj)
                continue

            # LiDAR 클러스터 근처(수평 15도 이내, 거리 0.5m 이내)에 YOLO 감지 객체가 있는지 융합 검증
            matched_yolo = None
            for y_obj in yolo_objects:
                if (abs(y_obj.angle_deg - cluster.center_angle_deg) < 15.0 and
                        abs(y_obj.distance_m - cluster.distance_m) < 0.5):
                    matched_yolo = y_obj
                    break
            
            if matched_yolo is not None:
                # [융합 완료] LiDAR로 물리적 존재성이 증명되고, YOLO로 AI 비주얼 인지 완료된 고신뢰성 장애물
                matched_yolo.lidar_confirmed = True
                matched_yolo.source = "fused"  # 'Fused' 소스로 마크
                matched_yolo.object_type = self.tracker.update(matched_yolo)
                results.append(matched_yolo)
                
                # 매칭된 YOLO 임시 객체는 중복 추가 방지를 위해 목록에서 삭제
                yolo_objects.remove(matched_yolo)
            else:
                # 기존 3D 기하 분석 융합 분류 시도 (YOLO가 감지하지 못했을 때의 완벽한 백업 폴백)
                obj = self._classify_with_oak(cluster, oak_frame)
                if obj:
                    obj.object_type = self.tracker.update(obj)
                    results.append(obj)

        # 3단계: OAK(YOLO) 단독으로 선명히 검출된 사물 추가 (LiDAR 반사 각도 등으로 스캔 누락된 사람/장애물 구조)
        # 단, 실내 정적 노이즈 오탐 방지를 위해 신뢰도가 0.40 이상인 탐지만 안전하게 인정
        for y_obj in yolo_objects:
            if y_obj.confidence >= 0.40:
                results.append(y_obj)

        # 4단계: 특수 유리벽/파티션 감지 결과 반영
        results.extend(self._detect_glass_regions(oak_frame, clusters))

        results.sort(key=lambda o: o.distance_m)
        return results

    # ── 유리벽 탐지 ──────────────────────────────────────────────
    def _detect_glass_regions(
        self, oak_frame, clusters: List[LidarCluster]
    ) -> List[ClassifiedObject]:
        """
        유리벽/투명 장애물 탐지:
          - OAK 깊이맵에서 불안정한 구역 (NaN/0 비율 높음 + 주변 대비 갑자기 깊음)
          - 해당 각도에 LiDAR 포인트가 없거나 매우 적음
        """
        if oak_frame is None:
            return []  # OAK 데이터 없음

        depth_map = oak_frame.depth_map
        if depth_map is None or depth_map.size == 0:
            return []  # 깊이맵 없음

        h, w  = depth_map.shape  # 높이, 너비
        hfov  = config.OAK_HFOV_DEG  # 수평 시야각
        results = []  # 결과 리스트

        # 열 단위로 슬라이딩 윈도우 검사 (20열씩)
        step = 20
        for col_s in range(0, w - step, step):
            col_e  = col_s + step  # 끝 열
            region = depth_map[:, col_s:col_e]  # 영역 추출

            total_pixels = region.size  # 총 픽셀 수
            zero_ratio   = float(np.sum(region < 0.05) / total_pixels)  # 0 비율
            valid        = region[region > 0.1]  # 유효 깊이

            # 유효 픽셀이 거의 없는데 완전히 빈 것도 아님 → 유리 의심
            if 0.40 < zero_ratio < 0.85 and valid.size > 5:
                depth_std = float(np.std(valid))  # 깊이 표준편차
                # 깊이가 불안정하게 튐
                if depth_std > 0.30:
                    center_angle = ((col_s + col_e) / 2 / w - 0.5) * hfov  # 중심 각도
                    depth_median = float(np.median(valid))  # 중앙값 깊이

                    # 해당 각도에 LiDAR 클러스터가 없는지 확인
                    lidar_nearby = any(
                        abs(c.center_angle_deg - center_angle) < 12
                        for c in clusters
                    )
                    if not lidar_nearby:
                        # 유리벽 점수 계산
                        glass_score = float(np.clip(
                            zero_ratio * 0.5 + min(depth_std / 0.5, 1.0) * 0.5,
                            0.0, 1.0,
                        ))
                        if glass_score >= self.GLASS_SCORE_THRESH:
                            results.append(ClassifiedObject(
                                object_type     = ObjectType.GLASS_WALL,
                                distance_m      = depth_median,
                                angle_deg       = center_angle,
                                width_m         = step / w * depth_median * math.tan(
                                    math.radians(hfov / 2)) * 2,  # 폭 계산
                                height_ratio    = 1.0 - zero_ratio,
                                confidence      = glass_score * 0.75,
                                bbox_norm       = (col_s / w, 0.0, col_e / w, 1.0),
                                lidar_confirmed = False,
                                source          = "oak_glass",
                                glass_score     = glass_score,
                            ))

        return results

    # ── OAK 깊이맵 분류 ──────────────────────────────────────────
    def _classify_with_oak(
        self, cluster: LidarCluster, oak_frame
    ) -> Optional[ClassifiedObject]:
        """LiDAR 클러스터를 OAK 깊이맵과 융합하여 분류"""
        depth_map = oak_frame.depth_map
        if depth_map is None or depth_map.size == 0:
            return None  # 깊이맵 없음

        h, w = depth_map.shape  # 높이, 너비
        hfov = config.OAK_HFOV_DEG  # 수평 시야각

        # 클러스터 각도를 이미지 열로 변환
        col_l = self._angle_to_col(cluster.min_angle_deg, w, hfov)
        col_r = self._angle_to_col(cluster.max_angle_deg, w, hfov)
        col_l, col_r = sorted([col_l, col_r])  # 정렬
        col_l = max(0, col_l - 8)  # 여유 추가
        col_r = min(w, col_r + 8)

        if col_r - col_l < 3:
            return None  # 너무 좁음

        region = depth_map[:, col_l:col_r]  # 관심 영역
        valid  = region[(region > 0.1) & (region < config.OAK_DEPTH_MAX_MM / 1000.0)]  # 유효 깊이

        # OAK 부정 판단:
        # 해당 구역 유효 픽셀이 거의 없고 (깊이 데이터 없음)
        # LiDAR 거리보다 훨씬 먼 곳에 깊이가 잡히면 → 실제 장애물 없음
        total_pixels = region.size
        valid_ratio  = valid.size / max(total_pixels, 1)  # 유효 픽셀 비율
        if valid_ratio < 0.08:
            # 유효 픽셀 8% 미만 → OAK가 해당 구역에서 아무것도 못 잡음 → 부정
            return ClassifiedObject(
                object_type     = ObjectType.DENIED,
                distance_m      = cluster.distance_m,
                angle_deg       = cluster.center_angle_deg,
                width_m         = self._estimate_width(cluster),
                height_ratio    = 0.0,
                confidence      = 0.80,
                bbox_norm       = (col_l / w, 0.0, col_r / w, 1.0),
                lidar_confirmed = True,
                source          = "oak_denied",
            )

        if valid.size < 20:
            return None  # 유효 픽셀 부족

        # OAK 깊이 중앙값이 LiDAR 거리보다 0.5m 이상 멀면 → 장애물 없음
        raw_median = float(np.median(valid))
        h_diff = config.LIDAR_TO_OAK_OFFSET_Y
        oak_median_check = math.sqrt(max(0.01, raw_median**2 - h_diff**2))
        
        if oak_median_check > cluster.distance_m + 0.5 and valid_ratio < 0.25:
            return ClassifiedObject(
                object_type     = ObjectType.DENIED,
                distance_m      = cluster.distance_m,
                angle_deg       = cluster.center_angle_deg,
                width_m         = self._estimate_width(cluster),
                height_ratio    = 0.0,
                confidence      = 0.70,
                bbox_norm       = (col_l / w, 0.0, col_r / w, 1.0),
                lidar_confirmed = True,
                source          = "oak_denied",
            )

        depth_median = oak_median_check  # OAK 깊이 중앙값 (수평 보정 거리)
        depth_std    = float(np.std(valid))     # OAK 깊이 표준편차
        width_ratio  = (col_r - col_l) / w       # 폭 비율

        # 원거리 여부에 따라 벽 std 임계값 다르게 적용
        wall_std_thresh = (self.WALL_STD_THRESH_FAR
                           if cluster.distance_m > 3.0
                           else self.WALL_STD_THRESH_NEAR)

        # 벽 점수 계산
        wall_score   = self._wall_score(
            region, depth_map, depth_median, depth_std,
            width_ratio, cluster, h, w, col_l, col_r, wall_std_thresh,
        )
        width_m              = self._estimate_width(cluster)  # 폭 추정
        height_ratio, person_score = self._person_score(
            depth_map, cluster, col_l, col_r, h, width_m
        )  # 사람 점수 계산

        dist_match = abs(depth_median - cluster.distance_m) < 0.35  # 거리 일치 여부

        # 객체 타입 결정
        if wall_score >= self.WALL_SCORE_THRESH:
            obj_type   = ObjectType.WALL
            confidence = 0.70 + wall_score * 0.25
        elif person_score >= self.PERSON_SCORE_THRESH:
            obj_type   = ObjectType.PERSON
            confidence = 0.65 + person_score * 0.30
        else:
            obj_type   = ObjectType.OBSTACLE
            confidence = 0.60 + (1 - wall_score) * 0.20

        if not dist_match:
            confidence *= 0.80  # 거리 불일치 패널티

        return ClassifiedObject(
            object_type     = obj_type,
            distance_m      = depth_median if dist_match else cluster.distance_m,
            angle_deg       = cluster.center_angle_deg,
            width_m         = width_m,
            height_ratio    = height_ratio,
            confidence      = float(np.clip(confidence, 0.0, 1.0)),  # 신뢰도 클리핑
            bbox_norm       = (col_l / w, 0.0, col_r / w,
                                min(1.0, height_ratio + 0.05)),  # 바운딩 박스
            lidar_confirmed = True,
            source          = "fused",
            wall_score      = wall_score,
            person_score    = person_score,
        )

    # ── 벽 점수 ──────────────────────────────────────────────────
    def _wall_score(
        self, region, depth_map, depth_median, depth_std,
        width_ratio, cluster, h, w, col_l, col_r, std_thresh,
    ) -> float:
        """벽 점수 계산"""
        score = 0.0

        # 1. 깊이 표준편차 (거리별 임계값)
        std_score = float(np.clip(1.0 - (depth_std - 0.04) / (std_thresh * 2), 0.0, 1.0))
        score += std_score * 0.30

        # 2. 수평 폭 비율
        score += float(np.clip(width_ratio / 0.35, 0.0, 1.0)) * 0.25

        # 3. 수직 연속성
        col_mid   = (col_l + col_r) // 2  # 중앙 열
        col_slice = depth_map[:, max(0, col_mid - 3): col_mid + 3]  # 슬라이스
        in_range  = ((col_slice > depth_median - 0.25) &
                     (col_slice < depth_median + 0.25))  # 범위 내
        vert_cont = float(np.sum(np.any(in_range, axis=1))) / h  # 수직 연속성
        score += float(np.clip(vert_cont / 0.65, 0.0, 1.0)) * 0.25

        # 4. LiDAR 클러스터 거리 표준편차 낮으면 평면
        lidar_std_score = float(np.clip(1.0 - cluster.dist_std / 0.18, 0.0, 1.0))
        score += lidar_std_score * 0.20

        return float(np.clip(score, 0.0, 1.0))  # 점수 클리핑

    # ── 사람 점수 ────────────────────────────────────────────────
    def _person_score(
        self, depth_map, cluster, col_l, col_r, h, width_m
    ) -> Tuple[float, float]:
        """사람 점수 계산"""
        score = 0.0

        col_mid   = (col_l + col_r) // 2  # 중앙 열
        col_slice = depth_map[:, max(0, col_mid - 5): col_mid + 5]  # 슬라이스
        row_valid = np.any(
            (col_slice > 0.1) & (col_slice < cluster.distance_m + 0.5),
            axis=1,
        )  # 유효 행
        height_ratio = float(np.sum(row_valid) / h)  # 높이 비율

        # 1. 높이 비율 (30~90%)
        if 0.28 <= height_ratio <= 0.90:
            score += 0.28
        elif height_ratio > 0.90:
            score += 0.08

        # 2. 폭 (0.20~0.90m - 짐/코트 포함)
        if 0.20 <= width_m <= 0.90:
            score += 0.28
        elif width_m < 0.20:
            score += 0.08

        # 3. 종횡비
        if width_m > 0:
            aspect = (height_ratio * 2.0) / max(width_m, 0.1)  # 종횡비 계산
            if aspect > 1.4:
                score += 0.18

        # 4. 이동 감지 (식당 환경: 가중치 상향 0.20 → 0.26)
        if self.tracker.is_moving(cluster.center_angle_deg, cluster.distance_m):
            score += 0.26

        return height_ratio, float(np.clip(score, 0.0, 1.0))  # 높이 비율과 점수 반환

    # ── OAK 단독 장애물 ──────────────────────────────────────────
    def _oak_only_obstacles(
        self, oak_frame, confirmed: List[LidarCluster]
    ) -> List[ClassifiedObject]:
        """OAK에서만 감지된 장애물 처리"""
        results = []
        confirmed_angles = {c.center_angle_deg for c in confirmed}  # 확인된 각도 집합
        for obs in oak_frame.obstacles:
            if obs.is_wall:
                continue  # 벽 제외
            # 이미 LiDAR로 확인된 각도 근처 제외
            if any(abs(obs.angle_deg - ca) < 15 for ca in confirmed_angles):
                continue
            results.append(ClassifiedObject(
                object_type     = ObjectType.OBSTACLE,
                distance_m      = obs.distance_m,
                angle_deg       = obs.angle_deg,
                width_m         = 0.3,
                height_ratio    = 0.0,
                confidence      = obs.confidence * 0.65,
                bbox_norm       = obs.bbox_norm,
                lidar_confirmed = False,
                source          = "oak_only",
            ))
        return results

    # ── 유틸 ─────────────────────────────────────────────────────
    @staticmethod
    def _angle_to_col(angle_deg: float, img_width: int, hfov_deg: float) -> int:
        """각도를 이미지 열 인덱스로 변환"""
        ratio = (angle_deg + hfov_deg / 2) / hfov_deg  # 비율 계산
        return int(np.clip(ratio * img_width, 0, img_width - 1))  # 클리핑 후 반환

    @staticmethod
    def _estimate_width(cluster: LidarCluster) -> float:
        """클러스터 폭 추정"""
        span = abs(cluster.max_angle_deg - cluster.min_angle_deg)  # 각도 범위
        return max(0.1, cluster.distance_m * math.tan(
            math.radians(max(span, 1.0) / 2)) * 2)  # 삼각법으로 폭 계산

    # ── 시각화 ───────────────────────────────────────────────────
    def visualize(
        self, oak_frame, objects: List[ClassifiedObject]
    ) -> np.ndarray:
        """객체 분류 결과를 시각화 (Premium High-Contrast SF HUD UI)"""
        if oak_frame is None:
            canvas = np.zeros((400, 640, 3), dtype=np.uint8)  # 빈 캔버스
            cv2.putText(canvas, "OAK: N/A", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
            return canvas

        # RGB 프레임이 있으면 실물 화면(RGB)을 사용하고, 없으면 기존 깊이 맵(Depth)을 사용
        if oak_frame.rgb_frame is not None:
            canvas = oak_frame.rgb_frame.copy()
            h, w = canvas.shape[:2]
        else:
            # 깊이맵을 컬러맵으로 변환 (폴백)
            depth_vis = cv2.normalize(
                oak_frame.depth_map, None, 0, 255,
                cv2.NORM_MINMAX, dtype=cv2.CV_8U,
            )
            canvas = cv2.applyColorMap(depth_vis, cv2.COLORMAP_TURBO)
            h, w   = canvas.shape[:2]

        # 프리미엄 HSL 기반 매핑 색상 (BGR 포맷)
        TYPE_COLOR = {
            ObjectType.WALL:       (130, 130, 130),  # 플래티넘 그레이
            ObjectType.OBSTACLE:   (40,  160, 240),  # 테라코타 오렌지
            ObjectType.PERSON:     (80,  220, 100),  # 애시드 그린
            ObjectType.GLASS_WALL: (230, 210,  80),  # 일렉트릭 시안
            ObjectType.UNKNOWN:    (180, 180,  60),  # 샌드 옐로
        }
        TYPE_LABEL = {
            ObjectType.WALL:       "WALL",
            ObjectType.OBSTACLE:   "OBSTACLE",
            ObjectType.PERSON:     "PERSON",
            ObjectType.GLASS_WALL: "GLASS WALL",
            ObjectType.UNKNOWN:    "UNKNOWN",
        }

        for obj in objects:
            x1 = int(obj.bbox_norm[0] * w)
            y1 = int(obj.bbox_norm[1] * h)
            x2 = int(obj.bbox_norm[2] * w)
            y2 = int(obj.bbox_norm[3] * h)
            if x2 - x1 < 2 or y2 - y1 < 2:
                continue

            color = TYPE_COLOR.get(obj.object_type, (180, 180, 180))
            
            # [프리미엄 1] 하이테크 모서리 꺾쇠(Corner Brackets) 그리기
            box_w = x2 - x1
            box_h = y2 - y1
            corner_len = int(min(box_w, box_h) * 0.15)
            corner_len = max(5, min(corner_len, 25))
            
            if obj.object_type == ObjectType.GLASS_WALL:
                # 유리벽 점선 표시
                for i in range(x1, x2, 8):
                    cv2.line(canvas, (i, y1), (min(i+4, x2), y1), color, 1)
                    cv2.line(canvas, (i, y2), (min(i+4, x2), y2), color, 1)
                for j in range(y1, y2, 8):
                    cv2.line(canvas, (x1, j), (x1, min(j+4, y2)), color, 1)
                    cv2.line(canvas, (x2, j), (x2, min(j+4, y2)), color, 1)
            else:
                # 얇은 배경 사각형
                cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 1)
                
                # 네 모서리에 좀 더 두꺼운 꺾쇠를 그려 스캔 느낌을 강화 (fused 상태 시 더 강조)
                cthick = 3 if obj.lidar_confirmed else 2
                # 좌상단
                cv2.line(canvas, (x1, y1), (x1 + corner_len, y1), color, cthick)
                cv2.line(canvas, (x1, y1), (x1, y1 + corner_len), color, cthick)
                # 우상단
                cv2.line(canvas, (x2, y1), (x2 - corner_len, y1), color, cthick)
                cv2.line(canvas, (x2, y1), (x2, y1 + corner_len), color, cthick)
                # 좌하단
                cv2.line(canvas, (x1, y2), (x1 + corner_len, y2), color, cthick)
                cv2.line(canvas, (x1, y2), (x1, y2 - corner_len), color, cthick)
                # 우하단
                cv2.line(canvas, (x2, y2), (x2 - corner_len, y2), color, cthick)
                cv2.line(canvas, (x2, y2), (x2, y2 - corner_len), color, cthick)

            # [프리미엄 2] 반투명 텍스트 어둡게 오버레이
            label_text = TYPE_LABEL.get(obj.object_type, "?")
            src_str = "FUSED" if obj.source == "fused" else "OAK"
            if obj.source == "lidar_only":
                src_str = "LIDAR"
            elif obj.source == "oak_glass":
                src_str = "GLASS"
            
            line1 = f" {label_text} {obj.distance_m:.1f}m [{src_str}]"
            line2 = f" CONF: {obj.confidence:.0%}"
            if obj.object_type == ObjectType.WALL:
                line2 += f" | W:{obj.wall_score:.2f}"
            elif obj.object_type == ObjectType.PERSON:
                line2 += f" | P:{obj.person_score:.2f}"
            elif obj.object_type == ObjectType.GLASS_WALL:
                line2 += f" | G:{obj.glass_score:.2f}"

            # 텍스트 렌더링에 필요한 크기 측정
            (l1_w, l1_h), _ = cv2.getTextSize(line1, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
            (l2_w, l2_h), _ = cv2.getTextSize(line2, cv2.FONT_HERSHEY_SIMPLEX, 0.36, 1)
            
            p_w = max(l1_w, l2_w) + 12
            p_h = l1_h + l2_h + 12
            
            # 박스 표시할 좌표 지정 (바운딩 박스 좌상단 기준, 위 공간 없을 시 내부 표시)
            px1 = x1
            py1 = y1 - p_h - 4
            if py1 < 5:
                py1 = y1 + 5
            
            px2 = min(px1 + p_w, w - 5)
            py2 = min(py1 + p_h, h - 5)
            
            # 반투명 배경 합성
            sub_region = canvas[py1:py2, px1:px2]
            if sub_region.size > 0:
                overlay = sub_region.copy()
                cv2.rectangle(overlay, (0, 0), (px2 - px1, py2 - py1), (10, 10, 10), -1)
                cv2.addWeighted(overlay, 0.65, sub_region, 0.35, 0, sub_region)
                canvas[py1:py2, px1:px2] = sub_region
                
                # 텍스트의 외곽 경계선 (네온 하이라이팅 라인)
                cv2.rectangle(canvas, (px1, py1), (px2, py2), color, 1)
                
                # 텍스트 그리기
                cv2.putText(canvas, line1, (px1 + 4, py1 + l1_h + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(canvas, line2, (px1 + 4, py1 + l1_h + l2_h + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.36, color, 1, cv2.LINE_AA)
                
                # [프리미엄 3] 신뢰도 미니 게이지 바
                bar_x1 = px1 + 4
                bar_x2 = px2 - 6
                bar_y = py2 - 4
                cv2.line(canvas, (bar_x1, bar_y), (bar_x2, bar_y), (50, 50, 50), 2)  # 배경 회색 바
                active_x2 = int(bar_x1 + (bar_x2 - bar_x1) * obj.confidence)
                cv2.line(canvas, (bar_x1, bar_y), (active_x2, bar_y), color, 2)     # 신뢰도 연동 컬러 바

        # 범례 표시 (투명 어두운 하단 바 형태)
        legend_y1 = h - 26
        legend_region = canvas[legend_y1:h-2, 2:w-2]
        if legend_region.size > 0:
            overlay = legend_region.copy()
            cv2.rectangle(overlay, (0, 0), (w - 4, h - legend_y1 - 2), (20, 20, 20), -1)
            cv2.addWeighted(overlay, 0.7, legend_region, 0.3, 0, legend_region)
            canvas[legend_y1:h-2, 2:w-2] = legend_region
            cv2.rectangle(canvas, (2, legend_y1), (w - 2, h - 2), (60, 60, 60), 1)

        items = [
            ((130, 130, 130), "WALL"),
            ((40,  160, 240), "OBSTACLE"),
            ((80,  220, 100), "PERSON"),
            ((230, 210,  80), "GLASS"),
        ]
        lx, ly = 8, h - 10
        for color, lbl in items:
            cv2.rectangle(canvas, (lx, ly - 8), (lx + 8, ly), color, -1)
            cv2.putText(canvas, lbl, (lx + 12, ly - 1),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (220, 220, 220), 1, cv2.LINE_AA)
            lx += 75

        # 총 객체 수 배지
        objs_text = f"SCANNED OBJS: {len(objects)}"
        (tx_w, _), _ = cv2.getTextSize(objs_text, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)
        cv2.putText(canvas, objs_text, (w - tx_w - 12, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.34, (200, 255, 200), 1, cv2.LINE_AA)

        return canvas