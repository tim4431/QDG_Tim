import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# use seaborn plotting style defaults
# import seaborn as sns

# sns.set_theme(style="darkgrid")


def load_data(fileName, Imax=None):
    data = pd.read_csv(fileName)
    dataI = data["I"].to_numpy()
    dataC = data["c"].to_numpy()
    if Imax is not None:
        I_sel = dataI < Imax
        dataI = dataI[I_sel]
        dataC = dataC[I_sel]
    #
    I_list = sorted(list(set(dataI)))
    mean_c_list = []
    std_c_list = []
    for Is in I_list:
        # print(Is)
        # for I=Is, cal mean and std of c
        I_mask = dataI == Is
        mean_c = np.mean(dataC[I_mask])
        std_c = np.std(dataC[I_mask])
        mean_c_list.append(mean_c)
        std_c_list.append(std_c)

    return np.array(I_list), np.array(mean_c_list), np.array(std_c_list)


I1l, C1l, stdC1l = load_data("./data2/snspd1_lum_combine.csv", Imax=14.4)
I1d, C1d, stdC1d = load_data("./data2/snspd1_dark_combine.csv", Imax=14.4)
C1l = C1l - C1d  # type: ignore
stdC1l = np.sqrt(stdC1l**2 + stdC1d**2)  # type: ignore
#
I2l, C2l, stdC2l = load_data("./data2/snspd2_lum_combine.csv", Imax=15.8)
I2d, C2d, stdC2d = load_data("./data2/snspd2_dark_combine.csv", Imax=15.8)
C2l = C2l - C2d  # type: ignore
stdC2l = np.sqrt(stdC2l**2 + stdC2d**2)  # type: ignore
THEO_cps = 20.56 * 1e3
# Create a figure and axis for the primary plot
fig, ax1 = plt.subplots(figsize=(9, 6))
ax1.plot(
    I1l,
    C1l / THEO_cps,
    linestyle="-",
    color="b",
    label="snspd1,lum",
)

ax1.fill_between(
    I1l,
    (C1l - 3 * stdC1l) / THEO_cps,
    (C1l + 3 * stdC1l) / THEO_cps,
    alpha=0.2,
    color="b",
)

ax1.plot(
    I2l,
    C2l / THEO_cps,
    linestyle="-",
    color="orange",
    label="snspd2,lum",
)

ax1.fill_between(
    I2l,
    (C2l - 3 * stdC2l) / THEO_cps,
    (C2l + 3 * stdC2l) / THEO_cps,
    alpha=0.2,
    color="orange",
)


# Create a twin axis for the secondary plot
ax2 = ax1.twinx()


ax2.errorbar(
    I1d,
    C1d,
    yerr=3 * stdC1d,
    color="b",
    marker="+",
    linestyle="--",
    alpha=0.5,
    label="snspd1,dark",
)

ax2.errorbar(
    I2d,
    C2d,
    yerr=3 * stdC2d,
    color="orange",
    marker="+",
    linestyle="--",
    alpha=0.5,
    label="snspd2,dark",
)


# # Set y-axis and twin y-axis to log scale
# # ax1.set_yscale("log")
ax2.set_yscale("log")

# # Set y-ticks for both axes in the range [0.1, 1.1]
ax1.set_yticks(np.arange(0.1, 0.7, 0.1))
ax2.set_ylim(1, 1e7)

ax1.set_xlabel("Bias Current (" + r"$\mu$" + "A)")
ax1.set_ylabel("Efficiency")
ax2.set_ylabel("Dark counts per second")
#
idx_1 = 8
ax1.scatter(
    I1l[idx_1],
    C1l[idx_1] / THEO_cps,
    marker="o",
    color="b",
    label="{:.2f} uA,dark count={:.1f}, efficiency={:.2f}".format(
        I1l[idx_1], C1d[idx_1], C1l[idx_1] / THEO_cps
    ),
)
idx_2 = 9
ax1.scatter(
    I2l[idx_2],
    C2l[idx_2] / THEO_cps,
    marker="o",
    color="orange",
    label="{:.2f} uA,dark count={:.1f}, efficiency={:.2f}".format(
        I2l[idx_2], C2d[idx_2], C2l[idx_2] / THEO_cps
    ),
)

# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
# plt.grid()
# set grid to be gray, and partially transparent
ax1.grid(color="gray", alpha=0.2)

plt.savefig("snspd_cal_2.png", dpi=300, bbox_inches="tight")
plt.show()
