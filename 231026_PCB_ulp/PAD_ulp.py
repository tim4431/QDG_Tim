import numpy as np
import matplotlib.pyplot as plt


def via_gnd(x, y):
    return "VIA 'GND' ({:d} {:d});".format(round(x), round(y))


def get_trace_y(trace, x):
    # each mw trace: (x1,y1,x2,y2)
    x1, y1, x2, y2 = trace
    if (x1 <= x) and (x <= x2):
        return y1 + (y2 - y1) * ((x - x1) / (x2 - x1))
    else:
        return None


def y_dis(trace, w_via):
    x1, y1, x2, y2 = trace
    theta = np.arctan((y2 - y1) / (x2 - x1))
    return (w_via / 2) / np.cos(theta)


def _merge_y(ys, MIN_DIS):
    # if exist too close vias, merge them using the average value
    ys_new = []
    i = 0
    while i < len(ys) - 1:
        if (ys[i + 1] - ys[i]) < MIN_DIS:
            ys_new.append((ys[i + 1] + ys[i]) / 2)
            i += 2
        else:
            ys_new.append(ys[i])
            i += 1
    if i == len(ys) - 1:
        ys_new.append(ys[i])
    return ys_new


def get_via_ys(traces, x, w_via):
    MIN_VIA_DIS = 30
    ys = []
    for trace in traces:
        trace_y = get_trace_y(trace, x)
        if trace_y is None:
            continue
        else:
            trace_dis_y = y_dis(trace, w_via)
            ys.append(trace_y + trace_dis_y)
            ys.append(trace_y - trace_dis_y)
    ys = sorted(ys)
    return _merge_y(ys, MIN_VIA_DIS)


traces = [
    (448, 1072, 3360, 1472),
    (448, 972, 2910, 1138),
    (448, 872, 2910, 708),
    (448, 772, 3360, 372),
]
x = np.linspace(448, 3360, 25)
points = []
for trace in traces:
    plt.plot([trace[0], trace[2]], [trace[1], trace[3]], c="b")
for x_ in x:
    ys = get_via_ys(traces, x_, 100)
    # plt.scatter([x_] * len(ys), ys, c="r")
    points += [(x_, y) for y in ys]


#
def judge_if_close(points, x, y):
    MIN_VIA_DIS_LARGE = 100
    for x_, y_ in points:
        if ((x_ - x) ** 2 + (y_ - y) ** 2) < MIN_VIA_DIS_LARGE**2:
            return True
    return False


# add another grid of vias, but if any via is too close to the previous one, remove it
XMAX = 3582
YMAX = 2160
YMIN = -315
VIA_BG_DIS = 120
grid_x, grid_y = np.meshgrid(
    np.linspace(0, XMAX, round(XMAX / VIA_BG_DIS)),
    np.linspace(YMIN, YMAX, round((YMAX - YMIN) / VIA_BG_DIS)),
)
grid_points = [(x_, y_) for x_, y_ in zip(grid_x.flatten(), grid_y.flatten())]
grid_points_keep = [
    (x_, y_) for x_, y_ in grid_points if not judge_if_close(points, x_, y_)
]
#
points.extend(grid_points_keep)
plt.scatter([x for x, y in points], [y for x, y in points], c="r")

plt.show()
print(" ".join([via_gnd(x, y) for x, y in points]))
