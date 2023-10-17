import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# plt.gca().set_facecolor("gray")


def load_csv(filepath):
    df = pd.read_csv(filepath)
    w_via = df["w_via"]
    Z0 = df["Z0"]
    # convert to numpy array
    w_via = np.array(w_via)
    # Z0 is complex a+bi, convert from str, first replace j with i
    # then convert to complex, then take real part
    Z0 = np.array([complex(x.replace("i", "j")) for x in Z0])
    Z0 = np.real(Z0)
    return w_via, Z0


w_via, Z0 = load_csv("gcpw_via.csv")
Z0 = Z0 - 2.8

plt.plot(w_via, Z0, "o-", alpha=0.5)
plt.scatter(2.387, 52.76 - 2.8, marker="x", c="black", s=100)  # type: ignore
plt.xlabel("w_via (um)")
plt.ylabel("Z0 (Ohm)")
plt.scatter
# plt.grid()
plt.savefig("gcpw_via.png", dpi=200, bbox_inches="tight")
plt.show()
