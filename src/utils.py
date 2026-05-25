import math
import numpy as np


# v can be passed by reference because never modified
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


def idct(Y):
    """1-D inverse DCT .
    
    """
    N = len(Y)
    x = np.zeros(N, dtype=float)
    for n in range(N):
        x[n] = (1.0 / math.sqrt(N)) * Y[0]
        for k in range(1, N):
            x[n] += math.sqrt(2.0 / N) * Y[k] * math.cos(math.pi * k * (2 * n + 1) / (2 * N))
    return x


def idct2(m):
    """2-D inverse DCT (apply idct on rows then columns).

    """
    m_in = np.array(m, dtype=float)
    N = len(m_in)
    y_m = np.zeros_like(m_in)

    for j in range(N):
        y_m[j, :] = idct(m_in[j, :])

    for j in range(N):
        y_m[:, j] = idct(y_m[:, j].copy())

    return y_m