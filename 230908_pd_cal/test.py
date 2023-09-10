import sys

sys.path.append("..")
from lib.device.device import *

handle = init_labjack()
res = ljm.eReadName(handle, "AIN2")
print(res)
ljm.close(handle)
