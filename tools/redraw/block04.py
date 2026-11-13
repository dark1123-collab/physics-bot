"""Блок 4: ЕГЭ №13–20. Результат — tools/redraw/preview/ (имена как в images/)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle  # noqa: E402
from style import (ACCENT, FILL, FONT, GRID, INK, LW, MUTED, Circuit, Plot, _arc_scale, _num, badge,  # noqa: E402
                   block, canvas, dial_meter, dynamometer, hatch, save, vec)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")
OIL = "#fde68a"      # масло / керосин
SOUTH = "#fecaca"    # южный полюс магнита


def out(name):
    return os.path.join(OUT, name + ".png")


def rng(a, b, s):
    n = round((b - a) / s)
    return [round(a + i * s, 6) for i in range(n + 1)]


def circ_on(ax):
    """Circuit поверх готовых осей (для составных рисунков)."""
    c = Circuit.__new__(Circuit)
    c.ax, c.fig = ax, ax.figure
    ax.set_aspect("equal")
    ax.axis("off")
    return c


def wire(ax, *pts, color=INK, lw=LW, ls="-"):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=1)


def dot(ax, x, y, r=0.07, color=INK):
    ax.add_patch(Circle((x, y), r, fc=color, ec=color, zorder=5))


def arrow(ax, p1, p2, color=INK, lw=1.6, ms=16, style="-|>"):
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle=style, color=color, lw=lw, mutation_scale=ms,
                                                      shrinkA=0, shrinkB=0), zorder=5)


def ray(ax, p1, p2, frac=0.55, end_arrow=False):
    """Луч света: линия со стрелкой посередине (или на конце)."""
    wire(ax, p1, p2, color=ACCENT, lw=LW + 0.4)
    if end_arrow:
        arrow(ax, p1, p2, color=ACCENT, lw=0, ms=22)
    else:
        m = (p1[0] + (p2[0] - p1[0]) * frac, p1[1] + (p2[1] - p1[1]) * frac)
        e = (m[0] + (p2[0] - p1[0]) * 0.01, m[1] + (p2[1] - p1[1]) * 0.01)
        arrow(ax, m, e, color=ACCENT, lw=0, ms=22)


def coil_h(ax, x1, x2, y, n=5):
    w = (x2 - x1) / n
    for i in range(n):
        ax.add_patch(Arc((x1 + w * (i + 0.5), y), w, w * 1.5, theta1=0, theta2=180, color=INK, lw=LW))


def coil_v(ax, x, y1, y2, n=5):
    h = (y2 - y1) / n
    for i in range(n):
        ax.add_patch(Arc((x, y1 + h * (i + 0.5)), h * 1.5, h, theta1=90, theta2=270, color=INK, lw=LW))


def cap_h(ax, x, y, h=0.7, gap=0.18, label=None, dy=0.45):
    """Конденсатор в горизонтальном проводе (пластины вертикальны). Провод подводить к x ± gap/2."""
    for dx in (-gap / 2, gap / 2):
        ax.plot([x + dx] * 2, [y - h / 2, y + h / 2], color=INK, lw=LW + 0.8, zorder=3)
    if label:
        ax.text(x + 0.12, y + dy, label, ha="left", va="bottom", fontsize=FONT + 1, style="italic")


def cap_v(ax, x, y, w=0.7, gap=0.18, label=None):
    """Конденсатор в вертикальном проводе (пластины горизонтальны). Провод подводить к y ± gap/2."""
    for dy in (-gap / 2, gap / 2):
        ax.plot([x - w / 2, x + w / 2], [y + dy] * 2, color=INK, lw=LW + 0.8, zorder=3)
    if label:
        ax.text(x + w / 2 + 0.1, y + 0.05, label, ha="left", va="bottom", fontsize=FONT + 1, style="italic")


def rheo_arrow(ax, x, y_from, y_to):
    """Ползунок реостата — стрелка к корпусу."""
    arrow(ax, (x, y_from), (x, y_to), lw=1.6, ms=16)


def finish(fig, ax, name, xlim=None, ylim=None):
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    save(fig, out(name))


# ═════════════ ЕГЭ №13 ═════════════

# Ток в катушке: I = 5 sin(2πt/4) мА, нули в 0, 2, 4, 6 мкс
p = Plot((0, 6.5), (-7.5, 7.5), size=(7.4, 4.4), grid_x=rng(0, 6.5, 0.5), grid_y=rng(-7.5, 7.5, 2.5))
p.axes("t, мкс", "I, мА", yneg=-7.5)
p.xticks([1, 2, 3, 4, 5, 6])
p.yticks([-5, 5], ["−5", "5"])
p.curve(lambda t: 5 * math.sin(2 * math.pi * t / 4), 0, 6)
p.finish(out("t13_I_t"))

# Зеркало, угол между лучами 44°, γ — между падающим лучом и зеркалом
fig, ax = canvas((5.6, 4.6))
hatch(ax, -3.2, 3.2, 0)
wire(ax, (0, 0), (0, 4.3), color=MUTED, lw=1.3, ls=(0, (5, 4)))
L, a = 4.6, math.radians(22)
ray(ax, (-L * math.sin(a), L * math.cos(a)), (0, 0))
ray(ax, (0, 0), (L * math.sin(a), L * math.cos(a)), end_arrow=True)
ax.add_patch(Arc((0, 0), 4.4, 4.4, theta1=68, theta2=112, color=INK, lw=1.4))
ax.text(0.12, 2.42, "44°", ha="left", va="bottom", fontsize=FONT)
ax.add_patch(Arc((0, 0), 1.6, 1.6, theta1=112, theta2=180, color=INK, lw=1.4))
ax.text(-1.05 * math.cos(math.radians(36)), 1.05 * math.sin(math.radians(36)) + 0.02, "γ", ha="center",
        va="center", fontsize=FONT + 2)
finish(fig, ax, "t13_mirror_44", (-3.4, 3.4), (-0.4, 4.6))

# Поворот зеркала на 15° (по часовой стрелке), падение под 30°
fig, ax = canvas((6.2, 4.6))
hatch(ax, -3.0, 3.0, 0)
t = math.radians(-15)
wire(ax, (-3.6 * math.cos(t), -3.6 * math.sin(t)), (3.6 * math.cos(t), 3.6 * math.sin(t)), lw=1.4,
     ls=(0, (6, 4)))
ax.add_patch(Arc((0, 0), 6.4, 6.4, theta1=-15, theta2=0, color=INK, lw=1.4))
ax.text(3.35, -0.45, "15°", ha="left", va="center", fontsize=FONT)
wire(ax, (0, 0), (0, 4.4), color=MUTED, lw=1.3, ls=(0, (5, 4)))
L, a = 4.6, math.radians(30)
ray(ax, (-L * math.sin(a), L * math.cos(a)), (0, 0))
ray(ax, (0, 0), (L * math.sin(a), L * math.cos(a)), end_arrow=True)
ax.add_patch(Arc((0, 0), 4.6, 4.6, theta1=90, theta2=120, color=INK, lw=1.4))
ax.text(-0.62, 2.45, "30°", ha="center", va="bottom", fontsize=FONT)
ax.add_patch(Arc((0, 0), 2.2, 2.2, theta1=60, theta2=120, color=INK, lw=1.4))
ax.text(0.3, 1.2, "γ", ha="left", va="bottom", fontsize=FONT + 2)
finish(fig, ax, "t13_mirror_rotate", (-3.8, 4.4), (-1.3, 4.6))


def lens(ax, h, k=1.0):
    """Собирающая линза (стрелки наружу) высотой 2h, оптическая ось, F и 2F с обеих сторон (F = k)."""
    arrow(ax, (0, 0), (0, h), lw=2.2, ms=18)
    arrow(ax, (0, 0), (0, -h), lw=2.2, ms=18)
    for s in (-1, 1):
        for m, name in ((1, "F"), (2, "2F")):
            x = s * m * k
            ax.plot([x, x], [-0.07, 0.07], color=INK, lw=1.6)
            ax.text(x, -0.12, name, ha="center", va="top", fontsize=FONT - 1, style="italic")


# Точка S за 2F (x = 3F, h); изображение — точка 4 (1,5F; −h/2); 3 — на 2F; 1 — на отрезке S–O; 2 — на «зеркальной» прямой
K = 1.3
fig, ax = canvas((7.2, 3.8))
wire(ax, (-3.6 * K, 0), (3.8 * K, 0), lw=1.6)
lens(ax, 1.7, K)
h = 1.0
sl = h / 3                                    # наклон прямой S–O (в единицах F)
wire(ax, (-2.8 * K, -2.8 * sl * K), (3.25 * K, 3.25 * sl * K), color=ACCENT, lw=1.4, ls=(0, (5, 4)))
wire(ax, (-2.8 * K, 2.8 * sl * K), (3.25 * K, -3.25 * sl * K), color=ACCENT, lw=1.4, ls=(0, (5, 4)))
pts = {"S": (3, 1.0), "1": (0.6, 0.2), "2": (-1.0, 1 / 3), "3": (-2.0, -2 / 3), "4": (-1.5, -0.5)}
for nm, (x, y) in pts.items():
    ax.plot(x * K, y * K, "o", color=INK if nm == "S" else ACCENT, ms=8 if nm == "S" else 7, zorder=6)
lab = {"S": (0.12, 0.12, "left", "bottom"), "1": (0.05, 0.14, "left", "bottom"), "2": (0, 0.16, "center", "bottom"),
       "3": (-0.05, -0.14, "right", "top"), "4": (0.08, -0.14, "left", "top")}
for nm, (dx, dy, ha, va) in lab.items():
    x, y = pts[nm]
    ax.text(x * K + dx, y * K + dy, nm, ha=ha, va=va, fontsize=FONT + (2 if nm == "S" else 0),
            style="italic" if nm == "S" else "normal", fontweight="normal" if nm == "S" else "bold")
finish(fig, ax, "t13_lens_point", (-3.9 * K, 4.0 * K), (-1.95, 1.95))

# Изображение AB (x = 2,8F, h = 1) → предмет 2 (x = −1,556F, вниз на 0,556); 3 — длиннее; 1 — вверх; 4 — справа
K = 1.25
fig, ax = canvas((7.6, 3.9))
wire(ax, (-3.5 * K, 0), (3.5 * K, 0), lw=1.6)
lens(ax, 1.75, K)
for s in (1, -1):
    wire(ax, (-3.3 * K, -s * 3.3 / 2.8 * K), (3.3 * K, s * 3.3 / 2.8 * K), lw=1.3, ls=(0, (5, 4)))
xo = -1.0 / (1 - 1 / 2.8) * K                  # −1,556F
objs = [("1", xo, 0.5556), ("3", xo, -1.0), ("2", xo, -0.5556), ("4", 1.5 * K, -1.5 / 2.8)]
for nm, x, y in objs:
    arrow(ax, (x, 0), (x, y * K), color=ACCENT, lw=2.4, ms=18)
ax.text(xo + 0.14, 0.5556 * K + 0.02, "1", ha="left", va="bottom", fontsize=FONT, fontweight="bold")
ax.text(xo + 0.14, -0.5556 * K - 0.04, "2", ha="left", va="top", fontsize=FONT, fontweight="bold")
ax.text(xo + 0.14, -1.0 * K - 0.02, "3", ha="left", va="top", fontsize=FONT, fontweight="bold")
ax.text(1.5 * K + 0.12, -1.5 / 2.8 * K - 0.05, "4", ha="left", va="top", fontsize=FONT, fontweight="bold")
arrow(ax, (2.8 * K, 0), (2.8 * K, 1.0 * K), color=INK, lw=2.4, ms=18)
ax.text(2.8 * K + 0.14, 0.12, "A", ha="left", va="bottom", fontsize=FONT + 1, style="italic")
ax.text(2.8 * K + 0.14, 1.0 * K - 0.08, "B", ha="left", va="top", fontsize=FONT + 1, style="italic")
finish(fig, ax, "t13_lens_object", (-3.7 * K, 3.7 * K), (-2.0, 2.0))

# Ключ К: положение 1 — катушка L, положение 2 — катушка Lx
fig, ax = canvas((5.4, 3.8))
c = circ_on(ax)
c.wire((0, 1.6), (0, 0), (1.3, 0))
cap_h(ax, 1.4, 0)
ax.text(1.4, -0.45, "C", ha="center", va="top", fontsize=FONT + 1, style="italic")
c.wire((1.5, 0), (4.0, 0), (4.0, 1.5))
c.wire((0, 1.6), (0.3, 1.6))
dot(ax, 0.3, 1.6)
ax.text(0.3, 1.78, "К", ha="center", va="bottom", fontsize=FONT)
c.wire((0.3, 1.6), (1.05, 1.08))               # нож ключа — в положении 1
dot(ax, 1.1, 1.05)
dot(ax, 1.1, 2.45)
ax.text(1.1, 0.8, "1", ha="center", va="top", fontsize=FONT)
ax.text(1.1, 2.65, "2", ha="center", va="bottom", fontsize=FONT)
c.wire((1.1, 1.05), (1.6, 1.05))
coil_h(ax, 1.6, 3.3, 1.05)
ax.text(2.45, 1.62, "L", ha="center", va="bottom", fontsize=FONT + 1, style="italic")
c.wire((3.3, 1.05), (3.6, 1.05))
c.wire((1.1, 2.45), (1.6, 2.45))
coil_h(ax, 1.6, 3.3, 2.45)
ax.text(2.45, 3.1, "$L_x$", ha="center", va="bottom", fontsize=FONT + 2)
c.wire((3.3, 2.45), (3.6, 2.45), (3.6, 1.05))
c.wire((3.6, 1.5), (4.0, 1.5))
dot(ax, 3.6, 1.5)
finish(fig, ax, "t13_key_Lx", (-0.4, 4.4), (-1.0, 3.7))

# Катушка L; ключ К: положение 1 — конденсатор C, положение 2 — 4C
fig, ax = canvas((5.0, 4.0))
c = circ_on(ax)
c.wire((0, 0), (0, 0.7))
coil_v(ax, 0, 0.7, 2.3)
c.wire((0, 2.3), (0, 3.0), (2.8, 3.0))
dot(ax, 1.4, 3.0)
for x, lb in ((1.4, "C"), (2.8, "4C")):
    c.wire((x, 3.0), (x, 2.29))
    cap_v(ax, x, 2.2, label=lb)
    c.wire((x, 2.11), (x, 1.35))
    dot(ax, x, 1.35)
ax.text(1.18, 1.35, "1", ha="right", va="center", fontsize=FONT)
ax.text(3.02, 1.35, "2", ha="left", va="center", fontsize=FONT)
dot(ax, 2.1, 0.55)
c.wire((2.1, 0.55), (1.45, 1.3))               # нож ключа — в положении 1
ax.text(2.3, 0.75, "К", ha="left", va="center", fontsize=FONT)
c.wire((2.1, 0.55), (2.1, 0), (0, 0))
ax.text(-0.45, 1.5, "L", ha="right", va="center", fontsize=FONT + 1, style="italic")
finish(fig, ax, "t13_key_4c", (-1.0, 3.8), (-0.4, 3.4))


# ═════════════ ЕГЭ №14 ═════════════

def dim(ax, p1, p2, label, side=(0, 0.18), ha="center", va="bottom", color=ACCENT):
    """Размерная стрелка с подписью."""
    arrow(ax, p1, p2, color=color, lw=1.4, ms=12, style="<|-|>")
    m = ((p1[0] + p2[0]) / 2 + side[0], (p1[1] + p2[1]) / 2 + side[1])
    ax.text(*m, label, ha=ha, va=va, fontsize=FONT, color=INK, style="italic")


# Сфера радиуса R: B (R/2 от центра), D (на сфере), A (2R), F (на сфере снизу), C (2R снизу)
fig, ax = canvas((5.6, 5.4))
R = 2.0
ax.add_patch(Circle((0, 0), R, fc="#f8fafc", ec=INK, lw=LW))
P = {"B": (-1.0, 0), "O": (0, 0), "D": (2.0, 0), "A": (4.0, 0), "F": (0, -2.0), "C": (0, -4.0)}
for nm, q in P.items():
    dot(ax, *q, r=0.07)
dim(ax, (-1.0, 0), (0, 0), "R/2")
dim(ax, (0, 0), (2.0, 0), "R")
dim(ax, (2.0, 0), (4.0, 0), "R")
dim(ax, (0, 0), (0, -2.0), "R", side=(-0.15, 0), ha="right", va="center")
dim(ax, (0, -2.0), (0, -4.0), "R", side=(-0.15, 0), ha="right", va="center")
for nm, (dx, dy, ha, va) in {"B": (-0.05, -0.15, "center", "top"), "D": (0.12, -0.15, "left", "top"),
                             "A": (0.12, 0.1, "left", "bottom"), "F": (0.15, -0.12, "left", "top"),
                             "C": (0.15, -0.05, "left", "top")}.items():
    ax.text(P[nm][0] + dx, P[nm][1] + dy, nm, ha=ha, va=va, fontsize=FONT + 1, style="italic")
finish(fig, ax, "t14_sphere", (-2.4, 4.6), (-4.5, 2.3))

# Пластина внизу, линии напряжённости вниз; A и B на одной высоте, C выше
fig, ax = canvas((4.2, 4.4))
ax.add_patch(Rectangle((-1.9, -0.18), 3.8, 0.18, fc=MUTED, ec=INK, lw=1.4))
for x in (-1.2, -0.4, 0.4, 1.2):
    wire(ax, (x, 3.2), (x, 0), color=ACCENT, lw=1.8)
    arrow(ax, (x, 2.7), (x, 2.6), color=ACCENT, lw=0, ms=18)
ax.text(1.4, 3.05, "$\\vec{E}$", ha="left", va="center", fontsize=FONT + 3)
A_, B_, C_ = (-1.2, 0.9), (1.2, 0.9), (0, 2.1)
wire(ax, A_, B_, C_, A_, lw=1.2, ls=(0, (4, 3)))
for q in (A_, B_, C_):
    dot(ax, *q, r=0.07)
ax.text(A_[0] - 0.12, A_[1], "A", ha="right", va="center", fontsize=FONT + 1, style="italic",
        bbox=dict(fc="white", ec="none", pad=0.5))
ax.text(B_[0] + 0.12, B_[1], "B", ha="left", va="center", fontsize=FONT + 1, style="italic",
        bbox=dict(fc="white", ec="none", pad=0.5))
ax.text(C_[0] + 0.1, C_[1] + 0.12, "C", ha="left", va="bottom", fontsize=FONT + 1, style="italic",
        bbox=dict(fc="white", ec="none", pad=0.5))
finish(fig, ax, "t14_plate_field", (-2.1, 2.1), (-0.4, 3.5))

# Кольцо №1 (с выводами снизу), внутри — кольцо №2; цепь: реостат (левый вывод + ползунок) и источник «+ слева»
fig, ax = canvas((5.4, 4.6))
cy, R1, R2 = 2.6, 1.15, 0.68
ax.add_patch(Arc((0, cy), 2 * R1, 2 * R1, theta1=-70, theta2=250, color=INK, lw=LW + 0.4))
ax.add_patch(Circle((0, cy), R2, fc="none", ec=INK, lw=LW + 0.4))
xl = R1 * math.cos(math.radians(250))
yl = cy + R1 * math.sin(math.radians(250))
ax.text(-R1 - 0.12, cy + 0.6, "№1", ha="right", va="center", fontsize=FONT)
ax.text(0, cy, "№2", ha="center", va="center", fontsize=FONT)
c = circ_on(ax)
c.wire((xl, yl), (xl, 1.15), (-2.2, 1.15), (-2.2, 0), (-1.85, 0))
c.resistor(-1.2, 0)
c.wire((-1.2, 0.75), (0.25, 0.75), (0.25, 0), (0.52, 0))
rheo_arrow(ax, -1.2, 0.75, 0.21)
c.battery(0.6, 0)
ax.text(0.38, -0.3, "+", ha="center", va="top", fontsize=FONT + 1)
ax.text(0.85, -0.3, "−", ha="center", va="top", fontsize=FONT + 1)
c.wire((0.68, 0), (2.2, 0), (2.2, 1.15), (-xl, 1.15), (-xl, yl))
finish(fig, ax, "t14_coils_rheostat", (-2.6, 2.6), (-0.8, 4.0))


def magnet(ax, x, y, left, right, w=1.1, h=0.75):
    """Полосовой магнит из двух половин; подписи полюсов."""
    for i, nm in enumerate((left, right)):
        ax.add_patch(Rectangle((x + i * w, y), w, h, fc=FILL if nm == "N" else SOUTH, ec=INK, lw=LW, zorder=3))
        ax.text(x + i * w + w / 2, y + h / 2, nm, ha="center", va="center", fontsize=FONT + 2, style="italic",
                zorder=4)


# Магнит 1 (N|S) отодвигают влево от деревянного кольца №1; магнит 2 (S|N) — от медного кольца №2
fig, ax = canvas((8.4, 2.9))
for x0, (lp, rp), nm in ((0, ("N", "S"), "№ 1"), (4.6, ("S", "N"), "№ 2")):
    magnet(ax, x0, 0, lp, rp)
    ax.add_patch(Ellipse((x0 + 3.0, 0.375), 0.42, 1.7, fc="none", ec=INK, lw=LW + 1.2))
    ax.text(x0 + 3.3, 1.25, nm, ha="left", va="bottom", fontsize=FONT)
    arrow(ax, (x0 + 1.5, -0.4), (x0 + 0.5, -0.4), lw=1.8, ms=18)
finish(fig, ax, "t14_rings_magnet", (-0.3, 8.6), (-0.8, 1.7))

# Бусинки: A (+3q) — C (середина) — B (−1,5q)
fig, ax = canvas((5.2, 1.6))
wire(ax, (0, 0), (4.4, 0), lw=1.3, ls=(0, (5, 4)))
ax.add_patch(Circle((0, 0), 0.14, fc=ACCENT, ec=INK, lw=1.4, zorder=4))
ax.add_patch(Circle((4.4, 0), 0.14, fc=ACCENT, ec=INK, lw=1.4, zorder=4))
dot(ax, 2.2, 0)
ax.text(0, 0.3, "$+3q$", ha="center", va="bottom", fontsize=FONT + 1)
ax.text(4.4, 0.3, "$-1{,}5q$", ha="center", va="bottom", fontsize=FONT + 1)
for x, nm in ((0, "A"), (2.2, "C"), (4.4, "B")):
    ax.text(x, -0.3, nm, ha="center", va="top", fontsize=FONT + 1, style="italic")
finish(fig, ax, "t14_beads", (-0.6, 5.0), (-0.85, 0.85))

# Таблица q(t)
fig, ax = canvas((9.6, 1.4))
ts = list(range(10))
qs = ["1", "0,71", "0", "−0,71", "−1", "−0,71", "0", "0,71", "1", "0,71"]
w0, w, hh = 2.1, 0.78, 0.6
for r, (head, vals) in enumerate((("t, 10⁻⁶ с", [str(t) for t in ts]), ("q, 10⁻⁹ Кл", qs))):
    y = -r * hh
    ax.add_patch(Rectangle((0, y), w0, hh, fc=FILL, ec=INK, lw=1.4))
    ax.text(w0 / 2, y + hh / 2, head, ha="center", va="center", fontsize=FONT - 1)
    for i, v in enumerate(vals):
        ax.add_patch(Rectangle((w0 + i * w, y), w, hh, fc="white", ec=INK, lw=1.4))
        ax.text(w0 + i * w + w / 2, y + hh / 2, v, ha="center", va="center", fontsize=FONT - 2)
finish(fig, ax, "t14_lc_table", (-0.1, w0 + 10 * w + 0.1), (-hh - 0.1, hh + 0.1))

# Рис. 1: источник, амперметр, реостат (левый конец + ползунок), вольтметр на реостате. Рис. 2: U(I)
p = Plot((0, 13), (0, 12), size=(11.0, 4.6), grid_x=rng(0, 13, 1), grid_y=rng(0, 12, 1))
p.ax.set_position([0.42, 0.1, 0.56, 0.85])
p.axes("I, А", "U, В")
p.xticks([5, 10])
p.yticks([5, 10])
p.line([(2, 10), (12, 0)])
p.line([(2, 5), (12, 0)])
badge(p.ax, 7.6, 6.5, "1")
badge(p.ax, 4.6, 5.3, "2")
p.text(6.5, -2.2, "Рис. 2", ha="center", va="top", fontweight="bold")
ax1 = p.fig.add_axes([0.0, 0.12, 0.36, 0.8])
c = circ_on(ax1)
c.wire((0, 0), (0, 3.0), (0.68, 3.0))
c.meter(1.0, 3.0, "V")
c.wire((1.32, 3.0), (2.0, 3.0), (2.0, 1.52))
c.meter(2.0, 1.2, "A")
c.wire((2.0, 0.88), (2.0, 0), (1.08, 0))
c.battery(1.0, 0)
c.wire((0.92, 0), (0, 0))
dot(ax1, 0, 1.9)
c.wire((0, 1.9), (0.4, 1.9))
c.resistor(1.0, 1.9, w=1.2)
c.wire((1.2, 2.45), (2.0, 2.45))
dot(ax1, 2.0, 2.45)
rheo_arrow(ax1, 1.2, 2.45, 2.11)
ax1.text(1.0, -0.6, "Рис. 1", ha="center", va="top", fontsize=FONT, fontweight="bold")
ax1.set_xlim(-0.6, 2.6)
ax1.set_ylim(-1.2, 3.6)
p.finish(out("t14_emf_graphs"))

# Проводник АБ на проволочках, источник (+ к А), реостат (левый конец + ползунок), магнит N справа от проводника
fig, ax = canvas((6.2, 5.4))
A_, B_ = (0, 0), (2.4, 1.4)
PA, PB = (0, 3.0), (2.4, 4.4)
sup = ((-0.5, 2.71), (2.9, 4.69))
wire(ax, *sup, lw=LW)
for i in range(15):
    t = i / 14
    x = sup[0][0] + (sup[1][0] - sup[0][0]) * t
    y = sup[0][1] + (sup[1][1] - sup[0][1]) * t
    wire(ax, (x, y), (x + 0.12, y + 0.22), lw=1.1)
wire(ax, PA, A_, lw=1.3)
wire(ax, PB, (2.4, 3.12), lw=1.3)
wire(ax, (2.4, 2.88), B_, lw=1.3)
dot(ax, *PA)
dot(ax, *PB)
ax.plot([A_[0], B_[0]], [A_[1], B_[1]], color=INK, lw=6, solid_capstyle="round", zorder=4)
ax.plot([A_[0], B_[0]], [A_[1], B_[1]], color="#e5e7eb", lw=3.6, solid_capstyle="round", zorder=5)
ax.text(A_[0] - 0.15, A_[1] - 0.1, "А", ha="right", va="top", fontsize=FONT + 1)
ax.text(B_[0] - 0.1, B_[1] + 0.12, "Б", ha="right", va="bottom", fontsize=FONT + 1)
c = circ_on(ax)
c.wire(PA, (3.82, 3.0))
c.battery(3.9, 3.0)
ax.text(3.75, 3.45, "+", ha="center", va="bottom", fontsize=FONT + 1)
ax.text(4.08, 3.45, "−", ha="center", va="bottom", fontsize=FONT + 1)
c.wire((3.98, 3.0), (4.9, 3.0), (4.9, 4.95), (3.6, 4.95))
c.wire(PB, (3.0, 4.4))
c.resistor(3.6, 4.4, w=1.2)
rheo_arrow(ax, 3.6, 4.95, 4.61)
# магнит: передняя грань N|S, верх и бок в косоугольной проекции
mx, my, mw, mh, d = 2.0, -0.95, 1.1, 0.8, (0.45, 0.28)
magnet(ax, mx, my, "N", "S", w=mw, h=mh)
for i, fc in enumerate((FILL, SOUTH)):
    x1 = mx + i * mw
    ax.add_patch(Polygon([(x1, my + mh), (x1 + mw, my + mh), (x1 + mw + d[0], my + mh + d[1]),
                          (x1 + d[0], my + mh + d[1])], fc=fc, ec=INK, lw=1.6, zorder=2))
x2 = mx + 2 * mw
ax.add_patch(Polygon([(x2, my), (x2 + d[0], my + d[1]), (x2 + d[0], my + mh + d[1]), (x2, my + mh)],
                     fc=SOUTH, ec=INK, lw=1.6, zorder=2))
finish(fig, ax, "t14_conductor_magnet", (-0.9, 5.4), (-1.3, 5.3))

# Рис. а: рельсы LM и KN, проводник слева (v вправо), B — от нас, лампа MN. Рис. б: S(t)
p = Plot((0, 14), (0, 800), size=(11.4, 4.6), grid_x=rng(0, 14, 2), grid_y=rng(0, 800, 100))
p.ax.set_position([0.5, 0.1, 0.48, 0.85])
p.axes("t, с", "S, см²")
p.xticks([2, 4, 6, 8, 10, 12, 14])
p.yticks([200, 400, 600, 800])
p.line([(0, 800), (4, 800), (8, 400), (14, 100)])
p.text(7, -150, "Рис. б", ha="center", va="top", fontweight="bold")
ax1 = p.fig.add_axes([0.0, 0.12, 0.45, 0.8])
ax1.set_aspect("equal")
ax1.axis("off")
for y in (0, 2.0):
    ax1.plot([0, 6.2], [y, y], color=INK, lw=5, solid_capstyle="butt")
wire(ax1, (0.8, -0.35), (0.8, 2.35), lw=LW)
ax1.text(0.65, 2.15, "L", ha="right", va="bottom", fontsize=FONT + 1, style="italic")
ax1.text(0.65, -0.15, "K", ha="right", va="top", fontsize=FONT + 1, style="italic")
vec(ax1, 0.8, 1.35, 1.9, 1.35)
ax1.text(1.35, 1.5, "$\\vec{v}$", ha="center", va="bottom", fontsize=FONT + 2)
ax1.add_patch(Circle((3.0, 0.9), 0.25, fc="white", ec=INK, lw=1.6))
ax1.plot([2.83, 3.17], [0.73, 1.07], color=INK, lw=1.6)
ax1.plot([2.83, 3.17], [1.07, 0.73], color=INK, lw=1.6)
ax1.text(3.35, 0.9, "$\\vec{B}$", ha="left", va="center", fontsize=FONT + 2)
wire(ax1, (5.3, 0), (5.3, 0.62))
wire(ax1, (5.3, 1.38), (5.3, 2.0))
ax1.add_patch(Circle((5.3, 1.0), 0.38, fc="#fef9c3", ec=INK, lw=LW, zorder=3))
for s in (1, -1):
    ax1.plot([5.3 - 0.27, 5.3 + 0.27], [1.0 - s * 0.27, 1.0 + s * 0.27], color=INK, lw=1.6, zorder=4)
ax1.text(5.45, 2.15, "M", ha="left", va="bottom", fontsize=FONT + 1, style="italic")
ax1.text(5.45, -0.15, "N", ha="left", va="top", fontsize=FONT + 1, style="italic")
ax1.text(3.1, -0.75, "Рис. а", ha="center", va="top", fontsize=FONT, fontweight="bold")
ax1.set_xlim(-0.2, 6.4)
ax1.set_ylim(-1.4, 2.9)
p.finish(out("t14_rails_lamp"))

# ℰ слева; R₁ сверху; R₃ ∥ R₂ (вертикальные, R₃ ближе); R₄ снизу
c = Circuit(size=(5.4, 3.8))
c.battery(0, 1.2, vertical=True)
c.ax.text(-0.45, 1.25, "ℰ", ha="right", va="center", fontsize=FONT + 3)
c.wire((0, 1.28), (0, 2.4))
c.resistor_on(0, 2.6, 2.4, "$R_1$")
c.resistor_on(0, 2.6, 0, "$R_4$", label_side=-1)
c.wire((0, 0), (0, 1.12))
c.wire((2.6, 2.4), (3.8, 2.4), (3.8, 1.85))
c.wire((2.6, 2.4), (2.6, 1.85))
c.wire((2.6, 0), (3.8, 0), (3.8, 0.55))
c.wire((2.6, 0), (2.6, 0.55))
c.resistor(2.6, 1.2, "$R_3$", vertical=True, label_side=-1)
c.resistor(3.8, 1.2, "$R_2$", vertical=True)
c.node(2.6, 2.4)
c.node(2.6, 0)
c.save(out("t14_resistors"))

# Пластины на расстоянии d (рис. 1) и d/2 (рис. 2), подключены к клеммам «−» и «+»
fig, ax = canvas((7.4, 3.6))
for x0, gap, lb, cap in ((0, 1.6, "d", "Рис. 1"), (4.4, 0.8, "d/2", "Рис. 2")):
    xl, xr = x0 + 1.0 - gap / 2, x0 + 1.0 + gap / 2
    for x in (xl, xr):
        ax.plot([x, x], [0.9, 3.0], color=INK, lw=4, solid_capstyle="butt", zorder=3)
    wire(ax, (xl, 1.95), (x0 - 0.2, 1.95), (x0 - 0.2, 0), (x0 + 0.62, 0))
    wire(ax, (xr, 1.95), (x0 + 2.2, 1.95), (x0 + 2.2, 0), (x0 + 1.38, 0))
    for x, s in ((x0 + 0.72, "−"), (x0 + 1.28, "+")):
        ax.add_patch(Circle((x, 0), 0.1, fc="white", ec=INK, lw=1.6, zorder=4))
        ax.text(x, 0.18, s, ha="center", va="bottom", fontsize=FONT + 1)
    arrow(ax, (xl, 3.3), (xr, 3.3), color=MUTED, lw=1.3, ms=12, style="<|-|>")
    for x in (xl, xr):
        wire(ax, (x, 3.05), (x, 3.45), color=MUTED, lw=1.0)
    ax.text(x0 + 1.0, 3.42, lb, ha="center", va="bottom", fontsize=FONT, style="italic")
    ax.text(x0 + 1.0, -0.35, cap, ha="center", va="top", fontsize=FONT, fontweight="bold")
finish(fig, ax, "t14_capacitor_plates", (-0.6, 7.0), (-0.9, 4.0))


# ═════════════ ЕГЭ №15 ═════════════

# Свет: воздух → глицерин, α > β
fig, ax = canvas((4.8, 4.6))
ax.add_patch(Rectangle((-2.2, -2.4), 4.4, 2.4, fc=FILL, ec=INK, lw=1.6))
ax.text(-2.05, 0.15, "воздух", ha="left", va="bottom", fontsize=FONT - 1, color=MUTED)
ax.text(-2.05, -2.25, "глицерин", ha="left", va="bottom", fontsize=FONT - 1, color=MUTED)
wire(ax, (0, 2.3), (0, -2.4), color=MUTED, lw=1.3, ls=(0, (5, 4)))
a, b = math.radians(38), math.asin(math.sin(math.radians(38)) / 1.47)
ray(ax, (-2.6 * math.sin(a), 2.6 * math.cos(a)), (0, 0))
ray(ax, (0, 0), (2.4 * math.sin(b), -2.4 * math.cos(b)), end_arrow=True)
ax.add_patch(Arc((0, 0), 1.8, 1.8, theta1=90, theta2=90 + 38, color=INK, lw=1.4))
ax.text(-0.38, 1.12, "α", ha="center", va="bottom", fontsize=FONT + 2)
bd = math.degrees(b)
ax.add_patch(Arc((0, 0), 2.2, 2.2, theta1=-90, theta2=-90 + bd, color=INK, lw=1.4))
ax.text(0.28, -1.32, "β", ha="left", va="top", fontsize=FONT + 2)
finish(fig, ax, "t15_light_glycerin", (-2.4, 2.4), (-2.6, 2.4))

# ℰ сверху; R₁ последовательно; R₂ ∥ реостат R₃ (ползунок снизу, к левому узлу)
c = Circuit(size=(5.8, 3.8))
c.wire((0, 1.8), (0, 3.0), (2.42, 3.0))
c.battery(2.5, 3.0)
c.ax.text(2.6, 3.42, "ℰ", ha="left", va="bottom", fontsize=FONT + 3)
c.wire((2.58, 3.0), (5.0, 3.0), (5.0, 1.8))
c.resistor_on(0, 2.6, 1.8, "$R_1$")
c.resistor_on(2.6, 5.0, 1.8, "$R_2$")
c.node(2.6, 1.8)
c.node(5.0, 1.8)
c.resistor(3.8, 0.8, "$R_3$")
c.wire((4.45, 0.8), (5.0, 0.8), (5.0, 1.8))
c.wire((2.6, 1.8), (2.6, 0.0), (3.8, 0.0))
rheo_arrow(c.ax, 3.8, 0.0, 0.59)
c.save(out("t15_rheostat_parallel"))


def lc_graph(ax, fn, letter=None, ylabel=None, tmark_dash=True):
    """Маленький график величины за период T (T = 1)."""
    ax.axis("off")
    arrow(ax, (0, 0), (1.22, 0), lw=1.5, ms=14)
    arrow(ax, (0, -1.25), (0, 1.4), lw=1.5, ms=14)
    xs = [i / 300 for i in range(301)]
    ax.plot(xs, [fn(x) for x in xs], color=ACCENT, lw=LW + 0.4, zorder=3)
    ax.text(1.22, 0.1, "t", ha="center", va="bottom", fontsize=FONT, style="italic")
    ax.plot([1, 1], [-0.06, 0.06], color=INK, lw=1.4)
    ax.text(1.03, -0.08, "T", ha="left", va="top", fontsize=FONT, style="italic")
    if tmark_dash and abs(fn(1)) > 0.15:
        ax.plot([1, 1], [0, fn(1)], color=MUTED, lw=1.1, ls=(0, (4, 3)))
    ax.text(-0.04, -0.06, "0", ha="right", va="top", fontsize=FONT - 1)
    if ylabel:
        ax.text(0.05, 1.4, ylabel, ha="left", va="center", fontsize=FONT, style="italic")
    if letter:
        badge(ax, -0.3, 1.2, letter)
    ax.set_xlim(-0.45, 1.35)
    ax.set_ylim(-1.35, 1.6)


TWO = 2 * math.pi
# Сверху I(t) = cos; А — энергия катушки (cos², период T/2); Б — напряжение (sin)
fig = plt.figure(figsize=(8.4, 5.6))
lc_graph(fig.add_axes([0.28, 0.58, 0.44, 0.4]), lambda x: math.cos(TWO * x), ylabel="I")
lc_graph(fig.add_axes([0.02, 0.05, 0.44, 0.4]), lambda x: math.cos(TWO * x) ** 2, "А")
lc_graph(fig.add_axes([0.54, 0.05, 0.44, 0.4]), lambda x: math.sin(TWO * x), "Б")
save(fig, out("t15_lc_current_graphs"))


def lc_circuit_switch(ax):
    """Источник (− слева, + справа) сверху; C в средней ветви; переключатель К: 1 — к «+», 2 — к катушке L."""
    c = circ_on(ax)
    c.wire((0, 0), (0, 3.0), (0.5, 3.0))
    c.terminal(0.6, 3.0)
    c.terminal(1.4, 3.0)
    ax.text(0.6, 3.18, "−", ha="center", va="bottom", fontsize=FONT + 1)
    ax.text(1.4, 3.18, "+", ha="center", va="bottom", fontsize=FONT + 1)
    c.wire((1.5, 3.0), (2.7, 3.0), (2.7, 2.2))
    dot(ax, 2.7, 2.2)
    dot(ax, 0, 1.6)
    c.wire((0, 1.6), (1.11, 1.6))
    cap_h(ax, 1.2, 1.6, label="C", dy=0.42)
    c.wire((1.29, 1.6), (2.1, 1.6))
    dot(ax, 2.1, 1.6)
    c.wire((2.1, 1.6), (2.66, 2.15))           # в положении 1 (до t = 0)
    ax.text(2.05, 1.85, "К", ha="right", va="bottom", fontsize=FONT)
    dot(ax, 2.7, 1.0)
    ax.text(2.9, 2.2, "1", ha="left", va="center", fontsize=FONT)
    ax.text(2.9, 1.0, "2", ha="left", va="center", fontsize=FONT)
    c.wire((2.7, 1.0), (2.7, 0), (2.1, 0))
    coil_h(ax, 0.6, 2.1, 0)
    c.wire((0.6, 0), (0, 0))
    ax.text(1.35, 0.6, "L", ha="center", va="bottom", fontsize=FONT + 1, style="italic")
    ax.set_xlim(-0.4, 3.4)
    ax.set_ylim(-0.4, 3.7)


# Сверху схема; А — энергия катушки (sin², период T/2); Б — заряд левой обкладки (−cos)
fig = plt.figure(figsize=(8.4, 6.0))
lc_circuit_switch(fig.add_axes([0.32, 0.55, 0.36, 0.43]))
lc_graph(fig.add_axes([0.02, 0.04, 0.44, 0.4]), lambda x: math.sin(TWO * x) ** 2, "А")
lc_graph(fig.add_axes([0.54, 0.04, 0.44, 0.4]), lambda x: -math.cos(TWO * x), "Б")
save(fig, out("t15_lc_switch_graphs"))

# α-частица между пластинами (+ сверху, − снизу), отклоняется к «−» на угол α
fig, ax = canvas((7.0, 3.8))
for y, s in ((1.3, "+"), (-1.3, "−")):
    ax.plot([0, 5.0], [y, y], color=INK, lw=4, solid_capstyle="butt")
    for i in range(7):
        ax.text(0.25 + i * 0.75, y + (0.12 if y > 0 else -0.12), s, ha="center",
                va="bottom" if y > 0 else "top", fontsize=FONT + 2)
ax.add_patch(Circle((-1.4, 0), 0.15, fc=ACCENT, ec=INK, lw=1.4, zorder=5))
vec(ax, -1.25, 0, -0.45, 0)
ax.text(-0.85, 0.15, "$\\vec{v}$", ha="center", va="bottom", fontsize=FONT + 2)
wire(ax, (-0.4, 0), (6.4, 0), color=MUTED, lw=1.2, ls=(0, (5, 4)))
k = 0.032
xs = [i / 100 * 5 for i in range(101)]
ax.plot(xs, [-k * x * x for x in xs], color=ACCENT, lw=LW + 0.4, zorder=4)
ye, sl = -k * 25, -2 * k * 5
ax.plot([5, 6.5], [ye, ye + sl * 1.5], color=ACCENT, lw=LW + 0.4, zorder=4)
arrow(ax, (6.3, ye + sl * 1.3), (6.5, ye + sl * 1.5), color=ACCENT, lw=0, ms=20)
wire(ax, (5, ye), (6.5, ye), color=MUTED, lw=1.2, ls=(0, (5, 4)))
ax.add_patch(Arc((5, ye), 2.4, 2.4, theta1=math.degrees(math.atan(sl)), theta2=0, color=INK, lw=1.4))
ax.text(6.3, ye - 0.15, "α", ha="left", va="center", fontsize=FONT + 2)
arrow(ax, (1.0, -1.25), (1.0, 1.25), color=MUTED, lw=1.2, ms=12, style="<|-|>")
ax.text(1.12, 0.5, "d", ha="left", va="center", fontsize=FONT + 1, style="italic", color=INK)
finish(fig, ax, "t15_alpha_capacitor", (-1.8, 7.0), (-1.9, 1.9))

# U слева; сверху — к ползунку реостата R₂ (вертикальный); нижний вывод R₂ → R₁ → U
c = Circuit(size=(4.8, 3.8))
c.wire((0, 1.8), (0, 3.0), (2.9, 3.0), (2.9, 1.6))
c.ax.annotate("", xy=(3.38, 1.6), xytext=(2.9, 1.6),
              arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=16, shrinkA=0, shrinkB=0),
              zorder=5)
c.resistor(3.6, 1.6, "$R_2$", vertical=True)
c.wire((3.6, 0.95), (3.6, 0), (2.45, 0))
c.resistor(1.8, 0, "$R_1$", label_side=-1)
c.wire((1.15, 0), (0, 0), (0, 1.0))
c.node(0, 1.8)
c.node(0, 1.0)
c.ax.text(-0.2, 1.4, "U", ha="right", va="center", fontsize=FONT + 3, style="italic")
c.save(out("t15_rheostat_series"))


def lc_circuit_key(ax):
    """Источник (+ слева, − справа) через ключ К; L в средней ветви, C внизу."""
    c = circ_on(ax)
    c.wire((0, 0), (0, 3.0), (0.5, 3.0))
    c.terminal(0.6, 3.0)
    c.terminal(1.2, 3.0)
    ax.text(0.6, 3.18, "+", ha="center", va="bottom", fontsize=FONT + 1)
    ax.text(1.2, 3.18, "−", ha="center", va="bottom", fontsize=FONT + 1)
    c.wire((1.3, 3.0), (1.6, 3.0))
    c.key(1.6, 3.0, 2.5)
    c.wire((2.5, 3.0), (2.9, 3.0), (2.9, 0), (1.54, 0))
    cap_h(ax, 1.45, 0, label="C", dy=0.42)
    c.wire((1.36, 0), (0, 0))
    dot(ax, 0, 1.6)
    dot(ax, 2.9, 1.6)
    c.wire((0, 1.6), (0.7, 1.6))
    coil_h(ax, 0.7, 2.2, 1.6)
    c.wire((2.2, 1.6), (2.9, 1.6))
    ax.text(1.45, 2.2, "L", ha="center", va="bottom", fontsize=FONT + 1, style="italic")
    ax.set_xlim(-0.4, 3.3)
    ax.set_ylim(-0.6, 3.7)


# Сверху схема; А — заряд правой обкладки (sin); Б — ток в катушке (cos)
fig = plt.figure(figsize=(8.4, 6.0))
lc_circuit_key(fig.add_axes([0.32, 0.55, 0.36, 0.43]))
lc_graph(fig.add_axes([0.02, 0.04, 0.44, 0.4]), lambda x: math.sin(TWO * x), "А")
lc_graph(fig.add_axes([0.54, 0.04, 0.44, 0.4]), lambda x: math.cos(TWO * x), "Б")
save(fig, out("t15_lc_coil_graphs"))


# ═════════════ ЕГЭ №16 ═════════════

p = Plot((0, 250), (0, 100), size=(6.4, 4.2), grid_x=rng(0, 250, 50), grid_y=rng(0, 100, 25))
p.axes("t, с", "N, 10¹⁸")
p.xticks([50, 100, 150, 200, 250])
p.yticks([25, 50, 75, 100])
p.curve(lambda t: 100 * 2 ** (-t / 50), 0, 250)
p.finish(out("t16_halflife_eu"))

p = Plot((0, 35), (0, 7), size=(6.4, 4.6), grid_x=rng(0, 35, 5), grid_y=rng(0, 7, 1))
p.axes("t, мин", "N, 10²⁰")
p.xticks([5, 10, 15, 20, 25, 30, 35])
p.yticks([1, 2, 3, 4, 5, 6, 7])
p.curve(lambda t: 6 * 2 ** (-t / 5), 0, 30)
p.finish(out("t16_halflife_ir"))

p = Plot((0, 9), (0, 10), size=(5.8, 4.8), grid_x=rng(0, 9, 1.5), grid_y=rng(0, 10, 1))
p.axes("t, мин", "N, 10²⁰")
p.xticks([1.5, 3, 4.5, 6, 7.5, 9])
p.yticks([2, 4, 6, 8, 10])
for nm, (x, y) in {"1": (1.5, 2), "2": (3, 4), "3": (4.5, 5.5), "4": (6, 7.5)}.items():
    p.point(x, y, nm, dx=0.15, dy=0.15)
p.finish(out("t16_pb_points"))

p = Plot((0, 36), (0, 10), size=(6.4, 4.8), grid_x=rng(0, 36, 6), grid_y=rng(0, 10, 1))
p.axes("t, мин", "N, 10²⁰")
p.xticks([6, 12, 18, 24, 30, 36])
p.yticks([2, 4, 6, 8, 10])
for nm, (x, y) in {"A": (0, 8), "1": (6, 5), "2": (12, 3), "3": (18, 1), "4": (30, 1)}.items():
    p.point(x, y, nm, dx=0.6, dy=0.15)
p.finish(out("t16_chromium_points"))

# Фрагмент таблицы Менделеева (периоды 2–4, группы I–III)
fig, ax = canvas((7.6, 5.2))
cw, ch, c0, c1 = 2.0, 1.25, 1.0, 0.8
rows = [
    [("Li", 3, "ЛИТИЙ", "$7_{93}\\ \\ 6_{7}$"), ("Be", 4, "БЕРИЛЛИЙ", "$9_{100}$"),
     ("B", 5, "БОР", "$11_{80}\\ \\ 10_{20}$")],
    [("Na", 11, "НАТРИЙ", "$23_{100}$"), ("Mg", 12, "МАГНИЙ", "$24_{79}\\ 26_{11}\\ 25_{10}$"),
     ("Al", 13, "АЛЮМИНИЙ", "$27_{100}$")],
    [("K", 19, "КАЛИЙ", "$39_{93}\\ \\ 41_{6{,}7}$"), ("Ca", 20, "КАЛЬЦИЙ", "$40_{97}\\ \\ 44_{2{,}1}$"),
     ("Sc", 21, "СКАНДИЙ", "$45_{100}$")],
    [("Cu", 29, "МЕДЬ", "$63_{69}\\ \\ 65_{31}$"), ("Zn", 30, "ЦИНК", "$64_{49}\\ 66_{28}\\ 68_{19}$"),
     ("Ga", 31, "ГАЛЛИЙ", "$69_{60}\\ \\ 71_{40}$")],
]
rnames = ["II", "III", "IV", "V"]
for r, row in enumerate(rows):
    y = -(r + 1) * ch
    ax.add_patch(Rectangle((c0, y), c1, ch, fc="#f8fafc", ec=INK, lw=1.6))
    ax.text(c0 + c1 / 2, y + ch / 2, rnames[r], ha="center", va="center", fontsize=FONT)
    for i, (sym, z, name, iso) in enumerate(row):
        x = c0 + c1 + i * cw
        ax.add_patch(Rectangle((x, y), cw, ch, fc="white", ec=INK, lw=1.6))
        ax.text(x + 0.12, y + ch - 0.1, sym, ha="left", va="top", fontsize=FONT + 2, fontweight="bold")
        ax.text(x + cw - 0.12, y + ch - 0.1, str(z), ha="right", va="top", fontsize=FONT)
        ax.text(x + cw / 2, y + ch * 0.47, name, ha="center", va="center", fontsize=FONT - 6)
        ax.text(x + cw / 2, y + 0.1, iso, ha="center", va="bottom", fontsize=FONT - 2)
for nm, r0, n in (("2", 0, 1), ("3", 1, 1), ("4", 2, 2)):
    y = -(r0 + n) * ch
    ax.add_patch(Rectangle((0, y), c0, n * ch, fc="#f8fafc", ec=INK, lw=1.6))
    ax.text(c0 / 2, y + n * ch / 2, nm, ha="center", va="center", fontsize=FONT + 1)
ax.text(c0 / 2, 0.1, "период", ha="center", va="bottom", fontsize=FONT - 4, color=MUTED)
ax.text(c0 + c1 / 2, 0.1, "ряд", ha="center", va="bottom", fontsize=FONT - 4, color=MUTED)
for i, g in enumerate(("I", "II", "III")):
    ax.text(c0 + c1 + i * cw + cw / 2, 0.1, g + " группа", ha="center", va="bottom", fontsize=FONT - 4,
            color=MUTED)
finish(fig, ax, "t16_mendeleev", (-0.1, c0 + c1 + 3 * cw + 0.1), (-4 * ch - 0.1, 0.55))


# ═════════════ ЕГЭ №17 ═════════════

def levels(name, lv, arrows_, top_label=None, size=(4.6, 4.4), num=False):
    """Диаграмма уровней: lv — [(y, подпись)], arrows_ — [(x, y_от, y_до, подпись)]."""
    fig, ax = canvas(size)
    ymax = max(y for y, _ in lv)
    wire(ax, (0, -0.35), (0, ymax + 0.35), lw=1.6)
    for y, s in lv:
        dashed = s in ("0",)
        wire(ax, (0, y), (4.2, y), lw=1.3 if dashed else LW, ls=(0, (6, 4)) if dashed else "-")
        ax.text(-0.15, y, s, ha="right", va="center", fontsize=FONT)
    for x, y1, y2, s in arrows_:
        arrow(ax, (x, y1), (x, y2), color=ACCENT, lw=2.2, ms=20)
        dot(ax, x, y1, r=0.06, color=ACCENT)
        if s:
            ax.text(x, -0.12, s, ha="center", va="top", fontsize=FONT)
    if top_label:
        ax.text(0.12, ymax + 0.35, top_label, ha="left", va="center", fontsize=FONT)
    finish(fig, ax, name, (-1.4, 4.5), (-0.7 if num else -0.4, ymax + 0.6))


levels("t17_levels_numbered",
       [(0, "$E_0$"), (2.2, "$E_1$"), (3.6, "$E_2$"), (4.5, "$E_3$"), (5.05, "$E_4$"), (5.9, "0")],
       [(1.0, 2.2, 0, "1"), (1.8, 3.6, 0, "2"), (2.6, 0, 4.5, "3"), (3.4, 0, 5.05, "4")], num=True)

ev = {0: 6.0, -0.5: 5.25, -0.9: 4.65, -1.5: 3.8, -3.4: 2.5, -13.6: 0}
levels("t17_levels_ev", [(y, _num(v) if v else "0") for v, y in ev.items()],
       [(1.0, ev[-1.5], ev[-13.6], None), (1.9, ev[-0.9], ev[-13.6], None),
        (2.8, ev[-13.6], ev[-0.9], None), (3.7, ev[-13.6], ev[-0.5], None)], top_label="E, эВ")


def photo_graphs(name, labels=True):
    """А — гипербола E(λ), Б — ноль до порога, затем прямая."""
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.8))
    for ax, L in zip(axs, ("А", "Б")):
        ax.axis("off")
        arrow(ax, (0, 0), (4.4, 0), lw=1.5, ms=14)
        arrow(ax, (0, 0), (0, 4.4), lw=1.5, ms=14)
        ax.text(-0.1, -0.1, "0", ha="right", va="top", fontsize=FONT - 1)
        badge(ax, -0.8, 4.2, L)
        ax.set_xlim(-1.2, 4.8)
        ax.set_ylim(-0.6, 4.8)
    a, b = axs
    f = lambda x: 1.2 / x + 0.35  # noqa: E731 — гипербола со сдвигом, чтобы кривая шла над осью
    xs = [0.32 + i * (3.8 - 0.32) / 300 for i in range(301)]
    a.plot(xs, [f(x) for x in xs], color=ACCENT, lw=LW + 0.4, zorder=3)
    if labels:
        for x in (0.5, 1.0, 1.6, 2.4, 3.2):
            a.plot([x, x], [0, f(x)], color=MUTED, lw=1.0, ls=(0, (4, 3)))
            a.plot([0, x], [f(x), f(x)], color=MUTED, lw=1.0, ls=(0, (4, 3)))
            a.plot(x, f(x), "o", color=ACCENT, ms=6, zorder=4)
        a.text(0.12, 4.4, "E", ha="left", va="center", fontsize=FONT, style="italic")
        a.text(4.4, 0.12, "λ", ha="center", va="bottom", fontsize=FONT + 1)
        b.text(0.12, 4.4, "E", ha="left", va="center", fontsize=FONT, style="italic")
        b.text(4.4, 0.12, "ν", ha="center", va="bottom", fontsize=FONT + 1)
    b.plot([0, 1.4, 3.8], [0, 0, 3.9], color=ACCENT, lw=LW + 0.4, zorder=3)
    save(fig, out(name))


photo_graphs("t17_graphs")
photo_graphs("t17_graphs_photo", labels=False)


# ═════════════ ЕГЭ №19: приборы ═════════════

# Вольтметр 0–5 В, цена деления 0,2 В, стрелка — 4,6 В
fig, ax = dial_meter([(0, 5, 1, 5)], 4.6, 0, "V", ["−", "+"], ["−", "+"])
save(fig, out("t19_voltmeter_half"))

# Амперметр: шкалы 0–0,6 А и 0–3 А, подключён к клеммам «−» и «0,6 А», стрелка — 0,2 А (= 1 А по нижней)
fig, ax = dial_meter([(0, 0.6, 0.2, 10), (0, 3, 1, 10)], 0.2, 0, "A", ["−", "0,6 А", "3 А"], ["−", "0,6 А"])
save(fig, out("t19_ammeter_two_scales"))

# Динамометр 0–5 Н, цена деления 0,1 Н, показание 4,1 Н; на крючке груз
fig, ax = canvas((6.4, 8.2))
dynamometer(ax, 0, 8.0, 5, 1, 10, 6.0, "Н", value=4.1)
yv = 6.7 - 4.1 / 5 * 6.0                      # высота указателя
cx, cy, rr = 3.4, yv, 1.6
clip = Circle((cx, cy), rr, fc="white", ec=INK, lw=LW, zorder=6)
ax.add_patch(clip)
zoom = 4.0
for k in range(30, 52):
    v = k / 10
    y = cy - (v - 4.1) * 1.2 * zoom
    L = 0.75 if k % 10 == 0 else (0.5 if k % 5 == 0 else 0.3)
    ln, = ax.plot([cx + 0.05, cx + 0.05 + L], [y, y], color=INK, lw=2.0 if k % 10 == 0 else 1.2, zorder=7)
    ln.set_clip_path(clip)
    if k % 10 == 0 and abs(y - cy) < rr - 0.3:
        tx = ax.text(cx + 0.9, y, str(k // 10), ha="left", va="center", fontsize=FONT + 3, fontweight="bold",
                     zorder=7)
        tx.set_clip_path(clip)
ln, = ax.plot([cx - 0.6, cx - 0.6], [cy - 2, cy + 2], color=INK, lw=1.6, zorder=7)
ln.set_clip_path(clip)
pt = Polygon([(cx - 1.3, cy + 0.12), (cx + 0.3, cy + 0.12), (cx + 0.3, cy - 0.12), (cx - 1.3, cy - 0.12)],
             fc=ACCENT, ec=INK, lw=1.0, zorder=8)
ax.add_patch(pt)
pt.set_clip_path(clip)
ax.add_patch(Circle((-0.1, yv), 0.42, fc="none", ec=INK, lw=1.4, zorder=6))
wire(ax, (0.32, yv), (cx - rr, cy), lw=1.2)
ax.add_patch(Rectangle((-0.75, -1.75), 0.8, 0.9, fc=FILL, ec=INK, lw=LW))
wire(ax, (-0.35, -0.85), (-0.35, -0.65), lw=1.6)
ax.add_patch(Arc((-0.35, -0.5), 0.3, 0.3, theta1=-90, theta2=180, color=INK, lw=1.6))
finish(fig, ax, "t19_dynamometer", (-1.4, 5.2), (-1.9, 8.5))


def manometer(name, value):
    """Манометр 0–300 мм рт. ст.: подписи через 20, цена деления 2 мм рт. ст."""
    fig, ax = canvas((6.2, 6.2))
    ax.add_patch(Circle((0, 0), 3.65, fc="#f8fafc", ec=INK, lw=LW * 1.3))
    _arc_scale(ax, 0, 0, 2.8, 225, -45, 0, 300, 20, 10, inside=True, label_r=3.22)
    ax.text(0, -1.5, "мм рт. ст.", ha="center", va="center", fontsize=FONT - 1, color=MUTED)
    t = math.radians(225 - 270 * value / 300)
    ax.plot([-0.5 * math.cos(t), 2.75 * math.cos(t)], [-0.5 * math.sin(t), 2.75 * math.sin(t)],
            color=ACCENT, lw=3, solid_capstyle="round", zorder=5)
    ax.add_patch(Circle((0, 0), 0.18, fc=INK, zorder=6))
    finish(fig, ax, name, (-3.9, 3.9), (-3.9, 3.9))


manometer("t19_manometer_given", 136)
manometer("t19_manometer_half", 40)

# Комнатный термометр 0–50 °C, цена деления 1 °C, показание 22 °C
fig, ax = canvas((2.8, 7.6))
sy = 7.0 / 50
Y = lambda v: v * sy  # noqa: E731
ax.add_patch(FancyBboxPatch((-1.25, -1.45), 2.6, 9.55, boxstyle="round,pad=0,rounding_size=0.3",
                            fc="#f8fafc", ec=INK, lw=LW))
ax.add_patch(Circle((0, -0.85), 0.32, fc=ACCENT, ec=INK, lw=1.4, zorder=3))
ax.add_patch(Rectangle((-0.08, -0.6), 0.16, Y(22) + 0.6, fc=ACCENT, ec="none", zorder=3))
ax.add_patch(Rectangle((-0.08, -0.6), 0.16, Y(50) + 0.9, fc="none", ec=INK, lw=1.0, zorder=3))
for v in range(51):
    L = 0.42 if v % 10 == 0 else (0.3 if v % 5 == 0 else 0.18)
    ax.plot([0.18, 0.18 + L], [Y(v), Y(v)], color=INK, lw=1.4 if v % 10 == 0 else 0.8)
    if v % 10 == 0:
        ax.text(-0.25, Y(v), str(v), ha="right", va="center", fontsize=FONT - 1)
ax.text(-0.25, Y(50) + 0.6, "°C", ha="right", va="center", fontsize=FONT - 1)
finish(fig, ax, "t19_thermometer", (-1.4, 1.5), (-1.6, 8.3))


# ═════════════ ЕГЭ №20: выбор установок ═════════════

def numbered(ax, x, y, n):
    badge(ax, x, y, str(n))


# Динамометр с шариком в стакане с жидкостью
fig, ax = canvas((10.8, 6.2))
setups = [(1, "медь", "вода", 0.28), (2, "сталь", "керосин", 0.5), (3, "сталь", "вода", 0.28),
          (4, "алюминий", "керосин", 0.28), (5, "медь", "керосин", 0.28)]
pos = [(1.8, 3.4), (5.7, 3.4), (9.6, 3.4), (3.75, 0), (7.65, 0)]
for (n, mat, liq, r), (x, y) in zip(setups, pos):
    ax.add_patch(Rectangle((x - 0.18, y + 1.85), 0.36, 0.95, fc="white", ec=INK, lw=1.6))
    zz = [(x, y + 2.75)] + [(x + (0.1 if i % 2 else -0.1), y + 2.7 - i * 0.08) for i in range(1, 9)] + \
         [(x, y + 1.95)]
    ax.plot(*zip(*zz), color=INK, lw=1.2)
    wire(ax, (x, y + 1.85), (x, y + 0.75 + r), lw=1.2)
    ax.add_patch(Rectangle((x - 0.7, y + 0.15), 1.4, 1.15, fc=FILL if liq == "вода" else OIL, ec="none"))
    wire(ax, (x - 0.7, y + 1.6), (x - 0.7, y), (x + 0.7, y), (x + 0.7, y + 1.6), lw=LW + 0.6)
    ax.add_patch(Circle((x, y + 0.75), r, fc="white", ec=INK, lw=1.6, zorder=4))
    ax.text(x - 0.95, y + 0.75, mat, ha="right", va="center", fontsize=FONT - 1)
    wire(ax, (x - 0.9, y + 0.75), (x - r, y + 0.75), lw=1.0)
    ax.text(x + 0.85, y + 1.05, liq, ha="left", va="center", fontsize=FONT - 1)
    numbered(ax, x - 1.2, y + 2.6, n)
finish(fig, ax, "t20_archimedes", (-0.4, 11.2), (-0.3, 6.4))


def incline_panel(ax, x0, y0, n, m, ang, mu):
    ax.add_patch(Rectangle((x0, y0), 3.4, 2.0, fc="none", ec=GRID, lw=1.4))
    numbered(ax, x0 + 0.3, y0 + 1.7, n)
    a = math.radians(ang)
    L = 2.4 if ang < 30 else 1.9
    bx, by = x0 + 0.45, y0 + 0.3
    tx, ty = bx + L, by
    h = L * math.tan(a)
    ax.add_patch(Polygon([(bx, by), (tx, ty), (bx, by + h)], fc="#f8fafc", ec=INK, lw=LW))
    s = 0.42                                       # положение бруска вдоль склона (доля)
    px, py = bx + L * s, by + h * (1 - s)
    block(ax, px - 0.2 * math.cos(a), py + 0.2 * math.sin(a) - 0.02, 0.5, 0.26, angle=-ang, fc=ACCENT)
    ax.text(px + 0.15, py + 0.5, m, ha="left", va="bottom", fontsize=FONT, style="italic")
    ax.add_patch(Arc((tx, ty), 0.9, 0.9, theta1=180 - ang, theta2=180, color=INK, lw=1.3))
    ax.text(tx - 0.62, ty + 0.12, "α" if ang < 30 else "2α", ha="right", va="bottom", fontsize=FONT)
    ax.text(bx + 0.15, by - 0.08, mu, ha="left", va="top", fontsize=FONT)
    arrow(ax, (bx + 0.55, by - 0.15), (bx + L * 0.3, by + h * 0.7 - 0.06), color=MUTED, lw=1.0, ms=10)


fig, ax = canvas((10.2, 4.8))
for n, m, ang, mu, (x, y) in ((1, "2m", 18, "μ", (0, 2.2)), (2, "m", 18, "2μ", (3.4, 2.2)),
                               (3, "m", 18, "μ", (6.8, 2.2)), (4, "3m", 36, "μ", (1.7, 0)),
                               (5, "m", 36, "2μ", (5.1, 0))):
    incline_panel(ax, x, y, n, m, ang, mu)
finish(fig, ax, "t20_incline", (-0.1, 10.3), (-0.1, 4.3))


def small_circuit(ax, x0, y0, n, emf, r, R):
    numbered(ax, x0 - 0.5, y0 + 1.45, n)
    c = circ_on(ax)
    c.wire((x0, y0 + 0.58), (x0, y0 + 1.4), (x0 + 1.08, y0 + 1.4))
    c.battery(x0 + 1.15, y0 + 1.4)
    c.wire((x0 + 1.23, y0 + 1.4), (x0 + 2.3, y0 + 1.4), (x0 + 2.3, y0), (x0 + 1.75, y0))
    c.resistor(x0 + 1.15, y0, w=1.2)
    c.wire((x0 + 0.55, y0), (x0, y0), (x0, y0 + 0.18))
    c.meter(x0, y0 + 0.38, "A", r=0.22)
    ax.text(x0 + 1.35, y0 + 1.62, f"{emf}, {r}", ha="left", va="bottom", fontsize=FONT)
    ax.text(x0 + 1.15, y0 + 0.3, R, ha="center", va="bottom", fontsize=FONT)


fig, ax = canvas((8.4, 7.0))
for n, emf, r, R, (x, y) in ((1, "3ℰ", "r", "4R", (0.6, 4.8)), (4, "3ℰ", "2r", "4R", (4.6, 4.8)),
                             (2, "2ℰ", "2r", "R", (0.6, 2.4)), (5, "ℰ", "2r", "R", (4.6, 2.4)),
                             (3, "ℰ", "r", "4R", (2.6, 0))):
    small_circuit(ax, x, y, n, emf, r, R)
finish(fig, ax, "t20_internal_r", (-0.4, 7.6), (-0.5, 7.0))


def depth_vessel(ax, x, y, n, liquid, probe, shape="straight"):
    """Сосуд с жидкостью; датчик манометра на щупе на глубине probe от поверхности."""
    numbered(ax, x - 1.0, y + 2.6, n)
    top, lev = y + 2.0, y + 1.75
    if shape == "straight":
        inner = [(x - 0.7, top), (x - 0.7, y), (x + 0.7, y), (x + 0.7, top)]
        liq = [(x - 0.7, lev), (x - 0.7, y), (x + 0.7, y), (x + 0.7, lev)]
    else:
        wt, wb = (0.75, 0.45) if shape == "narrow" else (0.45, 0.75)
        k = lambda yy: wb + (wt - wb) * (yy - y) / (top - y)  # noqa: E731
        inner = [(x - wt, top), (x - wb, y), (x + wb, y), (x + wt, top)]
        liq = [(x - k(lev), lev), (x - wb, y), (x + wb, y), (x + k(lev), lev)]
    ax.add_patch(Polygon(liq, fc=FILL if liquid == "вода" else OIL, ec="none"))
    wire(ax, *inner, lw=LW + 0.6)
    hatch(ax, x - 1.1, x + 1.1, y - 0.04, step=0.2, lw=1.0)
    px = x + 0.3
    wire(ax, (px, y + 2.45), (px, lev - probe), lw=1.8)
    dot(ax, px, lev - probe, r=0.08)
    ax.add_patch(Rectangle((px - 0.9, y + 2.4), 0.9, 0.32, fc="white", ec=INK, lw=1.2))
    ax.text(px - 0.45, y + 2.56, "манометр", ha="center", va="center", fontsize=FONT - 7)
    ax.text(x - 0.15, y + 0.75, liquid, ha="center", va="center", fontsize=FONT - 3)


fig, ax = canvas((8.8, 6.4))
for n, liq, pr, sh, (x, y) in ((1, "вода", 0.35, "straight", (1.2, 3.3)), (2, "вода", 1.25, "straight", (4.2, 3.3)),
                               (3, "масло", 0.35, "straight", (7.2, 3.3)), (4, "масло", 1.25, "narrow", (2.7, 0)),
                               (5, "вода", 0.35, "wide", (5.7, 0))):
    depth_vessel(ax, x, y, n, liq, pr, sh)
finish(fig, ax, "t20_depth", (-0.2, 8.6), (-0.4, 6.2))


def cap_setup(ax, x, y, n, area, diel, d):
    """Конденсатор: пластины высотой h (S или 2S), диэлектрик толщиной d (d или 2d)."""
    h = 1.3 if area == "S" else 2.6
    w = 0.6 if d == "d" else 1.2
    numbered(ax, x + w / 2, y + h / 2 + 0.75, n)
    ax.add_patch(Rectangle((x, y - h / 2), w, h, fc="#e0f2fe" if diel == "стекло" else "#d6d3d1", ec="none"))
    for xx in (x, x + w):
        ax.plot([xx, xx], [y - h / 2, y + h / 2], color=INK, lw=3.5, solid_capstyle="butt")
    wire(ax, (x - 0.7, y), (x, y))
    wire(ax, (x + w, y), (x + w + 0.7, y))
    ax.text(x - 0.12, y + 0.12, area, ha="right", va="bottom", fontsize=FONT, style="italic")
    ax.text(x + w / 2, y, diel, ha="center", va="center", fontsize=FONT - 4, rotation=90 if w < 1 else 0)
    yy = y - h / 2 - 0.3
    arrow(ax, (x, yy), (x + w, yy), color=MUTED, lw=1.2, ms=10, style="<|-|>")
    ax.text(x + w / 2, yy - 0.08, "2d" if d == "2d" else "d", ha="center", va="top", fontsize=FONT, style="italic")


fig, ax = canvas((8.4, 6.6))
for n, area, diel, d, (x, y) in ((1, "S", "стекло", "d", (0.9, 5.2)), (2, "S", "керамика", "2d", (3.6, 5.2)),
                                 (3, "S", "керамика", "d", (6.9, 5.2)), (4, "2S", "стекло", "d", (2.3, 1.4)),
                                 (5, "2S", "керамика", "2d", (5.2, 1.4))):
    cap_setup(ax, x, y, n, area, diel, d)
finish(fig, ax, "t20_capacitor_dielectric", (-0.3, 8.3), (-0.4, 6.7))

print("ok")
