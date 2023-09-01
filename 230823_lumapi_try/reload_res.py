from lumapi_optimize import (
    getdataName,
    setup_source,
    fdtd_iter,
    load_template,
    optimize_wrapper,
)
import numpy as np
from json_uuid import load_json, save_json, uuid_to_logname, uuid_to_wd
from const_var import DEFAULT_PARA
import sys
import os
import matplotlib.pyplot as plt

sys.path.append("..")


def load_paras(uuid):
    dataName = getdataName(uuid)
    return np.loadtxt(dataName + "_paras.txt")


def setup_monitor(fdtd, monitor=False, movie=False):
    if monitor:
        fdtd.setnamed("index_monitor", "enabled", 1)
        fdtd.setnamed("field_monitor", "enabled", 1)
    else:
        fdtd.setnamed("index_monitor", "enabled", 0)
        fdtd.setnamed("field_monitor", "enabled", 0)
    #
    if movie:
        fdtd.setnamed("movie_monitor", "enabled", 1)
    else:
        fdtd.setnamed("movie_monitor", "enabled", 0)


def reload_work(uuid, dimension="2D", tether_typ=None, pause=False):
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
            setup_monitor(fdtd, monitor=True)
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
                    dpi=300,
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


def generate_gds_fileName(uuid, tether_typ: str = "empty"):
    kwargs = load_json(uuid)
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    working_directory = uuid_to_wd(uuid)
    #
    gds_fileName = os.path.join(
        working_directory,
        "{:s}_subwavelength_concentric_w{:d}_bw{:d}_arc_tether_{:s}.gds".format(
            uuid, int(lambda_0 * 1e9), int(FWHM * 1e9), str(tether_typ)
        ),
    )
    return gds_fileName


def create_gds(uuid, tether_typ: str = "empty"):
    from lib.grating.grating_tether import grating_tether, rect_tether, section_tether

    kwargs = load_json(uuid)
    paras = load_paras(uuid)
    #
    N = kwargs.get("N", DEFAULT_PARA["N"])
    NL = kwargs.get("NL", DEFAULT_PARA["NL"])
    NH = kwargs.get("NH", DEFAULT_PARA["NH"])
    #
    Lambda = paras[0]
    ffL = paras[1]
    ffH = paras[2]
    ff = paras[3]
    #
    rect_para = (rect_tether, 40)
    section_para = (section_tether, 24)
    empty_para = (None, 24)
    #
    if tether_typ == "rect":
        para = rect_para
    elif tether_typ == "section":
        para = section_para
    elif tether_typ == "empty":
        para = empty_para
    else:
        raise Exception("Unknown tether type")
    c = grating_tether(
        N,
        Lambda * 1e6,
        ff,
        ffL,
        ffH,
        NL,
        NH,
        tether_func=para[0],
        grating_angle=para[1],
        start_radius=10,
        input_length=10,
    )
    gds_fileName = generate_gds_fileName(uuid, tether_typ=tether_typ)
    c.write_gds(gds_fileName)
    c.show()
    #
    return gds_fileName


if __name__ == "__main__":
    gds_fileName = create_gds("5e56", tether_typ="empty")
    print(gds_fileName)
    reload_work(
        "5e56",
        dimension="3D",
        tether_typ="empty",
        pause=False,
    )
    # #
    # gds_fileName = create_gds("4cb4", tether_typ="rect")
    # print(gds_fileName)
    # reload_work(
    #     "4cb4",
    #     dimension="3D",
    #     tether_typ="rect",
    #     pause=False,
    # )
    # #
    # gds_fileName = create_gds("4cb4", tether_typ="section")
    # print(gds_fileName)
    # reload_work(
    #     "4cb4",
    #     dimension="3D",
    #     tether_typ="section",
    #     pause=False,
    # )
    # #
    # reload_work(
    #     "4cb4",
    #     dimension="2D",
    #     tether_typ=None,
    #     pause=False,
    # )
