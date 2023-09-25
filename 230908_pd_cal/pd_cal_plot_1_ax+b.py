import sys

sys.path.append("..")
from lib.process_data.csv_data import load_csv_data
import matplotlib.pyplot as plt
import numpy as np

att, p, _ = load_csv_data("./data/santec_power_sweep.csv", None, key_x="att", key_y="p")
p_lookup = {att: p for att, p in zip(att, p)}
for att in np.arange(9.00, 13.50, 0.5):
    p_calc = p_lookup[8.5] * (10 ** ((att - 8.5) / 10))
    p_lookup[att] = p_calc
p_max = np.max(list(p_lookup.values()))


def char_photodiode(
    ax,
    dataName,
    max_power: float,
    select_func=None,
    sigma_multiplier=1,
    fit=True,
    fittype="ax+b",
    nW=False,
):
    att, v, std_v = load_csv_data(
        dataName,
        select_func=select_func,
        key_x="att",
        key_y="v",
    )
    p_i = np.array([max_power * p_lookup[a] / p_max for a in att])
    if nW:
        p_i *= 1000
    if nW:
        v *= 1000  # type: ignore
    ax.scatter(p_i, v, marker="+", alpha=0.5, c="blue", label="data points")
    ax.fill_between(
        p_i,
        v - sigma_multiplier * std_v,  # type: ignore
        v + sigma_multiplier * std_v,  # type: ignore
        alpha=0.2,
        label=rf"$\pm {sigma_multiplier}\sigma$" + " std",
    )
    if not nW:
        ax.set_xlabel("Input power (uW)")
        ax.set_ylabel("Output voltage (V)")
    else:
        ax.set_xlabel("Input power (nW)")
        ax.set_ylabel("Output voltage (mV)")
    # fit using y=ax

    def f(x, a):
        return a * x

    def g(x, a, b):
        return a * x + b

    if fit:
        from scipy.optimize import curve_fit

        if fittype == "ax":
            popt, pcov = curve_fit(f, p_i, v)
            print(popt)

            if not nW:
                ax.plot(
                    p_i,
                    f(p_i, *popt),
                    alpha=0.5,
                    c="blue",
                    label="fit output(V)={:.4f} * p(uW)".format(popt[0]),
                )
            else:
                ax.plot(
                    p_i,
                    f(p_i, *popt),
                    alpha=0.5,
                    c="blue",
                    label="fit output(mV)={:.4f} * p(nW)".format(popt[0]),
                )
        elif fittype == "ax+b":
            popt, pcov = curve_fit(g, p_i, v)
            print(popt)
            if not nW:
                if popt[1] < 0:
                    ax.plot(
                        p_i,
                        g(p_i, *popt),
                        alpha=0.5,
                        c="blue",
                        label="fit output(V)={:.4f} * p(uW) - {:.4f}(mV)".format(
                            popt[0], -popt[1] * 1000
                        ),
                    )
                else:
                    ax.plot(
                        p_i,
                        g(p_i, *popt),
                        alpha=0.5,
                        c="blue",
                        label="fit output(V)={:.4f} * p(uW) + {:.4f}(mV)".format(
                            popt[0], popt[1] * 1000
                        ),
                    )
            else:
                if popt[1] < 0:
                    ax.plot(
                        p_i,
                        g(p_i, *popt),
                        alpha=0.5,
                        c="blue",
                        label="fit output(mV)={:.4f} * p(nW) - {:.4f}(mV)".format(
                            popt[0], -popt[1]
                        ),
                    )
                else:
                    ax.plot(
                        p_i,
                        g(p_i, *popt),
                        alpha=0.5,
                        c="blue",
                        label="fit output(mV)={:.4f} * p(nW) + {:.4f}(mV)".format(
                            popt[0], popt[1]
                        ),
                    )


fig, ax = plt.subplots()
char_photodiode(
    ax, "./data1/photodiode_power_sweep_560.csv", max_power=41.52, sigma_multiplier=10
)
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_560_log.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax, "./data1/photodiode_power_sweep_560_1.csv", max_power=40.77, sigma_multiplier=10
)
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_560_1_log.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax,
    "./data1/photodiode_power_sweep_560_1.csv",
    max_power=40.77,
    sigma_multiplier=10,
    select_func=lambda x, y: x < -6,
    nW=True,
)
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_560_1_log_mag.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax,
    "./data1/photodiode_power_sweep_560_1.csv",
    max_power=40.77,
    sigma_multiplier=3,
    fit=False,
)
plt.legend()
plt.savefig("./photodiode_560_1.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax,
    "./data1/photodiode_power_sweep_20dB_560.csv",
    max_power=14.06,
    sigma_multiplier=10,
)
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_560_20dB_log.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax,
    "./data1/photodiode_power_sweep_20dB_560_1.csv",
    max_power=14.15,
    sigma_multiplier=10,
)
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_560_20dB_1_log.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax,
    "./data1/photodiode_power_sweep_20dB_560_1.csv",
    max_power=14.15,
    sigma_multiplier=10,
    select_func=lambda x, y: x < -6,
    nW=True,
)
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_560_20dB_1_log_mag.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots()
char_photodiode(
    ax,
    "./data1/photodiode_power_sweep_330.csv",
    max_power=49.84,
    sigma_multiplier=3,
    fit=False,
)
# plt.xscale("log")
# plt.yscale("log")
plt.legend()
plt.savefig("./photodiode_330_saturated.png", dpi=200, bbox_inches="tight")

plt.show()
