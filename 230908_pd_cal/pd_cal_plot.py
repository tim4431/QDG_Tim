import sys

sys.path.append("..")
from lib.process_data.load_csv_data import load_csv_data
import matplotlib.pyplot as plt
import numpy as np

att, p, _ = load_csv_data("./data/santec_power_sweep.csv", None, key_x="att", key_y="p")
p_lookup = {att: p for att, p in zip(att, p)}
p_max = np.max(p)

select_func = lambda x, y: x < 8
att, v, std_v = load_csv_data(
    "./data/photodiode_power_sweep_1.2k.csv",
    select_func=select_func,
    key_x="att",
    key_y="v",
)
p_i = np.array([50.2 * p_lookup[a] / p_max for a in att])
plt.scatter(p_i, v, marker="+", alpha=0.5, c="blue", label="data points")
plt.fill_between(p_i, v - std_v, v + std_v, alpha=0.2, label=r"$\pm \sigma$" + " std")
plt.xlabel("Input power (uW)")
plt.ylabel("Output voltage (V)")
# fit using y=ax


def f(x, a):
    return a * x


from scipy.optimize import curve_fit

popt, pcov = curve_fit(f, p_i, v)
print(popt)

plt.plot(
    p_i,
    f(p_i, *popt),
    alpha=0.4,
    c="blue",
    label="fit output(V)={:.4f} * p(uW)".format(popt[0]),
)
plt.xscale("log")
plt.yscale("log")


plt.legend()
# plt.savefig("./pd_cal.png", dpi=200, bbox_inches="tight")
plt.show()
