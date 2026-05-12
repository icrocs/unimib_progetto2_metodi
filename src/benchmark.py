import time
import numpy as np
from scipy.fftpack import dctn, dct
import utils



# Run N tests from 1 to dimension
# Return 2D tuple with
# - First element millisec times for custom function
# - Second element millisec times for scipy function
def dct_benchmark(dimension: int):
    scipy_times = []
    custm_times = []

    for n in range(1, dimension + 1):
        x = np.random.randint(0, 255, (n, n)) - 128
        #x = np.ones((n, n))
        
        # Take scipy time
        start_t = time.perf_counter()
        y = dctn(x)
        end_t = time.perf_counter()

        #scipy_times.append(f"{n}:{(end_t - start_t) * 1000}")
        scipy_times.append((end_t - start_t) * 1000)

        #print(f'Output Scipy DCT2:\n{y}\n')

        # Take custom DCT2 time
        start_t = time.perf_counter()
        y = utils.dct2(x)
        end_t = time.perf_counter()

        #custm_times.append(f"{n}:{(end_t - start_t) * 1000}")
        custm_times.append((end_t - start_t) * 1000)

        #print(f'Output Custom DCT2:\n{y}\n')

    return (scipy_times, custm_times)

