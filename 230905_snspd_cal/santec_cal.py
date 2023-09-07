import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def load_data(fileName):
    data = pd.read_csv(fileName)
    dataatt = data["att"].to_numpy()
    datap = data["p"].to_numpy()
    return dataatt, datap


dataatt1, datap1 = load_data("./data3/santec_sweep_power_1.csv")
dataatt2, datap2 = load_data("./data3/santec_sweep_power_2.csv")
plt.plot(
    dataatt1,
    datap1,
    linestyle="-",
    color="b",
    marker=".",
    label="santec @ 1326nm, 1",
    alpha=0.6,
)
plt.plot(
    dataatt1,
    datap1,
    linestyle="-",
    color="orange",
    marker="+",
    label="santec @ 1326nm, 2",
    alpha=0.6,
)
plt.legend()
plt.yscale("log")
plt.xlabel("Output power (dBm)")
plt.ylabel("Measured power (uW)")
plt.savefig("./santec_sweep_power.png", dpi=200, bbox_inches="tight")
plt.show()
