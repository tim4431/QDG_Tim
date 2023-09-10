import sys

sys.path.append("..")
from lib.device.device import *

handle = init_labjack()
for i in range(8):
    ljm_conf_range_resolution(handle, i, 10, 0)
    print(ljm_read_range_resolution(handle, i))
ljm.close(handle)
