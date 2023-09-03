import sys
import matplotlib.pyplot as plt
import numpy as np

# sys.path.append("..")
from .subwavelength import subw_grating
from .grating_concentric import (
    grating_concentric_arc,
    grating_concentric_ellipse,
)
import gdsfactory as gf
from typing import List, Callable, Union


@gf.cell
def grating_mask_tether(grating, grating_mask, tether=None, input_length: float = 10):
    # construct
    c = gf.Component()

    #
    grating_ref = grating.ref()
    grating_ref.xmin = -input_length
    grating_ref.y = 0
    #
    mask_ref = grating_mask.ref()
    mask_ref.xmin = -input_length
    mask_ref.y = 0
    #
    # keep crosssection part of tether_mask and grating
    grating_masked = gf.geometry.boolean(
        mask_ref, grating_ref, operation="and", layer="WG"
    )
    grating_masked_ref = c << grating_masked

    # outer rectangle is inner rectangle + 3um margin
    outer_rect_length = mask_ref.xmax - mask_ref.xmin
    outer_rect_width = mask_ref.ymax - mask_ref.ymin
    MARGIN_WIDTH = 3
    outer_rectangle = gf.components.rectangle(
        size=(outer_rect_length + MARGIN_WIDTH, outer_rect_width + MARGIN_WIDTH * 2),
        layer="WG",
    )
    outer_rectangle_ref = outer_rectangle.ref()
    outer_rectangle_ref.xmin = -input_length
    outer_rectangle_ref.y = 0

    # keep difference part of mask_copy and outer_rectangle
    if tether is None:
        support = gf.geometry.boolean(
            outer_rectangle_ref, mask_ref, operation="not", layer="WG"
        )
        support_ref = c << support
    else:
        tether_ref = c << tether
        tether_ref.xmin = 0
        tether_ref.y = 0
        #
        mask_bounding_box_length = mask_ref.xmax - mask_ref.xmin
        mask_bounding_box_width = mask_ref.ymax - mask_ref.ymin
        mask_bounding_box = gf.components.rectangle(
            size=(mask_bounding_box_length, mask_bounding_box_width), layer="WG"
        )
        mask_bounding_box_ref = mask_bounding_box.ref()
        mask_bounding_box_ref.xmin = -input_length
        mask_bounding_box_ref.y = 0
        #
        outer_rectangle = gf.components.rectangle(
            size=(
                mask_bounding_box_length + MARGIN_WIDTH,
                mask_bounding_box_width + MARGIN_WIDTH * 2,
            ),
            layer="WG",
        )
        outer_rectangle_ref = outer_rectangle.ref()
        outer_rectangle_ref.xmin = -input_length
        outer_rectangle_ref.y = 0
        #
        support = gf.geometry.boolean(
            outer_rectangle_ref, mask_bounding_box_ref, operation="not", layer="WG"
        )
        support_ref = c << support

    #
    return c


