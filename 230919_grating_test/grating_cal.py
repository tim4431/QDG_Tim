import sys
import numpy as np

sys.path.append("..")
from lib.device.device import (
    ljm_auto_range_read,
    init_labjack,
    init_laser,
    init_sutter,
    sutter_move,
)
from lib.device.santec_internal_sweep import santec_internal_sweep
from lib.device.data_recorder import data_recorder
from lib.process_data.csv_data import appenddatas, init_csv_heads
import labjack.ljm as ljm
import datetime
import time
from typing import Union, List, Any, Tuple, Callable
import matplotlib.pyplot as plt
from scipy.optimize import minimize


def v_to_pd_power(v: Union[float, np.ndarray], numAIN: int) -> Union[float, np.ndarray]:
    """
    - v: voltage (V)
    - numAIN: 2 or 3, pin number
    - return p: power (uW)
    """
    # fill in your calibration coeffs here
    if numAIN == 2:
        p = 3.97730538 * v + 4.20229793e-04
    elif numAIN == 3:
        p = 3.71470995 * v - 4.70855634e-04
    else:
        raise ValueError("numAIN must be 2 or 3")
    return p


def _read_pd_power(handle: Any, numAIN: int) -> float:
    v = ljm_auto_range_read(handle, numAIN)
    p = v_to_pd_power(v, numAIN)
    return float(p)  # type: ignore


def _calc_transmission(
    input_p: Union[float, np.ndarray], output_p: Union[float, np.ndarray]
) -> np.ndarray:
    input_portion = 15.28
    output_portion = 1234
    att_ratio = (np.asarray(output_p) / output_portion) / (
        np.asarray(input_p) / input_portion
    )
    att_ratio[att_ratio <= 0] = 0
    return np.sqrt(att_ratio)


def transmission_input_output(handle) -> Tuple[float, float, float]:
    input_p = _read_pd_power(handle, 2)
    output_p = _read_pd_power(handle, 3)
    e = float(_calc_transmission(input_p, output_p))
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


def set_mems_switch(handle, source=0):
    """
    - source = 0, santec, source = 1, broadband
    """
    if source == 0:
        ljm.eWriteName(handle, "DAC0", 4.5)
        ljm.eWriteName(handle, "DAC1", 0.0)
    elif source == 1:
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
    uuid: str,
    handle: Any,
    lambda_start: float,
    lambda_end: float,
    lambda_step: float,
    power: float = 9.0,
):
    laser = init_laser()
    set_mems_switch(handle, source=0)  # should be santec
    # >>> sweep <<<
    l, datas = santec_internal_sweep(
        handle,
        laser,
        power=power,
        aScanListNames=["AIN2", "AIN3"],
        scanRate=1000,
        start=lambda_start,
        end=lambda_end,
        sweeprate=50,
    )
    input_v, output_v = datas
    input_p = v_to_pd_power(input_v, 2)
    output_p = v_to_pd_power(output_v, 3)
    transmission = _calc_transmission(input_p, output_p)
    # >>> extract data <<<
    x = l
    y = [input_p, output_p, transmission]
    # >>> save data <<<
    dataName = getDataName(
        uuid, lambda_start=lambda_start, lambda_end=lambda_end, lambda_step=lambda_step
    )
    print(dataName)
    init_csv_heads(
        dataName, xname="l", yname=["input_p(uW)", "output_p(uW)", "transmission"]
    )
    appenddatas(dataName, x, y)  # type: ignore
    # >>> plot data <<<
    plt.plot(l, transmission, label="Transmission")
    plt.legend()
    plt.xlabel(r"Wavelength $\lambda$(nm)")
    plt.ylabel(r"Transmission $T(\lamnbda)$")
    plt.savefig(dataName.replace(".csv", ".png"), dpi=200, bbox_inches="tight")
    plt.show()


def plot_ion_transmission(callback_func: Callable, HIST_LENGTH: int = 50):
    datas = []
    # >>> plot data <<<
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel("time")
    ax.set_ylabel("transmission")
    # ax.set_ylim(0, 1)
    (line,) = ax.plot([], [])
    # >>> update data <<<
    try:
        while True:
            e = callback_func()
            datas.append(e)
            while (len(datas)) > HIST_LENGTH:
                datas.pop(0)
            line.set_data(range(len(datas)), datas)
            ax.relim()
            ax.autoscale_view()
            fig.canvas.flush_events()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("KeyboardInterrupt, stop")
    finally:
        plt.ioff()


