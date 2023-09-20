import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser
from lib.device.data_recorder import data_recorder

handle = init_labjack()


def _read_pd_power(handle, numAIN) -> float:
    if numAIN == 3:
        v = ljm_auto_range_read(handle, 3)
        p = 1e-6 * (4.22701823 * v + 0.09182073)
    elif numAIN == 4:
        v = ljm_auto_range_read(handle, 4)
        p = 1e-6 * (4.34946232 * v + 0.10039678)
    return float(p)  # type: ignore


def efficiency_input_output(handle):
    input_p = _read_pd_power(handle, 3)
    output_p = _read_pd_power(handle, 4)
    e = output_p / input_p
    return e, input_p, output_p


def photodiode_lambda_sweep(dataName, numAIN):
    laser = init_laser()
    handle = init_labjack()
    #
    xname = "power"
    x_list = np.arange(1305, 1315, 1)
    x_func = lambda l: laser.write_wavelength(l)
    y_func = lambda: _read_pd_power(handle, numAIN)
    data_recorder(dataName, xname, x_list, x_func, y_func, wait=0.1, measure_num=8)


print(_read_pd_power(handle, 3))
