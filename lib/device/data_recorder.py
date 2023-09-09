import sys
import numpy as np
import time

sys.path.append(r"\\QDG-LABBEAR\\Users\\QDG-LABBEAR-SERVER\\Desktop\\LANAS\\DataBear")
from RemoteDevice import RemoteDevice  # type: ignore
from typing import Callable


def appenddata(dataName, x, y):
    with open(dataName, "a") as f:
        f.write("{:.2f},{:.5f}\n".format(float(x), float(y)))


def nop(x):
    pass


def data_recorder(
    dataName: str,
    xname: str,
    x_list: np.ndarray,
    x_func: Callable,
    y_func: Callable,
    idx_start: int = 0,
    wait: float = 2.0,
    measure_num=1,
):
    for x in x_list[idx_start:]:
        print("{:s}: {:.2f}".format(xname, x))
        x_func(x)
        if wait is not None:  # if is none, just don't wait
            if wait == 0:  # manual input
                a = input()
            else:
                time.sleep(wait)
        #
        print("begin")
        for j in range(measure_num):
            y = float(y_func())
            print(y)
            appenddata(dataName, x, y)
            time.sleep(0.2)
        print("finished")
