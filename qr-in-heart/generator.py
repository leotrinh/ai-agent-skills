"""A valid QR inside a geometric heart silhouette. Author: Leo."""
from __future__ import annotations

import math
import random
import re
from io import BytesIO
from PIL import Image, ImageDraw
import qrcode
from qrcode.constants import ERROR_CORRECT_H

DEFAULT_COLOR = "#ff1681"
CANVAS = 1254


def _check_color(color: str) -> str:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Color must be a six-digit hex value like #ff1681")
    rgb = tuple(int(color[i:i+2], 16) for i in (1,3,5))
    # Do not silently produce a nearly white, unreadable QR on white.
    luminance = sum(channel * weight for channel, weight in zip(rgb, (0.2126, 0.7152, 0.0722)))
    if luminance > 195:
        raise ValueError("Choose a darker color for readable contrast against white")
    return color


def _curve(p0, p1, p2, p3, steps=90):
    points = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        points.append((
            round(u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]),
            round(u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]),
        ))
    return points


def _heart_outline():
    notch, tip = (627, 290), (627, 1150)
    return (
        _curve(notch,(555,110),(320,60),(165,215)) +
        _curve((165,215),(20,340),(82,540),(228,710)) +
        _curve((228,710),(310,825),(520,1045),tip) +
        _curve(tip,(734,1045),(944,825),(1026,710)) +
        _curve((1026,710),(1172,540),(1234,340),(1089,215)) +
        _curve((1089,215),(934,60),(699,110),notch)
    )


def _qr_tile(text: str, color: str) -> Image.Image:
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()  # Includes quiet zone.
    # Keep final QR close to ~690px across so it fits inside the heart.
    module = max(5, min(16, round(695 / (len(matrix) * math.sqrt(2)))))
    size = len(matrix) * module
    image = Image.new("RGBA", (size, size), "white")
    draw = ImageDraw.Draw(image)
    for y,row in enumerate(matrix):
        for x,value in enumerate(row):
            if value:
                draw.rectangle((x*module,y*module,(x+1)*module-1,(y+1)*module-1),fill=color)
    tile = image.rotate(45, resample=Image.Resampling.NEAREST, expand=True, fillcolor=(255,255,255,0))
    return tile.crop(tile.getbbox())


def generate_image(text: str, color: str = DEFAULT_COLOR) -> Image.Image:
    if not text:
        raise ValueError("URL/text cannot be empty")
    color = _check_color(color or DEFAULT_COLOR)
    tile = _qr_tile(text, color)
    image = Image.new("RGBA", (CANVAS,CANVAS),"white")
    draw = ImageDraw.Draw(image)
    draw.polygon(_heart_outline(), fill=color)
    # Sparse white module-like pixels in upper lobes: decorative only.
    rng = random.Random(44)
    for y in range(115,650,14):
        for x in range(80,1174,14):
            if rng.random() < .10 and image.getpixel((x,y))[:3] != (255,255,255):
                draw.rectangle((x,y,x+12,y+12),fill="white")
    # Composite a WHOLE white-backed QR tile, including its real quiet zone;
    # decoration can never alter finder patterns or data modules.
    qx = (CANVAS - tile.width)//2
    qy = 410 + round((694 - tile.height) * .1)
    if qy + tile.height > 1148:
        qy = 1148 - tile.height
    image.alpha_composite(tile,(qx,qy))
    return image.convert("RGB")


def generate_png_bytes(text: str, color: str = DEFAULT_COLOR) -> bytes:
    buffer = BytesIO()
    generate_image(text,color).save(buffer,format="PNG")
    return buffer.getvalue()
