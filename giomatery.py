import numpy as np
import matplotlib.pyplot as plt

# 시간 변수 설정 (0초에서 10초까지)
time = np.linspace(0, 10, 500)

# 가정: 물로켓의 초기 속도는 20 m/s, 중력가속도는 9.8 m/s^2
initial_velocity = 20  # 초기 속도 (m/s)
gravity = 9.8  # 중력 가속도 (m/s^2)

# 속도의 간단한 모델: 상승 후 최고점에서 속도가 0이 되고, 그 이후 하강하면서 속도 증가
# 속도 = 초기속도 - 중력 * 시간 (상승하는 동안)
velocity = initial_velocity - gravity * time  # 상승하는 동안

# 속도가 0 이하로 떨어지면 하강 시작
velocity[velocity < 0] = -gravity * (time[velocity < 0] - time[velocity < 0][0])

# 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(time, velocity, label='속도', color='b')
plt.title('물로켓 속도 시간에 따른 그래프')
plt.xlabel('시간 (초)')
plt.ylabel('속도 (m/s)')
plt.grid(True)
plt.axhline(0, color='black',linewidth=1)
plt.legend()
plt.show()
