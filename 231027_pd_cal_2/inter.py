import numpy as np
import matplotlib.pyplot as plt

def p(V):
    if (V<0.5):
        return 3.98502261*V+ 0.02982022
    else:
        return 3.74467099*V+ 0.03763261
    
att_dB =np.linspace(0,50,50)
Vs=10/np.exp(att_dB/10)
ps=[p(V) for V in Vs]
plt.plot(ps,Vs)
plt.show()