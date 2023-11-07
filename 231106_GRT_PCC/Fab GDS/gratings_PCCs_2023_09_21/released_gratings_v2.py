import os, sys, gdspy, warnings, numpy as np
# sys.path.append('/Users/lkomza/Desktop/test')
sys.path.append('../..')
dir = os.path.dirname(__file__)

def shrink_rectangle(p1, p2, dxl=0, dxr=0, dyt=0, dyb=0):
    x_max = max(p1[0], p2[0])
    x_min = min(p1[0], p2[0])
    y_max = max(p1[1], p2[1])
    y_min = min(p1[1], p2[1])
    x_max -= dxr
    x_min += dxl
    y_max -= dyt
    y_min += dyb
    return [x_min, y_min],[x_max, y_max]

import PhotonForge as pf
forge = pf.Forge()
forge.load_yml()
forge.add_geometry(gdspy.Rectangle([-1e4/2, -1e4/2], [1e4/2, 1e4/2], layer=0))

x0,y0 = [0,-1e3]
start = x0 - 7.5*127
end = x0 + 7.5*127 - (8.5*127)
xs = np.arange(start, end+1, 127)
for x in xs:
    forge.xy = [x, y0]
    grating = pf.Component()
    grating.load_gds('grating_gds', dir+'/4e25.gds')
    grating.rotate(-np.pi/2)
    forge.add_component(grating)
    r = grating.get_bbox()
    r = shrink_rectangle(*r, dxl=2, dxr=2, dyt=0, dyb=3)
    forge.add_geometry(gdspy.Rectangle(*r, layer=2))

# # 1 and 4
# points = []
# x1,x2 = xs[0], xs[3]
# forge.xy = x1,y0
# points.append(forge.xy)
# forge.add(pf.waveguide, coordinates=[[0,0],[0,30]])
# forge.add(pf.tether, angle=np.pi/2)
# forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
# points.append([x1,forge.xy[1]])
# for i in range(12):
#     forge.add(pf.tether)
#     forge.add(pf.waveguide, coordinates=[[0,0],[22,0]])
# forge.add(pf.tether)
# points.append([x2,forge.xy[1]])
# dx = x2-forge.xy[0]-15
# forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
# forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
# forge.add(pf.tether, angle=-np.pi/2)
# forge.add(pf.waveguide, coordinates=[[0,0],[0,-30]])
# points.append(forge.xy)
# forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)

# 2 and 3
points = []
x1,x2 = xs[0], xs[1]
forge.xy = x1,y0
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=[[0,0],[0,10]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
points.append([x1,forge.xy[1]])
for i in range(3):
    forge.add(pf.tether)
    forge.add(pf.waveguide, coordinates=[[0,0],[23,0]])
forge.add(pf.tether)
points.append([x2,forge.xy[1]])
dx = x2-forge.xy[0]-15
forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
forge.add(pf.tether, angle=-np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,-10]])
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)

# 5 and 6
x1,x2 = xs[2], xs[3]
forge.xy = x1,y0
forge.add(pf.waveguide, coordinates=[[0,0],[0,10]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
second = forge.xy
forge.add(pf.pcc_bus, num_units = 3)
third = forge.xy
dx = x2-third[0]-15
forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
forge.add(pf.tether, angle=-np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,-10]])
end = forge.xy
start = x1,y0
p2 = start[0], second[1]
p3 = end[0], third[1]
forge.add(pf.waveguide, coordinates=[start,p2,p3,end], width=7, layer=2, relative=False)

# 7 and 8
points = []
x1,x2 = xs[4], xs[5]
forge.xy = x1,y0
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=[[0,0],[0,20]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,20]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,20]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
points.append([x1, forge.xy[1]])
# forge.yml['photonics.resonators.pcc_cavity']['a_m'] = 0.342
# forge.yml['photonics.resonators.pcc_cavity']['a_m'] = 0.342 - 0.05
# forge.yml['photonics.resonators.pcc_mirrors']['a_m'] = 0.342
# forge.yml['photonics.resonators.pcc_mirrors']['a_m'] = 0.342 - 0.05
forge.add(pf.pcc_bus, num_units = 4)
points.append([forge.xy[0]+15, forge.xy[1]])
forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-30],[0,-30]])
points.append([forge.xy[0]+15, forge.xy[1]])
forge.add(pf.pcc_bus, num_units = 3, angle=np.pi)
points.append([forge.xy[0]-15, forge.xy[1]])
forge.add(pf.waveguide, coordinates=[[0,0],[-15,0],[-15,-30],[0,-30]])
points.append([forge.xy[0]-15, forge.xy[1]])
forge.add(pf.pcc_bus, num_units = 2)
third = forge.xy
dx = x2-third[0]-15
points.append([forge.xy[0]+15+dx, forge.xy[1]])
forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
forge.add(pf.tether, angle=-np.pi/2)
y1 = forge.xy[1]
forge.add(pf.waveguide, coordinates=[[x2,y1],[x2,y0]], relative=False)
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)

