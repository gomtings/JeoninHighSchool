import numpy as np
import matplotlib.pyplot as plt

map_array = np.loadtxt('output.txt', delimiter=',')

plt.imshow(map_array, cmap='gray', interpolation='none')
plt.show()