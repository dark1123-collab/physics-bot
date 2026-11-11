"""Единый стиль картинок бота: графики, схемы, приборы.

Все картинки рисуются с нуля (matplotlib), без чужих рисунков.
Белый фон, тёмные линии, один акцентный синий цвет, шрифт DejaVu Sans.
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

INK = "#1f2937"      # линии, подписи
ACCENT = "#2563eb"   # график, стрелка прибора, выделенное
FILL = "#dbeafe"     # заливка (вода, корпус)
GRID = "#cbd5e1"     # сетка
MUTED = "#64748b"    # вспомогательные подписи
LW = 2.2             # основная толщина линий
FONT = 15

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": FONT,
    "mathtext.fontset": "dejavusans",
    "axes.edgecolor": INK,
    "text.color": INK,
})


def save(fig, path, dpi=200):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


# ───────────── графики ─────────────

def graph(points, xlabel, ylabel, xticks, yticks, xlim=None, ylim=None, size=(7.5, 4.6),
          marks=None, dashed=None):
    """Ломаная по точкам на клетчатой сетке со стрелками осей.
    points — [(x, y), ...] или список таких ломаных; marks — {"A": (x, y)}; dashed — [((x1,y1),(x2,y2)), ...]."""
    fig, ax = plt.subplots(figsize=size)
    xlim = xlim or (min(xticks), max(xticks))
    ylim = ylim or (min(yticks), max(yticks))
    for x in xticks:
        ax.plot([x, x], ylim, color=GRID, lw=1, zorder=0)
    for y in yticks:
        ax.plot(xlim, [y, y], color=GRID, lw=1, zorder=0)
    lines = points if isinstance(points[0][0], (list, tuple)) else [points]
    for line in lines:
        xs, ys = zip(*line)
        ax.plot(xs, ys, color=ACCENT, lw=LW + 0.6, solid_capstyle="round", zorder=3)
    for (a, b) in dashed or []:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=INK, lw=1.2, ls=(0, (5, 4)), zorder=2)
    for name, (x, y) in (marks or {}).items():
        ax.plot(x, y, "o", color=ACCENT, ms=7, zorder=4)
        ax.annotate(name, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=FONT)
    # оси со стрелками через ноль
    x0 = 0 if xlim[0] <= 0 <= xlim[1] else xlim[0]
    y0 = 0 if ylim[0] <= 0 <= ylim[1] else ylim[0]
    dx, dy = (xlim[1] - xlim[0]) * 0.08, (ylim[1] - ylim[0]) * 0.1
    ax.annotate("", xy=(xlim[1] + dx, y0), xytext=(xlim[0], y0),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=16))
    ax.annotate("", xy=(x0, ylim[1] + dy), xytext=(x0, ylim[0]),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=16))
    ax.text(xlim[1] + dx, y0 + dy * 0.2, xlabel, ha="right", va="bottom")
    ax.text(x0 + (xlim[1] - xlim[0]) * 0.015, ylim[1] + dy, ylabel, ha="left", va="top")
    for x in xticks:
        if x != x0:
            ax.text(x, y0 - dy * 0.25, _num(x), ha="center", va="top", fontsize=FONT - 1)
    for y in yticks:
        if y != y0:
            ax.text(x0 - (xlim[1] - xlim[0]) * 0.015, y, _num(y), ha="right", va="center", fontsize=FONT - 1)
    ax.text(x0 - (xlim[1] - xlim[0]) * 0.015, y0 - dy * 0.25, "0", ha="right", va="top", fontsize=FONT - 1)
    ax.set_xlim(xlim[0] - (xlim[1] - xlim[0]) * 0.08, xlim[1] + dx * 1.2)
    ax.set_ylim(ylim[0] - dy * 0.9, ylim[1] + dy * 1.4)
    ax.axis("off")
    return fig, ax


def _num(v):
    s = f"{v:g}"
    return s.replace("-", "−").replace(".", ",")


# ───────────── электрические схемы ─────────────

class Circuit:
    """Схема на координатной сетке: wire, resistor, meter, battery, key, node, terminal."""

    def __init__(self, size=(8, 3.6)):
        self.fig, self.ax = plt.subplots(figsize=size)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def wire(self, *pts):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=INK, lw=LW, solid_capstyle="round", zorder=1)

    def resistor(self, x, y, label=None, w=1.3, h=0.42, vertical=False, label_side=1):
        """Резистор с центром (x, y); провод к нему рисуется отдельно."""
        if vertical:
            w, h = h, w
        self.ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc="white", ec=INK, lw=LW, zorder=3))
        if label:
            if vertical:
                self.ax.text(x + label_side * (w / 2 + 0.15), y, label, ha="left" if label_side > 0 else "right",
                             va="center", fontsize=FONT + 1)
            else:
                self.ax.text(x, y + label_side * (h / 2 + 0.12), label, ha="center",
                             va="bottom" if label_side > 0 else "top", fontsize=FONT + 1)

    def resistor_on(self, x1, x2, y, label=None, w=1.3, label_side=1):
        """Горизонтальный участок провода x1→x2 с резистором посередине (провод доходит до краёв)."""
        xc = (x1 + x2) / 2
        self.wire((x1, y), (xc - w / 2, y))
        self.wire((xc + w / 2, y), (x2, y))
        self.resistor(xc, y, label, w=w, label_side=label_side)

    def meter_on(self, x1, x2, y, letter, r=0.32):
        """Горизонтальный участок x1→x2 с прибором посередине."""
        xc = (x1 + x2) / 2
        self.wire((x1, y), (xc - r, y))
        self.wire((xc + r, y), (x2, y))
        self.meter(xc, y, letter, r)

    def meter(self, x, y, letter, r=0.32):
        self.ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=LW, zorder=3))
        self.ax.text(x, y, letter, ha="center", va="center", fontsize=FONT + 1, zorder=4)

    def battery(self, x, y, vertical=False):
        """Источник тока: длинная тонкая и короткая толстая пластины."""
        if vertical:
            self.ax.plot([x - 0.35, x + 0.35], [y + 0.08, y + 0.08], color=INK, lw=LW, zorder=3)
            self.ax.plot([x - 0.18, x + 0.18], [y - 0.08, y - 0.08], color=INK, lw=LW * 2.4, zorder=3)
        else:
            self.ax.plot([x - 0.08, x - 0.08], [y - 0.35, y + 0.35], color=INK, lw=LW, zorder=3)
            self.ax.plot([x + 0.08, x + 0.08], [y - 0.18, y + 0.18], color=INK, lw=LW * 2.4, zorder=3)

    def key(self, x1, y, x2, label="К"):
        """Разомкнутый ключ между x1 и x2 на горизонтали y."""
        self.ax.plot([x1, x1 + (x2 - x1) * 0.25], [y, y], color=INK, lw=LW)
        self.ax.plot([x1 + (x2 - x1) * 0.25, x2 - (x2 - x1) * 0.1], [y, y + 0.32], color=INK, lw=LW)
        self.ax.plot([x2 - (x2 - x1) * 0.12, x2], [y, y], color=INK, lw=LW)
        if label:
            self.ax.text((x1 + x2) / 2, y - 0.18, label, ha="center", va="top", fontsize=FONT)

    def node(self, x, y):
        self.ax.add_patch(Circle((x, y), 0.07, fc=INK, ec=INK, zorder=5))

    def terminal(self, x, y, label=None, side=-1):
        self.ax.add_patch(Circle((x, y), 0.1, fc="white", ec=INK, lw=LW, zorder=5))
        if label:
            self.ax.text(x + side * 0.22, y, label, ha="right" if side < 0 else "left", va="center",
                         fontsize=FONT + 1)

    def save(self, path):
        self.ax.autoscale_view()
        self.ax.margins(0.06)
        save(self.fig, path)


# ───────────── приборы ─────────────

def dial_meter(scales, needle_value, scale_index, letter, terminals, connected, size=(6.4, 5.4)):
    """Стрелочный прибор с несколькими шкалами.
    scales — [(min, max, major_step, minor_per_major), ...] сверху вниз;
    needle_value — показание по шкале scale_index; terminals — подписи клемм; connected — какие клеммы подключены."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((-3.2, -2.9), 6.4, 6.0, boxstyle="round,pad=0.05,rounding_size=0.25",
                                fc="#f8fafc", ec=INK, lw=LW))
    cx, cy = 0, -1.15
    a0, a1 = 140, 40  # угол начала и конца шкалы, градусы
    radii = [3.0 - 0.75 * i for i in range(len(scales))]
    for (lo, hi, step, minor), R in zip(scales, radii):
        ax.add_patch(Arc((cx, cy), 2 * R, 2 * R, theta1=a1, theta2=a0, color=INK, lw=1.6))
        n = round((hi - lo) / step)
        for k in range(n * minor + 1):
            v = lo + k * step / minor
            ang = math.radians(a0 + (a1 - a0) * (v - lo) / (hi - lo))
            major = k % minor == 0
            l1 = R + (0.22 if major else 0.12)
            ax.plot([cx + R * math.cos(ang), cx + l1 * math.cos(ang)],
                    [cy + R * math.sin(ang), cy + l1 * math.sin(ang)], color=INK, lw=1.6 if major else 1.0)
            if major:
                ax.text(cx + (R + 0.45) * math.cos(ang), cy + (R + 0.45) * math.sin(ang), _num(v),
                        ha="center", va="center", fontsize=FONT - 1)
    lo, hi, _, _ = scales[scale_index]
    ang = math.radians(a0 + (a1 - a0) * (needle_value - lo) / (hi - lo))
    ax.plot([cx, cx + (radii[0] + 0.1) * math.cos(ang)], [cy, cy + (radii[0] + 0.1) * math.sin(ang)],
            color=ACCENT, lw=2.4, zorder=5)
    ax.add_patch(Circle((cx, cy), 0.16, fc=INK, zorder=6))
    ax.text(0, -0.1, letter, ha="center", va="center", fontsize=FONT + 10, fontweight="bold")
    # клеммы
    xs = [-2.0 + 4.0 * i / (len(terminals) - 1) for i in range(len(terminals))]
    for x, name in zip(xs, terminals):
        on = name in connected
        ax.add_patch(Circle((x, -2.35), 0.22, fc=ACCENT if on else "white", ec=INK, lw=LW, zorder=4))
        ax.text(x, -1.95, name, ha="center", va="bottom", fontsize=FONT)
        if on:
            ax.plot([x, x], [-2.57, -3.6], color=ACCENT, lw=3, zorder=3)
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-3.7, 3.3)
    return fig, ax