@gf.cell
def rect_mask(
    grating_length: float,
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
    L = grating_length - patch_length
    rect_length = L + start_radius + input_length
    rect_ref = c << gf.components.rectangle(size=(rect_length, rect_width), layer="WG")
    #
    return c


@gf.cell
def section_mask(
    grating_length: float,
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
):
    c = gf.Component()
    # construct
    L = grating_length - patch_length
    section_length = L + start_radius + patch_length
    DEG2RAD = np.pi / 180
    grating_width = 2 * section_length * np.sin(grating_angle * DEG2RAD)
    grating_length = section_length * np.cos(grating_angle * DEG2RAD)
    pts = [
        (0, 0),
        (grating_length, -grating_width / 2),
        (section_length, -grating_width / 2),
        (section_length, grating_width / 2),
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
    # print(rect_width)
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
        -grating_angle + skeleton_span / 2,
        grating_angle - skeleton_span / 2,
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
        skeleton_ref.xmin = 0
        skeleton_ref.ymin = 0
        skeleton_ref.rotate(center_angle - skeleton_span / 2, center=(0, 0))
    #
    return c


@gf.cell
def _tether(straight_length: float, angle: float = 0):
    # width: 200nm - 500nm, taper_length=1.5um
    # then add length straight, keep 500nm
    c = gf.Component()
    #
    taper_length = 1.2
    taper_width_1 = 0.2
    taper_width_2 = 0.5
    cross_section_1 = gf.cross_section.cross_section(width=taper_width_1, layer="WG")
    cross_section_2 = gf.cross_section.cross_section(width=taper_width_2, layer="WG")
    #
    taper = gf.components.taper_cross_section_linear(
        length=taper_length,
        cross_section1=cross_section_1,
        cross_section2=cross_section_2,
    )
    taper_ref = c << taper
    taper_ref.rotate(angle + 90)
    #
    straight = gf.components.straight(
        length=straight_length, cross_section=cross_section_2, layer="WG"
    )
    # add bend circular
    if angle != 0:
        bend = gf.components.bend_circular(
            radius=3, cross_section=cross_section_2, angle=angle, layer="WG"
        )
        bend_ref = c << bend
        bend_ref.connect("o2", taper_ref.ports["o2"])
        #
        # add straight
        straight_ref = c << straight
        straight_ref.connect("o1", bend_ref.ports["o1"])
    else:
        straight_ref = c << straight
        straight_ref.connect("o1", taper_ref.ports["o2"])
    #
    # add port
    c.add_port("o1", port=taper.ports["o1"])
    #
    return c


@gf.cell
def section_tether(
    grating_length: float,
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
):
    #
    DEG2RAD = np.pi / 180
    #
    c = gf.Component()
    #
    GL = grating_length + start_radius
    sk = skeleton(GL, grating_angle, N_skeleton=2, skeleton_span=1.5)
    sk_ref = c << sk
    sk_ref.xmin = 0
    sk_ref.y = 0
    #
    # add tether
    cross_section = gf.cross_section.cross_section(width=0.2, layer="WG")
    for i, x in enumerate(np.linspace(4, GL - 3, 4)):
        L_tether = (GL - x) * np.sin(grating_angle * DEG2RAD) - 1.1
        tether = _tether(straight_length=L_tether, angle=0)
        tether_ref = c << tether
        # create port
        c.add_port(
            "ou{:d}".format(i),
            center=(
                x * np.cos(grating_angle * DEG2RAD),
                x * np.sin(grating_angle * DEG2RAD) - 0.1,
            ),
            cross_section=cross_section,
            orientation=0,
        )
        tether_ref.connect("o1", c.ports["ou{:d}".format(i)])
        #
        tether_ref_bottom = c << tether
        # create port
        c.add_port(
            "ob{:d}".format(i),
            center=(
                x * np.cos(grating_angle * DEG2RAD),
                -(x * np.sin(grating_angle * DEG2RAD) - 0.1),
            ),
            cross_section=cross_section,
            orientation=180,
        )
        tether_ref_bottom.connect("o1", c.ports["ob{:d}".format(i)])
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
    mask_func: Union[Callable, None],
    tether_func: Union[Callable, None],
    grating_angle: float,
    start_radius: float = 10,
    suspend: bool = False,
    input_length: float = 10,
) -> gf.Component:
    # const
    PATCH_LENGTH = 0 if mask_func is None else 5
    #
    c = gf.Component("grating_gds")  # here we generate gds with designated cell name
    # constructW
    # generate grating
    grating = subw_grating(N, Lambda, ff, ffL, ffH, NL, NH)
    grating_length = grating[-1]
    if PATCH_LENGTH > 0:
        grating.append(grating_length)
        grating.append(grating_length + PATCH_LENGTH)
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
        tether = tether_func(
            grating_length=grating_length,
            grating_angle=grating_angle,
            start_radius=start_radius,
            patch_length=PATCH_LENGTH,
        )
    else:
        tether = None
    #
    if mask_func is not None:
        mask = mask_func(
            grating_length=grating_length,
            grating_angle=grating_angle,
            start_radius=start_radius,
            patch_length=PATCH_LENGTH,
        )
        gt = grating_mask_tether(g, mask, tether=tether, input_length=input_length)
        gt_ref = c << gt
    else:
        g_rec = c << g
    #
    # add suspension
    if (mask_func is not None) and suspend:
        suspend_ref = c << gf.components.rectangle(
            size=(start_radius + (grating[-1] - PATCH_LENGTH), 0.35), layer="WG"
        )
        suspend_ref.xmin = 2
        suspend_ref.y = 0
    #
    return c


def recipes(tether_typ: str) -> tuple:
    if tether_typ == "rect":
        return (rect_mask, None, 40)
    elif tether_typ == "section":
        return (section_mask, None, 24)
    elif tether_typ == "empty":
        return (None, None, 24)
    elif tether_typ == "section_tether":
        return (section_mask, section_tether, 24)
    else:
        return (None, None, None)


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
    para = recipes("section_tether")
    c = grating_tether(
        N,
        Lambda,
        ff,
        ffL,
        ffH,
        NL,
        NH,
        mask_func=para[0],
        tether_func=para[1],
        grating_angle=para[2],
        start_radius=10,
        input_length=10,
        suspend=False,
    )
    # c = section_tether(30, 24)
    # d = skeleton(30, 24, 3, 1.5)
    # d.show()
    c.show()
