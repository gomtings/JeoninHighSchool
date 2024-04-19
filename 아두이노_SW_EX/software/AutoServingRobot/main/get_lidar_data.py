from adafruit_rplidar import RPLidar
import math

def get_lidar_data() : 
    # Setup the RPLidar
    PORT_NAME = 'COM3'
    lidar = RPLidar(None, PORT_NAME, timeout=3)

    # used to scale data to fit on the screen
    # max_distance = 0

    def process_data(data, filename='lidar_data.csv'):
        data.sort(key=lambda x: x[0])
        angle, dist = zip(*data)

        return angle, dist
        

    scan_data = []

    t = 0
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            if t > 0 : 
                processed_angle = math.radians(float(angle))
                processed_dist  = float(distance)/1000
                scan_data.append((processed_angle, processed_dist))
        t += 1
        if t == 3 : 
            angle, dist = process_data(scan_data)
            break
    
    lidar.stop()
    lidar.disconnect()

    return angle, dist

if __name__ == '__main__' : 
    angle, dist = get_lidar_data()
    print(angle[0], dist[0])