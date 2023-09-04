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


with lumapi.FDTD() as fdtd:
    fdtd.addstructuregroup(name="grating")
    fdtd.setnamed("grating", "script", load_script("subw_grating_concentric.lsf"))
    while True:
        pass
