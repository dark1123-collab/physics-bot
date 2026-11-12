"""Блок 2: ЕГЭ №1–8. Результат — tools/redraw/preview/ (имена как в images/)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle, Polygon, Rectangle  # noqa: E402
from style import (ACCENT, FILL, FONT, GRID, INK, LW, MUTED, Plot, ball, block, canvas, cells,  # noqa: E402
                   hatch, hatch_v, save, spring, vec, badge, _num)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")


def out(name):
    return os.path.join(OUT, name + ".png")


def rng(a, b, s):
    n = round((b - a) / s)
    return [round(a + i * s, 6) for i in range(n + 1)]


def vt_graph(name, pts, xgrid, ygrid, xlab, ylab, xlabel="t, с", ylabel="vₓ, м/с", size=(7.2, 4.6), dots=False,
             yneg=None):
    p = Plot((xgrid[0], xgrid[-1]), (ygrid[0], ygrid[-1]), size=size, grid_x=xgrid, grid_y=ygrid)
    p.axes(xlabel, ylabel, yneg=yneg)
    p.xticks(xlab)
    p.yticks([y for y in ylab if y != 0])
    p.line(pts)
    if dots:
        for x, y in pts:
            p.point(x, y)
    p.finish(out(name))


# ───────────── ЕГЭ №1: кинематика ─────────────
vt_graph("graph1", [(0, 50), (40, -50)], rng(0, 40, 10), rng(-100, 100, 50), [10, 20, 30, 40],
         [-100, -50, 50, 100], ylabel="x, м", dots=True, yneg=-100)
vt_graph("graph2", [(0, 0), (1, 10), (3, 15), (5, 15), (7, 25)], rng(0, 7, 1), rng(0, 25, 5), rng(1, 7, 1),
         rng(5, 25, 5), ylabel="S, м", dots=True)
vt_graph("graph3", [(0, 7), (2, 2), (5, 2), (8, 5)], rng(0, 8, 1), rng(-4, 7, 1), rng(1, 8, 1),
         rng(-4, 7, 1), yneg=-4)
vt_graph("graph4", [(0, 8), (2, 0), (4, 12), (5, 0), (6, 2)], rng(0, 6, 1), rng(0, 12, 2), [2, 4, 6],
         rng(2, 12, 2))
vt_graph("graph5", [(0, 15), (5, -10), (7, -10), (12, 5), (15, 5), (19, -5)], rng(0, 20, 1), rng(-15, 15, 5),
         [5, 10, 15, 20], rng(-15, 15, 5), size=(7.6, 5), yneg=-15)
vt_graph("graph6", [(0, 10), (6, -5), (9, 2.5)], rng(0, 9, 1), rng(-8, 10, 2), rng(1, 9, 1), rng(-8, 10, 2),
         size=(7.2, 5.4), yneg=-8)

# x(t) = 3t²: сплошная при t ≥ 0, пунктир при t < 0
p = Plot((-3, 3), (0, 3), size=(7, 3.6), grid_x=rng(-3, 3, 1), grid_y=rng(0, 3, 1))
p.axes("t, с", "x, м", origin="", xneg=-3)
p.xticks([-2, -1, 0, 1, 2, 3])
p.yticks([1, 2, 3])
p.curve(lambda t: 3 * t * t, -1, 0, dashed=True)
p.curve(lambda t: 3 * t * t, 0, 1)
p.finish(out("graph7"))

vt_graph("t1_v_15_to_m15", [(0, 15), (20, -15), (30, 15)], rng(0, 30, 5), rng(-15, 15, 5),
         [5, 10, 15, 20, 25, 30], rng(-15, 15, 5), yneg=-15)
for nm in ("t1_v_zigzag_a_at_2", "t1_v_zigzag_a_25_3"):
    vt_graph(nm, [(0, 4), (0.5, 0), (1, 6), (1.5, 2), (2.5, 2), (3, -6)], rng(0, 3, 0.5), rng(-6, 6, 2),
             [1, 2, 3], rng(-6, 6, 2), size=(6.4, 5.2), yneg=-6)
vt_graph("t1_v_line_coord", [(0, 2), (3, 8)], rng(0, 3, 0.5), rng(0, 8, 1), [1, 2, 3], [2, 4, 6, 8],
         size=(6.2, 5))
vt_graph("t1_v_displacement_15", [(0, -20), (15, 10), (20, -10), (30, 20)], rng(0, 30, 5), rng(-20, 20, 10),
         [5, 10, 15, 20, 25, 30], rng(-20, 20, 10), dots=True, yneg=-20)
vt_graph("t1_v_trapezoid_avg", [(0, 0), (1, 10), (3, 10), (5, 0)], rng(0, 5, 0.5), rng(0, 12.5, 2.5),
         [1, 2, 3, 4, 5], [5, 10], ylabel="v, м/с")
vt_graph("t1_s_bicycle", [(0, 0), (10, 50), (30, 50), (50, 100), (70, 250)], rng(0, 70, 10), rng(0, 250, 50),
         rng(10, 70, 10), rng(50, 250, 50), ylabel="S, м")
vt_graph("t1_s_stop", [(0, 0), (1, 1), (3, 1), (5, 2)], rng(0, 5, 1), rng(0, 4, 1), [1, 2, 3, 4, 5], [1, 2, 3, 4],
         ylabel="S, м", size=(6.2, 4.6))
p = Plot((0, 9), (0, 12), size=(7, 4.8), grid_x=rng(0, 9, 1), grid_y=rng(0, 12, 2))
p.axes("t, с", "x, м")
p.xticks(rng(1, 9, 1))
p.yticks(rng(2, 12, 2))
p.curve(lambda t: 2 + 0.375 * t * t, 0, 5)
p.finish(out("t1_x_from_rest"))

fig, ax = canvas(size=(5, 5.4))
cells(ax, 0, 0, 6, 8)
o = (0, 4)
vec(ax, *o, 6, 8, r"$\vec F_1$", lx=0.15, ly=0.1)
vec(ax, *o, 6, 4, r"$\vec F_2$", lx=0.15)
vec(ax, *o, 0, 0, r"$\vec F_3$", lx=-0.15, ly=0.2, ha="right")
ax.add_patch(Circle(o, 0.12, fc=ACCENT, zorder=6))
ax.set_xlim(-1.1, 7.4)
ax.set_ylim(-0.4, 8.6)
save(fig, out("t1_forces_cells"))

vt_graph("t1_v_two_trapezoids", [(0, 15), (10, 5), (20, 20), (30, 0), (40, 25)], rng(0, 40, 5), rng(0, 25, 5),
         [10, 20, 30, 40], [10, 20])
vt_graph("t1_v_demo2026", [(0, 5), (10, 20), (20, 10), (30, 25), (40, 0)], rng(0, 40, 5), rng(0, 25, 5),
         [10, 20, 30, 40], [10, 20])

# ───────────── ЕГЭ №2: силы ─────────────
def forces1(name, solution):
    fig, ax = canvas(size=(5.4, 5.4))
    cells(ax, 0, 0, 6, 6)
    o = (1, 3)
    ax.plot([1, 2], [5.6, 5.6], color=INK, lw=2)
    for xx in (1, 2):
        ax.plot([xx, xx], [5.45, 5.75], color=INK, lw=2)
    ax.text(1.5, 5.85, "1 Н", ha="center", va="bottom", fontsize=FONT)
    vec(ax, *o, 4, 5, r"$\vec F_1$", lx=0.15, ly=0.15)
    vec(ax, *o, 1, 1, r"$\vec F_2$", lx=-0.15, ha="right")
    if solution:
        for a, b in (((4, 5), (4, 3)), ((1, 1), (4, 3))):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=MUTED, lw=1.6, ls=(0, (5, 4)), zorder=2)
        vec(ax, *o, 4, 3, r"$\vec R$", lx=0.15, ly=-0.3, color=INK)
    ax.add_patch(Circle(o, 0.12, fc=ACCENT, zorder=6))
    ax.set_xlim(-0.6, 6.8)
    ax.set_ylim(-0.3, 6.6)
    save(fig, out(name))


forces1("forces1", False)
forces1("forces1_solution", True)

p = Plot((0, 12), (0, 1.5), size=(7, 4.2), grid_x=rng(0, 12, 2), grid_y=rng(0, 1.5, 0.5))
p.axes("N, Н", "Fтр, Н")
p.xticks(rng(2, 12, 2))
p.yticks([0.5, 1.0, 1.5], labels=["0,5", "1,0", "1,5"])
p.line([(0, 0), (12.8, 1.6)])
p.finish(out("graph8"))

p = Plot((0, 6), (0, 6), size=(5.6, 5), grid_x=rng(0, 6, 1), grid_y=rng(0, 6, 1))
p.axes("l, см", "F, Н")
p.xticks(rng(1, 5, 1))
p.yticks([1, 3, 5])
p.line([(0, 0), (2, 0), (6, 4)])
p.finish(out("graph9"))

fig, ax = canvas(size=(8, 2.8))
hatch_v(ax, 0, 0, 2.2)
hatch(ax, 0, 7.2, 0)
spring(ax, 0, 2.2, 0.55, coils=7)
block(ax, 2.2, 0, 1.3, 1.1, "M")
spring(ax, 3.5, 5.7, 0.55, coils=7)
ax.text(1.1, 1.0, "k₁", ha="center", fontsize=FONT + 1)
ax.text(4.6, 1.0, "k₂", ha="center", fontsize=FONT + 1)
ax.add_patch(Circle((5.7, 0.55), 0.06, fc=INK, zorder=4))
vec(ax, 5.7, 0.55, 6.9, 0.55, r"$\vec F$", lx=-0.3, ly=0.45)
ax.set_xlim(-0.6, 7.4)
ax.set_ylim(-0.5, 2.4)
save(fig, out("forces2"))


# ───────────── ЕГЭ №3: законы сохранения ─────────────
def cart(ax, x, y, w=4.0, h=1.4, stone=None):
    hatch(ax, x - 1.2, x + w + 1.2, y - 0.62)
    ax.add_patch(Rectangle((x - 0.4, y - 0.62), w + 0.8, 0.12, fc=GRID, ec=INK, lw=1.2, zorder=2))  # рельсы
    ax.add_patch(Rectangle((x, y), w, h, fc="#fde68a", ec=INK, lw=LW, zorder=3))
    ax.plot([x, x], [y + h, y + h + 0.5], color=INK, lw=LW, zorder=3)
    ax.plot([x + w, x + w], [y + h, y + h + 0.5], color=INK, lw=LW, zorder=3)
    for wx in (x + 0.9, x + w - 0.9):
        ax.add_patch(Circle((wx, y - 0.2), 0.3, fc="#94a3b8", ec=INK, lw=1.6, zorder=4))
    ax.text(x + 0.5, y + h * 0.55, "M", fontsize=FONT + 2, style="italic", va="center", zorder=4)
    if stone:
        ball(ax, stone[0], stone[1], 0.32, "m", fc="#bbf7d0")


fig, ax = canvas(size=(7, 4.6))
cart(ax, 1, 0.6)
sx, sy = 2.0, 4.4
ball(ax, sx, sy, 0.32, "m", fc="#bbf7d0")
a = math.radians(60)
vec(ax, sx + 0.32 * math.cos(-a), sy + 0.32 * math.sin(-a), sx + 1.5 * math.cos(-a), sy + 1.5 * math.sin(-a),
    r"$\vec v$", lx=0.15, ly=0.1)
ax.plot([sx, sx + 1.6], [sy, sy], color=MUTED, lw=1.2, ls=(0, (5, 4)))
ax.add_patch(Arc((sx, sy), 1.4, 1.4, theta1=-60, theta2=0, color=INK, lw=1.4))
ax.text(sx + 0.95, sy - 0.42, "α", fontsize=FONT + 1)
ax.set_xlim(-0.6, 6.6)
ax.set_ylim(-0.4, 5.0)
save(fig, out("scheme1"))

fig, ax = canvas(size=(7, 3.2))
cart(ax, 1, 0.6, stone=(2.9, 2.0))
vec(ax, 3.0, 1.2, 5.6, 1.2, r"$\vec v\,'$", lx=0.1, ly=0.3)
ax.set_xlim(-0.6, 6.6)
ax.set_ylim(-0.4, 2.8)
save(fig, out("scheme1_solution"))

fig, ax = canvas(size=(7, 4.4))
ax.plot([0, 5.2], [0, 0], color=MUTED, lw=1.2, ls=(0, (5, 4)))
ball(ax, 0.6, 0, 0.32, fc=FILL)
vec(ax, 0.95, 0, 2.3, 0, r"$\vec v_1$", lx=-1.3, ly=0.38)
d = 1 / math.sqrt(2)
cx, cy = 4.6, 3.0
ax.plot([cx + 0.9, cx - 3.0 + 0.0], [cy + 0.9, cy - 3.0], color=MUTED, lw=1.2, ls=(0, (5, 4)))
ball(ax, cx, cy, 0.32, fc=FILL)
vec(ax, cx - 0.32 * d, cy - 0.32 * d, cx - 1.8 * d, cy - 1.8 * d, r"$\vec v_2$", lx=-0.25, ly=0.35, ha="right")
# угол между направлениями v1 (0°) и v2 (225°): дуга под осью, 135°
ax.plot([1.6, 0.9], [0, -0.7], color=MUTED, lw=1.2, ls=(0, (5, 4)))
ax.add_patch(Arc((1.6, 0), 1.1, 1.1, theta1=225, theta2=360, color=INK, lw=1.4))
ax.text(2.25, -0.5, "135°", fontsize=FONT, ha="left", va="top")
ax.set_xlim(-0.4, 6.0)
ax.set_ylim(-1.3, 4.2)
save(fig, out("graph40"))

# ───────────── ЕГЭ №4: статика ─────────────
fig, ax = canvas(size=(7, 3.4))
ax.plot([0, 5.5], [2, 2], color="#92400e", lw=6, solid_capstyle="round", zorder=3)   # палка AB, OA:OB = 3:8
o = 1.5
ax.add_patch(Polygon([(o - 0.3, 1.45), (o + 0.3, 1.45), (o, 1.95)], fc="#e2e8f0", ec=INK, lw=1.6, zorder=4))
for x, nm in ((0, "A"), (o, "O"), (5.5, "B")):
    ax.text(x, 2.35, nm, ha="center", va="bottom", fontsize=FONT + 1, style="italic")
ax.plot([0, 0], [2, 1.2], color=INK, lw=1.6)
ax.add_patch(Rectangle((-0.45, 0.25), 0.9, 0.95, fc="#bbf7d0", ec=INK, lw=LW, zorder=3))
ax.text(0, 0.72, "80 Н", ha="center", va="center", fontsize=FONT - 2)
vec(ax, 5.5, 2, 5.5, 0.9, r"$\vec F$", lx=0.15, ly=0.2)
ax.set_xlim(-1.0, 6.3)
ax.set_ylim(0, 3.0)
save(fig, out("scheme2"))

fig, ax = canvas(size=(7.4, 3.6))
hatch(ax, 3.4, 6.6, 3.2, down=False)
ax.plot([5, 5], [3.2, 2.3], color=INK, lw=1.6)
for i in range(10):
    ax.add_patch(Rectangle((i, 1.9), 1, 0.4, fc="white", ec=INK, lw=1.4, zorder=3))
ax.plot([8, 8], [1.9, 1.3], color=INK, lw=1.4)
ball(ax, 8, 0.85, 0.45, fc="#e2e8f0")
ax.plot([3, 3], [1.9, 1.3], color=INK, lw=1.4, ls=(0, (4, 3)))
ax.add_patch(Circle((3, 0.85), 0.45, fc="white", ec=INK, lw=1.4, ls=(0, (4, 3)), zorder=3))
ax.text(3, 0.85, "?", ha="center", va="center", fontsize=FONT + 2)
ax.set_xlim(-0.4, 10.4)
ax.set_ylim(0.2, 3.6)
save(fig, out("scheme3"))


def vessel_two_blocks(name, size=(4.6, 4.2)):
    fig, ax = canvas(size=size)
    hatch(ax, -0.6, 4.6, 0)
    ax.add_patch(Rectangle((0, 0), 4, 2.6, fc=FILL, ec="none", zorder=1))
    ax.plot([0, 0, 4, 4], [3.8, 0, 0, 3.8], color=INK, lw=LW, zorder=4)
    block(ax, 1.3, 2.0, 1.4, 0.6, fc="#86efac")   # нижний — в воде
    block(ax, 1.3, 2.6, 1.4, 0.6, fc="#86efac")   # верхний — над водой
    ax.plot([0, 1.3], [2.6, 2.6], color=ACCENT, lw=1.6, zorder=2)
    ax.plot([2.7, 4], [2.6, 2.6], color=ACCENT, lw=1.6, zorder=2)
    ax.set_xlim(-0.8, 4.8)
    ax.set_ylim(-0.4, 4.0)
    save(fig, out(name))


vessel_two_blocks("scheme4")
vessel_two_blocks("graph71_brick_cup")

fig, ax = canvas(size=(6, 1.6))
heads = ["F₁, Н", "l₁, м", "F₂, Н", "l₂, м"]
vals = ["40", "0,8", "?", "0,2"]
for i, (h, v) in enumerate(zip(heads, vals)):
    ax.add_patch(Rectangle((i * 1.6, 0.7), 1.6, 0.7, fc="#e0e7ff", ec=INK, lw=1.4))
    ax.add_patch(Rectangle((i * 1.6, 0), 1.6, 0.7, fc="white", ec=INK, lw=1.4))
    ax.text(i * 1.6 + 0.8, 1.05, h, ha="center", va="center", fontsize=FONT)
    ax.text(i * 1.6 + 0.8, 0.35, v, ha="center", va="center", fontsize=FONT)
ax.set_xlim(-0.1, 6.5)
ax.set_ylim(-0.1, 1.5)
save(fig, out("table2_lever_forces"))

# ───────────── ЕГЭ №5 ─────────────
p = Plot((0, 50), (0, 900), size=(6.6, 5.6), grid_x=rng(0, 50, 5), grid_y=rng(0, 900, 50))
p.axes("h, м", "p, кПа")
p.xticks(rng(10, 50, 10))
p.yticks(rng(100, 900, 100))
p.line([(0, 100), (50, 600)])
p.line([(0, 100), (25, 900)], color="#16a34a")
p.text(31, 640, "дийодметан", color="#16a34a", fontsize=FONT - 1, bbox=dict(fc="white", ec="none", pad=1))
p.text(41, 430, "вода", color=ACCENT, fontsize=FONT - 1, bbox=dict(fc="white", ec="none", pad=1))
p.finish(out("graph73_pressure_depth"))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, ymax, ylab in ((a1, 3.0, "F, Н"), (a2, 8.0, "A, Дж")):
    ax.axis("off")
    ax.annotate("", xy=(22.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
    ax.annotate("", xy=(0, ymax), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
    ax.text(22.5, -ymax * 0.06, "t, с", ha="center", va="top", fontsize=FONT)
    ax.text(0.5, ymax, ylab, ha="left", va="center", fontsize=FONT)
    ax.text(-0.4, -ymax * 0.03, "0", ha="right", va="top", fontsize=FONT - 1)
    for t in range(1, 21):
        ax.plot([t, t], [-ymax * 0.015, ymax * 0.015], color=INK, lw=1)
    for t in (10, 20):
        ax.text(t, -ymax * 0.05, str(t), ha="center", va="top", fontsize=FONT - 2)
    ax.set_xlim(-2, 24)
    ax.set_ylim(-ymax * 0.15, ymax * 1.08)
a1.plot([0, 12], [0, 2.4], color=ACCENT, lw=LW + 0.6)
a1.plot([12, 12, 20], [2.4, 2, 2], color=ACCENT, lw=LW + 0.6)
for x, y in ((10, 2), (12, 2.4), (20, 2)):
    a1.plot([x, x], [0, y], color=MUTED, lw=1.1, ls=(0, (4, 4)))
a1.plot([0, 10], [2, 2], color=MUTED, lw=1.1, ls=(0, (4, 4)))
a1.text(-0.4, 2, "2", ha="right", va="center", fontsize=FONT - 1)
a2.plot([0, 11], [0, 0], color=ACCENT, lw=LW + 0.6)
a2.plot([11, 20], [0, 6.5], color=ACCENT, lw=LW + 0.6)
for x in (10, 12):
    a2.plot([x, x], [0, 6.5], color=MUTED, lw=1.1, ls=(0, (4, 4)))
a2.plot([20, 20], [0, 6.5], color=MUTED, lw=1.1, ls=(0, (4, 4)))
a2.plot([0, 20], [6.5, 6.5], color=MUTED, lw=1.1, ls=(0, (4, 4)))
a2.text(-0.4, 6.5, "6,5", ha="right", va="center", fontsize=FONT - 1)
save(fig, out("graph72_F_A_graphs"))

p = Plot((0, 6), (-2, 2), size=(7.2, 4.2), grid_x=rng(0, 6, 0.5), grid_y=rng(-2, 2, 0.5))
p.axes("t, с", "x, см", yneg=-2)
p.xticks(rng(1, 6, 1))
p.yticks([-2, -1, 1, 2])
p.curve(lambda t: 2 * math.sin(math.pi * t / 2), 0, 6, color="#16a34a")
p.curve(lambda t: math.cos(math.pi * t / 2), 0, 6)
p.text(5.05, 2.05, "1", color="#16a34a", fontsize=FONT)
p.text(3.75, 1.1, "2", color=ACCENT, fontsize=FONT)
p.finish(out("graph76_two_springs"))

# ───────────── ЕГЭ №6 ─────────────
fig, ax = canvas(size=(6.4, 3.4))
ax.add_patch(Polygon([(0, 0), (6, 0), (0, 3)], closed=True, fc="white", ec=INK, lw=LW, zorder=1))
ang = math.degrees(math.atan2(-3, 6))
t = 0.42
bx, by = 6 * t, 3 * (1 - t)
block(ax, bx - 0.55, by + 0.02 - 0.0, 1.1, 0.55, "m", fc="#bbf7d0", angle=ang)
ax.add_patch(Arc((6, 0), 1.6, 1.6, theta1=180 + ang, theta2=180, color=INK, lw=1.4))
ax.text(4.95, 0.12, "α", fontsize=FONT + 1)
ax.set_xlim(-0.4, 6.4)
ax.set_ylim(-0.3, 3.4)
save(fig, out("graph50_incline_block"))

fig, ax = canvas(size=(5.4, 5))
hatch(ax, -0.4, 5.0, 0)
ball(ax, 0.8, 4.0, 0.22, fc="#bbf7d0")
vec(ax, 1.02, 4.0, 2.2, 4.0, r"$\vec v_0$", lx=-0.3, ly=0.35)
ax.plot([0.8, 0.8], [0, 3.78], color=MUTED, lw=1.2, ls=(0, (5, 4)))
xs = [0.8 + 3.4 * i / 40 for i in range(41)]
ax.plot(xs, [4.0 - 4.0 * ((x - 0.8) / 3.4) ** 2 for x in xs], color=MUTED, lw=1.4, ls=(0, (5, 4)))
ax.annotate("", xy=(0.25, 0), xytext=(0.25, 4.0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.2))
ax.text(0.05, 2.0, "H", ha="right", va="center", fontsize=FONT + 1, style="italic")
ax.annotate("", xy=(4.2, -0.45), xytext=(0.8, -0.45), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.2))
ax.text(2.5, -0.55, "L", ha="center", va="top", fontsize=FONT + 1, style="italic")
ax.set_xlim(-0.6, 5.2)
ax.set_ylim(-1.1, 4.7)
save(fig, out("graph51_projectile_HL"))


def ab_graphs(name, fa, fb, a_rng, b_rng, marks, t_end, size=(5.2, 5.6)):
    """Два графика А и Б одной ширины. fa, fb — функции от t на [0, t_end];
    a_rng/b_rng — пределы по вертикали; marks — [(t, подпись)] на оси t."""
    fig, axs = plt.subplots(2, 1, figsize=size)
    for ax, f, (lo, hi), lab in ((axs[0], fa, a_rng, "А"), (axs[1], fb, b_rng, "Б")):
        ax.axis("off")
        span = hi - lo
        ax.annotate("", xy=(t_end * 1.25, 0), xytext=(-t_end * 0.03, 0),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
        ax.annotate("", xy=(0, hi + span * 0.12), xytext=(0, lo - span * 0.02),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
        ax.text(t_end * 1.25, -span * 0.05, "t", ha="center", va="top", fontsize=FONT, style="italic")
        ax.text(-t_end * 0.03, -span * 0.04, "0", ha="right", va="top", fontsize=FONT - 1)
        ts = [t_end * i / 300 for i in range(301)]
        ax.plot(ts, [f(t) for t in ts], color=ACCENT, lw=LW + 0.6)
        for tm, tl in marks:
            ax.plot([tm, tm], [0, f(tm)], color=MUTED, lw=1.1, ls=(0, (4, 4)))
            ax.text(tm, -span * 0.05, tl, ha="center", va="top", fontsize=FONT, style="italic")
        badge(ax, -t_end * 0.32, hi, lab, r=t_end * 0.06)
        ax.set_xlim(-t_end * 0.42, t_end * 1.35)
        ax.set_ylim(lo - span * 0.22, hi + span * 0.2)
        ax.set_aspect(t_end * 0.55 / span)
    save(fig, out(name))


T = 1.0
w = 2 * math.pi
# q10: А — постоянная (модуль ускорения), Б — кинетическая энергия (минимум не ноль)
ab_graphs("graph52_q10", lambda t: 0.6, lambda t: 0.35 + 1.2 * (t - 0.35) ** 2, (0, 1), (0, 1),
          [], 1.0)
# q11 (бросок, y от точки броска): А — y (0 → max → 0 к t₀), Б — проекция импульса (прямая через 0)
ab_graphs("graph53_q11", lambda t: 4 * t * (1 - t), lambda t: 0.6 - 1.2 * t, (0, 1), (-0.6, 0.6),
          [(1.0, "t₀")], 1.0)
# q12: А — Eп ∝ cos², Б — x = −x₀cos
ab_graphs("graph54_q12", lambda t: math.cos(w * t) ** 2, lambda t: -math.cos(w * t), (0, 1), (-1, 1),
          [(T, "T")], T)
# q13: А — Eп ∝ cos², Б — vₓ ∝ sin
ab_graphs("graph55_q13", lambda t: math.cos(w * t) ** 2, lambda t: math.sin(w * t), (0, 1), (-1, 1),
          [(T, "T")], T)
# q18: А — Eк ∝ (t − t₁)², Б — vₓ, линейно, ноль в t₁
ab_graphs("graph56_q18", lambda t: 2.2 * (t - 0.4) ** 2, lambda t: 0.6 - 1.5 * t, (0, 0.8), (-0.6, 0.6),
          [(0.4, "t₁")], 1.0)
# q19: А — aᵧ < 0 постоянна, Б — Eк: максимум в начале и конце, ноль в середине
ab_graphs("graph57_q19", lambda t: -0.5, lambda t: 4 * (t - 0.5) ** 2, (-0.8, 0.4), (0, 1),
          [(1.0, "t₀")], 1.0)
# q20: А — Eк ∝ sin² (с нуля), Б — vₓ ∝ −sin
ab_graphs("graph58_q20", lambda t: math.sin(w * t) ** 2, lambda t: -math.sin(w * t), (0, 1), (-1, 1),
          [(T, "T")], T)

fig, ax = canvas(size=(6.4, 2.6))
hatch_v(ax, 0, 0, 1.8)
hatch(ax, 0, 6, 0)
spring(ax, 0, 3.0, 0.45, coils=8)
block(ax, 3.0, 0, 1.4, 0.9, "M")
ax.text(1.5, 0.85, "k", ha="center", fontsize=FONT + 1, style="italic")
ax.annotate("", xy=(5.1, 1.5), xytext=(3.4, 1.5), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
ax.annotate("", xy=(3.4, 1.25), xytext=(5.1, 1.25), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
ax.set_xlim(-0.6, 6.2)
ax.set_ylim(-0.4, 1.9)
save(fig, out("graph59_spring_M"))

fig, ax = canvas(size=(6.4, 2.8))
hatch_v(ax, 0, 0, 1.3)
ax.plot([0, 5.4], [0, 0], color=INK, lw=LW)
spring(ax, 0, 3.15, 0.38, coils=9)
block(ax, 3.15, 0, 0.7, 0.75, fc="#bbf7d0")
for x, nm in ((2.5, "1"), (3.5, "2"), (4.5, "3")):
    ax.plot([x, x], [0, -0.2], color=INK, lw=1.4)
    ax.text(x, -0.25, nm, ha="center", va="top", fontsize=FONT)
ax.annotate("", xy=(5.6, -1.05), xytext=(0, -1.05), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
ax.plot([3.5, 3.5], [-1.15, -0.95], color=INK, lw=1.4)
ax.text(3.5, -1.2, "0", ha="center", va="top", fontsize=FONT)
ax.text(5.6, -1.2, "x", ha="center", va="top", fontsize=FONT, style="italic")
ax.set_xlim(-0.6, 6.0)
ax.set_ylim(-1.7, 1.5)
save(fig, out("graph60_spring_x"))

# ───────────── ЕГЭ №7–8: МКТ и термодинамика ─────────────
p = Plot((0, 4.5), (0, 3.5), size=(5.6, 4.4))
p.axes("V, м³", "p, 10⁴ Па")
p.xticks([1, 2, 3, 4])
p.yticks([1, 2, 3])
p.guide(4, 1)
p.guide(4, 3, to_x=False)
p.line([(4, 1), (4, 3)])
p.arrow_mid((4, 1), (4, 3))
p.point(4, 1, "1", dx=0.12, va="center")
p.point(4, 3, "2", dx=0.12, va="center")
p.finish(out("graph10"))

p = Plot((0, 5), (0, 5), size=(5.2, 4.8), grid_x=rng(0, 5, 1), grid_y=rng(0, 5, 1))
p.axes("V", "p")
p.xticks([2, 4], labels=["2V₀", "4V₀"])
p.yticks([2, 4], labels=["2p₀", "4p₀"])
p.point(1, 3, "1", dx=0.12, dy=0.08)
p.point(3, 4, "2", dx=0.12, dy=0.08)
p.finish(out("graph11"))

p = Plot((0, 2.8), (0, 4), size=(6.6, 4.2))
p.axes("Q, 10⁴ Дж", "t, °C")
p.xticks([0.5, 1, 1.5, 2, 2.5], labels=["", "1", "", "2", ""])
p.line([(0, 1.2), (0.5, 2.4), (2, 2.4), (2.75, 3.6)])
for x, y in ((0.5, 2.4), (1, 2.4), (1.5, 2.4), (2, 2.4), (2.5, 3.2)):
    p.guide(x, y, to_y=False)
p.finish(out("graph12"))

p = Plot((0, 30), (0, 8), size=(6.6, 4.4), grid_x=rng(0, 30, 2.5), grid_y=rng(0, 8, 1))
p.axes("t, мин", "T")
p.xticks([5, 10, 15, 20, 25])
p.line([(0, 2), (5, 4), (15, 4), (25, 7)])
for x, y in ((5, 4), (10, 4), (15, 4), (20, 5.5), (25, 7)):
    p.guide(x, y, to_y=False)
p.finish(out("graph13"))

p = Plot((0, 10.5), (0, 6), size=(6.6, 4.2))
p.axes("Q, кДж", "T")
p.xticks([2, 4, 6, 8, 10], labels=["2", "4", "6", "8", ""])
p.line([(0, 5.6), (2, 1.2), (8, 1.2), (10, 0.5)])
for x in (2, 4, 6, 8):
    p.guide(x, 1.2, to_y=False)
p.finish(out("graph14"))

# T(Q) с разрывами осей: Q 100 → x = 3, 136 → x = 6,6; T 273 → y = 3, 293 → y = 5
qx = lambda q: 3 + (q - 100) * 0.1      # noqa: E731
ty = lambda T_: 3 + (T_ - 273) * 0.1     # noqa: E731
p = Plot((0, 8), (0, 6), size=(6.4, 4.6))
p.axes("Q, кДж", "T, К")
p.xticks([qx(100), qx(136)], labels=["100", "136"])
p.yticks([ty(273), ty(293)], labels=["273", "293"])
p.line([(qx(84), ty(273 - 16 * 20 / 36)), (qx(136), ty(293))])
p.point(qx(100), ty(273))
p.point(qx(136), ty(293))
p.guide(qx(100), ty(273))
p.guide(qx(136), ty(293))
p.break_y(1.0)
p.break_x(1.0)
p.finish(out("graph15"))

p = Plot((0, 80), (0, 500), size=(5.8, 4.6), grid_x=rng(0, 80, 20), grid_y=rng(0, 500, 100))
p.axes("Q, кДж", "T, К")
p.xticks([20, 40, 60, 80])
p.yticks([100, 200, 300, 400, 500])
p.line([(0, 200), (40, 400)])
p.finish(out("graph16"))

p = Plot((0, 3), (0, 3), size=(5.4, 4.2))
p.axes("V", "T")
p.xticks([1, 2], labels=["V₀", "2V₀"])
p.yticks([2], labels=["T₀"])
p.guide(1, 2)
p.guide(2, 2, to_y=False)
p.line([(1, 2), (2, 2)])
p.arrow_mid((1, 2), (2, 2))
p.point(1, 2, "1", dy=0.12, ha="center")
p.point(2, 2, "2", dy=0.12, ha="center")
p.finish(out("graph17"))

p = Plot((0, 0.25), (0, 350), size=(6, 4.4))
p.axes("V, л", "p, кПа")
p.xticks([0.05, 0.10, 0.15, 0.20], labels=["0,05", "0,10", "0,15", "0,20"])
p.yticks([100, 200, 300])
for x in (0.05, 0.10, 0.15, 0.20):
    p.guide(x, 300, to_y=False)
for y in (100, 200, 300):
    p.guide(0.20, y, to_x=False)
p.line([(0.05, 300), (0.20, 100)])
p.arrow_mid((0.05, 300), (0.20, 100), frac=0.5)
p.point(0.05, 300, "1", dy=12, ha="center")
p.point(0.20, 100, "2", dx=0.008, va="center")
p.finish(out("graph18"))

p = Plot((0, 5), (0, 5), size=(5.2, 4.8), grid_x=rng(0, 5, 1), grid_y=rng(0, 5, 1))
p.axes("V", "p")
p.line([(1, 4), (3, 4), (5, 2)])
p.point(1, 4, "1", dx=-0.1, dy=0.12, ha="right")
p.point(3, 4, "2", dy=0.15, ha="center")
p.point(5, 2, "3", dx=0.15, va="center")
p.finish(out("graph19"))

p = Plot((0, 6.5), (0, 6), size=(5.6, 5))
p.axes("T", "p")
a_, b_, c_, d_ = (4, 1.3), (4, 3.7), (4 * 5.0 / 3.7, 5.0), (1.4, 5.0)
p.line([(0, 0), b_], color=MUTED, lw=1.2, dashed=True)
p.line([a_, b_])
p.line([b_, c_])
p.line([c_, d_])
p.curve(lambda T_: 1.3 + 3.7 * ((4 - T_) / 2.6) ** 1.6, 1.4, 4)
for pa, pb in ((a_, b_), (b_, c_), (c_, d_)):
    p.arrow_mid(pa, pb, frac=0.5)
f4 = lambda T_: 1.3 + 3.7 * ((4 - T_) / 2.6) ** 1.6     # noqa: E731  (участок 4, d → a)
p.arrow_mid((1.9, f4(1.9)), (2.0, f4(2.0)), frac=0.5)
for pt in (a_, b_, c_, d_):
    p.point(*pt)
p.text(4.15, 2.4, "1")
p.text(4.75, 4.05, "2")
p.text(3.3, 5.15, "3")
p.text(1.75, 2.6, "4")
p.finish(out("graph21"))
# ЕГЭ №5 №13, №19: y(t) с точками A (минимум), B (на подъёме, ПОСЛЕ перегиба — график уже выпуклый вверх),
# C (максимум), D (сразу после максимума, выше B)
p = Plot((0, 6.0), (0, 3.2), size=(6.2, 4.4))
p.axes("t", "y", origin="0")
f = lambda t: 1.6 - 1.2 * math.cos(1.25 * (t - 1.2))     # noqa: E731  min при t=1,2; max при t≈3,71; перегиб ≈2,46
p.curve(f, 0.45, 4.9)
for nm, t, dx, dy, ha in (("A", 1.2, 0.0, -0.32, "center"), ("B", 3.05, -0.18, 0.05, "right"),
                          ("C", 3.713, 0.0, 0.14, "center"), ("D", 4.2, 0.16, 0.0, "left")):
    p.point(t, f(t), nm, dx=dx, dy=dy, ha=ha, va="center" if nm in "BD" else "bottom")
p.finish(out("graph70_abcd_wave"))

# ЕГЭ №5 №14, №15: шар M на нити, слева летит пуля m
fig, ax = canvas(size=(5.2, 4.4))
hatch(ax, 1.4, 3.2, 4.0, down=False)
ax.plot([2.3, 2.3], [4.0, 1.25], color=INK, lw=1.6)
ball(ax, 2.3, 1.0, 0.26, fc="#bbf7d0")
ax.add_patch(Polygon([(0.1, 0.92), (0.55, 0.92), (0.72, 1.0), (0.55, 1.08), (0.1, 1.08)], closed=True,
                     fc="#94a3b8", ec=INK, lw=1.4, zorder=3))
ax.plot([0.8, 1.95], [1.0, 1.0], color=MUTED, lw=1.2, ls=(0, (5, 4)))
ax.plot([2.65, 3.4], [1.0, 1.0], color=MUTED, lw=1.2, ls=(0, (5, 4)))
ax.text(0.35, 1.25, "m", ha="center", fontsize=FONT + 2, style="italic")
ax.text(2.75, 1.3, "M", ha="left", fontsize=FONT + 2, style="italic")
ax.set_xlim(-0.2, 3.8)
ax.set_ylim(0.4, 4.5)
save(fig, out("graph74_pendulum_bullet"))

# ЕГЭ №5 №12: таблица u(t)
fig, ax = canvas(size=(8, 1.6))
rows = [("t, с", ["0", "1", "2", "3", "4", "5", "6"]), ("u, м/с", ["0", "0,5", "1,0", "1,5", "2,0", "2,5", "3,0"])]
for r, (head, vals) in enumerate(rows):
    y = 0.7 * (1 - r)
    ax.add_patch(Rectangle((0, y), 1.6, 0.7, fc="#e0e7ff", ec=INK, lw=1.4))
    ax.text(0.8, y + 0.35, head, ha="center", va="center", fontsize=FONT)
    for i, v in enumerate(vals):
        ax.add_patch(Rectangle((1.6 + i * 0.9, y), 0.9, 0.7, fc="white", ec=INK, lw=1.4))
        ax.text(1.6 + i * 0.9 + 0.45, y + 0.35, v, ha="center", va="center", fontsize=FONT)
ax.set_xlim(-0.1, 8.0)
ax.set_ylim(-0.1, 1.5)
save(fig, out("graph75_velocity_table"))
print("ok")
