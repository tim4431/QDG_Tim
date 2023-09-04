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


def setup_grating_structuregroup(fdtd, grating_typ:str):
    fdtd.addstructuregroup(name=grating_typ)
    fdtd.adduserprop("wg_h", 2, 220e-9)
    fdtd.adduserprop("start_radius", 2, 10e-6)
    fdtd.adduserprop("taper_angle", 0, 24)
    fdtd.adduserprop("N", 0, 10)
    # adduserprop("property name", type, value);
    # type 0 - number, type 2 - Length, type 6 - matrix
    if grating_typ == "subw_grating":
        fdtd.adduserprop("Lambda", 2, 1.326e-6)
        fdtd.adduserprop("ff", 0, 0.5)
        fdtd.adduserprop("ffL", 0, 0.2)
        fdtd.adduserprop("ffH", 0, 0.8)
        fdtd.adduserprop("NL", 0, 2)
        fdtd.adduserprop("NH", 0, 3)
        #
        fdtd.setnamed(
            "subw_grating", "script", load_script("subw_grating_concentric.lsf")
        )
    elif grating_typ == "inverse_grating":
        fdtd.adduserprop("pitch_list", 6, np.array([0.5e-6] * 10))
        fdtd.adduserprop("ff_list", 6, np.array([0.2] * 10))
        #
        fdtd.setnamed(
            "inverse_grating", "script", load_script("inverse_grating_concentric.lsf")
        )


with lumapi.FDTD() as fdtd:
    setup_grating_structuregroup(fdtd, "subw_grating")
    # setup_grating_structuregroup(fdtd, "inverse_grating")
    while 1:
        pass
