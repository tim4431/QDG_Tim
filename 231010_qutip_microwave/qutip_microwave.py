from qutip import *
import numpy as np
import matplotlib.pyplot as plt

N_level = 2
ele_00 = basis(N_level, 0) * basis(N_level, 0).dag()
ele_11 = basis(N_level, 1) * basis(N_level, 1).dag()
ele_01 = basis(N_level, 0) * basis(N_level, 1).dag()  # A
sigma_x = ele_01 + ele_01.dag()
sigma_y = -1j * (ele_01 - ele_01.dag())
sigma_z = ele_11 - ele_00

detune = 0
omega = 2 * np.pi * 3e9  # splitting
Omegax = 2 * np.pi * 10e6
Omegaz = 2 * np.pi * 100e6
# Omegaz = 2 * np.pi * 0
gamma = 1 / (1e-6)
gamma_10 = gamma
# gamma_phi = 2 * np.pi * 2e9 / (2 * np.sqrt(2))
gamma_phi = 0
gamma_phi_10 = gamma_phi

t = np.linspace(0, 1e-6, int(1e-6 * omega))

H = [
    [Omegax * sigma_x, np.cos(omega * t) * np.cos(omega * t)],
    [Omegax * sigma_y, -np.cos(omega * t) * np.sin(omega * t)],
    [Omegaz * sigma_z, np.cos(omega * t)],
]

Cop_list = []
Cop_list.append(np.sqrt(gamma_10) * ele_01)
Cop_list.append(np.sqrt(gamma_phi_10 / 2) * sigma_z)

psi0 = basis(N_level, 0)
result = mesolve(H, psi0, t, Cop_list, [ele_00, ele_11])

plt.figure()
for j in range(N_level):
    plt.plot(t * 1e6, result.expect[j], label=f"{j}")
plt.legend()
plt.xlabel("times (us)")
plt.ylabel("population")
plt.show()
