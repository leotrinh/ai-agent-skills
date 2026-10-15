# qr-in-heart 💗

**Author:** Leo · **Version:** 1.4.0

A real, scannable QR inside a clearly recognizable pixel-textured heart. The QR payload is generated from scratch with its original matrix intact—not synthesized by image generation.

![Example](examples/phuong-heart-qr.png)

## Install

```bash
python -m pip install -r requirements.txt
```

## Command line

```bash
python scripts/generate.py --text "https://phuong.tinhtd.info/" --out phuong.png
python scripts/generate.py --text "A little message" --color "#C2185B" --out message.png
```

## Local web UI

```bash
python app.py
```

Open http://127.0.0.1:7860 for text, color picker, preview, and PNG download.

## Design and scan safety

- Real QR code (error correction H, four-module quiet zone), rotated 45 degrees.
- Pixel-textured heart outline is generated separately; the entire QR/quiet zone is pasted back intact.
- Exactly three finder patterns; no additional finder patterns from decorative blocks.
- The generator automatically verifies that OpenCV decodes the *exact input payload* and fails closed otherwise.
- Very long payloads or light colors may not be scannable. If validation fails, shorten the text or darken the color.
- Machine validation does not replace a physical camera test before printing, especially after resizing.

## Skill installation

Copy the `qr-in-heart` folder into your agent's local skills directory. This package includes the standard `SKILL.md` entry point and can also be published as a GitHub repository.

## License

MIT © Leo.
