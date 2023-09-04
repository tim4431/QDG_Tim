from lumapi_optimize import add_lumerical_path

add_lumerical_path()
import lumapi
import numpy as np


with lumapi.FDTD() as fdtd:
    fdtd.addstructuregroup(name="grating")
    fdtd.setnamed("grating", "scripts", "fk\n\shit\n")
    while True:
        pass
