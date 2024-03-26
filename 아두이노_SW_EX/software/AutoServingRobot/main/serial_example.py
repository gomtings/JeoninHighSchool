from rplidar import RPLidar

lidar = RPLidar('COM3')

for i, scan in enumerate(lidar.iter_scans()):
    print('Scan #%d:' % i)
    for measurement in scan:
        quality, angle, distance = measurement
        print('Angle: %f degrees, Distance: %f cm' % (angle, distance))
    if i > 10:
        break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
