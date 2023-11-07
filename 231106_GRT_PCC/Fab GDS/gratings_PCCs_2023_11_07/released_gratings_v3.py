import os, sys, gdspy, numpy as np

# sys.path.append('/Users/lkomza/Desktop/test')
sys.path.append("../..")
dir = os.path.dirname(__file__)
import PhotonForge as pf

forge = pf.Forge()
forge.load_yml()
forge.add_geometry(gdspy.Rectangle([-1e4 / 2, -1e4 / 2], [1e4 / 2, 1e4 / 2], layer=0))


def shrink_rectangle(p1, p2, dxl=0, dxr=0, dyt=0, dyb=0):
    x_max = max(p1[0], p2[0])
    x_min = min(p1[0], p2[0])
    y_max = max(p1[1], p2[1])
    y_min = min(p1[1], p2[1])
    x_max -= dxr
    x_min += dxl
    y_max -= dyt
    y_min += dyb
    return [x_min, y_min], [x_max, y_max]


def pts_sweep_x(x1, x2, y0, step=127):
    pts = []
    for x in np.arange(x1, x2 + 1, step):
        pts.append([x, y0])
    return pts


def add_grating(pts):
    for pt in pts:
        x_, y_ = pt
        forge.xy = [x_, y_]
        grating = pf.Component()
        grating.load_gds("grating_gds", dir + "/4e25.gds")
        grating.rotate(-np.pi / 2)
        forge.add_component(grating)
        r = grating.get_bbox()
        r = shrink_rectangle(*r, dxl=2, dxr=2, dyt=0, dyb=3)
        forge.add_geometry(gdspy.Rectangle(*r, layer=2))


x0, y0 = [0, -1e3]
start = x0 - 7.5 * 127
end = x0 + 7.5 * 127 - (8.5 * 127)
pts = pts_sweep_x(start, end, y0)

add_grating(pts)


# 9
def add_reflect_pcc_bus(pts):
    x_, y_ = pts
    forge.xy = [x_, y_]
    #
    # forge.yml["photonics.resonators.pcc_cavity"]["a_m"] = 0.342
    # forge.yml["photonics.resonators.pcc_cavity"]["a_d"] = 0.342 - 0.05
    # forge.yml["photonics.resonators.pcc_mirrors"]["a_m"] = 0.342
    # forge.yml["photonics.resonators.pcc_mirrors"]["a_d"] = 0.342 - 0.05
    #
    pos_mask_path = []
    pos_mask_path.append(forge.xy)
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 10]])
    forge.add(pf.tether, angle=np.pi / 2)
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 15], [15, 15]])
    pos_mask_path.append([x_, forge.xy[1]])
    forge.add(pf.pcc_bus, num_units=2)
    forge.add(pf.waveguide, coordinates=[[0, 0], [1, 0]])
    # forge.add(
    #     pf.taper,
    #     coordinates=[[0, 0], [1, 0]],
    #     initial_width=0.35,
    #     final_width=0.40,
    #     layer=1,
    # )
    forge.add(pf.waveguide, coordinates=[[0, 0], [1, 0]], width=0.4)
    forge.add(pf.pcc_mirrors, N_mirrors=10)
    forge.add(pf.pcc_cavity)
    forge.add(pf.pcc_mirrors)
    forge.add(pf.waveguide, coordinates=[[0, 0], [2, 0]], width=0.4)
    pos_mask_path.append(forge.xy)
    forge.add(pf.waveguide, coordinates=[[0, 0], [2, 0]], width=0.4)
    forge.add(pf.waveguide, coordinates=pos_mask_path, width=7, layer=2, relative=False)


# MLA Marker
size = 25 - 2
forge.add(
    pf.mla_marker,
    coordinates=[(-2e3, -2e3), (-2e3, 2e3), (2e3, -2e3)],
    width=1.25,
    length=50,
    layer=6,
    relative=False,
)
for c in [(-2e3, -2e3), (-2e3, 2e3), (2e3, -2e3)]:
    forge.add_geometry(
        gdspy.Rectangle((c[0] + size, c[1] + size), (c[0] - size, c[1] - size), layer=2)
    )


forge.write_gds()
# forge.bool([1,0], [4,0], 'and', 1)
forge.save()
