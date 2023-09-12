import sys

sys.path.append("../..")

from lib.gaussian.gaussian_fit_1d import arb_fit_1d
from lib.process_data.load_lumerical_data import load_lumerical_1d

l, T = load_lumerical_1d(
    "./3_grating_straight_w1326_released_1_expand_arc_transmission.txt"
)
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
arb_fit_1d(ax, l * 1e6, T, "spins_3_3D")
plt.savefig("./spins_3_transmission.png", dpi=200, bbox_inches="tight")
plt.show()
