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


def grating_to_pitch_ff(grating):
    pitch_list = []
    ff_list = []
    pitch_list.append(grating[1] - 0)
    ff_list.append((grating[1] - grating[0]) / (grating[1] - 0))
    #
    if len(grating) > 2:
        for i in range(3, len(grating), 2):
            pitch_i = grating[i] - grating[i - 2]
            l_i = grating[i] - grating[i - 1]
            ff_i = l_i / pitch_i
            pitch_list.append(pitch_i)
            ff_list.append(ff_i)
    #
    # return in (pitch, ff) format
    res = [(pitch_list[i], ff_list[i]) for i in range(len(pitch_list))]
    return res


def plot_grating(grating):
    h = 1
    plt.plot([0, grating[0]], [0, 0], color="black")
    plt.plot([grating[0], grating[0]], [0, 1], color="black")
    for i in range(1, len(grating)):
        plt.plot([grating[i - 1], grating[i]], [h, h], color="black")
        plt.plot([grating[i], grating[i]], [h, 1 - h], color="black")
        h = 1 - h
    plt.show()


def plot_pitch_ff(pitch_ff):
    _x = 0
    for pitch, ff in pitch_ff:
        plt.plot([_x, _x + pitch * (1 - ff)], [0, 0], color="black")
        plt.plot([_x + pitch * (1 - ff), _x + pitch * (1 - ff)], [0, 1], color="black")
        plt.plot([_x + pitch * (1 - ff), _x + pitch], [1, 1], color="black")
        plt.plot([_x + pitch, _x + pitch], [1, 0], color="black")
        _x += pitch
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
    pitch_ff = grating_to_pitch_ff(grating)
    # plot_pitch_ff(pitch_ff)
