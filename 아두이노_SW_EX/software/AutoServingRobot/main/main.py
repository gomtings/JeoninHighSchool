import sys
sys.path.append("C:/Users/User/OneDrive/바탕 화면/coding/AutoServingRobot/Software/main/modules/")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import lidar_to_grid_map
import math
# from dstar import dstar
from dstar import dstar
import random
import get_lidar_data

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

def modify_map(grid_map, center_x, center_y, undefined_points, goal_point) : 
    # 만들어진 Map을 상태에 따라 숫자로 저장
    """
    0 : 빈 공간(이동 가능한 곳)
    1 : 장애물 (이동이 불가능한 곳)
    2 : 경계면
    3 : 아직 모르는 곳
    4 : 시작 지점(lidar를 사용한 위치)
    5 : 이동 목표 지점
    """
    for row in range(len(grid_map)): 
        for col in range(len(grid_map[row])) : 
            if grid_map[row][col] == 0.5 : 
                grid_map[row][col] = 3
    grid_map[center_x][center_y] = 4
    for i in undefined_points : 
        x = i[0]
        y = i[1]
        grid_map[x][y] = 2
    grid_map[goal_point[0]][goal_point[1]] = 5
    
    return grid_map

def print_map(grid_map):
    cmap = ListedColormap(['white', 'black', 'green', 'lightgray', 'red', 'blue'])

    plt.imshow(grid_map, cmap=cmap, norm=plt.Normalize(vmin=0, vmax=5))
    plt.colorbar()

def main() : 
    file_path = "AutoServingRobot/Software/main/lidar.csv"
    ang, dist = get_data(file_path)

    mapped_data, center_x, center_y = lidar_to_grid_map.mapping(0.2, ang, dist)
    simplified_map, center_x, center_y = map_simplify(mapped_data, center_x, center_y)
    undefined_points = find_undefined_point(simplified_map)
    goal_point = undefined_points[random.randrange(len(undefined_points))] # 임시
    print(goal_point)
    plt.subplot(1,2,1)
    modified_map = modify_map(simplified_map, center_x, center_y, undefined_points, goal_point)
    np.savetxt('c:/Users/User/OneDrive/바탕 화면/coding/AutoServingRobot/Software/main/modified_map.txt', modified_map, fmt='%g', delimiter='\t')
    print_map(modified_map)
    # print(modified_map)
    # dstar
    plt.subplot(1,2,2)
    dstar(modified_map, (center_x, center_y), goal_point)

    plt.show()
if __name__ == '__main__' : 
    main()


"""
해야 할 일


--------------------------
현재 수정할 점(2024.03.14)
1. 맵의 크기가 지나치게 커서 경로 탐색에 시간이 걸림
2. 시작점과 도착점 위치가 제대로 잡히지 않음
3. D* 알고리즘 파악이 어려워 활용이 잘 되지 않음

Mapping 진행 과정
1. lidar 센서값 얻기 (이후 준서와 같이 탐색)
2. lidar 바탕으로 Mapping해보기
3. Mapping 결과 처리하기
4. 이동 목적지 설정과 이동
5. 다시 센서값 얻고, 기존 결과와 합치기
6. 지도 업데이트
7. 4~6 지도 완성할 때까지 진행
8. 지도 완성, 저장하기


lidar는 각도/거리 되어 있으니 이후에 각도만 맞추면 시야 문제는 해결 가능


범위만 지정하기
- 이동 범위만을 지정한 후 해당 범위 내에서 장애물을 발견하면 회피하는 형식
장점 : Mapping 과정이 매우 단순해짐, 길찾기가 빠르고 간단함
단점 : 이동 경로상에 장애물이 나타날 확률이 매우 높기에 실제 이동은 어려울 수 있음, 라이다, 초음파 센서의 크게 의존함

Map의 해상도를 매우 줄이는 방식
- 범위가 주어지고, 해당 위치에서 장애물 위치만 간단하게 나타내는 형식
장점 : Mapping 과정이 단순해짐, Map의 크기가 적어 데이터 처리과 길찾기에 능함
단점 : 정교한 움직임이 어렵고, 정작 빠른 길을 놓칠 수도 있음

현재 방식
- lidar 센서값을 그대로 Mapping하는 방식
장점 : 지도를 더 정교하게 만들고, 그에 따라 이동도 정교해짐
단점 : Mapping 과정이 매우 어려움
"""