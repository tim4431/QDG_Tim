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
    handle = init_labjack()
    #
    xname = "att"
    yname = "p"
    x_list = np.arange(-15, 13.5, 0.5)
    x_func = lambda p: laser.write_power(p)
    y_func = lambda: ljm_auto_range_read(handle, numAIN)
    data_recorder(
        dataName, xname, yname, x_list, x_func, y_func, wait=1.2, measure_num=8
    )


# photodiode_power_sweep("./data/photodiode_AIN3_cal.csv", 3)
# photodiode_power_sweep("./data/photodiode_AIN4_cal.csv", 4)

att, p, _ = load_csv_data("./data/santec_power_sweep.csv", None, key_x="att", key_y="p")
p_att_dict = {att: p for att, p in zip(att, p)}
#
fig, ax = plt.subplots()
popt = calibrate_photodiode(
    ax,
    "./data/photodiode_AIN3_cal.csv",
    max_att=11.00,
    max_power=38.92,
    p_att_dict=p_att_dict,
    sigma_multiplier=3,
)
print(popt)
#
fig, ax = plt.subplots()
popt = calibrate_photodiode(
    ax,
    "./data/photodiode_AIN4_cal.csv",
    max_att=11.00,
    max_power=38.92,
    p_att_dict=p_att_dict,
    sigma_multiplier=3,
)
print(popt)
plt.show()
