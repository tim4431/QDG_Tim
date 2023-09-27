import sys
import numpy as np
from collections import deque

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
) -> Union[float, np.ndarray]:
    input_portion = 15.28
    output_portion = 1234
    att_ratio = (output_p / output_portion) / (input_p / input_portion)
    if isinstance(att_ratio, float):
        att_ratio = max(att_ratio, 0)
        return float(np.sqrt(att_ratio))
    else:
        att_ratio[att_ratio <= 0] = 0
        return np.sqrt(att_ratio)


def transmission_input_output(handle) -> Tuple[float, float, float]:
    input_p = _read_pd_power(handle, 2)
    output_p = _read_pd_power(handle, 3)
    e = float(_calc_transmission(input_p, output_p))
    return e, input_p, output_p


def mean_transmission_input_output(
    handle, meanNum: int = 1
) -> Tuple[float, float, float]:
    T_List = []
    input_p_List = []
    output_p_List = []
    for i in range(meanNum):
        T, input_p, output_p = transmission_input_output(handle)
        T_List.append(T)
        input_p_List.append(input_p)
        output_p_List.append(output_p)
        time.sleep(0.0005)
    T = np.mean(T_List)
    input_p = np.mean(input_p_List)
    output_p = np.mean(output_p_List)
    return float(T), float(input_p), float(output_p)


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
    plt.ylabel(r"Transmission $T(\lambda)$")
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
    except Exception as e:
        print(e)
    finally:
        plt.ioff()


def plot_ion_position_transmission(
    callback_func: Callable, HIST_LENGTH: int = 1000, automatic=False
):
    datas = deque(maxlen=HIST_LENGTH)  # [(x1,y1,T1), (x2,y2,T2), ...)]
    # >>> plot data <<<
    plt.ion()
    fig, axs = plt.subplots(nrows=1, ncols=2)
    # axs[0].set_xlabel("x(um)")
    # axs[0].set_ylabel("y(um)")
    axs[0].set(xlim=(-10, 10), ylim=(-10, 10), xlabel="y(um)", ylabel="x(um)")
    axs[1].set_xlabel("time")
    axs[1].set_ylabel("transmission")
    # ax.set_ylim(0, 1)
    fig_new_pt = axs[0].scatter([], [], marker="x", c="black", s=50)
    fig_position = axs[0].scatter([], [], c=np.array([]), cmap="jet", vmin=0, vmax=1)
    (fig_transmission,) = axs[1].plot([], [])
    # print(aaa)
    # >>> update data <<<

    def _optimize_wrapper(datas, callback_func, paras):
        # >>> update plot <<<
        if len(datas) > 0:
            xs, ys, es = zip(*datas)
            fig_position.set_offsets(np.column_stack((ys, xs)))
            fig_position.set_array(es)
            fig_position.set_alpha(
                np.linspace(0.2, 0.4, len(xs))
            )  # alpha increase with time
            #
            fig_transmission.set_data(range(len(es)), es)
            axs[1].relim()
            axs[1].autoscale_view()
        # highlight the new point
        fig_new_pt.set_offsets(np.column_stack((paras[1], paras[0])))
        x, y, T = callback_func(paras)
        # >>> update data <<<
        datas.append((x, y, T))
        #
        fig.canvas.flush_events()
        #
        return -T

    #
    try:
        if automatic:
            paras = minimize(
                lambda paras: _optimize_wrapper(datas, callback_func, paras),
                x0=[0, 0],
                # method="Nelder-Mead",
                method="Powell",
                # method="L-BFGS-B",
                bounds=[(-10, 10), (-10, 10)],
                options={"disp": True, "maxiter": 80, "ftol": 1e-9},
            )
            paras_final = paras.x
            res = input(
                "Accept the Final Position x={:.4f}(um), y={:.4f}(um) (y/n)?".format(
                    *paras_final
                )
            ).strip()
            if res == "n":
                callback_func([0, 0])
            else:
                pass
        else:  # 2D scanning
            X = np.linspace(-10, 10, 21)
            Y = np.linspace(-10, 10, 21)
            for x in X:
                for y in Y:
                    _optimize_wrapper(datas, callback_func, [x, y])
            callback_func([0, 0])
        #
        # >>> plot datas <<<
        fig, ax = plt.subplots()
        xs, ys, es = zip(*datas)
        ax.scatter(xs, ys, c=es, cmap="jet", vmin=0, vmax=1)
        ax.set(xlim=(-10, 10), ylim=(-10, 10), xlabel="y(um)", ylabel="x(um)")
        plt.show()

    except Exception as e:
        print(e)
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
        # e, input_p, output_p = transmission_input_output(handle)
        T, input_p, output_p = mean_transmission_input_output(handle, meanNum=5)
        print(
            "input: {:.4f}(uW), output: {:.4f}(uW), T: {:.4f}".format(
                input_p, output_p, T
            )
        )
        return T

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
        print("x: {:.4f}(um), y:{:.4f}(um)".format(x, y))
        # check distance
        sutter_x = sutter.get_x_position()
        sutter_y = sutter.get_y_position()
        distance = np.sqrt((x - sutter_x) ** 2 + (y - sutter_y) ** 2)
        if distance > 10:
            a = input(
                "Distance = {:.2f} um, Confirm moving (y/n)?".format(distance)
            ).strip()
            if a in ["y", ""]:
                sutter_move(sutter, x, y)
            else:
                print("Cancel moving")
        else:
            sutter_move(sutter, x, y)
        # wait for sutter to move
        # time.sleep(0.01 + 0.01 * distance)
        # check deviation
        x_act = sutter.get_x_position()
        y_act = sutter.get_y_position()
        deviation = np.sqrt((x - x_act) ** 2 + (y - y_act) ** 2)
        print(
            "x_act: {:.4f}(um), y_act:{:.4f}(um), deviation: {:.4f} um".format(
                x_act, y_act, deviation
            )
        )
        if deviation > 0.8:
            a = input(
                "Deviation = {:.4f}um, too large (y/n)?".format(deviation)
            ).strip()
        # measure transmission
        # T, input_p, output_p = mean_transmission_input_output(handle, meanNum=5)
        # print(
        #     "x: {:.4f}(um), y:{:.4f}(um), input: {:.2f}(uW), output: {:.4f}(uW), T: {:.4f}".format(
        #         x, y, input_p, output_p, T
        #     )
        # )
        T = 1 / (1 + abs(x / 10) + abs(y / 10))
        return (x, y, T)

    #
    try:
        sutter = init_sutter()
        time.sleep(0.5)
        if not automatic:
            callback_func = lambda paras: transmission_manual(sutter, paras)
            plot_ion_position_transmission(callback_func, automatic=False)
        else:
            callback_func = lambda paras: sutter_step(sutter, paras)
            plot_ion_position_transmission(callback_func, automatic=True)
    except Exception as e:
        print(e)
    finally:
        print("Close Sutter")
        del sutter  # type: ignore


if __name__ == "__main__":
    handle = init_labjack()
    # handle = None
    try:
        # print(_read_pd_power(handle, 2))
        # print(_read_pd_power(handle, 3))
        # set_mems_switch(handle, source=0)
        align_grating_1D(handle=handle, source=0)
        # calibrate_grating("top3", handle, 1260, 1400, 1, power=9.0)
        # align_grating_2D(handle=handle, source=0, automatic=True)
    finally:
        if handle is not None:
            ljm.close(handle)
