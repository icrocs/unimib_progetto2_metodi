from concurrent.futures import ProcessPoolExecutor
import os

import numpy as np
from utils import dct, dct2, idct2
from PIL import Image


def block_splitter(A: np.ndarray, F: int) -> tuple[int, int, list[np.ndarray]]:
    """Split a 2-D array into F×F blocks (top-left aligned, remainder discarded).
    Returns (n_blocks_y, n_blocks_x, list_of_blocks).
    """
    h, w = A.shape
    n_y, n_x = h // F, w // F

    #crop the input array A to ensure its dimensions are multiples of F.
    A = A[: n_y * F, : n_x * F].astype(float)
    
    #extract the FxF block from the cropped array A for each block position (by, bx).
    return n_y, n_x, [
        A[by * F : (by + 1) * F, bx * F : (bx + 1) * F]
        for by in range(n_y)
        for bx in range(n_x)
    ]


def compress_block(block: np.ndarray, d: int) -> np.ndarray:
    c = dct2(block) 
    F = block.shape[0] 
    k, l = np.meshgrid(np.arange(F), np.arange(F), indexing="ij") #some magic of meshgrid to create two 2D arrays 
                                                                  #k and l that represent the row and column indices of the DCT coefficients in the block. 
                                                                  # The indexing="ij" argument ensures that the first dimension corresponds to rows (k) and the second dimension corresponds to columns (l).
    c[k + l >= d] = 0.0 #zero coefficients where k+l >= d
    return np.clip(np.round(idct2(c)), 0, 255).astype(np.uint8) #inverse DCT (DCT-III) and clip to [0, 255]


def compress_image(img: Image.Image, F: int, d: int) -> Image.Image:
    """Compress a grayscale PIL image with DCT2 block compression using multiple CPU cores."""
    A = np.array(img.convert("L")) # convert to grayscale
    n_y, n_x, blocks = block_splitter(A, F)
    core = os.cpu_count() or 1
    max_cores = max(1, core - 2) #lasciamo 2 core liberi per il sistema e altre operazioni( se meno di cpu.count() < 4 core allora ne usa 1)
    with ProcessPoolExecutor(max_workers=max_cores) as executor:
        compressed_iter = executor.map(
            compress_block, 
            blocks, 
            [d] * len(blocks)
        )
        compressed = list(compressed_iter)
    rows = [np.hstack(compressed[by * n_x : (by + 1) * n_x]) for by in range(n_y)]
    return Image.fromarray(np.vstack(rows))

def validate_params(img: Image.Image, F: int, d: int) -> str | None:
    """Return an error string when parameters are invalid, else None."""
    if F < 1:
        return "F must be ≥ 1"
    if F > min(img.size):
        return f"F ({F}) exceeds the smallest image dimension ({min(img.size)} px)"
    if not (0 <= d <= 2 * F - 2):
        return f"d must be in [0, {2 * F - 2}] (= 2F−2 for F={F})"
    return None


def kept_coefficients(F: int, d: int) -> int:
    """Count DCT coefficients per block that survive the cutoff d."""
    k, l = np.meshgrid(np.arange(F), np.arange(F), indexing="ij")
    return int(np.sum(k + l < d))