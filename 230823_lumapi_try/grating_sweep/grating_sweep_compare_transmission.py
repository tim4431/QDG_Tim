import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(12, 8))
    uuidList = [
        # "4c42",
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
        "b60c",
        "338d",
    ]
    lambdaList = [
        # 1080,
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
    dataList = []
    for uuid, lambda_0 in zip(uuidList, lambdaList):
        dataName = "{:s}_{:.1f}_bw=20.0_transmission.txt".format(uuid, lambda_0)
        data = np.loadtxt(dataName)
        amp, x0, _, _ = arb_fit_1d(False, data[:, 0] * 1e3, data[:, 1], "", label=False)
        ampList.append(amp)
        x0List.append(x0)
        dataList.append(data)

    # fit amp-x0 using amp = A*sin(ax+b)+B
    # def f(x, A, g, d, b):
    #     return A * (1 + g * np.cos(4 * np.pi * d / x + b))
    def f(x, A, g, d, b, g1, d1, b1):
        return (
            A
            * (1 + g * np.cos(4 * np.pi * d / x + b))
            * (1 + g1 * np.cos(4 * np.pi * d1 / x + b1))
        )

    def plot_data(A, g, d, b, g1, d1, b1):
        for data in dataList:
            amp, x0, _, _ = arb_fit_1d(
                ax, data[:, 0] * 1e3, data[:, 1], "", label=False
            )
        # popt = [0.5, 0.49, 4000, -3, 0.5, 230, 1]
        popt = [A, g, d, b, g1, d1, b1]
        x = np.linspace(np.min(lambdaList), np.max(lambdaList), 100)
        ax.plot(
            x,
            f(x, *popt),
            label=r"$fit={:.2f}*(1+{:.2f}*cos(4\pi*{:.0f}/x{:+.2f}))* (1+{:.0f}*cos(4\pi*{:.2f}/x{:+.2f}))$".format(
                *popt
            ),
        )

    # print(ampList)

    from scipy.optimize import curve_fit

    popt, pcov = curve_fit(
        f,
        x0List,
        ampList,
        p0=[0.29, 0.52, 4000, -3, 0.02, 327, -3],
        bounds=(
            [0, 0, 0, -2 * np.pi, 0, 0, -2 * np.pi],
            [1, 1, 6000, 2 * np.pi, 1, 1000, 2 * np.pi],
        ),
    )
    print(popt)
    # ax.set_xlabel("wavelength (nm)")
    # ax.set_ylabel("transmission")
    # ax.legend()
    #
    # plt.savefig("grating_sweep_compare_transmission.png", dpi=200, bbox_inches="tight")
    # plt.show()
