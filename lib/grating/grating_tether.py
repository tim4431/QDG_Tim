import sys
import matplotlib.pyplot as plt
import numpy as np

# sys.path.append("..")
# from grating.subwavelength import subw_grating
# from grating.grating_concentric import (
#     grating_concentric_arc,
#     grating_concentric_ellipse,
# )

from .subwavelength import subw_grating
from .grating_concentric import (
    grating_concentric_arc,
    grating_concentric_ellipse,
)
import gdsfactory as gf
from typing import List, Callable, Union
from gdsfactory.typings import Component


@gf.cell
def grating_mask_tether(
    grating: Component,
    grating_mask: Union[Component, None],
    tether=None,
    hole=False,
    suspend=False,
    input_length: float = 10,
):
    # construct
    c = gf.Component()

    # >>> add grating <<<
    grating_ref = grating.ref()
    grating_ref.xmin = -input_length
    grating_ref.y = 0
    c.add_ports(grating_ref.ports)
    # >>> add hole <<<
    if hole:
        vhf_hole = gf.components.rectangle(size=hole, layer="WG")
        hole_ref = vhf_hole.ref()
        hole_ref.x = 9
        hole_ref.y = 0
        grating = gf.geometry.boolean(
            grating_ref, hole_ref, operation="not", layer="WG"
        )
    # >>> add suspension <<<
    SUSPEND_XMIN = 11
    if suspend:
        suspend_ref = c << gf.components.rectangle(
            size=(grating_ref.xmax - SUSPEND_XMIN - 5, 0.35), layer="WG"
        )
        suspend_ref.xmin = SUSPEND_XMIN
        suspend_ref.y = 0
    # >>> add mask <<<
    if grating_mask is not None:
        mask_ref = grating_mask.ref()
        mask_ref.xmin = -input_length
        mask_ref.y = 0
        grating_masked = gf.geometry.boolean(
            mask_ref, grating.ref(), operation="and", layer="WG"
        )
    else:
        grating_masked = grating
    grating_masked_ref = c << grating_masked

    # >>> add tether <<<
    if tether is not None:
        tether_ref = c << tether
    # >>> add support <<<
    # outer rectangle is inner rectangle + margin
    # if grating_mask == None, then do not need to add outer rectangle
    if grating_mask is not None:
        MARGIN_WIDTH = 4
        mask_bbox_length = mask_ref.xmax - mask_ref.xmin  # type: ignore
        mask_bbox_width = mask_ref.ymax - mask_ref.ymin  # type: ignore
        outer_rectangle = gf.components.rectangle(
            size=(
                mask_bbox_length + MARGIN_WIDTH,
                mask_bbox_width + MARGIN_WIDTH * 2,
            ),
            layer="WG",
        )
        outer_rectangle_ref = outer_rectangle.ref()
        outer_rectangle_ref.xmin = -input_length
        outer_rectangle_ref.y = 0
        # if tether==None, support is just the difference between outer rectangle and mask
        if tether is None:
            support = gf.geometry.boolean(
                outer_rectangle_ref, mask_ref, operation="not", layer="WG"  # type: ignore
            )
        else:  # support is the difference between outer rectangle and bbox of mask
            mask_bbox = gf.components.rectangle(
                size=(mask_bbox_length, mask_bbox_width), layer="WG"
            )
            mask_bbox_ref = mask_bbox.ref()
            mask_bbox_ref.xmin = -input_length
            mask_bbox_ref.y = 0
            support = gf.geometry.boolean(
                outer_rectangle_ref, mask_bbox_ref, operation="not", layer="WG"
            )
        #
        support_ref = c << support
    #
    return c


