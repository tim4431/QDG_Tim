import sys
import matplotlib.pyplot as plt
import numpy as np

from .subwavelength import subw_grating
from .grating_concentric import (
    grating_concentric_arc,
    grating_concentric_ellipse,
)
import gdsfactory as gf
from typing import List, Callable, Union


@gf.cell
def grating_add_tether(grating, tether_mask, input_length: float = 10):
    # construct
    c = gf.Component()

    #
    grating_ref = grating.ref()
    grating_ref.xmin = -input_length
    grating_ref.y = 0
    #
    mask_ref = tether_mask.ref()
    mask_ref.xmin = -input_length
    mask_ref.y = 0
    #
    # keep crosssection part of tether_mask and grating
    grating_masked = gf.geometry.boolean(
        mask_ref, grating_ref, operation="and", layer="WG"
    )
    grating_masked_ref = c << grating_masked

    # outer rectangle is inner rectangle + 3um margin
    outer_rect_width = mask_ref.xmax - mask_ref.xmin
    outer_rect_height = mask_ref.ymax - mask_ref.ymin
    MARGIN_WIDTH = 3
    outer_rectangle = gf.components.rectangle(
        size=(outer_rect_width + MARGIN_WIDTH, outer_rect_height + MARGIN_WIDTH * 2),
        layer="WG",
    )
    outer_rectangle_ref = outer_rectangle.ref()
    outer_rectangle_ref.xmin = -input_length
    outer_rectangle_ref.y = 0

    # keep difference part of mask_copy and outer_rectangle
    tether = gf.geometry.boolean(
        outer_rectangle_ref, mask_ref, operation="not", layer="WG"
    )
    tether_ref = c << tether
    #
    return c


@gf.cell
def rect_tether(
    grating,
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
):
    c = gf.Component()
    #
    SHRINK_WIDTH = 0.1
    DEG2RAD = np.pi / 180
    rect_width = 2 * (start_radius * np.sin(grating_angle * DEG2RAD) - SHRINK_WIDTH)
    L = grating[-1] - patch_length
    rect_length = L + start_radius + input_length
    rect_ref = c << gf.components.rectangle(size=(rect_length, rect_width), layer="WG")
    #
    return c


@gf.cell
def section_tether(
    grating,
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
):
    c = gf.Component()
    # construct
    L = grating[-1] - patch_length
    section_length = L + start_radius + patch_length
    DEG2RAD = np.pi / 180
    grating_width = 2 * section_length * np.sin(grating_angle * DEG2RAD)
    grating_length = section_length * np.cos(grating_angle * DEG2RAD)
    pts = [
        (0, 0),
        (grating_length, -grating_width / 2),
        (grating_length, grating_width / 2),
        (0, 0),
    ]
    poly_ref = c.add_polygon(pts, layer="WG")
    poly_ref.xmin = 0
    poly_ref.y = 0
    #
    # add rectangle
    SHRINK_WIDTH = 0.1
    rect_width = 2 * (start_radius * np.sin(grating_angle * DEG2RAD) - SHRINK_WIDTH)
    print(rect_width)
    rect_ref = c << gf.components.rectangle(
        size=((start_radius + input_length), rect_width), layer="WG"
    )
    rect_ref.xmin = -input_length
    rect_ref.y = 0
    #
    return c


@gf.cell
def skeleton(
    grating_length: float, grating_angle: float, N_skeleton: int, skeleton_span: float
):
    # construct
    c = gf.Component()

    # skeleton
    center_angles = np.linspace(
        -grating_angle,
        grating_angle,
        N_skeleton,
    )
    single_skeleton = gf.components.ring(
        radius=grating_length / 2,
        width=grating_length,
        angle_resolution=0.1,
        angle=skeleton_span,
    )
    for center_angle in center_angles:
        skeleton_ref = c << single_skeleton
        skeleton_ref.rotate(center_angle - skeleton_span / 2, center=(0, 0))
    #
    return c


def grating_tether(
    N: int,
    Lambda: float,
    ff: float,
    ffL: float,
    ffH: float,
    NL: int,
    NH: int,
    #
    tether_func: Union[Callable, None],
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
) -> gf.Component:
    # const
    PATCH_LENGTH = 0 if tether_func is None else 5
    #
    c = gf.Component("grating_gds")  # here we generate gds with designated cell name
    # constructW
    # generate grating
    grating = subw_grating(N, Lambda, ff, ffL, ffH, NL, NH)
    if PATCH_LENGTH > 0:
        grating.append(grating[-1])
        grating.append(grating[-1] + PATCH_LENGTH)
    #
    g = grating_concentric_arc(
        taper_angle=grating_angle,
        grating_angle=grating_angle,
        start_radius=start_radius,
        grating=grating,
        input_length=input_length,
    )
    #
    if tether_func is not None:
        mask = tether_func(
            grating,
            grating_angle=grating_angle,
            start_radius=start_radius,
            patch_length=PATCH_LENGTH,
        )
        gt = grating_add_tether(g, mask, input_length=input_length)
        gt_ref = c << gt
    else:
        g_rec = c << g
    #
    # add suspension
    if tether_func is not None:
        suspend = c << gf.components.rectangle(
            size=(start_radius + (grating[-1] - PATCH_LENGTH), 0.35), layer="WG"
        )
        suspend.xmin = 2
        suspend.y = 0
    #
    return c


if __name__ == "__main__":
    # parameter
    Lambda = 1266 * 1e-3
    ff = 0.489
    ffL = 0.216
    ffH = 0.807
    NL = 2
    NH = 2
    N = 10
    #
    rect_para = (rect_tether, 40)
    section_para = (section_tether, 24)
    none_para = (None, 24)
    #
    para = rect_para
    c = grating_tether(
        N,
        Lambda,
        ff,
        ffL,
        ffH,
        NL,
        NH,
        tether_func=para[0],
        grating_angle=para[1],
        start_radius=10,
        input_length=10,
    )
    c.show()
