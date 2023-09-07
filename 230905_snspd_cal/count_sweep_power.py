import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, h


def load_data(key1, key2, fileName):
    data = pd.read_csv(fileName)
    data1 = data[key1].to_numpy()
    data2 = data[key2].to_numpy()
    return data1, data2


from snspd_cal_2 import load_process_cnt_data


dataatt, datap = load_data("att", "p", "./data3/santec_sweep_power_1.csv")
power_lookup = {att: p for att, p in zip(dataatt, datap)}

# att1l, C1l = load_data("att", "c", "./data3/snspd1_lum_sweep_power.csv")
att1l, C1l, stdC1l = load_process_cnt_data(
    "./data3/snspd1_lum_sweep_power.csv", key1="att", key2="c"
)
power1l = np.array([power_lookup[att] for att in att1l])
theo_cnt_1l = (power1l * 1e-6) * (10 ** (-95.64 / 10)) / (h * c / 1326e-9)
efficiency_1l = C1l / theo_cnt_1l
std_efficiency_1l = stdC1l / theo_cnt_1l
#
att2l, C2l, stdC2l = load_process_cnt_data(
    "./data3/snspd2_lum_sweep_power.csv", key1="att", key2="c"
)
power2l = np.array([power_lookup[att] for att in att2l])
theo_cnt_2l = (power2l * 1e-6) * (10 ** (-95.64 / 10)) / (h * c / 1326e-9)
efficiency_2l = C2l / theo_cnt_2l
std_efficiency_2l = stdC2l / theo_cnt_2l
#


plt.plot(
    theo_cnt_1l / 1e3,
    efficiency_1l,
    linestyle="-",
    color="b",
    marker=".",
    label="snspd 1 @ 11.97uA",
    alpha=0.5,
)
plt.fill_between(
    theo_cnt_1l / 1e3,
    (efficiency_1l - std_efficiency_1l),
    (efficiency_1l + std_efficiency_1l),
    alpha=0.1,
    color="b",
)
#
plt.plot(
    theo_cnt_2l / 1e3,
    efficiency_2l,
    linestyle="-",
    color="orange",
    marker=".",
    label="snspd 2 @ 13.00uA",
    alpha=0.5,
)
plt.fill_between(
    theo_cnt_2l / 1e3,
    (efficiency_2l - std_efficiency_2l),
    (efficiency_2l + std_efficiency_2l),
    alpha=0.1,
    color="orange",
)
#
plt.xlabel("Theoretical count rate (kcps)")
plt.ylabel("Efficiency")
plt.legend()
plt.savefig("./efficiency_cnt.png", dpi=200, bbox_inches="tight")
plt.show()
