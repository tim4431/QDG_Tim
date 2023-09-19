import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser

handle = init_labjack()


def efficiency_input_output(handle):
    input_p = ljm_auto_range_read(handle, 3)
    output_p = ljm_auto_range_read(handle, 4)
    e = output_p / input_p
    return e, input_p, output_p
