from lumapi_optimize import (
    getdataName,
    setup_geometry,
    setup_simulation_dir,
    setup_monitor,
    setup_grating_structuregroup,
    fdtd_iter,
    load_template,
)
import numpy as np
from json_uuid import load_json, load_paras
from const_var import DEFAULT_PARA
import sys
import os
import matplotlib.pyplot as plt
from create_gds import generate_gds_fileName
import time

sys.path.append("..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d


def reload_work(
    uuid: str,
    dimension: str = "2D",
    #
    reload_simulation_typ: int = 0,
    tether_typ=None,
    pause=False,
    monitor=True,
    movie=False,
    advanced_monitor=False,
):
    # >>> load uuid <<< #
    dataName = getdataName(uuid)
    kwargs = load_json(uuid)
    kwargs["plot"] = False
    print("Loading work: ", uuid)
    # print kwargs
    for key, value in kwargs.items():
        if key in DEFAULT_PARA.keys():
            print("{:s} = {:s}".format(key, str(value)))
        else:
            print("Unknown key: {:s}".format(key))
    # >>> load paras <<< #
    paras = load_paras(uuid)
    print("Loaded paras: ", paras)
    #
    # >>> begin simulation <<< #
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    with load_template(
        dataName,
        SOURCE_typ,
        purpose="{:s}_{:s}_simluated_{:d}".format(
            str(tether_typ), dimension, reload_simulation_typ
        ),
    ) as fdtd:
        try:
            # >>> setup monitor <<< #
            setup_geometry(fdtd, dimension=dimension, **kwargs)
            setup_monitor(
                fdtd,
                monitor=monitor,
                movie=movie,
                advanced_monitor=advanced_monitor,
            )
            # >>> setup grating <<< #
            if tether_typ is not None:  # import gds
                gds_fileName = generate_gds_fileName(uuid, tether_typ=tether_typ)
                print("Loading gds: ", gds_fileName)
                fdtd.gdsimport(
                    gds_fileName,
                    "grating_gds",
                    1,
                    "Si (Silicon) - Palik",
                    -0.11e-6,
                    0.11e-6,
                )
                fdtd.setnamed("gratings", "enabled", 0)
                fdtd.setnamed("GDS_LAYER_1:0", "first axis", "x")
                fdtd.setnamed("GDS_LAYER_1:0", "rotation 1", 90)
            else:  # setup by script
                setup_grating_structuregroup(fdtd, **kwargs)

            # >>> run simulation <<< #
            l, T, R, maxT, lambda_maxT, FWHM_fit, FOM = fdtd_iter(
                fdtd,
                paras,
                reload_simulation_typ=reload_simulation_typ,
                reload_gds=False if (tether_typ == None) else True,
                dimension=dimension,
                **kwargs,
            )
            print("MaxT: ", maxT)
            print("lambda_maxT: ", lambda_maxT)
            print("FWHM: ", FWHM_fit)
            print("FOM: ", FOM)
            #
            # >>> save data <<< #
            if reload_simulation_typ in [0, 2]:
                try:
                    a = np.transpose(np.vstack((l * 1e6, T)))  # wavelength in um
                    np.savetxt(
                        "{:s}_{:s}_{:s}_simulated_transmission.txt".format(
                            dataName, str(tether_typ), dimension
                        ),
                        a,
                    )
                except Exception as e:
                    print("reload_res: save transmission Error: ", str(e))
            #
            if reload_simulation_typ in [1, 2]:
                try:
                    a = np.transpose(np.vstack((l * 1e6, R)))  # wavelength in um
                    np.savetxt(
                        "{:s}_{:s}_{:s}_simulated_reflection.txt".format(
                            dataName, str(tether_typ), dimension
                        ),
                        a,
                    )
                except Exception as e:
                    print("reload_res: save reflection Error: ", str(e))
            # >>> plot <<< #
            if reload_simulation_typ in [0, 2]:
                try:
                    fig, ax = plt.subplots(figsize=(9, 6))
                    arb_fit_1d(ax, l * 1e9, T, r"$T(\lambda)$", label=True)
                    ax.legend(loc="upper right")
                    plt.title("Transmission vs wavelength")
                    plt.savefig(
                        "{:s}_{:s}_{:s}_simulated_transmission.png".format(
                            dataName, str(tether_typ), dimension
                        ),
                        bbox_inches="tight",
                        dpi=100,
                    )
                    plt.close()
                except Exception as e:
                    print("reload_res: save transmission figure Error: ", str(e))
            if reload_simulation_typ in [1, 2]:
                try:
                    fig, ax = plt.subplots(figsize=(9, 6))
                    arb_fit_1d(ax, l * 1e9, R, r"$R(\lambda)$", label=True)
                    ax.legend(loc="upper right")
                    plt.title("Reflection vs wavelength")
                    plt.savefig(
                        "{:s}_{:s}_{:s}_simulated_reflection.png".format(
                            dataName, str(tether_typ), dimension
                        ),
                        bbox_inches="tight",
                        dpi=100,
                    )
                    plt.close()
                except Exception as e:
                    print("reload_res: save reflection figure Error: ", str(e))
        except Exception as e:
            print("reload_res: Error: ", e)
        # >>> if pause, keeps the lumerical window open <<< #
        if pause:
            while 1:
                pass


if __name__ == "__main__":
    #
    reload_work(
        "f3b5",
        dimension="2D",
        reload_simulation_typ=2,
        tether_typ=None,
        pause=False,
        advanced_monitor=False,
    )
    reload_work(
        "f3b5",
        dimension="3D",
        reload_simulation_typ=0,
        tether_typ=None,
        pause=False,
        advanced_monitor=False,
    )
