import numpy as np
import matplotlib.pyplot as plt


def penalty(p, lambda_range, lambda_0):
    return lambda l: p * lambda_range / (lambda_range + np.abs(l - lambda_0))


a = penalty(0.2, 100e-9, 1.326e-6)
b = penalty(0.2, 10e-9, 1.326e-6)
c = lambda l: (2 / 3) * a(l) + (1 / 3) * b(l)

x = np.linspace(1.326e-6 - 200e-9, 1.326e-6 + 200e-9, 200)
ya = a(x)
yb = b(x)
yc = c(x)
plt.plot(x, ya)
plt.plot(x, yb)
plt.plot(x, yc)
plt.show()
