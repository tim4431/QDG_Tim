from lumapi_optimize import add_lumerical_path

add_lumerical_path()
import lumapi
import numpy as np
import os


def load_script(script_name):
    cwd = os.getcwd()
    with open(os.path.join(cwd, "script", script_name), "r") as f:
        script = f.read()
        return script


def setup_grating_structuregroup(fdtd, grating_typ):
    if grating_typ == "subw_grating":
        fdtd.addstructuregroup(name="subw_grating")
        fdtd.setnamed(
            "subw_grating", "script", load_script("subw_grating_concentric.lsf")
        )
    elif grating_typ == "inverse_grating":
        fdtd.addstructuregroup(name="inverse_grating")
        fdtd.setnamed(
            "inverse_grating", "script", load_script("inverse_grating_concentric.lsf")
        )


with lumapi.FDTD() as fdtd:
    setup_grating_structuregroup(fdtd, "subw_grating")
    setup_grating_structuregroup(fdtd, "inverse_grating")
    while 1:
        pass
