"""
obstacle_avoidance.py
장애물 회피 판단 및 로봇 명령 생성

구역 분류:
  DANGER  (< 0.5m) : 즉시 정지
  WARNING (< 1.2m) : 감속 + 경로 우회 탐색
  SAFE    (>= 1.2m): 정상 주행

회피 방향 결정:
  - 정면 장애물: 좌/우 중 더 넓은 공간으로 우회
  - 사각지대 장애물: 해당 방향 회피
  - 복수 장애물: 가중 합으로 최적 방향 선택
"""

from __future__ import annotations  # 미래 버전 호환성 (타입 힌트)
import math  # 수학 함수
import time  # 시간 관련 함수
import numpy as np  # 수치 계산 라이브러리
from dataclasses import dataclass, field  # 데이터 클래스 데코레이터
from enum import Enum, auto  # 열거형
from typing import List, Optional, Dict  # 타입 힌트
import config  # 설정 파일 임포트
from sensor_fusion import FusedObstacle  # 센서 융합 모듈에서 FusedObstacle 임포트


class ZoneLevel(Enum):
    """장애물 위험 구역 레벨 열거형"""
    SAFE    = auto()  # 안전 구역
    WARNING = auto()  # 경고 구역
    DANGER  = auto()  # 위험 구역


class AvoidDirection(Enum):
    """회피 방향 열거형"""
    NONE  = auto()  # 회피 없음
    LEFT  = auto()  # 좌측 회피
    RIGHT = auto()  # 우측 회피
    BACK  = auto()  # 후진 또는 제자리 회전 (사방 막힘)


@dataclass
class RobotCommand:
    """로봇 구동부로 전달할 명령 데이터 클래스"""
    linear_speed: float      # 전진 속도 0.0~1.0 (정규화)
    angular_speed: float     # 회전 속도 -1.0(좌)~+1.0(우)
    zone: ZoneLevel          # 현재 구역 레벨
    avoid_dir: AvoidDirection  # 회피 방향
    stop: bool               # 즉시 정지 플래그
    nearest_obstacle_m: float  # 가장 가까운 장애물 거리 (미터)
    message: str = ""        # 디버그 메시지

    def __str__(self) -> str:
        """명령을 문자열로 표현"""
        return (
            f"[{self.zone.name}] "
            f"linear={self.linear_speed:.2f} "
            f"angular={self.angular_speed:+.2f} "
            f"avoid={self.avoid_dir.name} "
            f"nearest={self.nearest_obstacle_m:.2f}m"
            + (f" | {self.message}" if self.message else "")
        )


