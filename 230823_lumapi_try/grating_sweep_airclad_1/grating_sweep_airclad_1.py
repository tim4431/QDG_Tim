import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(12, 8))
    uuidList = [
        "82d5",
        "0a7a",
        "8e24",
        "d491",
        "61a5",
        "f38f",
        "d6b1",
        "e00e",
        "cf31",
        "a67d",
        "f855",
        "98f0",
        "45ec",
        "686a",
        "92da",
        "cde0",
        "c62e",
        "c2bc",
        "4901",
        "8572",
        "3442",
        "de6b",
        "8977",
        "c158",
        "71de",
        "8cfd",
        "7081",
        "6184",
        "b2a6",
        "bae3",
        "3140",
        "c4e5",
        "7e80",
        "1574",
        "f951",
        "224e",
        "231c",
        "fdb9",
        "3d59",
        "6469",
        "ea47",
        "1074",
        "e435",
        "1920",
        "f1f8",
    ]

    lambdaList = range(820, 1720, 20)
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
    def f1(x, A, g, d, b):
        return A * (1 + g * np.cos(4 * np.pi * d / x + b))

    def f2(x, A, g, d, b, g1, d1, b1):
        return (
            A
            * (1 + g * np.cos(4 * np.pi * d / x + b))
            * (1 + g1 * np.cos(4 * np.pi * d1 / x + b1))
        )

    def plot_data_f1(A, g, d, b):
        for data in dataList:
            amp, x0, _, _ = arb_fit_1d(
                ax, data[:, 0] * 1e3, data[:, 1], "", label=False
            )
        # popt = [0.5, 0.49, 4000, -3, 0.5, 230, 1]
        popt = [A, g, d, b]
        x = np.linspace(np.min(lambdaList), np.max(lambdaList), 100)
        ax.plot(
            x,
            f1(x, *popt),
            label=r"$fit={:.2f}*(1+{:.2f}*cos(4\pi*{:.0f}/x{:+.2f}))$".format(*popt),
        )

    def plot_data_f2(A, g, d, b, g1, d1, b1):
        for data in dataList:
            amp, x0, _, _ = arb_fit_1d(
                ax, data[:, 0] * 1e3, data[:, 1], "", label=False
            )
        # popt = [0.5, 0.49, 4000, -3, 0.5, 230, 1]
        popt = [A, g, d, b, g1, d1, b1]
        x = np.linspace(np.min(lambdaList), np.max(lambdaList), 100)
        ax.plot(
            x,
            f2(x, *popt),
            label=r"$fit={:.2f}*(1+{:.2f}*cos(4\pi*{:.0f}/x{:+.2f}))* (1+{:.0f}*cos(4\pi*{:.2f}/x{:+.2f}))$".format(
                *popt
            ),
        )

    # print(ampList)

    from scipy.optimize import curve_fit

    # popt, pcov = curve_fit(
    #     f1,
    #     x0List,
    #     ampList,
    #     p0=[0.29, 0.40, 5210, -1.4],
    #     bounds=(
    #         [0, 0, 0, -2 * np.pi],
    #         [1, 1, 6000, 2 * np.pi],
    #     ),
    # )
    #
    popt, pcov = curve_fit(
        f2,
        x0List,
        ampList,
        p0=[0.27, 0.37, 5161, -0.97, 0.19, 560, 1.58],
        bounds=(
            [0, 0, 0, -2 * np.pi, 0, 0, -2 * np.pi],
            [1, 1, 6000, 2 * np.pi, 1, 1000, 2 * np.pi],
        ),
    )
    #
    print(popt)
    popt = [0.27, 0.37, 5161, -0.97, 0.19, 560, 1.58]
    # plot_data_f1(*popt)
    plot_data_f2(*popt)
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("transmission")
    ax.legend()
    #
    plt.savefig("grating_sweep_compare_airclad_1.png", dpi=200, bbox_inches="tight")
    plt.show()
