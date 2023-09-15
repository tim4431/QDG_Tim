import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
sys.path.append("..")
from json_uuid import uuid_to_wd, getdataName
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    uuid = "4e25"
    dataName = getdataName(uuid)
    fig, ax = plt.subplots(figsize=(6, 6))
    # >>> 2D <<< #
    fileName = "{:s}_transmission.txt".format(dataName)
    data = np.loadtxt(fileName)
    l = data[:, 0]
    T = data[:, 1]
    arb_fit_1d(ax, l * 1e3, T, "2D")
    #
    from lib.gaussian.FOM_analysis import FOM_analysis

    analysis = FOM_analysis()
    maxT = np.max(T)

    T_theo = analysis.gaussian_curve(l * 1e-6, 1326e-9, 40e-9) * maxT
    ax.plot(l * 1e3, T_theo, c="red", label="Gaussian_1326_40", alpha=0.4)
    plt.legend()
    #
    plt.savefig("4e25_ncc.png", bbox_inches="tight", dpi=200)
    plt.show()
