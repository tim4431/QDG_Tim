import sys
import numpy as np

sys.path.append("..")
from lib.process_data.load_csv_data import load_csv_data

l, p, _ = load_csv_data("./data1/photodiode_AIN_3_lambda_sweep.csv", None, "l", "p")
import matplotlib.pyplot as plt

plt.plot(l, p)
plt.show()
