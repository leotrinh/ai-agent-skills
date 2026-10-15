---
name: qr-in-heart
description: Generate a scannable pink (or custom-color) QR code inside a clearly shaped heart from a URL or text; preserve the actual QR matrix and validate the decoded payload before delivering artwork.
---

# QR in Heart

Author: Leo

Use this skill when the user asks for a romantic, heart-shaped QR graphic. Accept `text` (URL or any plain text) and optional `color` (default `#ff1681`).

## Procedure

1. Install requirements with `python -m pip install -r requirements.txt` from this skill directory if not already installed.
2. Run `python scripts/generate.py --text "<URL or text>" --color "#ff1681" --out "<output.png>"`.
3. The generator uses a real QR matrix (error correction H), preserves all three finder patterns, rotates the unmodified QR image, and draws a separate heart silhouette outside the QR's white quiet zone. No AI re-drawing of the QR modules.
4. The script verifies the output with OpenCV QRCodeDetector. If it does not decode to the exact original payload, it exits with an error instead of claiming success. For long payloads or low-contrast colors, use a shorter URL and/or darker color if validation fails.
5. Deliver the verified PNG. Before printing, additionally scan with a real iPhone/Android camera at final printed size.

CLI flags: `--text` (required), `--color` (optional, default `#ff1681`), `--out` (required). Local preview UI: `python app.py` (requires Flask).
