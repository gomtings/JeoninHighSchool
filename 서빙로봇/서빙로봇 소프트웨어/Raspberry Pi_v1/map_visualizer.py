"""
map_visualizer.py
1280 x 960 대시보드 GUI 및 2D SLAM 점유 격자 지도 시각화 모듈

레이아웃:
  - Total Size: 1280 x 960
  - Left Panel (380 x 960): 서빙로봇 현재 위치 패널, Target X/Y 입력 필드, 주행시작/초기화/비상정지 버튼, 시스템 정보
  - Right Panel (900 x 960): 2D 점유 맵, 로봇 Pose, 7방향 추천 화살표, 목표 과녁 오버레이
"""

import cv2
import numpy as np
import math
from typing import Optional, Tuple, Dict, Any
from mapper import OccupancyMap, CELL_FREE, CELL_WALL, CELL_OBSTACLE, CELL_UNKNOWN
from path_recommender import PathRecommendation, DirectionScore
import config


class MapVisualizer:
    # ── 창 및 패널 규격 ───────────────────────────────────────────────
    WINDOW_WIDTH  = 1280
    WINDOW_HEIGHT = 960

    LEFT_PANEL_W  = 380
    MAP_WIDTH     = 900
    MAP_HEIGHT    = 960

    # ── 색상 팔레트 (Ultra-Modern Cyberpunk Sleek Dark - BGR) ──────────
    COLOR_BG_DARK       = (14, 18, 24)       # 패널 배경 (딥 미드나이트)
    COLOR_CARD_BG       = (24, 30, 40)       # 카드 배경 (슬릭 챠콜)
    COLOR_CARD_BORDER   = (55, 70, 95)       # 카드 테두리 (네온 스트라이프)
    COLOR_TEXT_WHITE    = (250, 252, 255)    # 주 텍스트
    COLOR_TEXT_GRAY     = (170, 182, 198)    # 보조 텍스트
    COLOR_TEXT_DIM      = (115, 128, 145)    # 희미한 텍스트

    # 울트라 모던 버튼 색상
    COLOR_BTN_START     = (40, 160, 70)      # 주행 시작 (네온 에메랄드)
    COLOR_BTN_START_HOV = (60, 210, 95)
    COLOR_BTN_RESET     = (180, 125, 30)     # 초기화 (앰버 골드)
    COLOR_BTN_RESET_HOV = (210, 155, 45)
    COLOR_BTN_STOP      = (35, 35, 210)      # 비상정지 (네온 크림슨)
    COLOR_BTN_STOP_HOV  = (55, 55, 240)
    COLOR_BTN_QUIT      = (75, 25, 125)      # 시스템 종료 (다크 메탈릭 시클라멘)
    COLOR_BTN_QUIT_HOV  = (130, 40, 180)

    # 입력창
    COLOR_INPUT_BG      = (18, 22, 30)
    COLOR_INPUT_BORDER  = (65, 80, 105)
    COLOR_INPUT_ACTIVE  = (240, 190, 40)     # 활성화 시 네온 시안/골드

    # 맵 셀 색상 (슬릭 네온 SLAM 맵 & 듀얼 컬러 레이어링)
    COLOR_UNKNOWN           = (18, 20, 26)       # 미지 영역
    COLOR_FREE              = (225, 230, 235)    # 빈 공간 (밝은 슬레이트 세라믹)
    COLOR_STATIC_WALL       = (90, 100, 115)     # [사전 저장] 고정 벽 (차분한 슬레이트 블루)
    COLOR_STATIC_OBSTACLE   = (175, 140, 70)     # [사전 저장] 고정 장애물 (차분한 앰버 골드)
    COLOR_LIVE_WALL         = (60, 185, 245)     # [실시간] 새로 감지된 벽 (네온 일렉트릭 블루)
    COLOR_LIVE_OBSTACLE     = (30, 95, 255)      # [실시간] 새로 감지된 장애물 (선명한 네온 코랄 오렌지)
    COLOR_WALL              = (95, 102, 115)     # 기본 벽 색상
    COLOR_OBSTACLE          = (30, 110, 245)     # 기본 장애물 색상
    COLOR_ROBOT             = (240, 200, 30)     # 로봇 위치 (네온 시안)
    COLOR_BEST_DIR          = (80, 235, 120)     # 최적 방향 (일렉트릭 링)
    COLOR_BAD_DIR           = (45, 45, 220)      # 위험 방향 (빨강)
    COLOR_GRID              = (36, 42, 54)       # 격자선
    COLOR_AXIS              = (125, 135, 150)    # 축
    COLOR_LABEL             = (210, 215, 225)    # 레이블

    TICK_INTERVAL_M = 1.0

    # ── 테이블 프리셋 좌표 사전 정의 (X_m, Y_m, Name) ────────────────
    TABLE_PRESETS = {
        "T1": (2.00, 1.50, "Table 1"),
        "T2": (-1.80, 2.20, "Table 2"),
        "T3": (2.20, -1.50, "Table 3"),
        "HOME": (0.00, 0.00, "Kitchen (Home)"),
    }

    # ── UI 요소 ROI (Region of Interest) 정의 (X, Y, W, H) ─────────────
    ROI_INPUT_X       = (30, 226, 150, 36)
    ROI_INPUT_Y       = (200, 226, 150, 36)
    ROI_BTN_T1        = (30, 268, 75, 32)    # [T 1]
    ROI_BTN_T2        = (112, 268, 75, 32)   # [T 2]
    ROI_BTN_T3        = (194, 268, 75, 32)   # [T 3]
    ROI_BTN_HOME      = (276, 268, 74, 32)   # [🏠 HOME]
    ROI_BTN_START     = (30, 306, 320, 32)   # [▶ START CUSTOM DRIVE]
    ROI_BTN_ALIGN_HEAD= (30, 376, 320, 30)   # [🧭 ALIGN HEADING]
    ROI_BTN_SAVE_MAP  = (30, 412, 155, 30)   # [💾 SAVE MAP]
    ROI_BTN_LOAD_MAP  = (195, 412, 155, 30)  # [📂 LOAD MAP]
    ROI_BTN_RESET     = (30, 448, 320, 28)
    ROI_BTN_STOP      = (30, 482, 320, 34)
    ROI_BTN_QUIT      = (30, 522, 320, 30)   # [EXIT / QUIT SYSTEM]

    def __init__(self, occ_map: OccupancyMap):
        self.occ_map = occ_map
        # 900x960 맵 영역에 맞춰 셀 당 픽셀 수 계산
        self.px_per_cell = min(self.MAP_WIDTH / occ_map.width_cells, self.MAP_HEIGHT / occ_map.height_cells)

    def render(
        self,
        recommendation: Optional[PathRecommendation] = None,
        fps: float = 0.0,
        lidar_points: int = 0,
        input_target_x_str: str = "0.00",
        input_target_y_str: str = "0.00",
        active_input: Optional[str] = None,  # 'x' or 'y' or None
        is_driving: bool = False,
        is_emergency: bool = False,
        status_msg: str = "READY",
    ) -> np.ndarray:
        """1280x960 대시보드 렌더링"""
        canvas = np.full((self.WINDOW_HEIGHT, self.WINDOW_WIDTH, 3), self.COLOR_BG_DARK, dtype=np.uint8)

        # 1. 왼쪽 대시보드 패널 렌더링 (0 ~ 380)
        left_panel = self._render_left_panel(
            recommendation=recommendation,
            fps=fps,
            lidar_points=lidar_points,
            input_target_x_str=input_target_x_str,
            input_target_y_str=input_target_y_str,
            active_input=active_input,
            is_driving=is_driving,
            is_emergency=is_emergency,
            status_msg=status_msg,
        )
        canvas[0:960, 0:380] = left_panel

        # 2. 오른쪽 2D SLAM 맵 렌더링 (380 ~ 1280)
        map_canvas = self._render_map_area(recommendation)
        canvas[0:960, 380:1280] = map_canvas

        # 구분선 (Left | Right)
        cv2.line(canvas, (380, 0), (380, 960), (60, 70, 85), 2)

        return canvas

    # ── Left Panel 렌더링 ─────────────────────────────────────────────
    def _render_left_panel(
        self,
        recommendation: Optional[PathRecommendation],
        fps: float,
        lidar_points: int,
        input_target_x_str: str,
        input_target_y_str: str,
        active_input: Optional[str],
        is_driving: bool,
        is_emergency: bool,
        status_msg: str,
    ) -> np.ndarray:
        panel = np.full((self.WINDOW_HEIGHT, self.LEFT_PANEL_W, 3), self.COLOR_BG_DARK, dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Title Header
        cv2.rectangle(panel, (0, 0), (self.LEFT_PANEL_W, 56), (28, 34, 44), -1)
        cv2.putText(panel, "SERVING ROBOT CONTROL", (20, 36), font, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(panel, (0, 56), (self.LEFT_PANEL_W, 56), (55, 65, 80), 1)

        # ─────────────────────────────────────────────────────────────
        # Card 1: 📍 현재 서빙로봇 실시간 위치 좌표 (Real-time Robot Pose & Target)
        # ─────────────────────────────────────────────────────────────
        self._draw_card(panel, (15, 64, 350, 115), "REAL-TIME ROBOT POSE & TARGET")
        
        robot_x = recommendation.robot_x if recommendation else 0.0
        robot_y = recommendation.robot_y if recommendation else 0.0
        robot_deg = recommendation.robot_heading_deg if recommendation else 0.0

        # 실시간 위치 좌표 박스 컨테이너
        cv2.rectangle(panel, (26, 92), (345, 128), (18, 24, 34), -1)
        cv2.rectangle(panel, (26, 92), (345, 128), (55, 75, 105), 1)
        cv2.putText(panel, f"X : {robot_x:+5.2f}m", (34, 116), font, 0.46, (80, 235, 255), 2, cv2.LINE_AA)
        cv2.putText(panel, f"Y : {robot_y:+5.2f}m", (140, 116), font, 0.46, (80, 235, 255), 2, cv2.LINE_AA)
        cv2.putText(panel, f"{robot_deg:+5.1f}*", (250, 116), font, 0.46, (255, 215, 60), 2, cv2.LINE_AA)

        # 목표 정보
        target_name = recommendation.target_name if recommendation and recommendation.target_name else "None"
        dist_str = f"{recommendation.dist_to_goal_m:.2f}m" if recommendation and recommendation.dist_to_goal_m is not None else "--"
        cv2.putText(panel, f"Target: {target_name} | Remain: {dist_str}", (28, 154), font, 0.38, (255, 215, 100), 1, cv2.LINE_AA)

        # ─────────────────────────────────────────────────────────────
        # Card 2: 🎯 테이블 원클릭 프리셋 & 좌표 입력 (Table Presets & Target)
        # ─────────────────────────────────────────────────────────────
        self._draw_card(panel, (15, 186, 350, 158), "TABLE PRESETS & TARGET INPUT")

        # 1) Target X, Y Input Box
        ix_x, ix_y, iw, ih = self.ROI_INPUT_X
        border_x = self.COLOR_INPUT_ACTIVE if active_input == 'x' else self.COLOR_INPUT_BORDER
        cv2.putText(panel, "Target X (m):", (ix_x, ix_y - 7), font, 0.36, self.COLOR_TEXT_GRAY, 1, cv2.LINE_AA)
        cv2.rectangle(panel, (ix_x, ix_y), (ix_x + iw, ix_y + ih), self.COLOR_INPUT_BG, -1)
        cv2.rectangle(panel, (ix_x, ix_y), (ix_x + iw, ix_y + ih), border_x, 2 if active_input == 'x' else 1)
        disp_x = input_target_x_str + ("|" if active_input == 'x' else "")
        cv2.putText(panel, disp_x, (ix_x + 10, ix_y + 24), font, 0.52, self.COLOR_TEXT_WHITE, 2, cv2.LINE_AA)

        border_y = self.COLOR_INPUT_ACTIVE if active_input == 'y' else self.COLOR_INPUT_BORDER
        cv2.putText(panel, "Target Y (m):", (self.ROI_INPUT_Y[0], ix_y - 7), font, 0.36, self.COLOR_TEXT_GRAY, 1, cv2.LINE_AA)
        cv2.rectangle(panel, (self.ROI_INPUT_Y[0], ix_y), (self.ROI_INPUT_Y[0] + iw, ix_y + ih), self.COLOR_INPUT_BG, -1)
        cv2.rectangle(panel, (self.ROI_INPUT_Y[0], ix_y), (self.ROI_INPUT_Y[0] + iw, ix_y + ih), border_y, 2 if active_input == 'y' else 1)
        disp_y = input_target_y_str + ("|" if active_input == 'y' else "")
        cv2.putText(panel, disp_y, (self.ROI_INPUT_Y[0] + 10, ix_y + 24), font, 0.52, self.COLOR_TEXT_WHITE, 2, cv2.LINE_AA)

        # 2) 테이블 프리셋 버튼 4개 [T1] [T2] [T3] [HOME] (주행 중일 때는 잠금/비활성화 시각 효과)
        t_bg = (40, 75, 120) if not is_driving else (26, 32, 42)
        t_border = (70, 130, 210) if not is_driving else (45, 55, 70)
        t_txt_color = (255, 255, 255) if not is_driving else (110, 120, 135)

        home_bg = (110, 65, 30) if not is_driving else (32, 28, 24)
        home_border = (210, 130, 50) if not is_driving else (60, 50, 40)

        t1_x, t1_y, t1_w, t1_h = self.ROI_BTN_T1
        cv2.rectangle(panel, (t1_x, t1_y), (t1_x + t1_w, t1_y + t1_h), t_bg, -1)
        cv2.rectangle(panel, (t1_x, t1_y), (t1_x + t1_w, t1_y + t1_h), t_border, 1)
        cv2.putText(panel, "TABLE 1", (t1_x + 9, t1_y + 21), font, 0.38, t_txt_color, 1, cv2.LINE_AA)

        t2_x, t2_y, t2_w, t2_h = self.ROI_BTN_T2
        cv2.rectangle(panel, (t2_x, t2_y), (t2_x + t2_w, t2_y + t2_h), t_bg, -1)
        cv2.rectangle(panel, (t2_x, t2_y), (t2_x + t2_w, t2_y + t2_h), t_border, 1)
        cv2.putText(panel, "TABLE 2", (t2_x + 9, t2_y + 21), font, 0.38, t_txt_color, 1, cv2.LINE_AA)

        t3_x, t3_y, t3_w, t3_h = self.ROI_BTN_T3
        cv2.rectangle(panel, (t3_x, t3_y), (t3_x + t3_w, t3_y + t3_h), t_bg, -1)
        cv2.rectangle(panel, (t3_x, t3_y), (t3_x + t3_w, t3_y + t3_h), t_border, 1)
        cv2.putText(panel, "TABLE 3", (t3_x + 9, t3_y + 21), font, 0.38, t_txt_color, 1, cv2.LINE_AA)

        th_x, th_y, th_w, th_h = self.ROI_BTN_HOME
        cv2.rectangle(panel, (th_x, th_y), (th_x + th_w, th_y + th_h), home_bg, -1)
        cv2.rectangle(panel, (th_x, th_y), (th_x + th_w, th_y + th_h), home_border, 1)
        cv2.putText(panel, "KITCHEN", (th_x + 8, th_y + 21), font, 0.38, t_txt_color, 1, cv2.LINE_AA)

        # 3) 커스텀 주행 시작 버튼
        bx, by, bw, bh = self.ROI_BTN_START
        btn_start_bg = (40, 150, 65) if not is_driving else (26, 32, 42)
        btn_start_border = (80, 235, 120) if not is_driving else (45, 55, 70)
        btn_start_txt = "> START CUSTOM DRIVE" if not is_driving else "[ DRIVING IN PROGRESS... ]"
        btn_start_txt_color = (255, 255, 255) if not is_driving else (110, 120, 135)
        cv2.rectangle(panel, (bx, by), (bx + bw, by + bh), btn_start_bg, -1)
        cv2.rectangle(panel, (bx, by), (bx + bw, by + bh), btn_start_border, 1 if is_driving else 2)
        cv2.putText(panel, btn_start_txt, (bx + (38 if is_driving else 56), by + 21), font, 0.42 if is_driving else 0.44, btn_start_txt_color, 1, cv2.LINE_AA)

        # ─────────────────────────────────────────────────────────────
        # Card 3: 🕹️ 제어 버튼 (Control Actions)
        # ─────────────────────────────────────────────────────────────
        self._draw_card(panel, (15, 350, 350, 206), "SYSTEM CONTROL PANEL")

        # 1) 헤딩 0°/360° 정렬 버튼
        ax, ay, aw, ah = self.ROI_BTN_ALIGN_HEAD
        cv2.rectangle(panel, (ax, ay), (ax + aw, ay + ah), (30, 100, 180), -1)
        cv2.rectangle(panel, (ax, ay), (ax + aw, ay + ah), (50, 160, 255), 1)
        cv2.putText(panel, "[ ALIGN HEADING (0/360) ]", (ax + 50, ay + 20), font, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # 2) 맵 저장 및 불러오기 버튼 (나란히 배치)
        sx, sy, sw, sh = self.ROI_BTN_SAVE_MAP
        cv2.rectangle(panel, (sx, sy), (sx + sw, sy + sh), (35, 85, 145), -1)
        cv2.rectangle(panel, (sx, sy), (sx + sw, sy + sh), (65, 140, 230), 1)
        cv2.putText(panel, "SAVE MAP", (sx + 36, sy + 20), font, 0.40, (255, 255, 255), 1, cv2.LINE_AA)

        lx, ly, lw, lh = self.ROI_BTN_LOAD_MAP
        cv2.rectangle(panel, (lx, ly), (lx + lw, ly + lh), (110, 70, 30), -1)
        cv2.rectangle(panel, (lx, ly), (lx + lw, ly + lh), (210, 140, 50), 1)
        cv2.putText(panel, "LOAD MAP", (lx + 36, ly + 20), font, 0.40, (255, 255, 255), 1, cv2.LINE_AA)

        # 3) 초기화 버튼
        rx, ry, rw, rh = self.ROI_BTN_RESET
        cv2.rectangle(panel, (rx, ry), (rx + rw, ry + rh), self.COLOR_BTN_RESET, -1)
        cv2.rectangle(panel, (rx, ry), (rx + rw, ry + rh), (220, 170, 50), 1)
        cv2.putText(panel, "RESET MAP & POSE", (rx + 78, ry + 19), font, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # 4) 비상정지 버튼
        ex, ey, ew, eh = self.ROI_BTN_STOP
        cv2.rectangle(panel, (ex, ey), (ex + ew, ey + eh), self.COLOR_BTN_STOP, -1)
        cv2.rectangle(panel, (ex, ey), (ex + ew, ey + eh), (90, 90, 255), 2)
        cv2.putText(panel, "EMERGENCY STOP", (ex + 80, ey + 22), font, 0.46, (255, 255, 255), 2, cv2.LINE_AA)

        # 5) 시스템 종료 버튼 (QUIT SYSTEM)
        qx, qy, qw, qh = self.ROI_BTN_QUIT
        cv2.rectangle(panel, (qx, qy), (qx + qw, qy + qh), self.COLOR_BTN_QUIT, -1)
        cv2.rectangle(panel, (qx, qy), (qx + qw, qy + qh), (190, 60, 230), 2)
        cv2.putText(panel, "QUIT SYSTEM (EXIT)", (qx + 72, qy + 20), font, 0.44, (255, 255, 255), 2, cv2.LINE_AA)

        # ─────────────────────────────────────────────────────────────
        # Card 4: 📊 10° 단위 세분화 경로 분석 & 시스템 상태
        # ─────────────────────────────────────────────────────────────
        self._draw_card(panel, (15, 564, 350, 384), "10-DEG STEP PATH & STATS")

        if recommendation:
            stuck_txt = " [STUCK]" if recommendation.is_stuck else ""
            # 타이틀 구분선 아래로 충분한 여백 확보 (y=614)
            cv2.putText(panel, f"Recommendation: {recommendation.best_label}{stuck_txt}",
                        (30, 614), font, 0.44, (80, 230, 100), 1, cv2.LINE_AA)

            # [실시간 장애물 크기 및 동적 회피 목표치 표시]
            if getattr(recommendation, "obs_w", 0.0) > 0.05:
                cv2.putText(panel, f"Obs Size: W {recommendation.obs_w:.2f}m x L {recommendation.obs_l:.2f}m",
                            (30, 636), font, 0.38, (245, 180, 50), 1, cv2.LINE_AA)
                cv2.putText(panel, f"Avoid: Side {recommendation.target_avoid_w:.2f}m | Pass {recommendation.target_avoid_l:.2f}m",
                            (30, 656), font, 0.38, (80, 235, 255), 1, cv2.LINE_AA)
                reason_y = 678
            else:
                reason_y = 638

            # 상세 사유 줄바꿈 표시
            reason_lines = self._wrap_text(recommendation.reason, max_chars=34)
            for i, line in enumerate(reason_lines[:2]):
                cv2.putText(panel, line, (30, reason_y + i * 19), font, 0.37, (180, 200, 190), 1, cv2.LINE_AA)

        # 맵 통계
        stats = self.occ_map.stats()
        stat_lines = [
            f"Explored Area: {stats['explored_pct']}%",
            f"Free/Wall/Obst: {stats['free']}/{stats['wall']}/{stats['obstacle']}",
            f"LiDAR Pts: {lidar_points}  |  FPS: {fps:.1f}",
            f"Status Msg: {status_msg}",
        ]
        for i, line in enumerate(stat_lines):
            cv2.putText(panel, line, (30, 725 + i * 19), font, 0.36, self.COLOR_TEXT_GRAY, 1, cv2.LINE_AA)

        # 범례 표시 (듀얼 컬러 레이어 안내)
        cv2.putText(panel, "[ Legend ]", (30, 818), font, 0.38, self.COLOR_TEXT_WHITE, 1, cv2.LINE_AA)
        legend = [
            (self.COLOR_FREE, "Free"),
            (self.COLOR_STATIC_WALL, "Static"),
            (self.COLOR_LIVE_OBSTACLE, "Live Obs"),
            (self.COLOR_ROBOT, "Robot"),
        ]
        lx, ly = 30, 844
        for color, label in legend:
            cv2.rectangle(panel, (lx, ly - 10), (lx + 14, ly + 4), color, -1)
            cv2.putText(panel, label, (lx + 18, ly + 2), font, 0.35, self.COLOR_TEXT_GRAY, 1, cv2.LINE_AA)
            lx += 82

        return panel

    def _draw_card(self, panel: np.ndarray, bbox: Tuple[int, int, int, int], title: str):
        x, y, w, h = bbox
        # 카드 배경
        cv2.rectangle(panel, (x, y), (x + w, y + h), self.COLOR_CARD_BG, -1)
        cv2.rectangle(panel, (x, y), (x + w, y + h), self.COLOR_CARD_BORDER, 1)
        # 타이틀 상단 모던 헤더 바
        cv2.rectangle(panel, (x + 1, y + 1), (x + w - 1, y + 24), (32, 40, 54), -1)
        # 좌측 네온 시안 Accent 포인트
        cv2.rectangle(panel, (x + 8, y + 5), (x + 12, y + 19), (240, 190, 40), -1)
        cv2.putText(panel, title, (x + 18, y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.40, self.COLOR_TEXT_WHITE, 1, cv2.LINE_AA)
        cv2.line(panel, (x + 1, y + 24), (x + w - 1, y + 24), (60, 75, 95), 1)

    # ── Right Panel (900x960 2D Map) 렌더링 ───────────────────────────
    def _render_map_area(self, recommendation: Optional[PathRecommendation]) -> np.ndarray:
        MW, MH = self.MAP_WIDTH, self.MAP_HEIGHT
        px = self.px_per_cell
        canvas = np.full((MH, MW, 3), self.COLOR_BG_DARK, dtype=np.uint8)

        grid = self.occ_map.grid
        static_grid = getattr(self.occ_map, "static_grid", None)
        H, W = grid.shape

        # 중앙 정렬을 위한 오프셋
        offset_x = int((MW - W * px) / 2)
        offset_y = int((MH - H * px) / 2)

        cell_px = max(1, int(px))
        for row in range(H):
            for col in range(W):
                val = grid[row, col]
                s_val = static_grid[row, col] if static_grid is not None else CELL_UNKNOWN

                if val == CELL_UNKNOWN:
                    color = self.COLOR_UNKNOWN
                elif val < CELL_WALL:
                    color = self.COLOR_FREE
                elif val < CELL_OBSTACLE:
                    # 벽 (Wall) -> 사전 로드된 정적 벽 vs 실시간 감지 벽
                    if s_val >= CELL_WALL:
                        color = self.COLOR_STATIC_WALL     # 차분한 슬레이트 블루
                    else:
                        color = self.COLOR_LIVE_WALL       # 네온 스카이 블루
                elif val == 0.6:
                    color = (200, 220, 255)                # 유리벽
                else:
                    # 장애물 (Obstacle) -> 사전 로드된 정적 장애물 vs 실시간 동적 장애물
                    if s_val >= CELL_OBSTACLE:
                        color = self.COLOR_STATIC_OBSTACLE # 차분한 앰버 골드
                    else:
                        color = self.COLOR_LIVE_OBSTACLE   # 선명한 네온 코랄 오렌지

                y1 = offset_y + int(row * px)
                x1 = offset_x + int(col * px)
                y2 = min(y1 + cell_px, MH)
                x2 = min(x1 + cell_px, MW)
                if x1 < MW and y1 < MH:
                    canvas[y1:y2, x1:x2] = color

        # 격자선 (1m 간격)
        grid_m = 1.0
        grid_cells = max(1, int(grid_m / self.occ_map.resolution))
        for i in range(0, W, grid_cells):
            x = offset_x + int(i * px)
            cv2.line(canvas, (x, offset_y), (x, offset_y + int(H * px)), self.COLOR_GRID, 1)
        for j in range(0, H, grid_cells):
            y = offset_y + int(j * px)
            cv2.line(canvas, (offset_x, y), (offset_x + int(W * px), y), self.COLOR_GRID, 1)

        # 축 표시 (로봇 0,0 기준)
        rx = offset_x + int(self.occ_map.robot_col * px + px / 2)
        ry = offset_y + int(self.occ_map.robot_row * px + px / 2)

        cv2.line(canvas, (offset_x, ry), (offset_x + int(W * px), ry), self.COLOR_AXIS, 1)
        cv2.line(canvas, (rx, offset_y), (rx, offset_y + int(H * px)), self.COLOR_AXIS, 1)

        # 눈금 숫자 표시
        font = cv2.FONT_HERSHEY_SIMPLEX
        tick_cells = max(1, int(self.TICK_INTERVAL_M / self.occ_map.resolution))
        for col in range(0, W, tick_cells):
            x = offset_x + int(col * px + px / 2)
            cv2.line(canvas, (x, ry - 5), (x, ry + 5), self.COLOR_AXIS, 1)
            if col == self.occ_map.robot_col:
                continue
            x_m = (col - self.occ_map.robot_col) * self.occ_map.resolution
            label = f"{x_m:.0f}" if abs(x_m - round(x_m)) < 1e-6 else f"{x_m:.1f}"
            cv2.putText(canvas, label, (x - 12, ry + 22), font, 0.35, self.COLOR_LABEL, 1, cv2.LINE_AA)

        # [2D 맵 테이블 프리셋 고정 마커 렌더링 (T1, T2, T3, Kitchen/Home)]
        tgt_x = recommendation.target_x if recommendation else None
        tgt_y = recommendation.target_y if recommendation else None

        for p_key, (px_m, py_m, p_name) in self.TABLE_PRESETS.items():
            rel_x = px_m - (recommendation.robot_x if recommendation else 0.0)
            rel_y = py_m - (recommendation.robot_y if recommendation else 0.0)
            row_p, col_p = self.occ_map.world_to_cell(rel_x, rel_y)
            cx = offset_x + int(col_p * px + px / 2)
            cy = offset_y + int(row_p * px + px / 2)

            if 10 <= cx < MW - 10 and 10 <= cy < MH - 10:
                # 현재 선택된 목표 테이블인지 판정
                is_selected = False
                if tgt_x is not None and tgt_y is not None:
                    if abs(px_m - tgt_x) < 0.25 and abs(py_m - tgt_y) < 0.25:
                        is_selected = True

                if is_selected:
                    # 🌟 [선택된 목표 테이블] -> 눈에 확 띄는 네온 옐로우/골드 과녁 마커
                    color_active = (0, 240, 255)
                    cv2.circle(canvas, (cx, cy), 16, color_active, 2, cv2.LINE_AA)
                    cv2.circle(canvas, (cx, cy), 6, color_active, -1, cv2.LINE_AA)
                    cv2.line(canvas, (cx - 20, cy), (cx + 20, cy), color_active, 1, cv2.LINE_AA)
                    cv2.line(canvas, (cx, cy - 20), (cx, cy + 20), color_active, 1, cv2.LINE_AA)
                    # 강조 뱃지 텍스트
                    badge_str = f"TARGET [{p_key}]"
                    cv2.rectangle(canvas, (cx + 12, cy - 14), (cx + 120, cy + 8), (20, 26, 36), -1)
                    cv2.rectangle(canvas, (cx + 12, cy - 14), (cx + 120, cy + 8), color_active, 1)
                    cv2.putText(canvas, badge_str, (cx + 16, cy + 2), font, 0.42, color_active, 1, cv2.LINE_AA)
                else:
                    # ⚪ [일반 대기 테이블] -> 시인성 높은 산뜻한 파스텔 시안/에메랄드
                    if p_key == "HOME":
                        color_idle = (60, 220, 120)   # 주방: 에메랄드 그린
                        label_str = "[KITCHEN]"
                    else:
                        color_idle = (235, 180, 70)   # 일반 테이블: 밝은 골드/스카이
                        label_str = f"[{p_key}]"

                    cv2.circle(canvas, (cx, cy), 10, color_idle, 1, cv2.LINE_AA)
                    cv2.circle(canvas, (cx, cy), 3, color_idle, -1, cv2.LINE_AA)
                    cv2.putText(canvas, label_str, (cx + 12, cy + 4), font, 0.38, color_idle, 1, cv2.LINE_AA)

        for row in range(0, H, tick_cells):
            y = offset_y + int(row * px + px / 2)
            cv2.line(canvas, (rx - 5, y), (rx + 5, y), self.COLOR_AXIS, 1)
            if row == self.occ_map.robot_row:
                continue
            y_m = (self.occ_map.robot_row - row) * self.occ_map.resolution
            label = f"{y_m:.0f}" if abs(y_m - round(y_m)) < 1e-6 else f"{y_m:.1f}"
            cv2.putText(canvas, label, (rx + 10, y + 4), font, 0.35, self.COLOR_LABEL, 1, cv2.LINE_AA)

        # 로봇 원형 표식
        cv2.circle(canvas, (rx, ry), 10, self.COLOR_ROBOT, -1, cv2.LINE_AA)
        cv2.circle(canvas, (rx, ry), 10, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, "ROBOT (0,0)", (rx + 14, ry - 12), font, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # 위험/경고/안전 구역 동심원
        for zone_m, color in [
            (config.ZONE_DANGER_M,  (40,  40, 220)),
            (config.ZONE_WARNING_M, (40, 160, 230)),
            (config.ZONE_SAFE_M,    (60, 210,  60)),
        ]:
            r_px = int(zone_m / self.occ_map.resolution * px)
            cv2.circle(canvas, (rx, ry), r_px, color, 1, cv2.LINE_AA)

        # 경로 추천 및 목표 오버레이 그리기
        if recommendation:
            self._draw_recommendation_overlay(canvas, recommendation, rx, ry, offset_x, offset_y, px)

        return canvas

    def _draw_recommendation_overlay(
        self, canvas: np.ndarray, rec: PathRecommendation, rx: int, ry: int, offset_x: int, offset_y: int, px: float
    ):
        font = cv2.FONT_HERSHEY_SIMPLEX

        # 목표 지점 표시
        if rec.target_x is not None and rec.target_y is not None:
            rel_tx = rec.target_x - rec.robot_x
            rel_ty = rec.target_y - rec.robot_y

            row_t, col_t = self.occ_map.world_to_cell(rel_tx, rel_ty)
            tx = offset_x + int(col_t * px + px / 2)
            ty = offset_y + int(row_t * px + px / 2)

            color_target = (0, 215, 255) if not rec.is_goal_reached else (50, 255, 50)
            cv2.circle(canvas, (tx, ty), 14, color_target, 2, cv2.LINE_AA)
            cv2.circle(canvas, (tx, ty), 5, color_target, -1, cv2.LINE_AA)
            cv2.line(canvas, (tx - 18, ty), (tx + 18, ty), color_target, 1, cv2.LINE_AA)
            cv2.line(canvas, (tx, ty - 18), (tx, ty + 18), color_target, 1, cv2.LINE_AA)

            # 로봇 ~ 목표 가이드 라인
            cv2.line(canvas, (rx, ry), (tx, ty), (0, 190, 255), 1, cv2.LINE_AA)
            label_goal = f"TARGET ({rec.target_x:.1f}, {rec.target_y:.1f})"
            cv2.putText(canvas, label_goal, (tx + 16, ty + 4), font, 0.45, color_target, 1, cv2.LINE_AA)

        # 2D 지도 상단 HUD 배너: 실시간 좌표 (X, Y, Heading) 오버레이
        hud_bg_color = (20, 26, 36)
        hud_border = (60, 75, 95)
        cv2.rectangle(canvas, (20, 15), (480, 55), hud_bg_color, -1)
        cv2.rectangle(canvas, (20, 15), (480, 55), hud_border, 1)
        cv2.rectangle(canvas, (25, 20), (29, 50), (240, 190, 40), -1)
        
        hud_str1 = f"REAL-TIME POSE: X={rec.robot_x:+.2f}m, Y={rec.robot_y:+.2f}m, Head={rec.robot_heading_deg:+.1f} deg"
        cv2.putText(canvas, hud_str1, (38, 40), font, 0.45, (80, 235, 255), 1, cv2.LINE_AA)

        # [2D 맵 전방 장애물 바운딩 박스 & 치수 태그 렌더링]
        if getattr(rec, "obs_w", 0.0) > 0.05:
            # 로봇 전방 장애물 영역 박스 좌표 계산 (로봇 중심 기준)
            half_w = rec.obs_w / 2.0
            y_front_min = 0.15
            y_front_max = y_front_min + max(0.20, rec.obs_l)

            r_top, c_left  = self.occ_map.world_to_cell(-half_w, y_front_max)
            r_bot, c_right = self.occ_map.world_to_cell(half_w, y_front_min)

            bx1 = offset_x + int(min(c_left, c_right) * px)
            by1 = offset_y + int(min(r_top, r_bot) * px)
            bx2 = offset_x + int(max(c_left, c_right) * px + px)
            by2 = offset_y + int(max(r_top, r_bot) * px + px)

            # 형광 오렌지 네온 바운딩 박스
            cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (30, 140, 255), 2, cv2.LINE_AA)
            cv2.rectangle(canvas, (bx1, max(0, by1 - 22)), (bx1 + 175, by1), (20, 26, 36), -1)
            cv2.rectangle(canvas, (bx1, max(0, by1 - 22)), (bx1 + 175, by1), (30, 140, 255), 1)
            obs_tag = f"Obs: W{rec.obs_w:.2f}m x L{rec.obs_l:.2f}m"
            cv2.putText(canvas, obs_tag, (bx1 + 6, max(14, by1 - 6)), font, 0.38, (80, 220, 255), 1, cv2.LINE_AA)

        # 19방향 추천 화살표
        for ds in rec.scores:
            rad = math.radians(ds.angle_deg)
            length = int(ds.clearance_m / self.occ_map.resolution * px * 0.85)
            ex = int(rx + length * math.sin(rad))
            ey = int(ry - length * math.cos(rad))

            if ds.angle_deg == rec.best_angle_deg:
                cv2.arrowedLine(canvas, (rx, ry), (ex, ey), self.COLOR_BEST_DIR, 3, tipLength=0.22, line_type=cv2.LINE_AA)
                cv2.putText(canvas, rec.best_label, (ex + 10, ey - 5), font, 0.55, self.COLOR_BEST_DIR, 2, cv2.LINE_AA)
            else:
                cv2.line(canvas, (rx, ry), (ex, ey), self.COLOR_BAD_DIR, 1, cv2.LINE_AA)

    @staticmethod
    def _wrap_text(text: str, max_chars: int) -> list:
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current += (" " if current else "") + word
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines[:3]