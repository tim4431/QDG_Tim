import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser
from lib.device.data_recorder import data_recorder
import datetime


def _read_pd_power(handle, numAIN) -> float:
    v = ljm_auto_range_read(handle, numAIN)
    # print(v)
    if numAIN == 2:
        p = 4.22701823 * v + 0.09182073
    elif numAIN == 3:
        p = 4.34946232 * v + 0.10039678
    return float(p)  # type: ignore


def efficiency_input_output(handle):
    input_p = _read_pd_power(handle, 3)
    output_p = _read_pd_power(handle, 4)
    e = output_p / input_p
    return e, input_p, output_p


def getDataName(uuid, lambda_start, lambda_end, lambda_step):
    now = datetime.datetime.now()
    date_str = now.strftime("%y%m%d")
    datetime_str = now.strftime("%y%m%d_%H%M%S")
    fileName = "./data_{:s}/{:s}_{:s}_{:.1f}_{:.1f}_{:.2f}.csv".format(
        date_str, datetime_str, uuid, lambda_start, lambda_end, lambda_step
    )
    return fileName


def set_mems_switch(handle, dir=0):
    if dir == 0:
        ljm.eWriteName(handle, "DAC0", 4.5)
        ljm.eWriteName(handle, "DAC1", 0.0)
    elif dir == 1:
        ljm.eWriteName(handle, "DAC0", 0.0)
        ljm.eWriteName(handle, "DAC1", 4.5)


def photodiode_lambda_sweep(
    uuid: str, lambda_start: float, lambda_end: float, lambda_step: float, numAIN: int
):
    laser = init_laser()
    handle = init_labjack()
    laser.write_power(8.0)
    #
    xname = "l"
    yname = "p"
    x_list = np.arange(lambda_start, lambda_end, lambda_step)
    x_func = lambda l: laser.write_wavelength(l)
    y_func = lambda: _read_pd_power(handle, numAIN)
    #
    dataName = getDataName(uuid, lambda_start, lambda_end, lambda_step)
    print(dataName)
    #
    data_recorder(
        dataName,
        xname,
        yname,
        x_list,
        x_func,
        y_func,
        wait=0.1,
        measure_num=3,
    )


if __name__ == "__main__":
    handle = init_labjack()
    # print(_read_pd_power(handle, 2))
    set_mems_switch(handle, dir=0)
