"""Make a print-ready QR code.  Needs:  pip install "qrcode[pil]"
Usage:  python tools/make_qr.py https://your-site.example  qr.png"""
import sys, qrcode
from qrcode.constants import ERROR_CORRECT_H
url, out = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "qr.png")
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=24, border=4); qr.add_data(url); qr.make(fit=True)
qr.make_image(fill_color="#25235e", back_color="white").save(out); print("Saved", out)
