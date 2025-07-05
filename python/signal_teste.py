import numpy as np
import matplotlib.pyplot as plt




def gerar_sinal_com_harmonicas(f_sinal=1000, n_ciclos=4,
                                f_amostragem_dac=200_000_000 / 4000,
                                f_amostragem_adc=200_000_000 / 8000):
    """
    Gera uma senoide com harmônicas para o DAC e ajusta as amostras do ADC
    para capturar a mesma janela temporal.

    Parâmetros:
    - f_sinal: frequência da senoide fundamental (Hz)
    - n_ciclos: número de ciclos da senoide
    - f_amostragem_dac: frequência de amostragem do DAC (Hz)
    - f_amostragem_adc: frequência de amostragem do ADC (Hz)

    Retorna:
    - sinal_dac: vetor da senoide com harmônicas (np.uint16)
    - N_adc: número de amostras para o ADC
    """
    # Escolher um vetor de DAC que resulte em ~1000 amostras
    N_dac = round((1000 // n_ciclos) * n_ciclos)
    tempo_total = N_dac / f_amostragem_dac
    t_dac = np.linspace(0, tempo_total, N_dac, endpoint=False)

    # Frequência ajustada para ter n_ciclos em N_dac amostras
    f_sinal_real = n_ciclos / tempo_total

    # Gera sinal com harmônicas
    sinal = (
        1000 * np.sin(2 * np.pi * f_sinal_real * t_dac) +
        100 * np.sin(2 * np.pi * 3 * f_sinal_real * t_dac) +
        400 * np.sin(2 * np.pi * 120 * f_sinal_real * t_dac) +
        1500  # offset
    )

    # Número de amostras do ADC que cobrem o mesmo tempo
    N_adc = int(tempo_total * f_amostragem_adc)

    print("=== Parâmetros Calculados ===")
    print(f"Frequência da senoide (ajustada): {f_sinal_real:.2f} Hz")
    print(f"Tamanho do vetor do DAC (e Python): {N_dac} amostras")
    print(f"Tamanho do vetor do ADC: {N_adc} amostras")
    print(f"Duração do sinal: {tempo_total:.6f} segundos")
    print(f"Frequência de amostragem do DAC: {f_amostragem_dac:.2f} Hz")
    print(f"Frequência de amostragem do ADC: {f_amostragem_adc:.2f} Hz")

    # Plota o sinal
    plt.figure(figsize=(10, 4))
    plt.plot(t_dac, sinal)
    plt.title(f"Sinal com {n_ciclos} ciclos - f ≈ {f_sinal_real:.2f} Hz")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return np.round(sinal).astype(np.uint16)
