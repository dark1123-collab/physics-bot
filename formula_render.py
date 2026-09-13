# Рендер формул в картинки (дроби, корни и степени "в столбик"),
# чтобы не показывать их одной строкой текста. Использует matplotlib mathtext —
# полноценный LaTeX не нужен. Картинки кешируются в formula_cache/, чтобы не
# перерисовывать одну и ту же формулу при каждом показе вопроса.

import hashlib
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CACHE_DIR = "formula_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def render_formula(latex: str) -> str:
    key = hashlib.sha1(latex.encode("utf-8")).hexdigest()
    path = os.path.join(CACHE_DIR, f"{key}.png")
    if os.path.exists(path):
        return path

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, latex, fontsize=30)
    fig.savefig(
        path,
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.2,
        facecolor="white",
    )
    plt.close(fig)
    return path