# 9
points = []
x1 = xs[6]
forge.xy = x1,y0
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=[[0,0],[0,10]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
points.append([x1,forge.xy[1]])
forge.add(pf.pcc_bus, num_units = 2)
forge.add(pf.waveguide, coordinates=[[0,0],[1,0]])
forge.add(pf.taper, coordinates=[[0,0],[1,0]], initial_width=0.35, final_width=0.40, layer=1)
forge.add(pf.waveguide, coordinates=[[0,0],[1,0]], width=0.4)
forge.add(pf.pcc_mirrors,  N_mirrors=10)
forge.add(pf.pcc_cavity)
forge.add(pf.pcc_mirrors)
forge.add(pf.waveguide, coordinates=[[0,0],[2,0]], width=0.4)
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=[[0,0],[2,0]], width=0.4)
forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)




start = x0 + 7.5*127 - (7*127) + 127
end = x0 + 7.5*127 - (5*127)
xs = np.arange(start, end+1, 127)
for x in xs:
    forge.xy = [x, y0]
    grating = pf.Component()
    grating.load_gds('grating_gds', dir+'/f93f.gds')
    grating.rotate(-np.pi/2)
    forge.add_component(grating)
    r = grating.get_bbox()
    r = shrink_rectangle(*r, dxl=2, dxr=2, dyt=0, dyb=3)
    forge.add_geometry(gdspy.Rectangle(*r, layer=2))

# 1 and 4
# points = []
# x1,x2 = xs[0], xs[3]
# forge.xy = x1,y0
# points.append(forge.xy)
# forge.add(pf.waveguide, coordinates=[[0,0],[0,30]])
# forge.add(pf.tether, angle=np.pi/2)
# forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
# points.append([x1,forge.xy[1]])
# for i in range(12):
#     forge.add(pf.tether)
#     forge.add(pf.waveguide, coordinates=[[0,0],[22,0]])
# forge.add(pf.tether)
# points.append([x2,forge.xy[1]])
# dx = x2-forge.xy[0]-15
# forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
# forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
# forge.add(pf.tether, angle=-np.pi/2)
# forge.add(pf.waveguide, coordinates=[[0,0],[0,-30]])
# points.append(forge.xy)
# forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)

# 2 and 3
points = []
x1,x2 = xs[0], xs[1]
forge.xy = x1,y0
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=[[0,0],[0,10]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
points.append([x1,forge.xy[1]])
for i in range(3):
    forge.add(pf.tether)
    forge.add(pf.waveguide, coordinates=[[0,0],[23,0]])
forge.add(pf.tether)
points.append([x2,forge.xy[1]])
dx = x2-forge.xy[0]-15
forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
forge.add(pf.tether, angle=-np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,-10]])
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)

x0,y0 = [0,-1e3]
start = x0 - 9.5*127
end = x0 - 8.5*127
xs = np.arange(start, end+1, 127)
for x in xs:
    forge.xy = [x, y0]
    grating = pf.Component()
    grating.load_gds('grating_gds', dir+'/24d0.gds')
    grating.rotate(-np.pi/2)
    forge.add_component(grating)
    r = grating.get_bbox()
    r = shrink_rectangle(*r, dxl=2, dxr=2, dyt=0, dyb=3)
    forge.add_geometry(gdspy.Rectangle(*r, layer=2))
points = []
x1,x2 = xs[0], xs[1]
forge.xy = x1,y0
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=[[0,0],[0,10]])
forge.add(pf.tether, angle=np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,15],[15,15]])
points.append([x1,forge.xy[1]])
for i in range(3):
    forge.add(pf.tether)
    forge.add(pf.waveguide, coordinates=[[0,0],[23,0]])
forge.add(pf.tether)
points.append([x2,forge.xy[1]])
dx = x2-forge.xy[0]-15
forge.add(pf.waveguide, coordinates=[[0,0],[dx,0]])
forge.add(pf.waveguide, coordinates=[[0,0],[15,0],[15,-15]])
forge.add(pf.tether, angle=-np.pi/2)
forge.add(pf.waveguide, coordinates=[[0,0],[0,-10]])
points.append(forge.xy)
forge.add(pf.waveguide, coordinates=points, width=7, layer=2, relative=False)

size = 25 - 2
forge.add(pf.mla_marker, coordinates=[(-2e3,-2e3),(-2e3,2e3),(2e3,-2e3)], width=1.25, length=50, layer=6, relative=False)
for c in [(-2e3,-2e3),(-2e3,2e3),(2e3,-2e3)]:
	forge.add_geometry(gdspy.Rectangle( (c[0]+size,c[1]+size), (c[0]-size,c[1]-size) , layer=2))


forge.write_gds()
#forge.bool([1,0], [4,0], 'and', 1)
forge.save()