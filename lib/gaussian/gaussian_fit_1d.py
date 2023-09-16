import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# Define the Gaussian function
def gaussian(x, amplitude, x0, sigma):
    return amplitude * np.exp(-((x - x0) ** 2) / (sigma**2))


def _data_wrapper(x_data, y_data, x_range):
    # sort wrt x
    sort_index = np.argsort(x_data)
    x_data = x_data[sort_index]
    y_data = y_data[sort_index]
    #
    if x_range is not None:
        x_min, x_max = x_range
        mask = (x_data >= x_min) & (x_data <= x_max)
        x_data = x_data[mask]
        y_data = y_data[mask]
    return x_data, y_data


def _annote_wrapper(ax, amp, x0, xl, xr):
    # center, FWMH
    # get current plot color
    if ax is None:
        ax = plt.gca()
    #
    color = ax.lines[-1].get_color()

    ax.plot([x0, x0], [0, amp], color=color, linestyle="--", alpha=0.2)
    ax.plot(
        [xl, xr],
        [amp / 2, amp / 2],
        color=color,
        linestyle="dotted",
        alpha=0.2,
    )

    # Add labels and legend
    ax.set_xlabel(r"$\lambda$ (nm)")
    ax.set_ylabel(r"$T(\lambda$)")
    # ax.legend(loc="upper right")


def _fit_gaussian(x_data, y_data, p0):
    params, _ = curve_fit(gaussian, x_data, y_data, p0=p0)
    amp, x0, sigma = params

    return amp, x0, sigma


def gaussian_fit_1d(ax, x_data, y_data, name, x_range=None):
    x_data, y_data = _data_wrapper(x_data, y_data, x_range)
    # Perform the Gaussian fit
    amp, x0, sigma = _fit_gaussian(x_data, y_data, p0=[1, 1326, 100])
    FWMH = sigma * 2 * np.sqrt(np.log(2))
    #
    # Generate the fitted Gaussian curve
    x_fit = np.linspace(np.min(x_data), np.max(x_data), 100)
    y_fit = gaussian(x_fit, amp, x0, sigma)
    #
    if ax is None:
        ax = plt.gca()
    # Plot the data points and the fit line
    ax.scatter(
        x_data,
        y_data,
        label="{:s}, data pts".format(name),
        marker="+",
        alpha=0.2,
    )
    ax.plot(
        x_fit,
        y_fit,
        label="{:s}, fit: {:.1f}_{:.1f}".format(name, x0, FWMH),
    )
    #
    _annote_wrapper(ax, amp, x0, x0 - FWMH / 2, x0 + FWMH / 2)

    return amp, x0, FWMH


def arb_fit_1d(ax, x_data, y_data, name, x_range=None):
    x_data, y_data = _data_wrapper(x_data, y_data, x_range)
    max_index = np.argmax(y_data)
    amp_coarse = y_data[max_index]
    x0_coarse = x_data[max_index]
    #
    # # fit near x0_coarse using gaussian function to obtain fine x0 and amp value
    # idx1 = max(0, max_index - 3)
    # idx2 = min(max_index + 3, len(x_data) - 1)
    # if idx2 - idx1 >= 5:
    #     x_near_max = x_data[idx1:idx2]
    #     y_near_max = y_data[idx1:idx2]
    #     amp, x0, _ = _fit_gaussian(
    #         x_near_max, y_near_max, p0=[amp_coarse, x0_coarse, 100]
    #     )
    # else:  # cannot fit
    #     amp = amp_coarse
    #     x0 = x0_coarse
    amp = amp_coarse
    x0 = x0_coarse

    def _interp(y0, x1, y1, x2, y2):
        x0 = x1 + (x2 - x1) * (y0 - y1) / (y2 - y1)
        xmax = max(x1, x2)
        xmin = min(x1, x2)
        return min(max(xmin, x0), xmax)

    # left intersect
    left_index = max_index
    while (left_index > 0) and y_data[left_index] > amp / 2:
        left_index -= 1
    x_left = _interp(
        amp / 2,
        x_data[left_index],
        y_data[left_index],
        x_data[left_index + 1],
        y_data[left_index + 1],
    )

    # right intersect
    right_index = max_index
    while (right_index < len(x_data) - 1) and (y_data[right_index] > amp / 2):
        right_index += 1
    x_right = _interp(
        amp / 2,
        x_data[right_index - 1],
        y_data[right_index - 1],
        x_data[right_index],
        y_data[right_index],
    )

    FWMH = x_right - x_left  # type: ignore
    #
    CE = 10 * np.log10(amp)
    #
    if ax == False:  # do not plot
        return amp, x0, FWMH, CE
    elif ax is None:
        ax = plt.gca()
    # Plot the data point
    ax.scatter(
        x_data,
        y_data,
        # label="{:s}, data pts".format(name),
        marker="+",
        alpha=0.3,
    )
    ax.plot(
        x_data,
        y_data,
        label="{:s}, {:.1f}_{:.1f}_{:.1f}dB".format(name, x0, FWMH, CE),
        alpha=0.5,
    )
    #
    _annote_wrapper(ax, amp, x0, x_left, x_right)
    #
    return amp, x0, FWMH, CE


if __name__ == "__main__":
    from load_lumerical import load_lumerical_1d

    fig, ax = plt.subplots()

    x, y = load_lumerical_1d("./4_sub_transmission_arc.txt")
    # gaussian_fit_1d(x, y, "arc")
    arb_fit_1d(ax, x, y, "arc")
    plt.show()
    print(2 * np.sqrt(np.log(2)))
