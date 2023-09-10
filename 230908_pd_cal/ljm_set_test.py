import sys

sys.path.append("..")
from lib.device.device import *

handle = init_labjack()
ljm_conf_range_resolution(handle, 2, 10, 4)
print(ljm_read_range_resolution(handle, 2))
ljm_conf_range_resolution(handle, 2, 1, 7)
print(ljm_read_range_resolution(handle, 2))
ljm.close(handle)
