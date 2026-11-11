"""Сравнение «было | стало» для проверки перерисовки.

python tools/redraw/compare.py t1_v_15_to_m15 [ещё имена...]
Берёт images/<name>.png (оригинал) и tools/redraw/preview/<name>.png (новая),
кладёт рядом в tools/redraw/compare/<name>.png.
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))


def flat(path, h):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    im = Image.alpha_composite(bg, im).convert("RGB")
    return im.resize((round(im.width * h / im.height), h))


def compare(name, h=600):
    old = flat(os.path.join(ROOT, "images", name + ".png"), h)
    new = flat(os.path.join(HERE, "preview", name + ".png"), h)
    out = Image.new("RGB", (old.width + new.width + 30, h + 50), "white")
    out.paste(old, (0, 50))
    out.paste(new, (old.width + 30, 50))
    d = ImageDraw.Draw(out)
    d.line([(old.width + 15, 0), (old.width + 15, h + 50)], fill="#999999", width=3)
    d.text((10, 10), "БЫЛО", fill="black")
    d.text((old.width + 40, 10), "СТАЛО", fill="black")
    os.makedirs(os.path.join(HERE, "compare"), exist_ok=True)
    out.save(os.path.join(HERE, "compare", name + ".png"))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        compare(n)
    print("ok")
