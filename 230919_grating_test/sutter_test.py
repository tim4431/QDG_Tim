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

sutter= init_sutter()
sutter.set_x_position(1)
print(sutter.getPosition())