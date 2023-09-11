import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("..")
from json_uuid import uuid_to_wd, getdataName
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    dataName = getdataName("4e25")
    fig, ax = plt.subplots(figsize=(10, 6))
    # fileName = "{:s}_None_2D_simulated_transmission.txt".format(dataName)
    # data = np.loadtxt(fileName)
    # arb_fit_1d(ax, data[:, 0] * 1e3, data[:, 1], "2D")

    # tether_typ_list = ["empty", "section_tether", "section_rect_tether"]
    tether_typ_list = [
        "empty",
        "section_rect_tether",
        "section_rect_tether_suspend",
        "section_rect_tether_hole",
        "section_rect_tether_hole_suspend",
    ]
    for tether_typ in tether_typ_list:
        fileName = "{:s}_{:s}_3D_simulated_transmission.txt".format(
            dataName, tether_typ
        )
        data = np.loadtxt(fileName)
        arb_fit_1d(ax, data[:, 0] * 1e3, data[:, 1], "3D_{:s}".format(tether_typ))

    plt.legend()
    plt.savefig("4e25_compare_transmission_1.png", dpi=200, bbox_inches="tight")
    plt.show()
