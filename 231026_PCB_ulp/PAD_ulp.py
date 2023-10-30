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
    MIN_VIA_DIS = 30
    return _merge_y(ys, MIN_VIA_DIS)


traces = [
    (-1442, -333, 830, -645),
    (-1060, -615, 830, -738),
    (-1060, -950, 830, -831),
    (-1442, -1231, 830, -925),
]
x = np.linspace(-1442, 830, 21)
for trace in traces:
    plt.plot([trace[0], trace[2]], [trace[1], trace[3]], c="b")
for x_ in x:
    ys = get_via_ys(traces, x_, 94)
    plt.scatter([x_] * len(ys), ys, c="r")


plt.show()
