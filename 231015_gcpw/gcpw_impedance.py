import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.gca().set_facecolor("gray")


def load_csv(filepath):
    df = pd.read_csv(filepath)
    w_c = df["w_c"]
    w_s = df["w_s"]
    Z0 = df["Z0"]
    # convert to numpy array
    w_c = np.array(w_c)
    w_s = np.array(w_s)
    # Z0 is complex a+bi, convert from str, first replace j with i
    # then convert to complex, then take real part
    Z0 = np.array([complex(x.replace("i", "j")) for x in Z0])
    Z0 = np.real(Z0)
    return w_c, w_s, Z0


w_c, w_s, Z0 = load_csv("wc_ws_1.csv")
datas1 = [(w_c[i], w_s[i], Z0[i]) for i in range(len(w_c))]
w_c, w_s, Z0 = load_csv("wc_ws_2.csv")
datas2 = [(w_c[i], w_s[i], Z0[i]) for i in range(len(w_c))]
w_c, w_s, Z0 = load_csv("wc_ws_3.csv")
datas3 = [(w_c[i], w_s[i], Z0[i]) for i in range(len(w_c))]
datas = datas1 + datas2 + datas3


def finddata(datas, w_c, w_s):
    EPS = 1e-5
    for data in datas:
        if abs(data[0] - w_c) < EPS and abs(data[1] - w_s) < EPS:
            return data[2]
    return np.nan


wc_List = np.arange(0.6, 1.2, 0.05)
ws_List = np.arange(0.9, 1.9, 0.1)
x_grid, y_grid = np.meshgrid(ws_List, wc_List)

Z0_grid = np.zeros(x_grid.shape)
for i in range(len(wc_List)):
    for j in range(len(ws_List)):
        Z0_grid[i, j] = finddata(datas, wc_List[i], ws_List[j])

# plt.contourf(x_grid, y_grid, Z0_grid, levels=40, cmap="RdGy")
plt.contourf(x_grid, y_grid, Z0_grid, levels=40, cmap="plasma")
plt.colorbar()
# 添加R=50 Ohm的等高线
plt.contourf(
    x_grid,
    y_grid,
    Z0_grid,
    levels=[49.9, 50.1],
    colors="white",
    alpha=0.8,
    linestyles="dotted",
)
plt.scatter(1.067, 0.762, marker="x", color="white", s=100)
plt.xlabel("w_s (mm)")
plt.ylabel("w_c (mm)")

from matplotlib.patches import Patch

# 手动创建一个带有标签的图例
legend_elements = [
    Patch(
        facecolor="white",
        edgecolor="black",
        alpha=0.8,
        linestyle="dotted",
        label="R=50 Ohm",
    )
]
plt.legend(handles=legend_elements)
plt.savefig("gcpw_impedance.png", dpi=200, bbox_inches="tight")
plt.show()
