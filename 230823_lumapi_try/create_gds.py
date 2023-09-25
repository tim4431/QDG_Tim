from json_uuid import load_json, uuid_to_wd, load_paras
from const_var import DEFAULT_PARA
import sys
import gdsfactory as gf

sys.path.append("..")
import os
from lib.grating.grating_tether import (
    grating_tether,
    recipes,
)
from lib.grating.subwavelength import (
    subw_grating,
    apodized_subw_grating,
    ordinary_grating,
    apodized_grating,
    inverse_grating,
)


def generate_gds_fileName(uuid, tether_typ: str = "empty"):
    kwargs = load_json(uuid)
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    working_directory = uuid_to_wd(uuid)
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    #
    gds_fileName = os.path.join(
        working_directory,
        "{:s}_{:s}_concentric_w{:d}_bw{:d}_arc_tether_{:s}.gds".format(
            uuid, grating_typ, int(lambda_0 * 1e9), int(FWHM * 1e9), str(tether_typ)
        ),
    )
    return gds_fileName


def generate_grating(paras, **kwargs):
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    #
    N = kwargs.get("N", DEFAULT_PARA["N"])
    NL = kwargs.get("NL", DEFAULT_PARA["NL"])
    NH = kwargs.get("NH", DEFAULT_PARA["NH"])
    #
    if grating_typ == "subw_grating":
        Lambda = paras[0]
        ffL = paras[1]
        ffH = paras[2]
        ff = paras[3]
        #
        grating = subw_grating(N, Lambda, ff, ffL, ffH, NL, NH)
    elif grating_typ == "apodized_subw_grating":
        Lambda_i = paras[0]
        Lambda_f = paras[1]
        ffL_i = paras[2]
        ffL_f = paras[3]
        ffH_i = paras[4]
        ffH_f = paras[5]
        ff_i = paras[6]
        ff_f = paras[7]
        #
        grating = apodized_subw_grating(
            N, NL, NH, Lambda_i, Lambda_f, ffL_i, ffL_f, ffH_i, ffH_f, ff_i, ff_f
        )
    elif grating_typ == "grating":
        Lambda = paras[0]
        ff = paras[1]
        #
        grating = ordinary_grating(N, Lambda, ff)
    elif grating_typ == "apodized_grating":
        Lambda_i = paras[0]
        Lambda_f = paras[1]
        ff_i = paras[2]
        ff_f = paras[3]
        #
        grating = apodized_grating(N, Lambda_i, Lambda_f, ff_i, ff_f)
    elif grating_typ == "inverse_grating":  # [pitch_list, ff_list, fiberx]
        pitch_list = paras[0:N]
        ff_list = paras[N : 2 * N]
        fiberx = paras[2 * N]
        #
        grating = inverse_grating(pitch_list, ff_list, fiberx)
    else:
        raise ValueError("Unknown grating_typ: {:s}".format(grating_typ))
    #
    grating = [g * 1e6 for g in grating]  # to convert to um
    return grating


def create_gds(uuid, tether_typ: str = "empty"):
    kwargs = load_json(uuid)
    paras = load_paras(uuid)
    #
    recipe = recipes(tether_typ)
    start_radius = kwargs.get("start_radius", DEFAULT_PARA["start_radius"])
    #
    grating = generate_grating(paras, **kwargs)
    c = grating_tether(grating, start_radius=start_radius * 1e6, **recipe)
    gds_fileName = generate_gds_fileName(uuid, tether_typ=tether_typ)
    c.write_gds(gds_fileName, precision=2e-9)
    c.show()
    #
    return gds_fileName


if __name__ == "__main__":
    # tether_typ_list = ["empty", "section_tether", "section_rect_tether"]
    tether_typ_avail_list = [
        "empty",  # 0
        "section_rect_tether",  # 1
        #
        "section_rect_tether_hole",  # 2
        "section_rect_tether_suspend",  # 3
        "section_rect_tether_hole_suspend",  # 4
        #
        "section_rect_tether_multisuspend",  # 5
        "section_rect_tether_hole_multisuspend",  # 6
        #
        "section_rect_tether_unbox",  # 7
        "section_rect_tether_hole_unbox",  # 8
        "section_rect_tether_suspend_unbox",  # 9
        "section_rect_tether_hole_suspend_unbox",  # 10
        #
        "section_rect_tether_multisuspend_unbox",  # 11
        "section_rect_tether_hole_multisuspend_unbox",  # 12
    ]
    uuid = "e251"
    idx_list = [0, 11]
    for idx in idx_list:
        tether_typ = tether_typ_avail_list[idx]
        gds_fileName = create_gds(uuid, tether_typ=tether_typ)
        print(gds_fileName)
