from lumapi_optimize import add_lumerical_path
add_lumerical_path()
import lumapi
import numpy as np


with lumapi.FDTD() as fdtd:
    fdtd.addstructuregroup(name="grating")
    fdtd.addstructuregroup(name="grating1")
    fdtd.addstructuregroup(name="grating2")


    fdtd.addrect()
    fdtd.addtogroup("grating")
    fdtd.select("grating3")
    fdtd.delete()
    while 1:
        pass
