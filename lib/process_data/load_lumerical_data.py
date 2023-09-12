import numpy as np


def load_lumerical_1d(fileName):
    data = np.loadtxt(fileName, delimiter=",")
    x = data[:, 0].squeeze()
    y = data[:, 1].squeeze()
    return x * 1e3, y
