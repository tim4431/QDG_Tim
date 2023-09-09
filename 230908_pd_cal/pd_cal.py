import sys
sys.path.append("..")
from lib.device.examples import santec_power_sweep,photodiode_power_sweep

# santec_power_sweep("./data/santec_power_sweep.csv")

photodiode_power_sweep("./data/photodiode_power_sweep_1.2k.csv")