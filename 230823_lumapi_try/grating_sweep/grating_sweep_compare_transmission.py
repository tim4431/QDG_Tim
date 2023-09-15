import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(12, 8))
    uuidList = [
        "0eb0",
        "570e",
        "e199",
        "793c",
        "e86b",
        "15a5",
        "d1fd",
        "6ade",
        "674e",
        "a72b",
        "aa7c",
    ]
    lambdaList = [1120, 1160, 1200, 1240, 1280, 1320, 1360, 1400, 1440, 1480, 1520]
    ampList = []
    x0List = []
    for uuid, lambda_0 in zip(uuidList, lambdaList):
        dataName = "{:s}_{:.1f}_bw=20.0_transmission.txt".format(uuid, lambda_0)
        data = np.loadtxt(dataName)
        amp, x0, _, _ = arb_fit_1d(
            ax, data[:, 0] * 1e3, data[:, 1], "{:.1f}".format(lambda_0)
        )
        ampList.append(amp)
        x0List.append(x0)

    # print(ampList)

    # fit amp-x0 using amp = A*sin(ax+b)+B
    def f(x, A, a, b, B):
        return A * np.sin(2 * np.pi * x / a + b) + B

    from scipy.optimize import curve_fit

    popt, pcov = curve_fit(
        f,
        x0List,
        ampList,
        p0=[0.17, 200, 0, 0.3],
        bounds=([0, 0, 0, -2 * np.pi], [1, 500, 2 * np.pi, 1]),
    )
    print(popt)
    # popt = [0.2, 1 / 500, 0, 0]
    x = np.linspace(1120, 1520, 100)
    ax.plot(
        x,
        f(x, *popt),
        label=r"$fit={:.2f}*sin(2 \pi x/{:.2f}+{:.2f})+{:.2f}$".format(*popt),
    )
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("transmission")
    ax.legend()
    #
    plt.savefig("grating_sweep_compare_transmission.png", dpi=200, bbox_inches="tight")
    plt.show()
