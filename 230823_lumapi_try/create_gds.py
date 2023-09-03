from json_uuid import load_json, save_json, uuid_to_logname, uuid_to_wd
from const_var import DEFAULT_PARA
import sys
import os
from lumapi_optimize import load_paras


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
    from lib.grating.grating_tether import (
        grating_tether,
        recipes,
    )

    kwargs = load_json(uuid)
    paras = load_paras(uuid)
    #
    N = kwargs.get("N", DEFAULT_PARA["N"])
    NL = kwargs.get("NL", DEFAULT_PARA["NL"])
    NH = kwargs.get("NH", DEFAULT_PARA["NH"])
    start_radius = kwargs.get("start_radius", DEFAULT_PARA["start_radius"])
    #
    Lambda = paras[0]
    ffL = paras[1]
    ffH = paras[2]
    ff = paras[3]
    #
    para = recipes(tether_typ)
    c = grating_tether(
        N,
        Lambda * 1e6,
        ff,
        ffL,
        ffH,
        NL,
        NH,
        mask_func=para[0],
        tether_func=para[1],
        grating_angle=para[2],
        start_radius=start_radius * 1e6,
        input_length=10,
        suspend=False,
    )
    gds_fileName = generate_gds_fileName(uuid, tether_typ=tether_typ)
    c.write_gds(gds_fileName)
    # c.show()
    #
    return gds_fileName


if __name__ == "__main__":
    uuid = "4e25"
    tether_typ_list = ["empty", "section_tether", "section_rect_tether"]
    for tether_typ in tether_typ_list:
        gds_fileName = create_gds(uuid, tether_typ=tether_typ)
        print(gds_fileName)
