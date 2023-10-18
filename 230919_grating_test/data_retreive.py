import matplotlib.pyplot as plt
import numpy as np

dataName = "./data_231017/231017_175212_top3_1280.0_1370.0_0.0010.csv"

# load csv
data = np.loadtxt(dataName, delimiter=",", skiprows=1)
l = data[:, 0]
T = data[:, 3]
# plt.plot(l, T)
mask = np.logical_and(l > 1320, l < 1330)
plt.plot(l[mask], T[mask])
plt.xlabel("Wavelength " + r"$\lambda$" + "(nm)")
plt.ylabel("Transmission " + r"$T(\lambda)$")
plt.savefig("data_231017.png", dpi=200, bbox_inches="tight")
plt.show()
