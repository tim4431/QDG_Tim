from data_recorder import *


def _init_laser():
    laser = RemoteDevice("SantecTSL570")
    laser.write_laser_status("On")
    laser.write_wavelength(1326.0)
    return laser


def _init_picoharp():
    return RemoteDevice("PicoHarp300")


def santec_power_sweep():
    laser = _init_laser()
    dataName = "./santec_power_sweep.csv"
    xname = "power"
    x_list = np.arange(-14, -6, 0.5)
    x_func = laser.write_power
    y_func = input
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=2, measure_num=1)


def snspd_cal():
    picoharp = _init_picoharp()

    current_list_1 = np.array(
        [
            7.97,
            8.50,
            8.99,
            9.48,
            10.02,
            10.51,
            11.00,
            11.49,
            11.97,
            12.51,
            13.00,
        ]
    )
    current_list_2 = np.array(
        [
            7.97,
            8.50,
            8.99,
            9.48,
            10.02,
            10.51,
            11.00,
            11.49,
            11.97,
            12.51,
            13.00,
            13.49,
        ]
    )
    current_fine_list_1 = np.array(
        [
            13.25,
            13.49,
            13.73,
            13.98,
            14.27,
            14.52,
            14.76,
            15.00,
            15.25,
            15.49,
        ]
    )
    current_fine_list_2 = np.array(
        [
            13.73,
            13.98,
            14.27,
            14.52,
            14.76,
            15.00,
            15.25,
            15.49,
            15.74,
            15.98,
        ]
    )
    dataName = "./snspd1_lum_comnbine.csv"
    xname = "current"
    x_list = current_list_1
    x_func = lambda: None
    y_func = lambda: picoharp.aver_count1(5)
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=0, measure_num=5)
    #
    xname = "current"
    x_list = current_fine_list_1
    x_func = lambda: None
    y_func = lambda: picoharp.aver_count1(5)
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=0, measure_num=5)


def photodiode_power_sweep():
    laser = _init_laser()
    picoharp = _init_picoharp()
    #
    dataName = "./photodiode_power_sweep.csv"
    xname = "power"
    x_list = np.arange(-14, -6, 0.5)
    x_func = laser.write_power
    y_func = lambda: picoharp.aver_count1(5)
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=2, measure_num=1)
