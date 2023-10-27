import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser
from lib.device.data_recorder import data_recorder
from lib.process_data.calibration import calibrate_photodiode
from lib.process_data.csv_data import load_csv_data
import matplotlib.pyplot as plt


def photodiode_power_sweep(dataName, numAIN):
    laser = init_laser()
    handle = init_labjack(system=0)
    #
    xname = "att"
    yname = "v"
    x_list = np.arange(-15, 13.5, 0.5)
    x_func = lambda p: laser.write_power(p)
    y_func = lambda: ljm_auto_range_read(handle, numAIN)
    data_recorder(
        dataName, xname, yname, x_list, x_func, y_func, wait=0.1, measure_num=8
    )


# photodiode_power_sweep("./data_231027/photodiode_AIN2_L_cal.csv", 2)

att, p, _ = load_csv_data("./data/santec_power_sweep.csv", None, key_x="att", key_y="p")
p_att_dict = {att: p for att, p in zip(att, p)}
#
fig, ax = plt.subplots()
popt = calibrate_photodiode(
    ax,
    "./data_231027/photodiode_AIN2_H_cal.csv",
    max_att=13.00,
    max_power=0.5442,
    p_att_dict=p_att_dict,
    sigma_multiplier=3,
)
plt.xscale("log")
plt.yscale("log")
print(popt)
plt.show()
