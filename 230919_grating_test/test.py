import matplotlib.pyplot as plt
import numpy as np

# Create a figure and axis
fig, ax = plt.subplots()

# Create the initial scatter plot
fig_position = ax.scatter([], [], c=np.array([]), cmap="hot", vmin=0, vmax=1)

# Create a new scatter plot and assign it to fig_new_pt
fig_new_pt = ax.scatter([], [], c=np.array([]), cmap="cool", vmin=0, vmax=1)

# Now, you can individually address points in fig_position and fig_new_pt
# For example, you can set the data for the first scatter plot (fig_position) as follows:
x_data_position = [1, 2, 3, 4, 5]
y_data_position = [0.2, 0.4, 0.6, 0.8, 1.0]
c_data_position = [0.1, 0.3, 0.5, 0.7, 0.9]
fig_position.set_offsets(np.column_stack((x_data_position, y_data_position)))
fig_position.set_array(np.array(c_data_position))

# And you can set the data for the second scatter plot (fig_new_pt) separately:
x_data_new_pt = [3, 4, 5, 6, 7]
y_data_new_pt = [0.3, 0.5, 0.7, 0.9, 1.1]
c_data_new_pt = [0.2, 0.4, 0.6, 0.8, 1.0]
fig_new_pt.set_offsets(np.column_stack((x_data_new_pt, y_data_new_pt)))
fig_new_pt.set_array(np.array(c_data_new_pt))

# Finally, you can show the plot
plt.xlim(0, 10)
plt.ylim(0, 2)
plt.show()