def plot_ion_position_transmission(
    callback_func: Callable, HIST_LENGTH: int = 50, automatic=False
):
    datas = []  # [(x1,y1,T1), (x2,y2,T2), ...)]
    # >>> plot data <<<
    plt.ion()
    fig, axs = plt.subplots(nrows=1, ncols=2)
    axs[0].set_xlabel("x(um)")
    axs[0].set_ylabel("y(um)")
    axs[0].set(xlim=(-1000, 1000), ylim=(-1000, 1000))
    axs[1].set_xlabel("time")
    axs[1].set_ylabel("transmission")
    # ax.set_ylim(0, 1)
    fig_position = axs[0].scatter([], [])
    (fig_transmission,) = axs[1].plot([], [])
    # >>> update data <<<

    def _optimize_wrapper(datas, callback_func, paras):
        x, y, T = callback_func(paras)
        datas.append((x, y, T))
        while (len(datas)) > HIST_LENGTH:
            datas.pop(0)
        #
        xs, ys, es = zip(*datas)
        fig_position.set_offsets(np.column_stack((xs, ys)))
        fig_position.set_array(es)
        # fig_position.set_alpha(np.linspace(0.1, 1, len(xs)))  # alpha increase with time
        # fig_position.set_cmap("jet")
        # axs[0].relim()
        # axs[0].autoscale_view()
        #
        fig_transmission.set_data(range(len(es)), es)
        axs[1].relim()
        axs[1].autoscale_view()
        #
        fig.canvas.flush_events()
        #
        return -T

    #
    try:
        if automatic:
            minimize(
                lambda paras: _optimize_wrapper(datas, callback_func, paras),
                x0=[0, 0],
                method="L-BFGS-B",
                bounds=[(-10, 10), (-10, 10)],
            )
        else:
            while True:
                _optimize_wrapper(datas, callback_func, paras=[0, 0])
                time.sleep(0.2)

    except KeyboardInterrupt:
        print("KeyboardInterrupt, stop")
    finally:
        plt.ioff()
        return


def align_grating_1D(handle, power: float = 9.0, source: Union[None, int] = None):
    if source == None:
        pass
    elif source == 0:
        laser = init_laser(wavelength=1326.0, power=power)
        set_mems_switch(handle, source=0)
    elif source == 1:
        set_mems_switch(handle, source=1)
    #
    print("Start Calibration")
    time.sleep(0.5)

    #
    def transmission_manual():
        e, input_p, output_p = transmission_input_output(handle)
        print(
            "input: {:.4f}(uW), output: {:.4f}(uW), transmission: {:.4f}".format(
                input_p, output_p, e
            )
        )
        return e

    #
    callback_func = transmission_manual
    plot_ion_transmission(callback_func)


def align_grating_2D(
    handle, power: float = 9.0, source: Union[None, int] = None, automatic=False
):
    if source == None:
        pass
    elif source == 0:
        laser = init_laser(wavelength=1326.0, power=power)
        set_mems_switch(handle, source=0)
    elif source == 1:
        set_mems_switch(handle, source=1)
    #
    print("Start Calibration")
    time.sleep(0.5)

    #
    def transmission_manual(sutter, paras):
        # e, input_p, output_p = transmission_input_output(handle)
        # print(
        #     "input: {:.4f}(uW), output: {:.4f}(uW), transmission: {:.4f}".format(
        #         input_p, output_p, e
        #     )
        # )
        # return e
        x = sutter.get_x_position()
        y = sutter.get_y_position()
        e = 0.1 * x**2 + 0.5 * y**2
        print("x: {:.4f}(um), y:{:.4f}(um)".format(x, y))
        return (x, y, e)

    def sutter_step(sutter, paras):
        x = paras[0]
        y = paras[1]
        # sutter_move(sutter, x, y)
        time.sleep(0.1)
        x = sutter.get_x_position()
        y = sutter.get_y_position()
        T, input_p, output_p = transmission_input_output(handle)
        print(
            "x: {:.4f}(um), y:{:.4f}(um), input: {:.4f}(uW), output: {:.4f}(uW), transmission: {:.4f}".format(
                x, y, input_p, output_p, T
            )
        )
        return (x, y, T)

    #
    try:
        sutter = init_sutter()
        # sutter.sendReset()
        time.sleep(0.5)
        print(sutter.getPosition())
        if not automatic:
            callback_func = lambda paras: transmission_manual(sutter, paras)
            plot_ion_position_transmission(callback_func, automatic=False)
        else:
            callback_func = lambda paras: sutter_step(sutter, paras)
            plot_ion_position_transmission(callback_func, automatic=True)
    finally:
        print("Close Sutter")
        del sutter  # type: ignore


if __name__ == "__main__":
    # handle = init_labjack()
    handle = None
    try:
        # print(_read_pd_power(handle, 2))
        # print(_read_pd_power(handle, 3))
        # set_mems_switch(handle, source=0)
        # align_grating_1D(handle=handle, source=None)
        # calibrate_grating("xxxx",1260,1300, 1)
        align_grating_2D(handle=handle, source=None, automatic=False)
    finally:
        if handle is not None:
            ljm.close(handle)
