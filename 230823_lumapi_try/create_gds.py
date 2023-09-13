from json_uuid import load_json, uuid_to_wd, load_paras
from const_var import DEFAULT_PARA
import sys

sys.path.append("..")
import os
from lib.grating.grating_tether import (
    grating_tether,
    recipes,
)
from lib.grating.subwavelength import subw_grating, apodized_grating


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
    kwargs = load_json(uuid)
    paras = load_paras(uuid)
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    #
    N = kwargs.get("N", DEFAULT_PARA["N"])
    NL = kwargs.get("NL", DEFAULT_PARA["NL"])
    NH = kwargs.get("NH", DEFAULT_PARA["NH"])
    start_radius = kwargs.get("start_radius", DEFAULT_PARA["start_radius"])
    #
    recipe = recipes(tether_typ)
    #
    if grating_typ == "subw_grating":
        Lambda = paras[0]
        ffL = paras[1]
        ffH = paras[2]
        ff = paras[3]
        #
        grating = subw_grating(N, Lambda, ff, ffL, ffH, NL, NH)
        grating = [g * 1e6 for g in grating]
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
        grating = apodized_grating(
            N, NL, NH, Lambda_i, Lambda_f, ffL_i, ffL_f, ffH_i, ffH_f, ff_i, ff_f
        )
        grating = [g * 1e6 for g in grating]
    else:
        raise NotImplementedError
    #
    c = grating_tether(grating, start_radius=start_radius * 1e6, **recipe)
    gds_fileName = generate_gds_fileName(uuid, tether_typ=tether_typ)
    c.write_gds(gds_fileName)
    c.show()
    #
    return gds_fileName


if __name__ == "__main__":
    uuid = "38b2"
    # tether_typ_list = ["empty", "section_tether", "section_rect_tether"]
    tether_typ_avail_list = [
        "empty",
        "section_rect_tether",
        "section_rect_tether_multiskeleton",
        "section_rect_tether_suspend",
        "section_rect_tether_hole",
        "section_rect_tether_hole_suspend",
        "section_rect_tether_hole_unbox",
        "section_rect_tether_suspend_unbox",
        "section_rect_tether_hole_suspend_unbox",
    ]
    idx_list = [0, 1, 2]
    for idx in idx_list:
        tether_typ = tether_typ_avail_list[idx]
        gds_fileName = create_gds(uuid, tether_typ=tether_typ)
        print(gds_fileName)
