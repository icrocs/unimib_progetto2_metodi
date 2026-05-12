import sys
import benchmark
import matplotlib
try:
    import gi
    gi.require_foreign("cairo")
    matplotlib.use('GTK4cairo')
except:
    pass
import matplotlib.pyplot as plt

import numpy as np
from scipy.fftpack import dctn, idctn
from PIL import Image


# Subdivide matrix A to FxF blocks
# remaining values are dropped
# Return array of 2D blocks (3D array)
# TODO gestire caso F > len(A)?
# TODO! gestire caso matrice non quadrata
def block_splitter(A, F):
    N_x = A.shape[0]
    N_y = A.shape[1]
    split_x = int(N_x / F)
    split_y = int(N_y / F)
    last_x = -(N_x % F) or None
    last_y = -(N_y % F) or None
    #print(f'Cutting last {last_x}, {last_y} and subdividing in {split_x}x{split_y} pieces')
    c_A = A[0:last_x, 0:last_y]
    return (split_y, split_x, [M for sub_A in np.split(c_A, split_x, axis = 0) for M in np.split(sub_A , split_y, axis = 1)])


def matrix_apply(A, func):
    for x in range(A.shape[0]):
        for y in range(A.shape[1]):
            func(A, x, y, A[x][y])

def cut_freq(A, x, y, v):
    if x + y >= d:
        A[x][y] = 0.

def reverse_val(A, x, y, v):
    val = round(v)
    if val > 255: val = 255
    if val < 0: val = 0
    A[x][y] = val

def main(argc: int, argv: str):
    global A
    global F
    global d

    if argc < 3:
        print(f'Usage: {argv[0]} <F> <d>')
        return -1

    im = Image.open(argv[1])
    A = np.array(im)
    F = int(argv[2])
    d = int(argv[3])

    print(f'Loaded matrix of size {A.shape}')
    print(f'matrix width: {len(A[0])}')
    print(f'matrix height: {len(A[:, 0])}')
    print(A)

    # Consistency checks
    if d > 2 * F - 2:
        print(f'Error: d must be <= 2F - 2')
        return -1
    
    # Consistency checks
    if F > min(A.shape):
        print(f'Error: F must not exceed matrix size')
        return -1

    split_x, split_y, splitted_image = block_splitter(A, F)
    print(f'Subdivided in {split_x}x{split_y} pieces')
    #for i in range(5):
    #    print(splitted_image[i])
    compressed_chunks = []
    for chunk in splitted_image:
        # Use numpy 'ortho' for normalization
        # If not ustilized it explodes imediatelly to high values

        chunk_dct2 = dctn(chunk, type=2, norm='ortho')
        matrix_apply(chunk_dct2, cut_freq)

        chunk_idct2 = idctn(chunk_dct2, type=2, norm='ortho')
        matrix_apply(chunk_idct2, reverse_val)
        
        compressed_chunks.append(np.array(chunk_idct2, dtype=int))

    #for i in range(len(compressed_chunks)):
    #for i in range(5):
    #    if (i % split_x) == 0:
    #        print('\nSplitting x axis\n')
    #    print(f'{compressed_chunks[i]}')

    h_stacked = []
    for chunk_y in range(split_y):
        base_chunk = chunk_y * split_x
        stacked_h = np.hstack(compressed_chunks[base_chunk:base_chunk + split_x])
        h_stacked.append(stacked_h)

    result = np.vstack(h_stacked)

    print(f'Result:\n{result}')
    print(f'\nOriginal:\n{A}')

    img = Image.fromarray(result.astype(np.uint8))
    img.show()




    #print(f'\nStacked: {np.hstack((compressed_chunks[0], compressed_chunks[1]))}')

    return 1


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)