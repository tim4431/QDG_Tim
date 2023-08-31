import numpy as np
import matplotlib.pyplot as plt

# Enable interactive mode
plt.ion()

# Create a figure with a grid of subplots
fig, axs = plt.subplots(nrows=1, ncols=2)

# Initialize data for the left and right subplots
transmission_lambda, transmission_T = [], []
FOM_iter, FOM_his = [], []

# Initialize lines for the left and right subplots
(fig_transmission,) = axs[0].plot(transmission_lambda, transmission_T, "bo")
(fig_FOM_his,) = axs[1].plot(FOM_iter, FOM_his, "ro")


# Function to update a subplot with new data
def update_subplot(ax, data_x, data_y, new_x, new_y):
    data_x.append(new_x)
    data_y.append(new_y)
    fig_transmission.set_data(transmission_lambda, transmission_T)
    fig_FOM_his.set_data(FOM_iter, FOM_his)
    ax.relim()
    ax.autoscale_view()
    ax.figure.canvas.flush_events()


# Simulate receiving and updating new data for left and right subplots
for i in range(50):
    new_x_left = i
    new_y_left = np.random.random() * 10

    update_subplot(axs[0], transmission_lambda, transmission_T, new_x_left, new_y_left)

    new_x_right = i
    new_y_right = np.random.random() * 10
    update_subplot(axs[1], FOM_iter, FOM_his, new_x_right, new_y_right)

    plt.pause(0.1)  # Pause to allow time for plot update

# Keep the plot window open until it's manually closed
plt.ioff()
plt.show()