@gf.cell
def rect_mask(
    grating: List[float],
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
):
    c = gf.Component()
    #
    grating_length = grating[-1] - patch_length
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
    grating: List[float],
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
    width_factor: float = 1,
):
    c = gf.Component()
    # construct
    grating_length = grating[-1] - patch_length
    L = grating_length - patch_length
    section_length = L + start_radius + patch_length
    DEG2RAD = np.pi / 180
    grating_width = 2 * section_length * np.sin(grating_angle * DEG2RAD)
    grating_length = section_length * np.cos(grating_angle * DEG2RAD)
    pts = [
        (0, 0),
        (grating_length * width_factor, -grating_width * width_factor / 2),
        (section_length, -grating_width * width_factor / 2),
        (section_length, grating_width * width_factor / 2),
        (grating_length * width_factor, grating_width * width_factor / 2),
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


section_rect_mask = gf.partial(section_mask, width_factor=0.8)


def add_skeleton(
    c: Component,
    grating_length_inner: float,
    grating_length_outer: float,
    grating_angle: float,
    N_skeleton: int,
    skeleton_span: float,
    **kwargs,
):
    # skeleton
    if N_skeleton == 1:
        center_angles = [0]
    else:
        center_angles = np.linspace(
            -grating_angle + skeleton_span / 2,
            grating_angle - skeleton_span / 2,
            N_skeleton,
        )
    single_skeleton = gf.components.ring(
        radius=(grating_length_inner + grating_length_outer) / 2,
        width=(grating_length_outer - grating_length_inner),
        angle_resolution=0.1,
        angle=skeleton_span,
        **kwargs,
    )
    for center_angle in center_angles:
        skeleton_ref = c << single_skeleton
        skeleton_ref.rotate(center_angle - skeleton_span / 2, center=(0, 0))


@gf.cell
def skeleton(
    grating_length_inner: float,
    grating_length_outer: float,
    grating_angle: float,
    N_skeleton: int,
    skeleton_span: float,
    **kwargs,
):
    # construct
    c = gf.Component()
    add_skeleton(
        c,
        grating_length_inner,
        grating_length_outer,
        grating_angle,
        N_skeleton,
        skeleton_span,
        **kwargs,
    )
    return c


@gf.cell
def _tether(straight_length: float, angle: float = 0):
    # width: 200nm - 500nm, taper_length=1.5um
    # then add length straight, keep 500nm
    c = gf.Component()
    #
    taper_length = 2.5
    taper_width_1 = 0.2
    taper_width_2 = 1.5
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


def _array_tether(
    c: Component,
    GL: float,
    grating_angle: float,
    tether_angle: Union[None, float] = 0,
    L_tether_bias: float = 2,
):
    DEG2RAD = np.pi / 180
    grating_angle_rad = grating_angle * DEG2RAD
    cross_section = gf.cross_section.cross_section(width=0.2, layer="WG")
    if tether_angle == None:
        TETHER_ANGLE = grating_angle_rad
    else:
        TETHER_ANGLE = tether_angle
    #
    SHRINK_LENGTH = 0.07
    for i, x in enumerate(np.linspace(4, GL - 3, 4)):
        L_tether = (GL - x) * np.sin(grating_angle_rad) + L_tether_bias
        # >>> top <<<
        tether = _tether(straight_length=L_tether, angle=TETHER_ANGLE)
        tether_ref = c << tether
        # create port
        c.add_port(
            "ou{:d}".format(i),
            center=(
                x * np.cos(grating_angle_rad),
                x * np.sin(grating_angle_rad) - SHRINK_LENGTH,
            ),
            cross_section=cross_section,
            orientation=0,
        )
        tether_ref.connect("o1", c.ports["ou{:d}".format(i)])
        # >>> bottom <<<
        tether = _tether(straight_length=L_tether, angle=-TETHER_ANGLE)
        tether_ref_bottom = c << tether
        # create port
        c.add_port(
            "ob{:d}".format(i),
            center=(
                x * np.cos(grating_angle_rad),
                -(x * np.sin(grating_angle_rad) - SHRINK_LENGTH),
            ),
            cross_section=cross_section,
            orientation=180,
        )
        tether_ref_bottom.connect("o1", c.ports["ob{:d}".format(i)])


@gf.cell
def section_2skeleton_tether(
    grating: List[float],
    grating_angle: float,
    start_radius: float = 10,
    input_length: float = 10,
    patch_length: float = 5,
):
    #
    c = gf.Component()
    #
    grating_length = grating[-1] - patch_length
    GL = grating_length + start_radius
    add_skeleton(c, 0, GL, grating_angle, N_skeleton=2, skeleton_span=1.5)
    #
    _array_tether(c, GL, grating_angle, tether_angle=0, L_tether_bias=2)
    #
    return c


@gf.cell
def section_multiskeleton_tether(
    grating: List[float],
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
    grating_length = grating[-1] - patch_length
    GL = grating_length + start_radius
    gratings = np.array(grating).reshape(-1, 2)
    # add grating skeleton
    add_skeleton(c, 0, GL, grating_angle, N_skeleton=2, skeleton_span=1.5)
    # print(gratings)
    ATTACH_LENGTH = 10e-3
    for i in range(1, len(gratings), 2):
        grating_inner = start_radius + gratings[i][1] - ATTACH_LENGTH
        grating_outer = start_radius + gratings[i + 1][0] + ATTACH_LENGTH
        grating_rad = (grating_inner + grating_outer) / 2
        # print(grating_inner, grating_outer)
        N_skeleton = 2
        # N_skeleton = 2 if (i % 4 == 1) else 1
        add_skeleton(
            c,
            grating_inner,
            grating_outer,
            grating_angle * (2 / 5),
            N_skeleton=N_skeleton,
            skeleton_span=(50e-9 / (grating_rad * 1e-6)) / DEG2RAD,
        )
    #
    _array_tether(c, GL, grating_angle, tether_angle=0, L_tether_bias=2)
    #
    return c


def grating_tether(
    grating: List[float],
    #
    mask_func: Union[Callable, None],
    tether_func: Union[Callable, None],
    grating_angle: float,
    start_radius: float = 10,
    hole: bool = False,
    suspend: bool = False,
    input_length: float = 10,
) -> gf.Component:
    # const
    PATCH_LENGTH = 0 if (mask_func is None and tether_func is None) else 5
    #
    c = gf.Component("grating_gds")  # here we generate gds with designated cell name
    # construct
    from copy import deepcopy

    grating = deepcopy(grating)
    if grating[0] < 40e-3:  # 40nm
        grating[0] = -1  # Tim: to connect to the taper
    grating_length = grating[-1]
    #
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
            grating=grating,
            grating_angle=grating_angle,
            start_radius=start_radius,
            patch_length=PATCH_LENGTH,
        )
    else:
        tether = None
    #
    if mask_func is not None:
        mask = mask_func(
            grating=grating,
            grating_angle=grating_angle,
            start_radius=start_radius,
            patch_length=PATCH_LENGTH,
        )
    else:
        mask = None
    #
    gt = grating_mask_tether(
        g,
        mask,
        tether=tether,
        input_length=input_length,
        hole=hole,
        suspend=suspend,
    )
    gt_ref = c << gt
    c.add_ports(gt_ref.ports)
    #
    return c


def recipes(tether_typ: str) -> dict:
    if tether_typ == "rect":
        return {"mask_func": rect_mask, "tether_func": None, "grating_angle": 40}
    elif tether_typ == "section":
        return {"mask_func": section_mask, "tether_func": None, "grating_angle": 24}
    elif tether_typ == "empty":
        return {"mask_func": None, "tether_func": None, "grating_angle": 24}
    elif tether_typ == "section_tether":
        return {
            "mask_func": section_mask,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
        }
    elif tether_typ == "section_rect_tether":
        return {
            "mask_func": section_rect_mask,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": False,
        }
    elif tether_typ == "section_rect_tether_multisuspend":
        return {
            "mask_func": section_rect_mask,
            "tether_func": section_multiskeleton_tether,
            "grating_angle": 24,
            "suspend": False,
        }
    elif tether_typ == "section_rect_tether_hole_multisuspend":
        return {
            "mask_func": section_rect_mask,
            "tether_func": section_multiskeleton_tether,
            "grating_angle": 24,
            "suspend": False,
            "hole": True,
        }
    elif tether_typ == "section_rect_tether_suspend":
        return {
            "mask_func": section_rect_mask,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": True,
        }
    elif tether_typ == "section_rect_tether_hole":
        return {
            "mask_func": section_rect_mask,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": False,
            "hole": True,
        }
    elif tether_typ == "section_rect_tether_hole_suspend":
        return {
            "mask_func": section_rect_mask,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": True,
            "hole": True,
        }
    elif tether_typ == "section_rect_tether_hole_unbox":
        return {
            "mask_func": None,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": False,
            "hole": True,
            "input_length": 0,
        }
    elif tether_typ == "section_rect_tether_suspend_unbox":
        return {
            "mask_func": None,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": True,
            "hole": False,
            "input_length": 0,
        }
    elif tether_typ == "section_rect_tether_hole_suspend_unbox":
        return {
            "mask_func": None,
            "tether_func": section_2skeleton_tether,
            "grating_angle": 24,
            "suspend": True,
            "hole": True,
            "input_length": 0,
        }
    elif tether_typ == "section_rect_tether_hole_multisuspend_unbox":
        return {
            "mask_func": None,
            "tether_func": section_multiskeleton_tether,
            "grating_angle": 24,
            "suspend": False,
            "hole": True,
            "input_length": 0,
        }
    else:
        return {
            "mask_func": None,
            "tether_func": None,
            "grating_angle": None,
        }


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
    grating = subw_grating(N, Lambda, ff, ffL, ffH, NL, NH)
    recipe = recipes("section_rect_tether_multisuspend")
    c = grating_tether(
        grating,
        **recipe,
    )
    # c = section_tether(30, 24)
    # d = skeleton(30, 24, 3, 1.5)
    c.show(show_ports=True)
