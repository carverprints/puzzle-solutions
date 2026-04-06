#!/usr/bin/env python3
"""Generate a print-ready QR code for a puzzle solutions book."""

import argparse
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage

GITHUB_USERNAME = "carverprints"
BASE_URL = f"https://{GITHUB_USERNAME}.github.io/puzzle-solutions"
QR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr-codes")


def generate_qr(book_id: str, output_dir: str = QR_DIR) -> str:
    """Generate a high-resolution QR code PNG for the given book.

    Returns the path to the saved file.
    """
    url = f"{BASE_URL}/{book_id}/"
    os.makedirs(output_dir, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,  # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,       # pixels per module — gives ~300 DPI at 1.5"+ print
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Set DPI metadata for print
    dpi = (300, 300)
    output_path = os.path.join(output_dir, f"qr-{book_id}.png")
    img.save(output_path, dpi=dpi)

    width_in = img.size[0] / dpi[0]
    print(f"QR code saved: {output_path}")
    print(f"  URL:  {url}")
    print(f"  Size: {img.size[0]}x{img.size[1]} px — prints at {width_in:.1f}\" square at 300 DPI")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a QR code for a puzzle book.")
    parser.add_argument("book_id", help="Book folder name (e.g. book1)")
    args = parser.parse_args()
    generate_qr(args.book_id)
