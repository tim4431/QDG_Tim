import gdsfactory as gf

from grating_tether import skeleton, add_skeleton

c = gf.Component()
add_skeleton(c, 10, 11, 30, 2, 10)
c.show()
