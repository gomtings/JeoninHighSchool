"""
visualize_saved_map.py
saved_map.npz 맵 데이터 분석 및 고대비 컬러 시각화 도구
"""
# cd "c:\GitHub\JeoninHighSchool\서빙로봇\서빙로봇 소프트웨어\Raspberry Pi_v2"
# .\.venv\Scripts\python.exe visualize_saved_map.py

import os
import sys
import numpy as np
import cv2
from mapper import (
    OccupancyMap,
    CELL_UNKNOWN,
    CELL_FREE,
    CELL_WALL,
    CELL_OBSTACLE,
    CELL_GLASS_WALL,
)
from console_utils import safe_print


def main():
    map_npz = "saved_map.npz"
    if not os.path.exists(map_npz):
        safe_print(f"[오류] {map_npz} 파일을 찾을 수 없습니다.")
        return

    # 1. OccupancyMap 인스턴스를 통해 로드 및 갱신 저장
    occ = OccupancyMap()
    if not occ.load_map(map_npz):
        safe_print("[오류] 맵 로드에 실패했습니다.")
        return

    # 2. save_map을 호출하여 최신 고대비 3채널 PNG로 갱신 저장
    occ.save_map(map_npz)

    # 3. 맵 통계 분석 및 출력
    data = np.load(map_npz)
    grid = data["grid"]
    hc = data["hit_count"] if "hit_count" in data else np.zeros_like(grid)
    fc = data["free_count"] if "free_count" in data else np.zeros_like(grid)
    res = float(data.get("resolution", 0.05))

    total_cells = grid.size
    free_cells = int(np.sum(grid == CELL_FREE))
    wall_cells = int(np.sum(grid == CELL_WALL))
    obs_cells = int(np.sum(grid >= CELL_OBSTACLE))
    unknown_cells = int(np.sum(grid == CELL_UNKNOWN))

    # 탐색된 영역 바운딩 박스
    explored_mask = grid != CELL_UNKNOWN
    if np.any(explored_mask):
        rows, cols = np.where(explored_mask)
        w_m = (np.max(cols) - np.min(cols) + 1) * res
        h_m = (np.max(rows) - np.min(rows) + 1) * res
    else:
        w_m, h_m = 0.0, 0.0

    safe_print("=" * 60)
    safe_print("        [saved_map.npz 맵 정밀 분석 및 시각화 결과]")
    safe_print("=" * 60)
    safe_print(
        f" * 전체 격자 규격     : {grid.shape[1]} x {grid.shape[0]} 셀 (20.0m x 20.0m, 해상도 {res * 100:.0f}cm/셀)"
    )
    safe_print(f" * 실제 탐색 바운딩박스 : 가로 {w_m:.2f}m x 세로 {h_m:.2f}m")
    safe_print(
        f" * 주행 가능 빈 공간   : {free_cells} 셀 ({free_cells * (res**2):.2f} m^2)"
    )
    safe_print(f" * 감지된 벽(경계)     : {wall_cells} 셀")
    safe_print(
        f" * 미탐색 배경 구역    : {unknown_cells} 셀 ({unknown_cells / total_cells * 100:.1f}%)"
    )
    safe_print(f" * 고대비 컬러 이미지  : saved_map.png 저장 완료!")
    safe_print("=" * 60)

    # 이미지 화면 표시 (--no-show 인자가 없을 때)
    if "--no-show" not in sys.argv:
        png_path = "saved_map.png"
        if os.path.exists(png_path):
            try:
                img_array = np.fromfile(png_path, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    win_name = "Saved Map Viewer (High Contrast 800x800) - Press Any Key to Close"
                    cv2.imshow(win_name, img)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
            except Exception as e:
                safe_print(f"[시각화 창 오류] {e}")


if __name__ == "__main__":
    main()
