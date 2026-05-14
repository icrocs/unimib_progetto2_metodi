import sys
import time

import numpy as np
from scipy.fftpack import dctn, dct
import matplotlib.pyplot as plt

import utils


# Run N tests from 1 to dimension
# Return 2D tuple with
# - First element millisec times for custom function
# - Second element millisec times for scipy function
def dct_benchmark(n_values):
    scipy_times = []
    custm_times = []

    for n in n_values:

        x = np.random.randint(0, 255, (n, n)).astype(float) - 128
        
        start_t = time.perf_counter()
        _ = dctn(x, type=2, norm='ortho')
        end_t = time.perf_counter()
        scipy_times.append((end_t - start_t) * 1000)

        start_t = time.perf_counter()
        _ = utils.dct2(x)
        end_t = time.perf_counter()
        custm_times.append((end_t - start_t) * 1000)
        
        print(f"Test completato per N={n}")

    return scipy_times, custm_times


def main():

    n_values = np.arange(10, 201, 10)

    print(f"Inizio benchmark su N: {n_values}")
    scipy_t, custom_t = dct_benchmark(n_values)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(n_values, scipy_t, 'o-', label="Scipy DCT2 (Fast)", color="blue", linewidth=2)
    ax.plot(n_values, custom_t, 's-', label="Custom DCT2 (O(N³))", color="red", linewidth=2)

    ax.set_yscale('log')
    

    ax.set_title("Confronto Prestazioni DCT2: Custom vs Scipy")
    ax.set_xlabel("Dimensione Matrice (N x N)")
    ax.set_ylabel("Tempo di esecuzione (ms) - Scala Log")
    
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
