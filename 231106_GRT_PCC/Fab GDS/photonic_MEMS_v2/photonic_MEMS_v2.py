import os, sys, gdspy, warnings, numpy as np
sys.path.append('/Users/lkomza/Desktop/test')
dir = os.path.dirname(__file__)

import PhotonForge as pf
forge = pf.Forge()
forge.load_yml()
forge.add_geometry(gdspy.Rectangle([-1e4/2, -1e4/2], [1e4/2, 1e4/2], layer=0))

def make_photonic_MEMS():
    forge.add(pf.exponential_taper)
    forge.add(pf.tether)
    forge.add(pf.waveguide, coordinates=[[0,0],[5,0]])
    forge.add(pf.taper, initial_width=0.35, final_width=0.4, coordinates=[[0,0],[1,0]], layer=1)
    forge.add(pf.pcc_mirrors, N_mirrors = 10)
    forge.add(pf.pcc_cavity)
    forge.add(pf.pcc_mirrors)
    forge.add(pf.waveguide, coordinates=[[0,0],[1,0]], width=0.4)
    forge.add(pf.waveguide, coordinates=[[0,0],[1,0]], width=0.4, update=False)
    MEMS = forge.add(pf.spider_actuator, tolerance=2)
    return MEMS

gaps = [0.25, 0.5, 1]
ys = [-100, 0, 100]

input_metal = []

x0,y0 = [10,-30]
for g,y in zip(gaps,ys):
    forge.xy = x0, y0+y
    forge.yml['MEMS.actuators.spider_actuator']['gap'] = g
    MEMS = make_photonic_MEMS()
    input_metal.append(MEMS.ports)

for dict in input_metal:
    #print(dict)
    w1 = np.abs(dict['VCC_0'][1] - dict['VCC_1'][1])
    w2 = np.abs(dict['GND_10'][1] - dict['GND_01'][1])
    forge.xy = dict['VCC_1'][0], dict['VCC_1'][1]-np.abs(dict['VCC_0'][1]-dict['VCC_1'][1])/2
    p1 = forge.make(pf.waveguide, coordinates=[[0,0],[10,0]], width=w1, layer=4)
    p2 = forge.make(pf.waveguide, coordinates=[[0,0],[10,0]], width=w2, layer=4)
    #forge.add_component(p1, update=False)
    #forge.add_component(p2)
    p3 = gdspy.boolean(p1.geometry, p2.geometry, 'xor', layer=4)
    path = pf.Component(p3, {'input': forge.xy, 'output': forge.xy})
    #forge.add_component(path)

forge.write_gds()
#forge.bool([4,0], [4,0], 'xor', 2)
forge.save()    