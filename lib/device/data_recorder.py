import sys
import numpy as np
import time

sys.path.append(r"\\QDG-LABBEAR\\Users\\QDG-LABBEAR-SERVER\\Desktop\\LANAS\\DataBear")
from RemoteDevice import RemoteDevice
from typing import Callable

picoharp = RemoteDevice("PicoHarp300")
laser = RemoteDevice("SantecTSL570")

laser.write_laser_status("On")
laser.write_wavelength(1326.0)


def appenddata(dataName, x, y):
    with open(dataName, "a") as f:
        f.write("{:.2f},{:.2f}\n".format(x, y))


def _nop(x):
    pass


def data_recorder(
    dataName: str,
    xname: str,
    x_list: np.ndarray,
    x_func: Callable,
    y_func: Callable,
    idx_start: int = 0,
    wait=2,
    measure_num=1,
):
    for x in x_list[idx_start:]:
        print("{:s}, {:.2f}".format(xname, x))
        x_func(x)
        if wait is not None:
            if wait == 0:
                a = input()
            else:
                time.sleep(wait)
        #
        print("begin")
        for j in range(measure_num):
            y = y_func()
            print(y)
            appenddata(dataName, x, y)
        print("finished")
