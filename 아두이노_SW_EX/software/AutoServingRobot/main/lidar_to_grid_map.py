"""

LIDAR to 2D grid map example

author: Erno Horvath, Csaba Hajdu based on Atsushi Sakai's scripts

"""

import math
from collections import deque

import matplotlib.pyplot as plt
import numpy as np

EXTEND_AREA = 1.0


def file_read(f):
    """
    Reading LIDAR laser beams (angles and corresponding distance data)
    """
    with open(f) as data:
        measures = [line.split(",") for line in data]
    angles = []
    distances = []
    for measure in measures:
        angles.append(float(measure[0]))
        distances.append(float(measure[1]))
    angles = np.array(angles)
    distances = np.array(distances)
    return angles, distances


def bresenham(start, end):
    """
    Implementation of Bresenham's line drawing algorithm
    See en.wikipedia.org/wiki/Bresenham's_line_algorithm
    Bresenham's Line Algorithm
    Produces a np.array from start and end (original from roguebasin.com)
    >>> points1 = bresenham((4, 4), (6, 10))
    >>> print(points1)
    np.array([[4,4], [4,5], [5,6], [5,7], [5,8], [6,9], [6,10]])
    """
    # setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    is_steep = abs(dy) > abs(dx)  # determine how steep the line is
    if is_steep:  # rotate line
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    # swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
    dx = x2 - x1  # recalculate differentials
    dy = y2 - y1  # recalculate differentials
    error = int(dx / 2.0)  # calculate error
    y_step = 1 if y1 < y2 else -1
    # iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = [y, x] if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx
    if swapped:  # reverse the list if the coordinates were swapped
        points.reverse()
    points = np.array(points)
    return points


def calc_grid_map_config(ox, oy, xy_resolution):
    """
    Calculates the size, and the maximum distances according to the the
    measurement center
    """
    min_x = round(min(ox) - EXTEND_AREA / 2.0)
    min_y = round(min(oy) - EXTEND_AREA / 2.0)
    max_x = round(max(ox) + EXTEND_AREA / 2.0)
    max_y = round(max(oy) + EXTEND_AREA / 2.0)
    xw = int(round((max_x - min_x) / xy_resolution))
    yw = int(round((max_y - min_y) / xy_resolution))
    print("The grid map is ", xw, "x", yw, ".")
    return min_x, min_y, max_x, max_y, xw, yw


def atan_zero_to_twopi(y, x):
    angle = math.atan2(y, x)
    if angle < 0.0:
        angle += math.pi * 2.0
    return angle


def init_flood_fill(center_point, obstacle_points, xy_points, min_coord,
                    xy_resolution):
    """
    center_point: center point
    obstacle_points: detected obstacles points (x,y)
    xy_points: (x,y) point pairs
    """
    center_x, center_y = center_point
    prev_ix, prev_iy = center_x - 1, center_y
    ox, oy = obstacle_points
    xw, yw = xy_points
    min_x, min_y = min_coord
    occupancy_map = (np.ones((xw, yw))) * 0.5
    for (x, y) in zip(ox, oy):
        # x coordinate of the the occupied area
        ix = int(round((x - min_x) / xy_resolution))
        # y coordinate of the the occupied area
        iy = int(round((y - min_y) / xy_resolution))
        free_area = bresenham((prev_ix, prev_iy), (ix, iy))
        for fa in free_area:
            occupancy_map[fa[0]][fa[1]] = 0  # free area 0.0
        prev_ix = ix
        prev_iy = iy
    return occupancy_map


def flood_fill(center_point, occupancy_map):
    """
    center_point: starting point (x,y) of fill
    occupancy_map: occupancy map generated from Bresenham ray-tracing
    """
    # Fill empty areas with queue method
    sx, sy = occupancy_map.shape
    fringe = deque()
    fringe.appendleft(center_point)
    while fringe:
        n = fringe.pop()
        nx, ny = n
        # West
        if nx > 0:
            if occupancy_map[nx - 1, ny] == 0.5:
                occupancy_map[nx - 1, ny] = 0.0
                fringe.appendleft((nx - 1, ny))
        # East
        if nx < sx - 1:
            if occupancy_map[nx + 1, ny] == 0.5:
                occupancy_map[nx + 1, ny] = 0.0
                fringe.appendleft((nx + 1, ny))
        # North
        if ny > 0:
            if occupancy_map[nx, ny - 1] == 0.5:
                occupancy_map[nx, ny - 1] = 0.0
                fringe.appendleft((nx, ny - 1))
        # South
        if ny < sy - 1:
            if occupancy_map[nx, ny + 1] == 0.5:
                occupancy_map[nx, ny + 1] = 0.0
                fringe.appendleft((nx, ny + 1))


