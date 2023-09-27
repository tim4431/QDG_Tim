import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque

# Initialize the figure and axis
fig, ax = plt.subplots()

# Create a deque to store data points
max_points = 1000  # You can adjust this to control the number of points displayed
data = deque(maxlen=max_points)

s1 = ax.scatter([], [])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# You can also set labels and titles if needed
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_title("Live Scatter Plot")


def update():
    # Generate a new data point
    new_point = (np.random.rand(), np.random.rand())
    # Append the new point to the deque
    data.append(new_point)
    x, y = zip(*data)
    s1.set_offsets(np.column_stack((x, y)))
    print(len(data))


while 1:
    update()
    plt.pause(0.001)
    plt.draw()
