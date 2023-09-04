import lumapi
import numpy as np

with lumapi.FDTD() as fdtd:
    fdtd.addgroup("grating")
    fdtd.addrect()
    fdtd.addtogroup("grating")
    while 1:
        pass
