import time
import math
import matplotlib.pyplot as plt
from rplidar import RPLidar

PORT = 'COM7'
BAUDRATE = 115200

MIN_DISTANCE_MM = 200
MAX_DISTANCE_MM = 6000
SAFE_DISTANCE_MM = 800

STEP = 80                 # 전진 거리
TURN_ANGLE = math.radians(15)

# 로봇 상태 (월드 좌표)
robot_x = 0.0
robot_y = 0.0
robot_theta = 0.0

trajectory = []

plt.ion()
fig, ax = plt.subplots()


def classify_direction(angle):
    if angle >= 330 or angle <= 30:
        return "front"
    elif 30 < angle <= 120:
        return "left"
    elif 240 <= angle < 330:
        return "right"
    return None


def decide_path(min_dist):
    if min_dist["front"] > SAFE_DISTANCE_MM:
        return "GO_STRAIGHT"
    if min_dist["left"] > min_dist["right"]:
        return "TURN_LEFT"
    if min_dist["right"] > min_dist["left"]:
        return "TURN_RIGHT"
    return "GO_BACK"


def update_robot(decision):
    global robot_x, robot_y, robot_theta

    if decision == "GO_STRAIGHT":
        robot_x += STEP * math.cos(robot_theta)
        robot_y += STEP * math.sin(robot_theta)
    elif decision == "GO_BACK":
        robot_x -= STEP * math.cos(robot_theta)
        robot_y -= STEP * math.sin(robot_theta)
    elif decision == "TURN_LEFT":
        robot_theta += TURN_ANGLE
    elif decision == "TURN_RIGHT":
        robot_theta -= TURN_ANGLE

    trajectory.append((robot_x, robot_y))


def draw(obstacles_x, obstacles_y, decision):
    ax.clear()

    # 장애물 (로봇 기준으로 같이 움직임)
    ax.scatter(obstacles_x, obstacles_y, s=4, c='black')

    # 경로
    if trajectory:
        tx, ty = zip(*trajectory)
        ax.plot(tx, ty, c='blue', linewidth=2)

    # 로봇
    ax.scatter(robot_x, robot_y, c='red', s=70)
    ax.arrow(
        robot_x, robot_y,
        200 * math.cos(robot_theta),
        200 * math.sin(robot_theta),
        head_width=80,
        color='red'
    )

    ax.set_xlim(robot_x - 3000, robot_x + 3000)
    ax.set_ylim(robot_y - 3000, robot_y + 3000)
    ax.set_aspect('equal')
    ax.set_title(f"Decision: {decision}")

    plt.pause(0.01)


def main():
    lidar = RPLidar(PORT, baudrate=BAUDRATE)
    lidar.start_motor()
    time.sleep(1)

    try:
        for scan in lidar.iter_scans(max_buf_meas=1200):

            distances = {"front": [], "left": [], "right": []}
            obstacles_x = []
            obstacles_y = []

            for _, angle, dist in scan:
                if dist < MIN_DISTANCE_MM or dist > MAX_DISTANCE_MM:
                    continue

                # 🔹 장애물 점 개수 조금 늘림 (angle % 2)
                if int(angle) % 2 != 0:
                    continue

                # 로봇 기준 → 월드 좌표
                lx = dist * math.cos(math.radians(angle))
                ly = dist * math.sin(math.radians(angle))

                wx = robot_x + lx * math.cos(robot_theta) - ly * math.sin(robot_theta)
                wy = robot_y + lx * math.sin(robot_theta) + ly * math.cos(robot_theta)

                obstacles_x.append(wx)
                obstacles_y.append(wy)

                d = classify_direction(angle)
                if d:
                    distances[d].append(dist)

            min_dist = {
                k: min(v) if v else float('inf')
                for k, v in distances.items()
            }

            decision = decide_path(min_dist)
            update_robot(decision)

            print(
                f"F:{min_dist['front']:.0f} "
                f"L:{min_dist['left']:.0f} "
                f"R:{min_dist['right']:.0f} → {decision}"
            )

            draw(obstacles_x, obstacles_y, decision)
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
