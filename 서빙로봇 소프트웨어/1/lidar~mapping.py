# 라이다 데이터 통해 매핑까지
# data = [[ang1, dist1], [ang2, dist2], [ang3, dist3]...]

import numpy as np
import lidar_to_grid_map

def get_data(data) : 
    # data = [[ang1, dist1], [ang2, dist2], [ang3, dist3]...]
    angles = []
    distances = []
    for measure in data : 
        angles.append(float(measure[0]))
        distances.append(float(measure[1]))
    angles = np.array(angles)
    distances = np.array(distances)
    return angles, distances

data = [[0.008450416037156572,0.5335], [0.046902201120156306,0.5345], [0.08508127850753233,0.537], [0.1979822644959155,0.2605], [0.21189035697274505,0.2625]]
ang, dist = get_data(data)

lidar_to_grid_map.mapping(0.2, ang, dist)