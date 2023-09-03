import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("..")
from json_uuid import uuid_to_wd, getdataName


dataName = getdataName("4e25")
tether_typ_list = ["empty", "section_tether", "section_rect_tether"]
for tether_typ in tether_typ_list:
    fileName = "{:s}_{:s}_3D_simulated_transmission.txt".format(dataName, tether_typ)
    data = np.loadtxt(fileName)
    plt.plot(data[:, 0], data[:, 1], label=tether_typ, alpha=0.4)

plt.legend()
plt.show()
