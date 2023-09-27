import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque

# Initialize the figure and axis
fig, ax = plt.subplots()

# Create a deque to store data points
max_points = 1000  # You can adjust this to control the number of points displayed
data = deque(maxlen=max_points)


# Define a function to update the scatter plot
def update(frame):
    # Generate a new data point
    new_point = (np.random.rand(), np.random.rand())

    # Append the new point to the deque
    data.append(new_point)

    # Clear the existing scatter plot
    ax.clear()

    # Create a scatter plot with the current data points
    x, y = zip(*data)
    ax.scatter(x, y)

    # Optionally, you can set axis limits to keep the plot fixed within a certain range
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # You can also set labels and titles if needed
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Live Scatter Plot")
    print(len(data))


# Create the FuncAnimation object to update the plot at a specified interval
interval_ms = 0.01  # Adjust this value to control the update speed
ani = FuncAnimation(fig, update, interval=interval_ms)

# Display the plot
plt.show()
