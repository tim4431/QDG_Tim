import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser
from lib.device.data_recorder import data_recorder


def photodiode_power_sweep(dataName, numAIN):
    laser = init_laser()
    handle = init_labjack()
    #
    xname = "power"
    x_list = np.arange(-15, 13.5, 0.5)
    x_func = lambda p: laser.write_power(p)
    y_func = lambda: ljm_auto_range_read(handle, numAIN)
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=1.2, measure_num=8)


photodiode_power_sweep("./data/photodiode_AIN3_cal.csv", 3)
# photodiode_power_sweep("./data/photodiode_AIN4_cal.csv", 4)
