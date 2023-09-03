from lumapi_optimize import (
    getdataName,
    setup_source,
    setup_monitor,
    fdtd_iter,
    load_template,
    load_paras,
)
import numpy as np
from json_uuid import load_json, save_json, uuid_to_logname, uuid_to_wd
from const_var import DEFAULT_PARA
import sys
import os
import matplotlib.pyplot as plt
from create_gds import generate_gds_fileName

sys.path.append("..")


def reload_work(uuid, dimension="2D", tether_typ=None, pause=False, monitor=True):
    dataName = getdataName(uuid)
    kwargs = load_json(uuid)
    kwargs["plot"] = False
    # print kwargs
    for key, value in kwargs.items():
        if key in DEFAULT_PARA.keys():
            print("{:s} = {:s}".format(key, str(value)))
        else:
            print("Unknown key: {:s}".format(key))
    #
    paras = load_paras(uuid)
    # paras[0] = paras[0] * 1.05
    print("Loaded paras: ", paras)
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    #
    with load_template(
        dataName,
        SOURCE_typ,
        purpose="{:s}_{:s}_simluated".format(str(tether_typ), dimension),
    ) as fdtd:
        try:
            setup_source(fdtd, lambda_0, FWHM, SOURCE_typ, dimension=dimension)
            setup_monitor(fdtd, monitor=monitor, movie=False)
            #
            if tether_typ is not None:
                gds_fileName = generate_gds_fileName(uuid, tether_typ=tether_typ)
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
            #
            l, T, maxT, lambda_maxT, FWHM_fit, FOM = fdtd_iter(fdtd, paras, **kwargs)
            # print(l)
            # print(T)
            try:
                a = np.transpose(np.vstack((l * 1e6, T)))  # wavelength in um
                np.savetxt(
                    "{:s}_{:s}_{:s}_simulated_transmission.txt".format(
                        dataName, str(tether_typ), dimension
                    ),
                    a,
                )
            except Exception as e:
                print("Error: ", str(e))
            #
            try:
                plt.figure(figsize=(9, 6))
                plt.plot(l * 1e9, T)
                plt.xlabel("Wavelength (nm)")
                plt.ylabel("Transmission")
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
                print("Error: ", str(e))
            #
            print(maxT, lambda_maxT, FWHM_fit, FOM)
        except Exception as e:
            print("Error: ", e)
        # whatever happens, keeps the lumerical window open
        if pause:
            while 1:
                pass


if __name__ == "__main__":
    uuid = "4e25"

    #
    reload_work(
        uuid,
        dimension="3D",
        tether_typ="empty",
        pause=False,
    )
    #
    reload_work(
        uuid,
        dimension="3D",
        tether_typ="section_tether",
        pause=False,
    )
    #
    reload_work(
        uuid,
        dimension="3D",
        tether_typ="section_rect_tether",
        pause=False,
    )
