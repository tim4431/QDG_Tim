import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append("../..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(12, 8))
    uuidList = [
        # "83d2",
        # "686f",
        # "b3c1",
        # "f8ad",
        # "c1c6",
        # "89e9",
        # "bda1",
        # "4690",
        # "a2f5",
        "3087",
        "65e2",
        "2799",
        "128d",
        "9f24",
        "4c42",
        "28d4",
        "25c8",
        "b7ed",
        "a25c",
        "d412",
        "70ab",
        "03f6",
        "b73b",
        "ae85",
        "e2b1",
        "7e91",
        "ef87",
        "24f0",
        "fca4",
        "fde7",
        "21a8",
        "0b81",
        "4aac",
        "b648",
        "922a",
        "814d",
        "ccde",
        "2d91",
        "b60c",
        "f894",
        "8a45",
        "2e9e",
        "a930",
        "d0b6",
        "5de2",
        "6ab4",
    ]
    lambdaList = range(980, 1720, 20)
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

    # def f2(x, A, g, d, b, g1, d1, b1):
    #     return (
    #         A
    #         * (1 + g * np.cos(4 * np.pi * d / x + b))
    #         * (1 + g1 * np.cos(4 * np.pi * d1 / x + b1))
    #     )

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

    # def plot_data_f2(A, g, d, b, g1, d1, b1):
    #     for data in dataList:
    #         amp, x0, _, _ = arb_fit_1d(
    #             ax, data[:, 0] * 1e3, data[:, 1], "", label=False
    #         )
    #     # popt = [0.5, 0.49, 4000, -3, 0.5, 230, 1]
    #     popt = [A, g, d, b, g1, d1, b1]
    #     x = np.linspace(np.min(lambdaList), np.max(lambdaList), 100)
    #     ax.plot(
    #         x,
    #         f2(x, *popt),
    #         label=r"$fit={:.2f}*(1+{:.2f}*cos(4\pi*{:.0f}/x{:+.2f}))* (1+{:.0f}*cos(4\pi*{:.2f}/x{:+.2f}))$".format(
    #             *popt
    #         ),
    #     )

    # print(ampList)

    from scipy.optimize import curve_fit

    popt, pcov = curve_fit(
        f1,
        x0List,
        ampList,
        p0=[0.30, 0.58, 3630, 0.3],
        bounds=(
            [0, 0, 0, -2 * np.pi],
            [1, 1, 6000, 2 * np.pi],
        ),
    )
    # popt, pcov = curve_fit(
    #     f2,
    #     x0List,
    #     ampList,
    #     p0=[0.42, 0.59, 3600, -1, 0.41, 130, 1.10],
    #     bounds=(
    #         [0, 0, 0, -2 * np.pi, 0, 0, -2 * np.pi],
    #         [1, 1, 6000, 2 * np.pi, 1, 1000, 2 * np.pi],
    #     ),
    # )
    print(popt)
    plot_data_f1(*popt)
    # ax.set_xlabel("wavelength (nm)")
    # ax.set_ylabel("transmission")
    # ax.legend()
    #
    # plt.savefig("grating_sweep_compare_transmission.png", dpi=200, bbox_inches="tight")
    plt.show()
