import sys

sys.path.append("../..")
from lib.grating.load_grating_data import load_grating_data
from lib.grating.grating_concentric import grating_concentric_arc

grating = load_grating_data("./output", grating_len=12000)
c = grating_concentric_arc(
    taper_angle=24, grating_angle=24, start_radius=12, grating=grating
)
c.show()
c.write_gds("0_grating_straight_w1326_0_arc.gds")
