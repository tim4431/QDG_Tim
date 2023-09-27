import numpy as np
import time
from lib.process_data.csv_data import init_csv_heads, appenddata
from typing import Union, List, Callable, Any, Tuple


def nop(x):
    pass


def data_recorder(
    dataName: str,
    xname: str,
    yname: Union[List[str], str],
    x_list: np.ndarray,
    x_func: Callable,
    y_func: Union[List[Callable], Callable],
    idx_start: int = 0,
    wait: Union[None, float] = 2.0,
    measure_num=1,
):
    """
    - dataName: file name to save data
    - wait: None: no wait, 0: manual input, else: wait time in seconds
    """
    # assertion
    if isinstance(yname, str):
        yname = [yname]
    if isinstance(y_func, Callable):
        y_func = [y_func]
    assert len(yname) == len(y_func), "yname and y_func should have same length"
    # init csv file
    init_csv_heads(dataName, xname, yname)
    # Measure
    # using tqdm
    from tqdm import tqdm

    for idx, x in enumerate(tqdm(x_list[idx_start:])):
        print("{:s}: \t{:.4f}".format(xname, x))
        x_func(x)
        # wait
        if wait is not None:  # if is none, just don't wait
            if wait == 0:  # manual input
                a = input()
            else:
                time.sleep(wait)
        # measure
        print("Begin Measuring")
        for j in range(measure_num):
            y = []
            for yname_i, y_func_i in zip(yname, y_func):
                y_i = float(y_func_i())
                print("{:s}: \t{:.8f}".format(yname_i, y_i))
                y.append(y_i)
            #
            appenddata(dataName, x, y)
            time.sleep(0.001)
        print("Finished Measuring")
