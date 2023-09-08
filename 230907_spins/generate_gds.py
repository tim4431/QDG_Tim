import sys
import os

sys.path.append("..")
from lib.grating.load_grating_data import load_grating_data
from lib.grating.grating_concentric import grating_concentric_arc


def generate_gds(dataDirname):
    grating = load_grating_data(
        os.path.join(".", dataDirname, "output"), grating_len=12000
    )
    c = grating_concentric_arc(
        taper_angle=24, grating_angle=24, start_radius=12.0, grating=grating
    )
    c.show()
    c.write_gds(os.path.join(".", dataDirname, "output", "_arc.gds"))


if __name__ == "__main__":
    dataDirname = "0_grating_straight_w1326_0"
    generate_gds(dataDirname)