def generate_ray_casting_grid_map(ox, oy, xy_resolution, breshen=True):
    """
    The breshen boolean tells if it's computed with bresenham ray casting
    (True) or with flood fill (False)
    """
    min_x, min_y, max_x, max_y, x_w, y_w = calc_grid_map_config(
        ox, oy, xy_resolution)
    # default 0.5 -- [[0.5 for i in range(y_w)] for i in range(x_w)]
    occupancy_map = np.ones((x_w, y_w)) / 2
    center_x = int(
        round(-min_x / xy_resolution))  # center x coordinate of the grid map
    center_y = int(
        round(-min_y / xy_resolution))  # center y coordinate of the grid map
    # occupancy grid computed with bresenham ray casting
    if breshen:
        for (x, y) in zip(ox, oy):
            # x coordinate of the the occupied area
            ix = int(round((x - min_x) / xy_resolution))
            # y coordinate of the the occupied area
            iy = int(round((y - min_y) / xy_resolution))
            laser_beams = bresenham((center_x, center_y), (
                ix, iy))  # line form the lidar to the occupied point
            for laser_beam in laser_beams:
                occupancy_map[laser_beam[0]][
                    laser_beam[1]] = 0.0  # free area 0.0
            occupancy_map[ix][iy] = 1.0  # occupied area 1.0
            occupancy_map[ix + 1][iy] = 1.0  # extend the occupied area
            occupancy_map[ix][iy + 1] = 1.0  # extend the occupied area
            occupancy_map[ix + 1][iy + 1] = 1.0  # extend the occupied area
    # occupancy grid computed with with flood fill
    else:
        occupancy_map = init_flood_fill((center_x, center_y), (ox, oy),
                                        (x_w, y_w),
                                        (min_x, min_y), xy_resolution)
        flood_fill((center_x, center_y), occupancy_map)
        occupancy_map = np.array(occupancy_map, dtype=float)
        for (x, y) in zip(ox, oy):
            ix = int(round((x - min_x) / xy_resolution))
            iy = int(round((y - min_y) / xy_resolution))
            occupancy_map[ix][iy] = 1.0  # occupied area 1.0
            occupancy_map[ix + 1][iy] = 1.0  # extend the occupied area
            occupancy_map[ix][iy + 1] = 1.0  # extend the occupied area
            occupancy_map[ix + 1][iy + 1] = 1.0  # extend the occupied area
    return occupancy_map, min_x, max_x, min_y, max_y, xy_resolution

# call at main : lidar_to_grid_map(angle, dist) 
def lidar_to_grid_map(ang, dist, is_show):
    xy_resolution = 0.2  # x-y grid resolution
    # ang, dist = file_read("lidar01.csv")

    ox = np.sin(ang) * dist
    oy = np.cos(ang) * dist
    
    occupancy_map, min_x, max_x, min_y, max_y, xy_resolution = \
        generate_ray_casting_grid_map(ox, oy, xy_resolution, True)
    if is_show :
        xy_res = np.array(occupancy_map).shape
        plt.figure(1, figsize=(10, 4))
        plt.subplot(122)
        plt.imshow(occupancy_map, cmap="PiYG_r")
        # cmap = "binary" "PiYG_r" "PiYG_r" "bone" "bone_r" "RdYlGn_r"
        plt.clim(-0.4, 1.4)
        plt.gca().set_xticks(np.arange(-.5, xy_res[1], 1), minor=True)
        plt.gca().set_yticks(np.arange(-.5, xy_res[0], 1), minor=True)
        plt.grid(True, which="minor", color="w", linewidth=0.6, alpha=0.5)
        plt.colorbar()
        plt.subplot(121)
        plt.plot([oy, np.zeros(np.size(oy))], [ox, np.zeros(np.size(oy))], "ro-")
        plt.axis("equal")
        plt.plot(0.0, 0.0, "ob")
        plt.gca().set_aspect("equal", "box")
        bottom, top = plt.ylim()  # return the current y-lim
        plt.ylim((top, bottom))  # rescale y axis, to match the grid orientation
        plt.grid(True)
        plt.show()

    return occupancy_map


