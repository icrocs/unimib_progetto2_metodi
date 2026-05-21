import numpy as np
from utils import dct, dct2, idct2
from PIL import Image


def block_splitter(A: np.ndarray, F: int) -> tuple[int, int, list[np.ndarray]]:
    """Split a 2-D array into F×F blocks (top-left aligned, remainder discarded).

    Returns (n_blocks_y, n_blocks_x, list_of_blocks).
    """
    h, w = A.shape
    n_y, n_x = h // F, w // F
    A = A[: n_y * F, : n_x * F].astype(float) #crop the input array A to ensure its dimensions are multiples of F, and convert to float for DCT processing. This is necessary because the DCT operates on blocks of size F×F, and any leftover pixels that don't fit into a complete block would be discarded. By cropping the image to the nearest multiple of F, we ensure that all pixels are included in the block processing without any issues.
    return n_y, n_x, [
        A[by * F : (by + 1) * F, bx * F : (bx + 1) * F] #extract the F×F block from the cropped array A for each block position (by, bx) and store it in a list. 
        for by in range(n_y)                            #The blocks are ordered row-wise, 
        for bx in range(n_x)                            #meaning that we first iterate over the blocks in the y-direction (rows)
                                                        # and then over the blocks in the x-direction (columns) within each row.
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
    """Compress a grayscale PIL image with DCT2 block compression.

    Args:
        img: PIL Image (converted to grayscale internally).
        F:   Block size in pixels.
        d:   Frequency cutoff — coefficients c[k,l] with k+l ≥ d are zeroed.
             Range: 0 (keep nothing) … 2F-2 (drop only the very last coefficient).

    Returns:
        Compressed PIL Image (grayscale), cropped to the nearest multiple of F.
    """
    A = np.array(img.convert("L")) #covert to grayscale
    n_y, n_x, blocks = block_splitter(A, F)
    compressed = [compress_block(b, d) for b in blocks]
    rows = [np.hstack(compressed[by * n_x : (by + 1) * n_x]) for by in range(n_y)] #reassemble the compressed blocks into rows, then stack the rows vertically to form the final compressed image array
    return Image.fromarray(np.vstack(rows)) #convert the final compressed image array back to a PIL Image and return it


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