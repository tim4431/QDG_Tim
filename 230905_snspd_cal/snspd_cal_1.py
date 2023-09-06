import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def load_data(fileName):
    data = pd.read_csv(fileName)
    dataI = data["I"].to_numpy()
    dataC = data["c"].to_numpy()
    I_mask = dataI < 14.6
    return dataI[I_mask], dataC[I_mask]


I1l, C1l = load_data("./data1/snspd1_lum.csv")
I1d, C1d = load_data("./data1/snspd1_dark.csv")
C1l = C1l - C1d
I2l, C2l = load_data("./data1/snspd2_lum.csv")
I2d, C2d = load_data("./data1/snspd2_dark.csv")
C2l = C2l - C2d

THEO_cps = 41.96 * 1e3
# Create a figure and axis for the primary plot
fig, ax1 = plt.subplots(figsize=(9, 5))
ax1.plot(
    I1l,
    C1l / THEO_cps,
    linestyle="-",
    color="b",
    label="snspd1,lum",
)

ax1.plot(
    I2l,
    C2l / THEO_cps,
    linestyle="-",
    color="orange",
    label="snspd2,lum",
)


# Create a twin axis for the secondary plot
ax2 = ax1.twinx()


ax2.plot(
    I1d,
    C1d,
    color="b",
    marker="+",
    linestyle="--",
    alpha=0.5,
    label="snspd1,dark",
)

ax2.plot(
    I2d,
    C2d,
    marker="+",
    linestyle="--",
    color="orange",
    alpha=0.5,
    label="snspd2,dark",
)

# Set y-axis and twin y-axis to log scale
# ax1.set_yscale("log")
ax2.set_yscale("log")

# Set y-ticks for both axes in the range [0.1, 1.1]
ax1.set_yticks(np.arange(0.1, 1.0, 0.1))
ax2.set_ylim(1, 1e7)
# ax2.set_yticks(np.arange(0.1, 1.1, 0.1))

ax1.set_xlabel("Bias Current (" + r"$\mu$" + "A)")
ax1.set_ylabel("Efficiency")
ax2.set_ylabel("Dark counts per second")
ax1.axhline(y=0.64, color="r", linestyle="--", label="efficiency = 0.64")

# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
plt.grid(True)
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.savefig("snspd_cal_1.png", bbox_inches="tight")
plt.show()