if __name__ == '__main__':
    angle = (0.125, 0.140625, 6.625, 6.671875, 7.921875, 7.953125, 9.203125, 9.25, 10.515625, 10.546875, 11.828125, 11.84375, 13.109375, 13.140625, 14.40625, 14.453125, 15.734375, 15.75, 17.015625, 17.0625, 18.34375, 18.40625, 20.9375, 20.9375, 22.21875, 22.265625, 28.71875, 28.765625, 29.984375, 30.03125, 31.265625, 31.3125, 37.875, 37.9375, 39.1875, 39.21875, 41.75, 41.828125, 46.9375, 47.015625, 48.234375, 48.296875, 49.53125, 49.625, 50.84375, 50.921875, 52.15625, 52.234375, 53.484375, 53.546875, 54.78125, 54.859375, 56.09375, 56.171875, 57.390625, 57.5, 58.734375, 58.84375, 60.078125, 60.15625, 61.40625, 61.484375, 62.6875, 62.78125, 64.03125, 64.125, 65.34375, 65.453125, 66.625, 66.734375, 69.234375, 70.578125, 70.6875, 71.875, 71.984375, 73.171875, 73.3125, 74.5, 74.625, 75.796875, 75.9375, 77.140625, 77.25, 78.46875, 78.5625, 79.75, 88.84375, 93.71875, 94.859375, 94.96875, 96.234375, 96.328125, 100.09375, 101.375, 101.53125, 102.765625, 102.84375, 103.984375, 104.125, 105.28125, 111.03125, 111.1875, 112.328125, 112.46875, 113.625, 113.78125, 119.953125, 120.140625, 137.015625, 137.4375, 138.9375, 139.0625, 139.828125, 140.59375, 141.40625, 141.59375, 142.546875, 142.9375, 143.984375, 144.28125, 145.265625, 145.5, 146.71875, 147.125, 147.84375, 148.0625, 149.046875, 149.75, 150.28125, 150.5625, 151.71875, 152.078125, 153.046875, 153.859375, 154.640625, 154.921875, 155.71875, 156.796875, 159.171875, 159.71875, 160.09375, 160.828125, 161.1875, 162.28125, 162.625, 163.046875, 163.90625, 164.453125, 164.984375, 166.15625, 166.171875, 166.984375, 167.03125, 173.21875, 173.296875, 174.1875, 174.421875, 179.25, 179.296875, 182.625, 182.8125, 187.546875, 189.0625, 189.109375, 190.078125, 190.578125, 206.328125, 218.9375, 220.5625, 221.578125, 221.84375, 222.84375, 223.140625, 224.15625, 225.46875, 228.375, 228.6875, 229.6875, 230.015625, 231.015625, 231.3125, 232.3125, 232.609375, 233.640625, 233.9375, 234.953125, 235.25, 236.21875, 236.5, 237.53125, 237.8125, 238.828125, 239.109375, 240.109375, 242.296875, 243.625, 243.921875, 244.921875, 245.234375, 246.234375, 246.53125, 247.546875, 247.84375, 248.84375, 256.953125, 258.21875, 259.328125, 259.5625, 260.609375, 260.859375, 261.921875, 262.140625, 263.234375, 263.46875, 264.546875, 264.765625, 265.84375, 266.078125, 267.15625, 267.375, 268.46875, 268.671875, 269.78125, 269.984375, 282.296875, 282.5625, 283.65625, 285.953125, 288.84375, 288.921875, 290.0, 290.21875, 291.34375, 291.625, 292.625, 293.046875, 294.09375, 294.328125, 295.21875, 295.515625, 296.5, 296.796875, 297.84375, 297.953125, 299.234375, 299.421875, 300.453125, 300.8125, 301.75, 303.09375, 303.703125, 304.734375, 304.90625, 306.046875, 306.3125, 309.0, 310.1875, 310.4375, 311.46875, 311.734375, 313.15625, 314.234375, 314.46875, 315.53125, 315.703125, 316.796875, 316.984375, 319.84375, 320.015625, 321.015625, 321.34375, 323.65625, 323.71875, 324.90625, 325.09375, 326.09375, 326.390625, 327.40625, 327.5625, 331.359375, 331.5, 332.6875, 332.828125, 333.984375, 334.125, 335.28125, 335.421875, 336.578125, 336.734375, 337.890625, 338.0625, 339.234375, 339.34375, 340.53125, 340.640625, 341.859375, 341.96875, 343.171875, 343.28125, 344.4375, 344.59375, 345.765625, 345.875, 347.03125, 347.203125, 348.359375, 348.5, 349.671875, 349.796875, 350.96875, 352.28125, 352.328125, 353.59375, 353.59375, 354.890625, 354.921875, 356.21875, 356.25, 357.515625, 357.53125, 358.78125, 358.8125)
    dist = (2233.5, 2234.0, 2243.25, 2243.0, 2247.5, 2248.5, 2251.0, 2252.25, 2264.5, 2264.0, 2278.75, 2278.75, 2288.75, 2288.5, 2298.25, 2298.0, 2307.25, 2307.75, 2323.25, 2323.25, 2303.5, 2300.75, 2381.5, 2382.0, 2399.75, 2400.5, 2538.0, 2537.5, 2578.0, 2576.25, 2613.0, 2613.25, 2823.75, 2828.25, 2878.75, 2879.75, 3107.75, 3105.0, 3408.75, 3412.25, 3478.25, 3480.75, 3560.0, 3561.75, 3588.0, 3583.25, 3594.5, 3589.75, 3583.0, 3582.0, 3508.0, 3505.75, 3455.75, 3456.0, 3423.5, 3424.25, 3380.0, 3375.25, 3332.75, 3322.5, 3293.0, 3287.0, 3254.75, 3253.5, 3205.75, 3202.0, 3155.75, 3150.75, 3155.5, 3155.5, 3263.5, 3198.5, 3196.25, 3168.0, 3169.5, 3147.0, 3146.0, 3129.5, 3123.5, 3110.5, 3106.25, 3091.25, 3094.5, 3073.75, 3075.0, 3074.5, 3129.25, 1106.25, 1102.75, 1106.5, 1123.25, 1120.75, 1134.0, 1140.75, 1132.75, 1141.5, 1139.25, 1142.5, 1143.25, 1150.5, 2544.25, 2549.25, 2565.25, 2568.75, 2569.75, 2574.25, 3725.5, 3714.0, 323.25, 322.25, 316.25, 316.75, 310.5, 310.0, 306.0, 305.75, 305.5, 308.25, 307.5, 309.5, 305.0, 305.75, 301.0, 301.5, 299.0, 298.75, 297.75, 297.5, 298.25, 298.5, 300.5, 301.25, 304.25, 304.75, 307.25, 307.5, 309.5, 313.0, 305.5, 303.25, 303.5, 306.0, 307.25, 311.0, 312.5, 317.0, 318.5, 322.75, 323.5, 325.0, 325.0, 326.25, 326.75, 367.0, 365.25, 371.75, 373.0, 406.75, 404.75, 434.75, 437.0, 471.25, 477.75, 476.75, 486.0, 483.25, 307.5, 3268.25, 3146.0, 3108.75, 3110.25, 3137.5, 3151.0, 3214.25, 3294.75, 2065.0, 2051.25, 2032.25, 2027.25, 2024.25, 2024.0, 2018.25, 2018.25, 2014.75, 2015.5, 2034.25, 2035.75, 2056.5, 2056.0, 2082.0, 2083.0, 2123.0, 2124.5, 2180.5, 6053.5, 6003.5, 6000.25, 5942.25, 5923.0, 5876.0, 5858.25, 5816.5, 5782.75, 5772.25, 5492.5, 5476.25, 5488.25, 5475.5, 5449.75, 5448.5, 5429.0, 5417.25, 5395.0, 5389.5, 5368.25, 5368.5, 5362.0, 5348.5, 5343.75, 5338.0, 5342.75, 5351.5, 5363.0, 5359.75, 1212.25, 1210.75, 1217.75, 747.25, 599.75, 600.75, 602.0, 602.5, 601.0, 602.0, 599.0, 598.75, 598.0, 597.0, 600.5, 601.25, 603.5, 607.25, 604.5, 611.5, 604.0, 613.75, 605.5, 616.0, 611.0, 621.5, 1049.0, 1044.0, 1051.0, 1040.75, 1047.5, 929.25, 912.0, 908.75, 892.25, 890.0, 868.5, 850.0, 850.25, 844.0, 844.5, 842.25, 843.0, 711.0, 710.75, 703.75, 703.25, 731.75, 731.75, 738.5, 739.25, 744.75, 745.75, 758.25, 760.0, 2546.25, 2543.5, 2509.0, 2507.25, 2480.0, 2477.5, 2451.0, 2454.75, 2418.25, 2423.75, 2397.25, 2397.0, 2383.5, 2385.0, 2369.0, 2365.75, 2344.75, 2340.25, 2321.0, 2320.0, 2307.0, 2305.25, 2298.0, 2294.5, 2288.75, 2285.75, 2278.0, 2279.5, 2266.25, 2268.75, 2256.5, 2247.5, 2247.75, 2240.5, 2240.75, 2238.5, 2238.0, 2235.0, 2234.75, 2232.0, 2232.25, 2233.5, 2233.75)

    # print(angle[200])
    # print(dist[200])
    # print(np.sin(angle[200])*dist[200])

    map = lidar_to_grid_map(angle, dist, True)