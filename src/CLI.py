import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

import jpeg


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="main.py",
        description="JPEG-like DCT2 image compressor.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python main.py photo.bmp 8 5\n"
            "  python main.py photo.bmp 16 10 --output result.bmp --show\n"
            "  python main.py photo.bmp 8 0   # keep NO frequencies (blank image)\n"
        ),
    )
    p.add_argument("image",  type=Path, help="Input image file (.bmp / .png / .jpg)")
    p.add_argument("F",      type=int,  help="Block size in pixels (e.g. 8)")
    p.add_argument("d",      type=int,  help="Frequency cutoff: zero coefficients where k+l >= d  (0 ... 2F-2)")
    p.add_argument("-o", "--output", type=Path, default=None,
                   help="Save compressed image to this path (optional)")
    p.add_argument("-s", "--show",   action="store_true",
                   help="Display original and compressed images side-by-side")
    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_cli() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.image.exists():
        parser.error(f"File not found: {args.image}")
    try:
        img = Image.open(args.image).convert("L")
    except Exception as exc:
        parser.error(f"Cannot open image: {exc}")

    err = jpeg.validate_params(img, args.F, args.d)
    if err:
        parser.error(err)

    kept  = jpeg.kept_coefficients(args.F, args.d)
    total = args.F ** 2
    print(f"Image   : {args.image.name}  ({img.width} x {img.height} px)")
    print(f"F = {args.F},  d = {args.d}")
    print(f"Kept    : {kept} / {total} coefficients per block  ({100*kept/total:.0f} %)")

    compressed = jpeg.compress_image(img, args.F, args.d)
    print(f"Output  : {compressed.width} x {compressed.height} px  (cropped to multiple of F)")

    if args.output:
        compressed.save(args.output)
        print(f"Saved   : {args.output}")
    if args.show:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(img, cmap='gray')
        axes[0].set_title(f"Originale ({img.width}x{img.height})")
        axes[0].axis('off')
        axes[1].imshow(compressed, cmap='gray')
        axes[1].set_title(f"Compressa (F={args.F}, d={args.d})")
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.show()

    return 0


if __name__ == "__main__":
    run_cli()