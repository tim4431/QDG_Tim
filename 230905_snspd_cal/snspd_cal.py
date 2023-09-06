import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def load_data(fileName):
    data = pd.read_csv(fileName)
    dataI = data["I"].to_numpy()
    dataC = data["c"].to_numpy()
    I_mask = dataI < 14.1
    return dataI[I_mask], dataC[I_mask]


I1l, C1l = load_data("./snspd1_lum.csv")
print(C1l[-1])
I1d, C1d = load_data("./snspd1_dark.csv")
print(C1d[-1])
I2l, C2l = load_data("./snspd2_lum.csv")
I2d, C2d = load_data("./snspd2_dark.csv")

plt.figure(figsize=(10, 6))

plt.plot(
    I1d,
    C1d,
    # marker="o",
    linestyle="dashdot",
    color="b",
    alpha=0.5,
    label="snspd1,dark",
)

plt.plot(
    I2d,
    C2d,
    # marker="o",
    linestyle="dashdot",
    color="orange",
    alpha=0.5,
    label="snspd2,dark",
)
THEO_cps = 39.83 * 1e3
# twin x plot efficiency = cps / THEO_cps
plt.plot(
    I1l,
    C1l,
    # marker="o",
    linestyle="-",
    color="b",
    label="snspd1,lum",
)
plt.plot(
    I2l,
    C2l,
    # marker="o",
    linestyle="-",
    color="orange",
    label="snspd2,lum",
)
#
plt.xlabel("Bias Current (" + r"$\mu$" + "A)")
plt.ylabel("Counts per second")
# log y
plt.legend()
plt.grid(True)

# plt.yscale("log")
# twin x y ticks
plt.twinx()
plt.yticks(np.arange(0, 1.1, 0.1))
# plt.yscale("log")

plt.show()
