from scipy.optimize import curve_fit
from .csv_data import load_csv_data
import numpy as np
import matplotlib.pyplot as plt


def calibrate_photodiode(
    ax,
    dataName,
    max_att: float,
    max_power: float,
    p_att_dict: dict,
    #
    select_func=None,
    sigma_multiplier: int = 1,
):
    att, v, std_v = load_csv_data(
        dataName,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    p_max = p_att_dict[max_att]
    p_i = np.array([max_power * p_att_dict[a] / p_max for a in att])
    #
    ax.scatter(p_i, v, marker="+", alpha=0.5, c="blue", label="data points")
    ax.fill_between(
        p_i,
        v - sigma_multiplier * std_v,  # type: ignore
        v + sigma_multiplier * std_v,  # type: ignore
        alpha=0.2,
        label=rf"$\pm {sigma_multiplier}\sigma$" + " std",
    )

    def f(x, a, b):
        return a * x + b

    popt, pcov = curve_fit(f, p_i, v)
    # print(popt)
    ax.plot(
        p_i,
        f(p_i, *popt),
        alpha=0.5,
        c="blue",
        label="fit voltage(V) = {:.4f} * p(uW) + {:.4f} V".format(*popt),
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
    # fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    # ax0 = ax[0]
    # ax1 = ax[1]
    fig, ax = plt.subplots()
    ax0 = ax
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
    print("attenuation_H: {:.2f}dB".format(10 * np.log10(p_H_attenuation)))

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
    strL = "fitL v(V) = {:.6f} * p(uW) + {:.6f}(V)".format(*popt_L)
    print(strL)
    #
    popt_H, pcov_H = curve_fit(f, v_H, p_H)
    strH = "fitH v(V) = {:.6f} * p(uW) + {:.6f}(V)".format(*popt_H)
    print(strH)
    #
    ax0.plot(f(v_L, *popt_L), v_L, alpha=0.5, c="blue", label=strL)  # type: ignore
    ax0.scatter(p_L, v_L, marker="+", alpha=0.5, c="blue", label="data points L")  # type: ignore
    ax0.plot(f(v_H, *popt_H), v_H, alpha=0.5, c="blue", label=strH)  # type: ignore
    ax0.scatter(p_H, v_H, marker="+", alpha=0.5, c="blue", label="data points H")  # type: ignore

    # find the intersection of two curves
    def diff(x):
        return f(x, *popt_L) - f(x, *popt_H)

    from scipy.optimize import fsolve

    x0 = fsolve(diff, 0)
    print("intersection: {:.6f} V".format(x0[0]))

    # # add a subplot in the lower right
    # from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    # axins = inset_axes(
    #     ax,
    #     width="40%",  # width = 30% of parent_bbox
    #     height="40%",  # height  = 30% of parent_bbox
    #     loc="center right",
    # )
    # cut data from low power region p< 100nW
    # P_LOWER_BOUND = 0.06
    # mask = p_i < P_LOWER_BOUND
    # axins.scatter(p_i[mask] * 1e3, v_i[mask] * 1e3, marker="+", alpha=0.5, c="blue")
    # axins.plot(
    #     f(v_i[mask] * 1e3, *popt1),
    #     v_i[mask] * 1e3,
    #     alpha=0.5,
    #     c="blue",
    # )
    # axins.set_xlim(-0.1 * P_LOWER_BOUND * 1e3, P_LOWER_BOUND * 1e3 * 1.1)
    # axins.set_ylim(1.1 * np.min(v_i[mask]) * 1e3, np.max(v_i[mask]) * 1e3 * 1.1)
    # axins.set_xlabel("laser power(nW)")
    # axins.set_ylabel("voltage(mV)")

    ax0.set_xlabel("laser power(uW)")
    ax0.set_ylabel("voltage(V)")
    ax0.legend()
    #
    # fit using v-pi curve
    return popt_L, popt_H
