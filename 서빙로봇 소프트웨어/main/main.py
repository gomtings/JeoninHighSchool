import sys
sys.path.append("C:/Users/User/OneDrive/바탕 화면/coding/AutoServingRobot/Software/main/modules/")

import numpy as np
import matplotlib.pyplot as plt
import lidar_to_grid_map
import math

def get_data(f) : # data = [[ang1, dist1], [ang2, dist2], [ang3, dist3]...]
    with open(f) as data : 
        measures = [line.split(" ") for line in data]
    angles = []
    distances = []
    for measure in measures:
        angles.append(math.radians(float(measure[0])))
        distances.append(float(measure[1])/1000)
    angles = np.array(angles)
    distances = np.array(distances)
    return angles, distances

def map_simplify(grid_map, center_x, center_y):
    grid_map[center_x][center_y] = 5
    rows_to_delete = set()
    cols_to_delete = set()
    for i, row in enumerate(grid_map):
        if all(val == 0.5 for val in row):
            rows_to_delete.add(i)
    for j in range(len(grid_map[0])):
        if all(row[j] == 0.5 for row in grid_map):
            cols_to_delete.add(j)
    simplified_map = [row for i, row in enumerate(grid_map) if i not in rows_to_delete]
    simplified_map = [[cell for j, cell in enumerate(row) if j not in cols_to_delete] for row in simplified_map]
    for row in simplified_map:
        row.insert(0, 0.5)
        row.append(0.5)
    top_bottom_row = [0.5] * len(simplified_map[0])
    simplified_map.insert(0, top_bottom_row)
    simplified_map.append(top_bottom_row)
    new_center_x = None
    new_center_y = None
    for i in range(len(simplified_map)) : 
        for j in range(len(simplified_map[i])) : 
            if simplified_map[i][j] == 5 : 
                new_center_x, new_center_y = i, j
                simplified_map[i][j] = 0
    return simplified_map, new_center_x, new_center_y

def find_undefined_point(grid_map) : 
    undefined_point = []
    for i in range(len(grid_map)) : 
        for j in range(len(grid_map[i])) : 
            if grid_map[i][j] == 0.5 : 
                neighbor_point = []
                for k in range(i-1, i+2) :
                    for l in range(j-1, j+2) : 
                        if 0 <= k < len(grid_map) and 0 <= l < len(grid_map[i]) : 
                            neighbor_point.append(grid_map[k][l])
                if 1 <= neighbor_point.count(0) <= 3 and neighbor_point.count(1) <= 3: 
                    undefined_point.append((i, j))
    return undefined_point

def print_map(grid_map, center_x, center_y, undefined_points) : 
    grid_map[center_x][center_y] = 3
    for i in undefined_points : 
        x = i[0]
        y = i[1]
        grid_map[x][y] = 2
    plt.imshow(grid_map, cmap='viridis', interpolation='nearest')
    plt.colorbar()
    plt.show()


def main() : 
    file_path = "AutoServingRobot/Software/main/lidar.csv"
    ang, dist = get_data(file_path)
    mapped_data, center_x, center_y = lidar_to_grid_map.mapping(0.2, ang, dist)
    simplified_map, center_x, center_y = map_simplify(mapped_data, center_x, center_y)
    np.savetxt('c:/Users/User/OneDrive/바탕 화면/coding/AutoServingRobot/Software/main/simplified_map.txt', simplified_map, fmt='%g', delimiter='\t')
    undefined_points = find_undefined_point(simplified_map)
    print_map(simplified_map, center_x, center_y, undefined_points)

if __name__ == '__main__' : 
    main()


"""
해야 할 일

lidar_to_grid_map 함수에서 실행 지점(실행 시 나오는 파란 점) 찾기 >>> center_x, center_y에 저장

마감되지 않은 경계면 찾기 >>> undefinde_points 리스트에 저장

실행 지점을 시작, 마감 안 된 경계면을 도착으로 설정하고 D*알고리즘 실행
# 만약 마감 안 된 경계면이 많을 경우, 우선순위 탐색
# 마감이 불가능한 상황도 고려(교실이라 치면 문이 열려 있다거나...)
-------------------------------------------------------------------lidar 실제 사용 필요
다시 매핑 진행하고 기존 결과와 합치기


D*알고리즘 사용해보고 main(지금 코드)에 직접 사용
이후에 가능하면 D*lite 사용해보기
"""