import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
sys.path.append("..")
from json_uuid import uuid_to_wd, getdataName
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    uuid = "ee71"
    dataName = getdataName(uuid)
    fig, ax = plt.subplots(figsize=(10, 6))
    # >>> 2D <<< #
    fileName = "{:s}_transmission.txt".format(dataName)
    data = np.loadtxt(fileName)
    arb_fit_1d(ax, data[:, 0] * 1e3, data[:, 1], "2D")
    # >>> 3D <<< #
    tether_typ_list = [
        "empty",
    ]
    for tether_typ in tether_typ_list:
        fileName = "{:s}_{:s}_3D_simulated_transmission.txt".format(
            dataName, tether_typ
        )
        data = np.loadtxt(fileName)
        arb_fit_1d(ax, data[:, 0] * 1e3, data[:, 1], "3D_{:s}".format(tether_typ))

    plt.legend()
    plt.savefig(
        "{:s}_compare_transmission.png".format(uuid), dpi=200, bbox_inches="tight"
    )
    plt.show()
