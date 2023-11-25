import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['figure.figsize'] = (10,6)
plt.rcParams.update({'font.size': 16})
import numpy as np
import sys
sys.path.append('C:\\Users\\QDG-DT5\\Documents\\Optics-Measurements')
from hardware_utility.hardware_helper import set_VOA_attenuation, set_laser, sequence_to_hist, sequence_to_hist_g2, sutter_stabilize
from hardware_utility.RemoteDevice import RemoteDevice
from hardware_utility import setup_manager

import pulsestreamer as pstreamer
from labjack import ljm
hw = setup_manager.get_hardware('s200a')
switch = hw['MEMS']
tf = hw['tunablefilter']
laser = hw['laser']
ps = hw['pulsestreamer']

def generate_squence(period, on_time, rel_delay):
    return [(rel_delay, 0), (on_time, 1), (period - on_time - rel_delay, 0)]

PL_seq = generate_squence(10e-3, 1e-6, 0)
PL_sequence = ps.createSequence()
PL_sequence.setDigital([3], PL_seq)
ps.stream(PL_sequence)