# test_lidar.py
from rplidar import RPLidar

lidar = RPLidar('COM7', baudrate=115200, timeout=3)
lidar.connect()
print(lidar.get_info())
print(lidar.get_health())

for i, scan in enumerate(lidar.iter_scans()):
    print(f"스캔 {i}: 포인트 수 = {len(scan)}")
    if i > 5:
        break

lidar.stop()
lidar.disconnect()