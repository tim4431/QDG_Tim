import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 6))
    uuidList = [
        "0eb0",
        "570e",
        "e199",
        "793c",
        "e86b",
        "15a5",
        "d1fd",
        "6ade",
        "674e",
        "a72b",
        "aa7c",
    ]
    lambdaList = [1120, 1160, 1200, 1240, 1280, 1320, 1360, 1400, 1440, 1480, 1520]
    for uuid, lambda_0 in zip(uuidList, lambdaList):
        dataName = "{:s}_{:.1f}_bw=20.0_transmission.txt".format(uuid, lambda_0)
        data = np.loadtxt(dataName)
        arb_fit_1d(ax, data[:, 0] * 1e3, data[:, 1], "{:.1f}".format(lambda_0))
    plt.legend()
    plt.savefig("grating_sweep_compare_transmission.png", dpi=200, bbox_inches="tight")
    plt.show()
