import matplotlib.pyplot as plt
import numpy as np
from lidar_to_grid_map import file_read, generate_ray_casting_grid_map

xy_resolution = 0.02  # x-y grid resolution
ang, dist = file_read("C:/Users/User/OneDrive/바탕 화면/coding/AutoServingRobot/Arduino/lidar.csv")
ox = np.sin(ang) * dist
oy = np.cos(ang) * dist
occupancy_map, min_x, max_x, min_y, max_y, xy_resolution = \
generate_ray_casting_grid_map(ox, oy, xy_resolution, True)

np.savetxt('output.txt', occupancy_map, fmt='%d', delimiter=',')

map_array = np.loadtxt('output.txt', delimiter=',')

plt.imshow(map_array, cmap='gray_r', interpolation='none')

plt.show()