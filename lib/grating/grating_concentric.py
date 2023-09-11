import matplotlib.pyplot as plt
import numpy as np
import gdsfactory as gf
from gdsfactory.component import Component
from typing import List


@gf.cell
def grating_concentric_arc(
    taper_angle: float,
    grating_angle: float,
    start_radius: float,
    grating: List,
    input_length: float = 10,
):
    # divide grating in groups of 2
    gratings = np.array(grating).reshape(-1, 2)
    # construct
    c = Component()
    WG_CROSS = gf.cross_section.cross_section(width=0.35, layer="WG")

    # add input taper
    from gdsfactory.components.grating_coupler_elliptical import grating_taper_points

    pts = grating_taper_points(
        a=start_radius,
        b=start_radius,
        x0=0,
        taper_length=0,
        taper_angle=taper_angle * 2,
        wg_width=0.35,
    )
    c.add_polygon(pts, "WG")
    #
    # add input wg
    if not (input_length == 0):
        wg = gf.components.straight(length=input_length, cross_section=WG_CROSS)
        wg_ref = c << wg
        wg_ref.xmax = 0
        c.add_port("o1", port=wg_ref.ports["o1"])
    else:
        c.add_port("o1", center=(0, 0), width=0.35, orientation=180, layer="WG")

    # add grating rings
    for i, (r1, r2) in enumerate(gratings):
        ring = gf.components.ring(
            angle=2 * grating_angle,
            radius=start_radius + (r1 + r2) / 2,
            width=(r2 - r1),
        )
        ring_ref = c << ring
        ring_ref.rotate(-grating_angle)
        ring_ref.xmax = start_radius + r2
    #
    return c


@gf.cell
def grating_concentric_ellipse(
    taper_angle: float,
    grating_angle: float,
    start_radius: float,
    grating: List,
    input_length=10,
):
    widths = [grating[i * 2 + 1] - grating[i * 2] for i in range(len(grating) // 2)]
    gaps = [grating[i * 2] - grating[i * 2 - 1] for i in range(1, len(grating) // 2)]
    gaps.insert(0, 0)
    # construct
    c = Component()
    WG_CROSS = gf.cross_section.cross_section(width=0.35, layer="WG")

    # add input wg
    wg = gf.components.straight(length=input_length, cross_section=WG_CROSS)
    wg_ref = c << wg
    wg_ref.xmax = 0
    #

    gc = gf.components.grating_coupler_elliptical_arbitrary(
        gaps=gaps,  # type: ignore
        widths=widths,  # type: ignore
        taper_length=start_radius,
        taper_angle=taper_angle * 2,
        wavelength=1.326,
        fiber_angle=10,
        nclad=1.468,
        layer_slab=None,
        polarization="te",
        spiked=True,
        bias_gap=0,
        cross_section=WG_CROSS,
    )
    gc_ref = c << gc
    gc_ref.xmin = 0
    return c


if __name__ == "__main__":
    grating = list(np.linspace(0, 10, 20))
    grating = list(np.linspace(0, 10, 20))
    c = grating_concentric_arc(
        taper_angle=24,
        grating_angle=24,
        start_radius=10,
        grating=grating,
        input_length=0,
    )
    # c = grating_concentric_ellipse(
    #     taper_angle=24, grating_angle=24, start_radius=10, grating=grating
    # )
    c.show(show_ports=True)