class ObstacleAvoidance:
    """장애물 판단 및 회피 명령 생성기 클래스"""

    def __init__(self):
        """초기화 메서드"""
        self._history: List[RobotCommand] = []  # 명령 히스토리
        self._last_cmd: Optional[RobotCommand] = None  # 마지막 명령
        self._consecutive_danger: int = 0  # 연속 위험 구역 카운트

    # ── 메인 판단 함수 ────────────────────────────────────────────
    def decide(self, obstacles: List[FusedObstacle]) -> RobotCommand:
        """
        융합된 장애물 리스트를 받아 로봇 명령을 생성한다.

        Args:
            obstacles: SensorFusion.fuse() 의 반환값

        Returns:
            RobotCommand
        """
        if not obstacles:
            # 장애물 없음: 안전 명령
            cmd = self._safe_command()
            self._record(cmd)
            return cmd

        # 정면(±45도) 장애물만 추출 (주행 경로 위험도 판단)
        front_obs = [
            o for o in obstacles
            if abs(o.angle_deg) <= 45 and o.distance_m < config.ZONE_SAFE_M
        ]
        # 사각지대 장애물 (전방위)
        blind_obs = [o for o in obstacles if o.is_blind_zone]

        # 가장 가까운 정면 장애물
        nearest_front = min(front_obs, key=lambda o: o.distance_m) if front_obs else None
        # 가장 가까운 사각지대 장애물
        nearest_blind = min(blind_obs, key=lambda o: o.distance_m) if blind_obs else None

        # 실질 위험도: 정면 또는 근접 사각지대 중 더 가까운 것
        effective_nearest = self._effective_nearest(nearest_front, nearest_blind)

        if effective_nearest is None:
            cmd = self._safe_command()
        else:
            zone = self._classify_zone(effective_nearest.distance_m)  # 구역 분류
            cmd  = self._build_command(zone, effective_nearest, obstacles)  # 명령 생성

        self._record(cmd)  # 히스토리 기록
        return cmd

    # ── 구역 분류 ─────────────────────────────────────────────────
    @staticmethod
    def _classify_zone(distance_m: float) -> ZoneLevel:
        """거리에 따라 구역 레벨을 분류"""
        if distance_m < config.ZONE_DANGER_M:
            return ZoneLevel.DANGER  # 위험 구역
        elif distance_m < config.ZONE_WARNING_M:
            return ZoneLevel.WARNING  # 경고 구역
        return ZoneLevel.SAFE  # 안전 구역

    # ── 실질 위험 장애물 선택 ─────────────────────────────────────
    @staticmethod
    def _effective_nearest(
        front: Optional[FusedObstacle],
        blind: Optional[FusedObstacle],
    ) -> Optional[FusedObstacle]:
        """실질적으로 위험한 장애물을 선택"""
        if front is None and blind is None:
            return None  # 장애물 없음
        if front is None:
            return blind  # 사각지대만
        if blind is None:
            return front  # 정면만
        # 사각지대 장애물이 경고 구역 안에 있으면 우선 고려
        if blind.distance_m < config.ZONE_WARNING_M:
            return blind if blind.distance_m < front.distance_m else front
        return front  # 정면 우선

    # ── 명령 생성 ─────────────────────────────────────────────────
    def _build_command(
        self,
        zone: ZoneLevel,
        nearest: FusedObstacle,
        all_obs: List[FusedObstacle],
    ) -> RobotCommand:
        """구역과 장애물 정보를 바탕으로 로봇 명령 생성"""

        if zone == ZoneLevel.DANGER:
            self._consecutive_danger += 1  # 연속 위험 카운트 증가
            avoid_dir = self._choose_avoid_direction(all_obs)  # 회피 방향 선택
            return RobotCommand(
                linear_speed        = 0.0,  # 정지
                angular_speed       = self._avoidance_angular(avoid_dir),  # 회피 회전
                zone                = zone,
                avoid_dir           = avoid_dir,
                stop                = True,  # 즉시 정지
                nearest_obstacle_m  = nearest.distance_m,
                message             = f"STOP: {nearest.source} {nearest.distance_m:.2f}m"
                                      + (" [사각지대]" if nearest.is_blind_zone else ""),
            )

        self._consecutive_danger = 0  # 위험 리셋
        if zone == ZoneLevel.WARNING:
            avoid_dir = self._choose_avoid_direction(all_obs)  # 회피 방향 선택
            # 거리에 비례하여 속도 감소
            speed_ratio = (nearest.distance_m - config.ZONE_DANGER_M) / (
                config.ZONE_WARNING_M - config.ZONE_DANGER_M
            )
            linear  = float(np.clip(speed_ratio * 0.5, 0.1, 0.5))  # 선형 속도
            angular = self._avoidance_angular(avoid_dir) * (1 - speed_ratio) * 0.8  # 각속도
            return RobotCommand(
                linear_speed        = linear,
                angular_speed       = angular,
                zone                = zone,
                avoid_dir           = avoid_dir,
                stop                = False,
                nearest_obstacle_m  = nearest.distance_m,
                message             = f"SLOW: {nearest.source} {nearest.distance_m:.2f}m",
            )

        return self._safe_command(nearest.distance_m)  # 안전 명령

    # ── 회피 방향 선택 ────────────────────────────────────────────
    def _choose_avoid_direction(
        self,
        obstacles: List[FusedObstacle],
    ) -> AvoidDirection:
        """
        좌/우 반구의 장애물 점수를 계산하여 더 여유로운 쪽을 선택한다.
        점수 = Σ (1 / distance_m) * confidence  (값이 낮을수록 여유)
        """
        left_score  = 0.0  # 좌측 점수
        right_score = 0.0  # 우측 점수

        for obs in obstacles:
            if obs.distance_m <= 0:
                continue  # 유효하지 않은 거리
            score = (1.0 / max(obs.distance_m, 0.1)) * obs.confidence  # 점수 계산
            if obs.angle_deg < 0:    # 좌측
                left_score  += score
            else:                    # 우측
                right_score += score

        # 양쪽 모두 막힌 경우
        if left_score > 5.0 and right_score > 5.0:
            return AvoidDirection.BACK  # 후진

        return AvoidDirection.RIGHT if left_score > right_score else AvoidDirection.LEFT  # 더 낮은 점수 방향

    @staticmethod
    def _avoidance_angular(direction: AvoidDirection) -> float:
        """회피 방향에 따른 각속도 매핑"""
        mapping = {
            AvoidDirection.LEFT:  -0.7,  # 좌측 회전
            AvoidDirection.RIGHT: +0.7,  # 우측 회전
            AvoidDirection.BACK:  +1.0,  # 제자리 회전
            AvoidDirection.NONE:   0.0,  # 회전 없음
        }
        return mapping.get(direction, 0.0)

    @staticmethod
    def _safe_command(nearest_m: float = float("inf")) -> RobotCommand:
        """안전 구역 명령 생성"""
        return RobotCommand(
            linear_speed        = 1.0,  # 최대 속도
            angular_speed       = 0.0,  # 직진
            zone                = ZoneLevel.SAFE,
            avoid_dir           = AvoidDirection.NONE,
            stop                = False,
            nearest_obstacle_m  = nearest_m,
            message             = "정상 주행",
        )

    def _record(self, cmd: RobotCommand):
        """명령을 히스토리에 기록"""
        self._last_cmd = cmd
        self._history.append(cmd)
        if len(self._history) > 300:
            self._history.pop(0)  # 오래된 기록 제거

    # ── 통계 요약 ─────────────────────────────────────────────────
    def stats(self) -> Dict[str, float]:
        """히스토리 기반 통계 요약"""
        if not self._history:
            return {}  # 히스토리 없음
        zones = [c.zone for c in self._history]  # 구역 리스트
        return {
            "danger_ratio":  zones.count(ZoneLevel.DANGER)  / len(zones),  # 위험 비율
            "warning_ratio": zones.count(ZoneLevel.WARNING) / len(zones),  # 경고 비율
            "safe_ratio":    zones.count(ZoneLevel.SAFE)    / len(zones),  # 안전 비율
            "avg_nearest_m": float(np.mean([c.nearest_obstacle_m for c in self._history
                                            if c.nearest_obstacle_m < 999])),  # 평균 가까운 거리
        }

    # ── 디버그 시각화 ─────────────────────────────────────────────
    def visualize_command(self, cmd: RobotCommand, size: int = 200) -> "np.ndarray":
        """명령을 시각화하여 이미지로 반환"""
        import cv2  # OpenCV 임포트
        canvas = np.zeros((size, size, 3), dtype=np.uint8)  # 캔버스 생성

        # 구역 색상
        zone_colors = {
            ZoneLevel.SAFE:    (0, 180, 0),    # 녹색
            ZoneLevel.WARNING: (0, 140, 255),  # 주황색
            ZoneLevel.DANGER:  (0, 0, 220),    # 빨간색
        }
        bg_color = zone_colors[cmd.zone]  # 배경 색상
        canvas[:] = [c // 6 for c in bg_color]  # 어두운 배경

        # 구역 텍스트
        cv2.putText(canvas, cmd.zone.name, (8, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, bg_color, 2)

        # 속도 바
        bar_w = int(cmd.linear_speed * (size - 16))  # 바 너비
        cv2.rectangle(canvas, (8, 50), (8 + bar_w, 70), (0, 200, 120), -1)  # 속도 바
        cv2.putText(canvas, f"speed: {cmd.linear_speed:.2f}", (8, 88),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

        # 회피 방향 화살표
        cx, cy = size // 2, 140  # 중심 좌표
        arrow_len = 30  # 화살표 길이
        arrows = {
            AvoidDirection.LEFT:  (-arrow_len, 0),  # 좌측
            AvoidDirection.RIGHT: (+arrow_len, 0),  # 우측
            AvoidDirection.BACK:  (0, +arrow_len),  # 후진
            AvoidDirection.NONE:  (0, -arrow_len),  # 전진
        }
        dx, dy = arrows.get(cmd.avoid_dir, (0, 0))  # 방향 벡터
        cv2.arrowedLine(canvas, (cx, cy), (cx + dx, cy + dy), bg_color, 3, tipLength=0.4)  # 화살표 그리기

        # 가장 가까운 장애물 거리
        dist_txt = (f"{cmd.nearest_obstacle_m:.2f}m"
                    if cmd.nearest_obstacle_m < 99 else "---")  # 거리 텍스트
        cv2.putText(canvas, dist_txt, (8, size - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
        return canvas
