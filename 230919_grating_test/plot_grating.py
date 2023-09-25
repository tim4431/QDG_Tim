import sys
import numpy as np

sys.path.append("..")
from QDG_Tim.lib.process_data.csv_data import load_csv_data

l, p, _ = load_csv_data(
    "./data_230920/photodiode_AIN_3_lambda_sweep_1.csv", None, "l", "p"
)
import matplotlib.pyplot as plt

plt.plot(l, p)
plt.show()
