import sys
import time
import math
import traceback
import config
from mapper import OccupancyMap
from path_recommender import PathRecommender
from lidar_processor import LidarProcessor

def run_test():
    print("디버깅을 위한 격자 및 충돌 검사 상세 테스트를 시작합니다.")
    try:
        occ_map = OccupancyMap()
        recommender = PathRecommender(occ_map)
        
        # 1. 로봇 위치 확인
        print(f"로봇 중심 격자: row={occ_map.robot_row}, col={occ_map.robot_col}")
        
        # 2. 0.4m 전방의 실제 격자 인덱스 계산해보기 (path_recommender logic 흉내내기)
        dist = 0.40
        rad = math.radians(0.0) # 0도 정면
        x_m = dist * math.sin(rad)
        y_m = dist * math.cos(rad)
        row_c, col_c = occ_map.world_to_cell(x_m, y_m)
        print(f"0.4m 전방 로봇 중심 기준 좌표: x={x_m:.2f}m, y={y_m:.2f}m")
        print(f"변환된 중심 격자 좌표: row_c={row_c}, col_c={col_c}")
        
        # 3. 인위적 장애물 배치
        print(">>> 로봇 전방 40cm 근방(row: robot_row - 15 ~ -5)에 장애물(0.8) 배치")
        for dr in range(-15, -5):
            for dc in range(-3, 4):
                if occ_map.in_bounds(occ_map.robot_row + dr, occ_map.robot_col + dc):
                    occ_map.grid[occ_map.robot_row + dr, occ_map.robot_col + dc] = 0.8

        # 4. 장애물 구역 내 맵 값 확인
        print(f"장애물 구역 내 중심 격자({row_c}, {col_c})의 맵 값: {occ_map.grid[row_c, col_c]}")
        
        # 5. _measure_clearance_with_footprint 결과 직접 수행해보기
        clearance = recommender._measure_clearance_with_footprint(0.0)
        print(f"[전방 측정 결과] clearance: {clearance:.2f}m")

        # 6. footprint_offsets 확인
        print(f"footprint_offsets 갯수: {len(recommender.footprint_offsets)}")
        
        # 7. 만약 hit가 나지 않았다면 각 스텝별로 상세 로그 출력해보기
        print("\n--- 스텝별 전방 collision check 로그 ---")
        dist_step = 0.05
        step_m = occ_map.resolution
        while dist_step <= recommender.MAX_RANGE_M:
            x = dist_step * math.sin(rad)
            y = dist_step * math.cos(rad)
            r_c, c_c = occ_map.world_to_cell(x, y)
            
            # 이 스텝의 풋프린트 오프셋 중 장애물 검출이 있는지 수동 검사
            hits = []
            for dr, dc in recommender.footprint_offsets:
                r = r_c + dr
                c = c_c + dc
                if occ_map.in_bounds(r, c):
                    val = occ_map.grid[r, c]
                    if val >= recommender.CELL_THRESHOLD:
                        hits.append((r, c, val))
            
            if hits:
                print(f"거리 {dist_step:.2f}m (격자: {r_c}, {c_c}) -> {len(hits)}개의 셀에서 충돌 검출! 첫 충돌 셀: {hits[0]}")
                break
            else:
                # 미지 영역 확인
                unknowns = 0
                for dr, dc in recommender.footprint_offsets:
                    r = r_c + dr
                    c = c_c + dc
                    if occ_map.in_bounds(r, c) and occ_map.grid[r, c] == 0.0:
                        unknowns += 1
                # print(f"거리 {dist_step:.2f}m (격자: {r_c}, {c_c}) -> 안전함 (Unknowns: {unknowns})")
                pass
            
            dist_step += step_m

    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