def _arc_scale(ax, cx, cy, R, a0, a1, lo, hi, major, minor, labels=True, inside=False, fmt=None, lw=1.4,
               label_r=None):
    """Дуговая шкала: значения lo…hi от угла a0 до a1 (градусы), штрихи наружу (или внутрь)."""
    ax.add_patch(Arc((cx, cy), 2 * R, 2 * R, theta1=min(a0, a1), theta2=max(a0, a1), color=INK, lw=lw))
    n = round((hi - lo) / major * minor)
    sgn = -1 if inside else 1
    for k in range(n + 1):
        v = lo + k * major / minor
        ang = math.radians(a0 + (a1 - a0) * (v - lo) / (hi - lo))
        is_major = k % minor == 0
        half = minor % 2 == 0 and k % (minor // 2) == 0
        L = 0.24 if is_major else (0.17 if half else 0.11)
        ax.plot([cx + R * math.cos(ang), cx + (R + sgn * L) * math.cos(ang)],
                [cy + R * math.sin(ang), cy + (R + sgn * L) * math.sin(ang)],
                color=INK, lw=1.6 if is_major else 0.9)
        if is_major and labels:
            r = label_r or (R + sgn * 0.5)
            ax.text(cx + r * math.cos(ang), cy + r * math.sin(ang), (fmt or _num)(v),
                    ha="center", va="center", fontsize=FONT - 1)


def barometer(value_mm, inner, size=(6.2, 6.2)):
    """Барометр-анероид: внешняя шкала 730…790 мм рт. ст. (цена деления 1), внутренняя — в inner ("кПа" или "гПа").
    Стрелка — на value_mm."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Circle((0, 0), 3.55, fc="#f8fafc", ec=INK, lw=LW * 1.3))
    a0, a1 = 225, -45                      # 730 мм — слева внизу, 790 — справа внизу
    lo, hi = 730, 790
    _arc_scale(ax, 0, 0, 2.75, a0, a1, lo, hi, 10, 10, label_r=2.3)
    ax.text(0, -2.55, "мм рт. ст.", ha="center", va="center", fontsize=FONT - 1, color=MUTED)
    # внутренняя шкала в тех же углах: давление p_mm ↔ p_inner
    k = 0.133322 if inner == "кПа" else 1.33322
    ilo, ihi = lo * k, hi * k
    if inner == "кПа":
        first, step, minor = 98, 1, 5
    else:
        first, step, minor = 980, 10, 5
    ang = lambda v: a0 + (a1 - a0) * (v - ilo) / (ihi - ilo)  # noqa: E731
    R = 1.85
    ax.add_patch(Arc((0, 0), 2 * R, 2 * R, theta1=a1, theta2=a0, color=INK, lw=1.2))
    v = first
    while v <= ihi + 1e-9:
        for j in range(minor):
            vv = v + j * step / minor
            if ilo <= vv <= ihi:
                t = math.radians(ang(vv))
                L = 0.2 if j == 0 else 0.1
                ax.plot([R * math.cos(t), (R - L) * math.cos(t)], [R * math.sin(t), (R - L) * math.sin(t)],
                        color=INK, lw=1.4 if j == 0 else 0.8)
        if ilo <= v <= ihi:
            t = math.radians(ang(v))
            ax.text((R - 0.48) * math.cos(t), (R - 0.48) * math.sin(t), _num(v), ha="center", va="center",
                    fontsize=FONT - 3)
        v += step
    ax.text(0, -0.8, inner, ha="center", va="center", fontsize=FONT - 1, color=MUTED)
    t = math.radians(a0 + (a1 - a0) * (value_mm - lo) / (hi - lo))
    ax.plot([-0.5 * math.cos(t), 2.85 * math.cos(t)], [-0.5 * math.sin(t), 2.85 * math.sin(t)],
            color=ACCENT, lw=3, solid_capstyle="round", zorder=5)
    ax.add_patch(Circle((0, 0), 0.18, fc=INK, zorder=6))
    ax.set_xlim(-3.8, 3.8)
    ax.set_ylim(-3.8, 3.8)
    return fig, ax


def thermometer_h(lo, hi, value, minor=10, size=(9, 1.9), mark=None):
    """Горизонтальный медицинский термометр: шкала lo…hi °C, деления 1/minor, столбик до value."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_aspect("equal")
    ax.axis("off")
    L = hi - lo
    sx = 8.0 / L                        # масштаб: всю шкалу — на 8 единиц
    x = lambda v: (v - lo) * sx          # noqa: E731
    ax.add_patch(FancyBboxPatch((x(lo) - 1.4, -1.0), 8.0 + 2.6, 1.85, boxstyle="round,pad=0,rounding_size=0.5",
                                fc="#f8fafc", ec=INK, lw=LW))
    ax.add_patch(Circle((x(lo) - 0.95, 0.15), 0.32, fc=ACCENT, ec=INK, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((x(lo) - 0.7, 0.07), x(value) - x(lo) + 0.7, 0.16, fc=ACCENT, ec="none", zorder=3))
    ax.add_patch(Rectangle((x(lo) - 0.7, 0.07), 8.0 + 0.9, 0.16, fc="none", ec=INK, lw=0.9, zorder=3))
    for k in range(L * minor + 1):
        v = lo + k / minor
        major = k % minor == 0
        half = k % (minor // 2) == 0
        h = 0.32 if major else (0.24 if half else 0.15)
        ax.plot([x(v), x(v)], [-0.05, -0.05 - h], color=INK, lw=1.4 if major else 0.8)
        if major:
            ax.text(x(v), -0.48, _num(v), ha="center", va="top", fontsize=FONT - 1)
    if mark is not None:
        ax.add_patch(Polygon([(x(mark) - 0.09, 0.62), (x(mark) + 0.09, 0.62), (x(mark), 0.42)], fc="#dc2626"))
    ax.text(x(hi) + 0.65, -0.48, "°C", ha="center", va="top", fontsize=FONT - 1)
    ax.set_xlim(x(lo) - 1.6, x(hi) + 1.4)
    ax.set_ylim(-1.2, 1.0)
    return fig, ax


def dynamometer(ax, x0, top, hi, step, minor, length, label, value=0):
    """Вертикальный школьный динамометр на ax: шкала 0…hi Н длиной length, ограничитель сразу под шкалой.
    Возвращает y ограничителя."""
    w = 1.9
    z = top - 1.3                        # ноль шкалы
    stop_y = z - length - 0.3
    bottom = stop_y - 0.55
    ax.add_patch(FancyBboxPatch((x0 - w / 2, bottom), w, top - bottom, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="#f8fafc", ec=INK, lw=LW))
    ax.add_patch(Rectangle((x0 - 0.12, top), 0.24, 0.35, fc="white", ec=INK, lw=1.4))   # подвес
    sx = x0 - 0.35                      # ось пружины и указателя
    n = 10
    ys = [top - 0.1 - i * (1.0 / n) for i in range(n + 1)]
    xs = [sx + (0.17 if i % 2 else -0.17) for i in range(n + 1)]
    xs[0] = xs[-1] = sx
    ax.plot([x0, sx], [top, top - 0.1], color=INK, lw=1.2)
    ax.plot(xs, ys, color=INK, lw=1.4)
    yv = z - value / hi * length
    ax.plot([sx, sx], [ys[-1], yv], color=INK, lw=1.2)
    ax.add_patch(Polygon([(sx - 0.2, yv + 0.06), (sx + 0.32, yv + 0.06), (sx + 0.32, yv - 0.06), (sx - 0.2, yv - 0.06)],
                         fc=ACCENT, ec=INK, lw=0.8, zorder=4))
    k_total = round(hi / step * minor)
    for k in range(k_total + 1):
        v = k * step / minor
        y = z - v / hi * length
        major = k % minor == 0
        L = 0.24 if major else 0.13
        ax.plot([x0 + 0.05, x0 + 0.05 + L], [y, y], color=INK, lw=1.3 if major else 0.8)
        if major:
            ax.text(x0 + 0.36, y, _num(v), ha="left", va="center", fontsize=FONT - 4)
    ax.text(x0 + 0.5, top - 0.55, label, ha="center", va="center", fontsize=FONT - 3, fontweight="bold")
    # ограничитель — планка под последним делением, стержень с крючком проходит через неё
    ax.add_patch(Rectangle((sx - 0.4, stop_y - 0.09), 0.8, 0.18, fc=INK, ec=INK, zorder=4))
    hook_top = bottom - 0.45
    ax.plot([sx, sx], [yv, hook_top], color=INK, lw=1.2)
    ax.add_patch(Arc((sx + 0.15, hook_top), 0.3, 0.3, theta1=180, theta2=360, color=INK, lw=1.6))
    ax.plot([sx + 0.3, sx + 0.3], [hook_top, hook_top + 0.12], color=INK, lw=1.6)
    return stop_y
