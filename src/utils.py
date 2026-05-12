import math
import numpy as np


# TODO cosi funziona, ma dagli appunti sarebbe diversa:
# la sommatoria con i non parte da 0 ma da 1, con conseguenze 2i non a 0 la prima volta
# ?????? 
def dct(v):
    N = len(v)
    y = np.zeros(N)

    for k in range(N):
        sum_cos = 0.

        # TODO Normalizzare? il prof non penso l'abbia messo
        # Per ora ho messo entrambi i casi
        if k == 0:
            Ck = 1.0 / math.sqrt(N)
            ww = N
        else:
            Ck = math.sqrt(2.0 / N)
            ww = N/2

        for i in range(N):
            # Calculate the cosine basis function value
            ak = math.cos((math.pi * k * (2*i + 1)) / (2 * N)) * v[i]
            ak /= ww
            sum_cos += ak

        y[k] = sum_cos

    return y



def dct2(m):
    N = len(m)
    y_m = m

    # DCT1 for columns
    for j in range(N):
        y_m[:,j] = dct(m[:,j])

    # DCT1 for rows
    for j in range(N):
        y_m[j,:] = np.transpose(dct(np.transpose(m[j,:])))

    return y_m