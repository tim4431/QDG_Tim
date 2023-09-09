import sys
import numpy as np

sys.path.append("..")
from lib.device.device import *
from lib.device.data_recorder import data_recorder


def ljm_handle_att(handle, att):
    p = (50) * (10 ** ((att - 13) / 10))
    estimated_v = 0.2319 * p
    print("estimated_v: ", estimated_v)
    ljm_auto_range_resolution(handle, 0, estimated_v)


def santec_power_sweep(dataName):
    laser = init_laser()
    xname = "power"
    x_list = np.arange(0, 10, 0.5)
    x_func = laser.write_power
    y_func = input
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=1, measure_num=1)


santec_power_sweep("./data/santec_power_sweep.csv")


def photodiode_power_sweep(dataName):
    laser = init_laser()
    handle = init_labjack()
    #
    xname = "power"
    x_list = np.arange(-15, 9.5, 0.5)
    x_func = laser.write_power
    y_func = lambda: ljm.eReadName(handle, "AIN2")
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=1.5, measure_num=6)


# photodiode_power_sweep("./data/photodiode_power_sweep_1.2k.csv")
