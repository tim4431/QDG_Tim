#
import numpy as np
import matplotlib.pyplot as plt


def _subw_part(x0, L, N, ff):
    l = L / N
    grating = []
    for i in range(N):
        grating.append(x0 + (i + 1 / 2) * l - (ff / 2) * l)
        grating.append(x0 + (i + 1 / 2) * l + (ff / 2) * l)
    return grating


def _single_subw_grating(x0, Lambda, ff, ffL, ffH, NL, NH):
    grating_H = _subw_part(x0, Lambda * ff, NH, ffH)
    grating_L = _subw_part(x0 + Lambda * ff, Lambda * (1 - ff), NL, ffL)
    grating = grating_H + grating_L
    return grating


def subw_grating(N, Lambda, ff, ffL, ffH, NL, NH):
    grating = []
    for i in range(N):
        grating += _single_subw_grating(i * Lambda, Lambda, ff, ffL, ffH, NL, NH)
    # grating = [0] + grating + [N * Lambda]
    return grating


def plot_grating(grating):
    h = 1
    for i in range(1, len(grating)):
        plt.plot([grating[i - 1], grating[i]], [h, h], color="black")
        plt.plot([grating[i], grating[i]], [h, 1 - h], color="black")
        h = 1 - h
    plt.show()


if __name__ == "__main__":
    Lambda = 845 * 1e-3
    ff = 0.5
    ffL = 0.16
    ffH = 0.49
    NL = 2
    NH = 3

    grating = subw_grating(1, Lambda, ff, ffL, ffH, NL, NH)
    plot_grating(grating)
