import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(12, 8))
    uuidList = [
        "686a",
        "cde0",
        "83a3",
        "4087",
        "de6b",
        "c158",
        "8cfd",
        "bb01",
        "ee95",
        "4117",
        "1574",
        "224e",
        "fdb9",
        "fbfd",
    ]
    lambdaList = [
        1080,
        1120,
        1160,
        1200,
        1240,
        1280,
        1320,
        1360,
        1400,
        1440,
        1480,
        1520,
        1560,
        1600,
    ]
    ampList = []
    x0List = []
    for uuid, lambda_0 in zip(uuidList, lambdaList):
        dataName = "{:s}_{:.1f}_bw=20.0_transmission.txt".format(uuid, lambda_0)
        data = np.loadtxt(dataName)
        amp, x0, _, _ = arb_fit_1d(
            ax, data[:, 0] * 1e3, data[:, 1], "{:.1f}".format(lambda_0), label=False
        )
        ampList.append(amp)
        x0List.append(x0)

    # print(ampList)

    # fit amp-x0 using amp = A*sin(ax+b)+B
    def f(x, A, g, d, b, g1, d1, b1):
        return (
            A
            * (1 + g * np.cos(4 * np.pi * d / x + b))
            * (1 + g1 * np.cos(4 * np.pi * d1 / x + b1))
        )

    from scipy.optimize import curve_fit

    popt, pcov = curve_fit(
        f,
        x0List,
        ampList,
        p0=[0.34, 0.3, 5100, -0.8, 0.14, 1500, -1],
        bounds=(
            [0, 0, 0, -2 * np.pi, 0, 0, -2 * np.pi],
            [1, 1, 8000, 2 * np.pi, 1, 3000, 2 * np.pi],
        ),
    )
    print(popt)
    # popt = [0.2, 1 / 500, 0, 0]
    x = np.linspace(np.min(lambdaList), np.max(lambdaList), 100)
    ax.plot(
        x,
        f(x, *popt),
        label=r"$fit={:.2f}*(1+{:.2f}*cos(4\pi*{:.0f}/x{:+.2f}))* (1+{:.0f}*cos(4\pi*{:.2f}/x{:+.2f}))$".format(
            *popt
        ),
    )
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("transmission")
    ax.legend()
    #
    plt.savefig(
        "grating_sweep_airclad_compare_transmission.png", dpi=200, bbox_inches="tight"
    )
    plt.show()
