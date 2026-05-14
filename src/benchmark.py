import sys
import time
import numpy as np
from scipy.fftpack import dctn
import matplotlib.pyplot as plt
import utils

def dct_benchmark(n_values):
    scipy_times = []
    custm_times = []

    for n in n_values:
        x = np.random.randint(0, 255, (n, n)).astype(float) - 128
    
        start_t = time.perf_counter()
        _ = dctn(x, type=2, norm='ortho')
        end_t = time.perf_counter()
        scipy_times.append((end_t - start_t) * 1000) # Convertiamo in ms

        start_t = time.perf_counter()
        _ = utils.dct2(x)
        end_t = time.perf_counter()
        custm_times.append((end_t - start_t) * 1000) # Convertiamo in ms
        
        print(f"Test completato per N={n}")

    return np.array(scipy_times), np.array(custm_times)

def main():
    # Definiamo i valori di N da testare
    n_values = np.arange(10, 201, 10) # Da 10 a 200 con step di 10

    print(f"Inizio benchmark su N: {n_values}")
    scipy_t, custom_t = dct_benchmark(n_values)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.plot(n_values, scipy_t, 'ob', label="Scipy DCT2 (Misurato)")
    ax.plot(n_values, custom_t, 'sr', label="Custom DCT2 (Misurato)")

    # --- RIFERIMENTI TEORICI (Normalizzati sull'ultimo punto) ---
    
    # 1. Trend N^3 per la tua Custom
    # Calcoliamo la costante c tale che: c * N_ultimo^3 = tempo_ultimo
    c_custom = custom_t[-1] / (n_values[-1]**3)
    theory_n3 = c_custom * (n_values**3)
    
    # 2. Trend N^2 log N per Scipy
    # Calcoliamo la costante c tale che: c * (N_ultimo^2 * log(N_ultimo)) = tempo_ultimo
    c_scipy = scipy_t[-1] / (n_values[-1]**2 * np.log2(n_values[-1]))
    theory_n2log = c_scipy * (n_values**2 * np.log2(n_values))


    ax.plot(n_values, theory_n3, '--', color="red", alpha=0.5, label="Trend Teorico O(N³)")
    ax.plot(n_values, theory_n2log, '--', color="blue", alpha=0.5, label="Trend Teorico O(N² log N)")

    ax.set_yscale('log') 
    
    ax.set_title("Analisi della Complessità Computazionale: DCT2", fontsize=14)
    ax.set_xlabel("Dimensione Matrice (N)", fontsize=12)
    ax.set_ylabel("Tempo di esecuzione (ms) - Scala Log", fontsize=12)
    
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.legend(loc="upper left")
    
    print("\nGrafico generato con successo.")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()