import math
import numpy as np


# TODO cosi funziona, ma dagli appunti sarebbe diversa:
# la sommatoria con i non parte da 0 ma da 1, con conseguenze 2i non a 0 la prima volta
# ?????? 
def dct(v):
    N = len(v)
    y = np.zeros(N, dtype=float)
    for k in range(N):
        sum_cos = 0.
        if k == 0:
            Ck = 1.0 / math.sqrt(N)
        else:
            Ck = math.sqrt(2.0 / N)

        for i in range(N):
            ak = math.cos((math.pi * k * (2*i + 1)) / (2 * N)) * v[i]
            sum_cos += ak
        y[k] = Ck * sum_cos
    return y



def dct2(m):
    m_in = np.array(m, dtype=float)
    N = len(m_in)
    y_m = m_in


    # DCT1 for columns
    for j in range(N):
        y_m[:,j] = dct(m_in[:,j])

    # DCT1 for rows
    for j in range(N):
        y_m[j,:] = np.transpose(dct(np.transpose(m_in[j,:])))

    return y_m