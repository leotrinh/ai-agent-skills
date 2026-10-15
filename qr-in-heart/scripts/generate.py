"""CLI generator with required payload verification. Author: Leo."""
import argparse
import sys
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generator import DEFAULT_COLOR, generate_image


def decode_image(image):
    pixels = cv2.cvtColor(np.asarray(image.convert("RGB")),cv2.COLOR_RGB2BGR)
    payload,_,_ = cv2.QRCodeDetector().detectAndDecode(pixels)
    return payload


def create_verified(text: str, color: str, out: Path):
    image = generate_image(text,color)
    decoded = decode_image(image)
    if decoded != text:
        raise RuntimeError("QR validation failed: decoded content does not match input. Try a shorter payload or darker color.")
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    return out


def main():
    ap=argparse.ArgumentParser(description="Generate a scannable QR inside a heart")
    ap.add_argument("--text",required=True,help="Exact URL/text to encode")
    ap.add_argument("--color",default=DEFAULT_COLOR,help="Hex color, default #ff1681")
    ap.add_argument("--out",required=True,help="Output PNG path")
    args=ap.parse_args()
    try:
        path=create_verified(args.text,args.color,Path(args.out))
    except (ValueError,RuntimeError) as exc:
        ap.exit(1,f"ERROR: {exc}\n")
    print(f"VALIDATED {args.text!r} => {path}")


if __name__ == "__main__":
    main()
