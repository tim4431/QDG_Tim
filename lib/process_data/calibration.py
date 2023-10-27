from scipy.optimize import curve_fit
from .csv_data import load_csv_data
import numpy as np


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
    ax,
    dataName_L,
    dataName_H,
    max_att: float,
    max_power_H: float,
    p_att_dict: dict,
    #
    select_func=None,
    sigma_multiplier: int = 1,
):
    #
    att_H, v_H, std_v_H = load_csv_data(
        dataName_H,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    p_max = p_att_dict[max_att]
    p_iH = np.array([max_power_H * p_att_dict[a] / p_max for a in att_H])
    #
    def f(x, a, b):
        return a * x + b

    popt, pcov = curve_fit(f, p_iH, v_H)
    #
    att_L, v_L, std_v_L = load_csv_data(
        dataName_L,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    p_max = p_att_dict[max_att]
    p_iL = np.array([max_power * p_att_dict[a] / p_max for a in att_L])
    
    #
    ax.scatter(p_i, v_L, marker="+", alpha=0.5, c="blue", label="data points")
    ax.fill_between(
        p_i,
        v - sigma_multiplier * std_v,  # type: ignore
        v + sigma_multiplier * std_v,  # type: ignore
        alpha=0.2,
        label=rf"$\pm {sigma_multiplier}\sigma$" + " std",
    )


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
