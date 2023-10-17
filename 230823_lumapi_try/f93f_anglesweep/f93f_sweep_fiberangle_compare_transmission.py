import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d
from lib.gaussian.FOM_analysis import FOM_analysis

analysis = FOM_analysis()

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(6, 4))
    # uuidList = ["c3e1", "cb2c", "4003", "7f22", "8b7f", "19bf", "3abc", "0460", "45c7"]
    # angleList = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    uuidList = ["c3e1", "cb2c", "4003", "7f22", "8b7f", "19bf", "3abc"]
    angleList = [5, 10, 15, 20, 25, 30, 35]
    ampList = []
    x0List = []
    for uuid, angle in zip(uuidList, angleList):
        dataName = "{:s}_{:.1f}_bw=50.0_transmission.txt".format(uuid, 1326.0)
        data = np.loadtxt(dataName)
        l, T = data[:, 0] * 1e3, data[:, 1]
        amp, x0, _, _ = arb_fit_1d(False, l, T, "{:.1f}".format(angle))
        # FWHM = 50.0
        # lambda_0 = 1326.0
        # _crop_range = 3 * FWHM
        # l_c, T_c = analysis.data_crop(l, T, lambda_0, _crop_range)
        # norm_T = analysis.mean_alpha(T_c, 2)
        ampList.append(amp)
        # ampList.append(norm_T)
        x0List.append(x0)

    # # print(ampList)

    ax.set_xlabel("Source angle (degree)")
    ax.set_ylabel("Peak Transmission")
    # ax.legend()
    plt.ylim(0.1, np.max(ampList) * 1.1)
    plt.xlim(5, 45)
    plt.plot(
        angleList, ampList, "o-", color="purple", label="3um, 1326nm,bw50nm,grating"
    )
    plt.legend(loc="lower right")
    #
    plt.savefig(
        "f93f_sweep_fiberangle_compare_transmission.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.show()
