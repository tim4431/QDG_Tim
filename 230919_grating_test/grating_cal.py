import sys
import numpy as np

sys.path.append("..")
from lib.device.device import ljm_auto_range_read, init_labjack, init_laser

handle = init_labjack()


def efficiency_input_output(handle):
    input_v = ljm_auto_range_read(handle, 3)
    input_p = 1e-6 * (4.22701823 * input_v + 0.09182073)
    output_v = ljm_auto_range_read(handle, 4)
    output_p = 1e-6 * (4.34946232 * output_v + 0.10039678)
    e = output_p / input_p
    return e, input_p, output_p
