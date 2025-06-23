import numpy as np
import matplotlib.pyplot as plt

def gerar_sinal(N=512, f_amostragem=1000, f_sinal=5):
    t = np.linspace(0, 1, N, endpoint=False)
    sinal = np.sin(2 * np.pi * f_sinal * t)
    return np.round(sinal*100).astype(np.int16) +100

tempo = np.linspace(0, 1, 512, endpoint=False)
mag = gerar_sinal()
plt.plot(tempo,mag)
plt.show()
