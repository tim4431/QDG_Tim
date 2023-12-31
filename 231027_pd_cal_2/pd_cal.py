import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser
from lib.device.data_recorder import data_recorder
from lib.process_data.calibration import calibrate_photodiode, calibrate_photodiode_LH
from lib.process_data.csv_data import load_csv_data
import matplotlib.pyplot as plt


def photodiode_power_sweep(dataName, numAIN):
    laser = init_laser(system=1)
    handle = init_labjack(system=1)
    #
    xname = "att"
    yname = "v"
    x_list = np.arange(-15, 13.5, 0.5)
    x_func = lambda p: laser.write_power(p)
    y_func = lambda: ljm_auto_range_read(handle, numAIN)
    data_recorder(
        dataName, xname, yname, x_list, x_func, y_func, wait=0.1, measure_num=8
    )


att, p, _ = load_csv_data("./data/santec_power_sweep.csv", None, key_x="att", key_y="p")
p_att_dict = {att: p for att, p in zip(att, p)}

if __name__ == "__main__":
    # # 1.measure data
    # photodiode_power_sweep("./data_231027/photodiode_AIN2b_L_cal.csv", 2)

    # 2. fit using ax+b
    fig, ax = plt.subplots()
    popt = calibrate_photodiode(
        ax,
        "./data_231027/photodiode_AIN2_H_cal.csv",
        # max_power=15.90,
        # max_power=15.90 / (10**2.37),
        max_power=37.29,
        # max_power=37.29 / (10**2),
        p_att_dict=p_att_dict,
        sigma_multiplier=3,
        color="blue",
    )
    popt = calibrate_photodiode(
        ax,
        "./data_230909/photodiode_power_sweep_560_1.csv",
        max_power=40.77,
        p_att_dict=p_att_dict,
        sigma_multiplier=3,
        color="purple",
    )
    # plt.xscale("log")
    # plt.yscale("log")
    # print(popt)
    plt.show()

    # # 3. fit L and H
    # popt = calibrate_photodiode_LH(
    #     dataName_L="./data_231027/photodiode_AIN2b_L_cal.csv",
    #     dataName_H="./data_231027/photodiode_AIN2b_H_cal.csv",
    #     max_power_H=15.90,
    #     p_att_dict=p_att_dict,
    #     sigma_multiplier=3,
    # )
    # # plt.xscale("log")
    # # plt.yscale("log")
    # # print(popt)
    # plt.show()
