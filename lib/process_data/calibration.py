from scipy.optimize import curve_fit
from .csv_data import load_csv_data
import numpy as np
import matplotlib.pyplot as plt


def calibrate_photodiode(
    ax,
    dataName,
    max_power: float,
    p_att_dict: dict,
    #
    select_func=None,
    sigma_multiplier: int = 1,
    **kwargs,
):
    att, v, std_v = load_csv_data(
        dataName,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    p_max = p_att_dict[np.max(att)]
    p_i = np.array([max_power * p_att_dict[a] / p_max for a in att])
    #
    ax.scatter(p_i, v, marker="+", alpha=0.5, label="data points", **kwargs)
    ax.fill_between(
        p_i,
        v - sigma_multiplier * std_v,  # type: ignore
        v + sigma_multiplier * std_v,  # type: ignore
        alpha=0.2,
        label=rf"$\pm {sigma_multiplier}\sigma$" + " std",
        **kwargs,
    )

    def f(x, a, b):
        return a * x + b

    popt, pcov = curve_fit(f, p_i, v)
    # print(popt)
    ax.plot(
        p_i,
        f(p_i, *popt),
        alpha=0.5,
        label="fit voltage(V) = {:.4f} * p(uW) + {:.4f} V".format(*popt),
        **kwargs,
    )
    ax.set_xlabel("laser power(uW)")
    ax.set_ylabel("voltage(V)")
    ax.legend()
    #
    # fit using v-pi curve
    popt, pcov = curve_fit(f, v, p_i)
    return popt


def calibrate_photodiode_LH(
    dataName_L,
    dataName_H,
    max_power_H: float,
    p_att_dict: dict,
    #
    select_func=None,
    sigma_multiplier: int = 1,
):
    # (1,2) subplot
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax0 = ax[0]
    ax1 = ax[1]
    #
    att_H, v_H, std_v_H = load_csv_data(
        dataName_H,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    p_max = p_att_dict[np.max(att_H)]
    p_H = np.array([max_power_H * p_att_dict[a] / p_max for a in att_H])
    p_H_attenuation = max_power_H / p_max
    print("attenuation_H: {:.2f} dB".format(10 * np.log10(p_H_attenuation)))

    #
    def f(x, a, b):
        return a * x + b

    popt, pcov = curve_fit(f, v_H, p_H)
    #
    att_L, v_L, std_v_L = load_csv_data(
        dataName_L,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    v_L_max = np.max(v_L)
    p_L_max_actual = f(v_L_max, *popt)
    p_L_max_count = p_att_dict[np.max(att_L)]
    p_L_attenuation = p_L_max_actual / p_L_max_count
    print("attenuation_L: {:.2f} dB".format(10 * np.log10(p_L_attenuation)))
    p_L = np.array([p_L_attenuation * p_att_dict[a] for a in att_L])
    #
    # merge data
    p_i = np.concatenate((p_L, p_H))
    p_i_sort_mask = np.argsort(p_i)
    p_i = p_i[p_i_sort_mask]
    v_i = np.concatenate((v_L, v_H))
    v_i = v_i[p_i_sort_mask]
    std_v = np.concatenate((std_v_L, std_v_H))
    std_v = std_v[p_i_sort_mask]
    #
    ax0.fill_between(
        p_L,
        v_L - sigma_multiplier * std_v_L,  # type: ignore
        v_L + sigma_multiplier * std_v_L,  # type: ignore
        alpha=0.2,
        label=rf"$\pm {sigma_multiplier}\sigma$" + " std",
    )
    #
    popt_L, pcov_L = curve_fit(f, v_L, p_L)
    strL = "fitL p(uW) = {:.6f} * v(V) + {:.6f}(uW)".format(*popt_L)
    print(strL)
    #
    popt_H, pcov_H = curve_fit(f, v_H, p_H)
    strH = "fitH p(uW) = {:.6f} * v(V) + {:.6f}(uW)".format(*popt_H)
    print(strH)

    #
    # find the intersection of two curves
    def diff(x):
        return f(x, *popt_L) - f(x, *popt_H)

    from scipy.optimize import fsolve

    x0 = fsolve(diff, 0)[0]
    print("intersection: {:.6f} V".format(x0))
    y0 = f(x0, *popt_L)
    print("intersection: {:.6f} uW".format(y0))

    #
    def f_piecewise(x):  # numpy
        return np.piecewise(
            x,
            [x <= x0, x > x0],
            [lambda x: f(x, *popt_L), lambda x: f(x, *popt_H)],
        )

    #
    ax0.plot(f_piecewise(v_L), v_L, alpha=0.4, c="purple", label=strL)  # type: ignore
    ax0.scatter(p_L, v_L, marker="+", alpha=0.3, c="purple", label="data points L")  # type: ignore
    ax0.plot(f_piecewise(v_H), v_H, alpha=0.4, c="blue", label=strH)  # type: ignore
    ax0.scatter(p_H, v_H, marker="+", alpha=0.4, c="blue", label="data points H")  # type: ignore
    #
    ax0.set_xlabel("laser power(uW)")
    ax0.set_ylabel("voltage(V)")
    ax0.legend()

    #
    # ax1: relative error
    ax1.axvline(x=x0, c="red", alpha=0.5, label="intersection, {:.6f} V, {:.6f} uW".format(x0, y0), linestyle="dashed", linewidth=1)  # type: ignore
    # plot piecewise function relative error at each data point
    err_pL = np.abs((p_L - f_piecewise(v_L)) / p_L)
    ax1.scatter(
        p_L,
        err_pL,
        alpha=0.5,
        marker="+",  # type: ignore
        c="purple",
        label="relative error L",
    )
    err_pH = np.abs((p_H - f_piecewise(v_H)) / p_H)
    ax1.scatter(
        p_H,
        err_pH,
        alpha=0.5,
        marker="+",  # type: ignore
        c="blue",
        label="relative error H",
    )
    ax1.set_ylim(0, 0.2)
    ax1.set_xlabel("laser power(uW)")
    ax1.set_ylabel("relative error")
    ax1.legend()
    ax1.set_xscale("log")
    # ax1.set_yscale("log")
    #
    # fit using v-pi curve
    return popt_L, popt_H
