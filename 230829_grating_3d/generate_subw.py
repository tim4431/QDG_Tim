import sys
import matplotlib.pyplot as plt

sys.path.append("..")
from lib.grating.subwavelength import subw_grating
from lib.grating.grating_concentric import (
    grating_concentric_arc,
    grating_concentric_ellipse,
)
import gdsfactory as gf
from gdsfactory.component import Component
from typing import List


if __name__ == "__main__":
    # parameter
    Lambda = 1253 * 1e-3
    ff = 0.544
    ffL = 0.145
    ffH = 0.867
    NL = 2
    NH = 3
    N = 10
    #
    grating = subw_grating(N, Lambda, ff, ffL, ffH, NL, NH)
    c = grating_concentric_arc(
        taper_angle=24, grating_angle=24, start_radius=10, grating=grating
    )
    c.show()
    c.write_gds("raw_grating.gds")
    #

    # L = grating[-1]
    # AFT_LENGTH = 0.1
    # grating.append(L + AFT_LENGTH)
    # grating.append(L + 5)
