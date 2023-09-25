import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser
from lib.device.santec_internal_sweep import santec_internal_sweep
from lib.device.data_recorder import data_recorder
from lib.process_data.csv_data import appenddatas
import labjack.ljm as ljm
import datetime
import time
from typing import Union, List, Any, Tuple
import matplotlib.pyplot as plt


def v_to_pd_power(v: Union[float, np.ndarray], numAIN: int) -> Union[float, np.ndarray]:
    """
    - v: voltage (V)
    - numAIN: 2 or 3, pin number
    - return p: power (uW)
    """
    if numAIN == 2:
        p = 4.22701823 * v + 0.09182073
    elif numAIN == 3:
        p = 4.34946232 * v + 0.10039678
    else:
        raise ValueError("numAIN must be 2 or 3")
    return p


def _read_pd_power(handle: Any, numAIN: int) -> float:
    v = ljm_auto_range_read(handle, numAIN)
    p = v_to_pd_power(v, numAIN)
    return float(p)  # type: ignore


def _calc_efficiency(
    input_p: Union[float, np.ndarray], output_p: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    input_portion = 0.01
    output_portion = 1.0
    return (output_p / output_portion) / (input_p / input_portion)


def efficiency_input_output(handle) -> Tuple[float, float, float]:
    input_p = _read_pd_power(handle, 3)
    output_p = _read_pd_power(handle, 4)
    e = _calc_efficiency(input_p, output_p)
    return e, input_p, output_p


def getDataName(
    uuid: str, lambda_start: float, lambda_end: float, lambda_step: float
) -> str:
    now = datetime.datetime.now()
    date_str = now.strftime("%y%m%d")
    datetime_str = now.strftime("%y%m%d_%H%M%S")
    fileName = "./data_{:s}/{:s}_{:s}_{:.1f}_{:.1f}_{:.2f}.csv".format(
        date_str, datetime_str, uuid, lambda_start, lambda_end, lambda_step
    )
    return fileName


def set_mems_switch(handle, dir=0):
    """
    - dir = 0, santec, dir = 1, broadband
    """
    if dir == 0:
        ljm.eWriteName(handle, "DAC0", 4.5)
        ljm.eWriteName(handle, "DAC1", 0.0)
    elif dir == 1:
        ljm.eWriteName(handle, "DAC0", 0.0)
        ljm.eWriteName(handle, "DAC1", 4.5)
    time.sleep(0.05)
    # return to 0
    ljm.eWriteName(handle, "DAC0", 0.0)
    ljm.eWriteName(handle, "DAC1", 0.0)


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


def calibrate_grating(
    uuid: str, lambda_start: float, lambda_end: float, lambda_step: float
):
    laser = init_laser()
    l, datas = santec_internal_sweep(
        laser,
        power=5,
        aScanListNames=["AIN2", "AIN3"],
        scanRate=10000,
        start=lambda_start,
        end=lambda_end,
        sweeprate=10,
    )
    input_v, output_v = datas
    input_p = v_to_pd_power(input_v, 2)
    output_p = v_to_pd_power(output_v, 3)
    efficiency = _calc_efficiency(input_p, output_p)
    #
    x = l
    y = [input_p, output_p, efficiency]
    # >>> save data <<<
    dataName = getDataName(
        uuid, lambda_start=lambda_start, lambda_end=lambda_end, lambda_step=lambda_step
    )
    print(dataName)
    appenddatas(dataName, x, y)  # type: ignore
    # >>> plot data <<<
    # plt.plot(l, input_p, label="input")
    # plt.plot(l, output_p, label="output")
    plt.plot(l, efficiency, label="efficiency")
    plt.legend()
    plt.xlabel("wavelength")
    plt.ylabel("efficiency")
    plt.savefig(dataName.replace(".csv", ".png"), dpi=200, bbox_inches="tight")


def align_grating(dir: int = 0):
    laser = init_laser()
    handle = init_labjack()
    laser.write_power(13)
    laser.write_wavelength(1326)
    set_mems_switch(handle, dir=dir)
    print("Start Calibration")
    time.sleep(1)
    #
    efficiency_List = []
    DATA_LENGTH = 50  # keep 50 data points in efficiency_List
    # matplotlib constantly update
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel("time")
    ax.set_ylabel("efficiency")
    ax.set_ylim(0, 1)
    (line,) = ax.plot([], [], label="efficiency")
    ax.legend()
    #
    while True:
        e, input_p, output_p = efficiency_input_output(handle)
        print(
            "input: {:.4f}(uW), output: {:.4f}(uW), efficiency: {:.4f}".format(
                input_p, output_p, e
            )
        )
        efficiency_List.append(e)
        while (len(efficiency_List)) > DATA_LENGTH:
            efficiency_List.pop(0)
        line.set_data(range(len(efficiency_List)), efficiency_List)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.05)


if __name__ == "__main__":
    handle = init_labjack()
    # print(_read_pd_power(handle, 2))
    set_mems_switch(handle, dir=0)
