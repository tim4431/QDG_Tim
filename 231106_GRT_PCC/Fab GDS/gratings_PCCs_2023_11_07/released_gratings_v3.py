import os, sys, gdspy, numpy as np
import matplotlib.pyplot as plt

# sys.path.append('/Users/lkomza/Desktop/test')
sys.path.append("../..")
dir = os.path.dirname(__file__)
import PhotonForge as pf

forge = pf.Forge()
forge.load_yml()


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


def pts_sweep_x(N, x0, y0, step=127):
    x1 = x0 - ((N - 1) / 2) * step
    x2 = x0 + ((N - 1) / 2) * step
    pts = []
    for x in np.arange(x1, x2 + 1, step):
        pts.append([x, y0])
    return pts


def pts_group3_sweep_x(N, x0, y0, step=127):
    # group by 3, spacing by step
    # group to group, spacing by 6*step
    x1 = x0 - ((N - 1) / 2) * (6 * step)
    x2 = x0 + ((N - 1) / 2) * (6 * step)
    pts = []
    for x in np.arange(x1, x2 + 1, 6 * step):
        for i in range(3):
            pts.append([x + i * step, y0])
    return pts


def add_grating(pts, layer):
    for pt in pts:
        x_, y_ = pt
        forge.xy = [x_, y_]
        grating = pf.Component()
        grating.load_gds("grating_gds", dir + "/4e25.gds")
        grating.copy_layers(1, layer)
        grating.rotate(-np.pi / 2)
        forge.add_component(grating)
        r = grating.get_bbox()
        r = shrink_rectangle(*r, dxl=2, dxr=2, dyt=0, dyb=3)
        forge.add_geometry(gdspy.Rectangle(*r, layer=2))


def add_reflect_pcc_bus(pt, ff_bragg, dff, layer):
    """
    ff_bragg: fill factor of the bragg grating
    dff: fill factor step size (ff-4*dff,...,ff+4*dff)
    to sweep ff_bragg, spacing at 6*dff, so that could have some overlap
    """
    x_, y_ = pt
    forge.xy = [x_, y_]
    #
    pos_mask_path = []
    pos_mask_path.append(forge.xy)
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 2]], layer=layer)
    forge.add(
        pf.pcc_bus_y_sweepfilling, num_units=2, ff_bragg=ff_bragg, dff=dff, layer=layer
    )
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 1]], layer=layer)
    # end cavity
    forge.add(
        pf.taper,
        coordinates=[[0, 0], [0, 1]],
        initial_width=0.35,
        final_width=0.40,
        layer=layer,
    )  # taper connecting bus to cavity
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 1]], width=0.4, layer=layer)
    forge.add(pf.pcc_mirrors, N_mirrors=10, angle=np.pi / 2, layer=layer)
    forge.add(pf.pcc_cavity, angle=np.pi / 2, layer=layer)
    forge.add(pf.pcc_mirrors, angle=np.pi / 2, layer=layer)
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 2]], width=0.4, layer=layer)
    pos_mask_path.append(forge.xy)
    forge.add(pf.waveguide, coordinates=[[0, 0], [0, 2]], width=0.4, layer=layer)
    # positive mask
    forge.add(pf.waveguide, coordinates=pos_mask_path, width=7, layer=2, relative=False)


def create_batch(x0, y0, layer, N=3, dff=0.01, ff0=0.45):
    X_step = 40

    # pts = pts_sweep_x(N, x0, y0, step=X_step)
    pts = pts_group3_sweep_x(N / 3, x0, y0, step=X_step)

    add_grating(pts, layer=layer)

    dff_bragg = 9 * dff
    for i in range(N):
        ff_bragg = ff0 + (i - (N - 1) / 2) * dff_bragg
        add_reflect_pcc_bus(pts[i], ff_bragg=ff_bragg, dff=dff, layer=layer)


def plot_ffs(N, ff0, dff):
    plt.figure()
    ff_List = []
    dff_bragg = 9 * dff
    for i in range(N):
        for j in range(-4, 5):
            ff_List.append(ff0 + (i - (N - 1) / 2) * dff_bragg + j * dff)
    plt.plot(ff_List, ".")
    plt.show()


if __name__ == "__main__":
    forge.add_geometry(
        gdspy.Rectangle([-1e4 / 2, -1e4 / 2], [1e4 / 2, 1e4 / 2], layer=0)
    )
    # i j scan
    N_SCAN_X = 8
    N_SCAN_Y = 8
    DIS_GROUP = 250
    for i in range(1, N_SCAN_X + 1):
        for j in range(1, N_SCAN_Y + 1):
            x0 = (i - (N_SCAN_X + 1) / 2) * DIS_GROUP
            y0 = (j - (N_SCAN_Y + 1) / 2) * DIS_GROUP
            create_batch(x0, y0, N=3, layer=10 * i + j, dff=0.01, ff0=0.45)
    # plot_ffs(3, 0.45, 0.01)
    # fine scan to make sure we see atleast a PCC
    create_batch(0, -1.5e3, N=9, dff=0.005, ff0=0.45, layer=1)
    plot_ffs(9, 0.45, 0.005)

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
            gdspy.Rectangle(
                (c[0] + size, c[1] + size), (c[0] - size, c[1] - size), layer=2
            )
        )

    forge.write_gds()
    # forge.bool([1,0], [4,0], 'and', 1)
    forge.save()
