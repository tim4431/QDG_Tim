import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Callable, Union, List


def init_csv_heads(dataName: str, xname: str, yname: List[str]):
    with open(dataName, "w") as f:
        # xname, yname[0], yname[1], ...
        f.write("{:s},{:s}\n".format(xname, ",".join(yname)))


def appenddata(dataName: str, x: float, y: Union[List[float], np.ndarray]):
    with open(dataName, "a") as f:
        # x, y[0], y[1], ...
        f.write("{:.4f},{:s}\n".format(x, ",".join(["{:.8f}".format(yi) for yi in y])))


def appenddatas(
    dataName: str,
    x: Union[List[float], np.ndarray],
    y: List[Union[List[float], np.ndarray]],
):
    with open(dataName, "a") as f:
        # x[0], y[0][0], y[1][0] ...
        # x[1], y[0][1], y[1][1] ...
        for i in range(len(x)):
            f.write(
                "{:.4f},\t{:s}\n".format(
                    x[i], ",\t".join(["{:.8f}".format(yi[i]) for yi in y])
                )
            )


def _simple_load_csv_data(fileName: str, key_x: str, key_y: str):
    data = pd.read_csv(fileName)
    datax = data[key_x].to_numpy()
    datay = data[key_y].to_numpy()
    return datax, datay


def load_csv_data(
    fileName: str, select_func: Union[Callable, None], key_x: str, key_y: str
):
    datax, datay = _simple_load_csv_data(fileName, key_x, key_y)
    #
    if select_func is not None:
        select_mask = select_func(datax, datay)
        datax = datax[select_mask]
        datay = datay[select_mask]
    #
    x_list = sorted(list(set(datax)))
    mean_y_list = []
    std_y_list = []
    for x in x_list:
        x_mask = datax == x
        y_x = datay[x_mask]
        mean_y = np.mean(y_x)
        std_y = np.std(y_x)
        mean_y_list.append(mean_y)
        std_y_list.append(std_y)

    return np.array(x_list), np.array(mean_y_list), np.array(std_y_list)
