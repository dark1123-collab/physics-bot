"""Обзорный лист оригиналов: python tools/redraw/sheet.py out.png img1 img2 ... (до 6, сетка 2×3)."""
import os
import sys

import matplotlib
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype(os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf"), 22)
W, H = 900, 520


def tile(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    im = Image.alpha_composite(bg, im).convert("RGB")
    im.thumbnail((W - 20, H - 50))
    cell = Image.new("RGB", (W, H), "white")
    cell.paste(im, ((W - im.width) // 2, 40))
    d = ImageDraw.Draw(cell)
    d.text((10, 8), os.path.basename(path), fill="#b91c1c", font=FONT)
    d.rectangle([0, 0, W - 1, H - 1], outline="#999999")
    return cell


out, paths = sys.argv[1], sys.argv[2:]
cols = 2
rows = (len(paths) + 1) // 2
sheet = Image.new("RGB", (W * cols, H * rows), "white")
for i, p in enumerate(paths):
    sheet.paste(tile(p), ((i % cols) * W, (i // cols) * H))
sheet.save(out)
