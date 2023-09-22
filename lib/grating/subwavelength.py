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


def _single_subw_grating(NL, NH, x0, Lambda, ff, ffL, ffH):
    grating_H = _subw_part(x0, Lambda * ff, NH, ffH)
    grating_L = _subw_part(x0 + Lambda * ff, Lambda * (1 - ff), NL, ffL)
    grating = grating_H + grating_L
    return grating


def _single_grating(x0, Lambda, ff):
    return [x0 + Lambda * (1 - ff), x0 + Lambda]


def ordinary_grating(N, Lambda, ff):
    grating = []
    for i in range(N):
        grating += _single_grating(i * Lambda, Lambda, ff)
    # grating = [0] + grating + [N * Lambda]
    return grating


def apodized_grating(N, Lambda_i, Lambda_f, ff_i, ff_f):
    grating = []
    Lambda_func = _linear_apodize_func(N, Lambda_i, Lambda_f)
    ff_func = _linear_apodize_func(N, ff_i, ff_f)
    #
    x0 = 0
    for i in range(N):
        Lambdai = Lambda_func(i)
        ffi = ff_func(i)
        grating += _single_grating(x0, Lambdai, ffi)
        x0 += Lambdai
    # grating = [0] + grating + [N * Lambda]
    return grating


def subw_grating(N, Lambda, ff, ffL, ffH, NL, NH):
    grating = []
    for i in range(N):
        grating += _single_subw_grating(NL, NH, i * Lambda, Lambda, ff, ffL, ffH)
    # grating = [0] + grating + [N * Lambda]
    return grating


def inverse_grating(pitch_list, ff_list, fiberx):
    grating = []
    x0 = 0
    for pitch, ff in zip(pitch_list, ff_list):
        grating += _single_grating(x0, pitch, ff)
        x0 += pitch
    return grating


def _linear_apodize_func(N, x_i, x_f):
    return lambda i: x_i + (x_f - x_i) * (i / (N - 1))


def apodized_subw_grating(
    N, NL, NH, Lambda_i, Lambda_f, ffL_i, ffL_f, ffH_i, ffH_f, ff_i, ff_f
):
    grating = []
    Lambda_func = _linear_apodize_func(N, Lambda_i, Lambda_f)
    ffL_func = _linear_apodize_func(N, ffL_i, ffL_f)
    ffH_func = _linear_apodize_func(N, ffH_i, ffH_f)
    ff_func = _linear_apodize_func(N, ff_i, ff_f)
    #
    x0 = 0
    for i in range(N):
        Lambdai = Lambda_func(i)
        ffLi = ffL_func(i)
        ffHi = ffH_func(i)
        ffi = ff_func(i)
        grating += _single_subw_grating(NL, NH, x0, Lambdai, ffi, ffLi, ffHi)
        x0 += Lambdai
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
    return np.array(pitch_list), np.array(ff_list)


def plot_grating(grating):
    h = 1
    plt.plot([0, grating[0]], [0, 0], color="black")
    plt.plot([grating[0], grating[0]], [0, 1], color="black")
    for i in range(1, len(grating)):
        plt.plot([grating[i - 1], grating[i]], [h, h], color="black")
        plt.plot([grating[i], grating[i]], [h, 1 - h], color="black")
        h = 1 - h
    plt.show()


def plot_pitch_ff(pitch_list, ff_list):
    _x = 0
    for pitch, ff in zip(pitch_list, ff_list):
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
    # plot_grating(grating)
    pitch_list, ff_list = grating_to_pitch_ff(grating)
    plot_pitch_ff(pitch_list, ff_list)
