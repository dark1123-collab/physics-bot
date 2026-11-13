"""Блок 3: ЕГЭ №9–12. Результат — tools/redraw/preview/ (имена как в images/)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle, Polygon, Rectangle  # noqa: E402
from style import (ACCENT, FILL, FONT, GRID, INK, LW, MUTED, Circuit, Plot, ball, badge, canvas,  # noqa: E402
                   hatch, save)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")


def out(name):
    return os.path.join(OUT, name + ".png")


def rng(a, b, s):
    n = round((b - a) / s)
    return [round(a + i * s, 6) for i in range(n + 1)]


def cycle(p, pts, closed=True, arrows=True, frac=0.55):
    """Ломаная по точкам (замкнутая), стрелки направления на каждом отрезке."""
    seq = pts + ([pts[0]] if closed else [])
    p.line(seq)
    if arrows:
        for a, b in zip(seq, seq[1:]):
            p.arrow_mid(a, b, frac=frac)
    for q in pts:
        p.point(*q)


def lab(p, x, y, s, dx=0.0, dy=0.0, ha="center", va="center"):
    p.text(x + dx, y + dy, s, ha=ha, va=va, fontsize=FONT)


# ───────────── ЕГЭ №9: газовые законы ─────────────
# V–T: 1(низ) →2(верх) — изотерма, 2→3 — изохора (T растёт), 3→4 — изотерма вниз, 4→1 — изохора
p = Plot((0, 5), (0, 4), size=(5, 4.2))
p.axes("T", "V")
P1, P2, P3, P4 = (1.5, 1.2), (1.5, 3.4), (4.2, 3.4), (4.2, 1.2)
cycle(p, [P1, P2, P3, P4])
lab(p, *P1, "1", dx=-0.25, dy=-0.25)
lab(p, *P2, "2", dx=-0.25, dy=0.25)
lab(p, *P3, "3", dx=0.25, dy=0.25)
lab(p, *P4, "4", dx=0.25, dy=-0.25)
p.finish(out("t9_VT_square"))

# p, кПа — V, л: 1(6;200) 2(8;200) 3(8;100) 4(6;100)
p = Plot((0, 10), (0, 300), size=(6, 4.4), grid_x=rng(0, 10, 2), grid_y=rng(0, 300, 100))
p.axes("V, л", "p, кПа")
p.xticks([2, 4, 6, 8, 10])
p.yticks([100, 200, 300])
cycle(p, [(6, 200), (8, 200), (8, 100), (6, 100)])
lab(p, 6, 200, "1", dx=-0.4, dy=22)
lab(p, 8, 200, "2", dx=0.4, dy=22)
lab(p, 8, 100, "3", dx=0.4, dy=-22)
lab(p, 6, 100, "4", dx=-0.4, dy=-22)
p.finish(out("t9_pV_square_kPa"))

# p–V: 1(V0;2p0) 2(3V0;2p0) 3(3V0;p0) 4(V0;p0)
p = Plot((0, 4), (0, 3), size=(5.6, 4.2))
p.axes("V", "p")
p.xticks([1, 2, 3], labels=["V₀", "2V₀", "3V₀"])
p.yticks([1, 2], labels=["p₀", "2p₀"])
for x, y in ((1, 2), (1, 1), (3, 1)):
    p.guide(x, y)
cycle(p, [(1, 2), (3, 2), (3, 1), (1, 1)])
lab(p, 1, 2, "1", dy=0.22)
lab(p, 3, 2, "2", dy=0.22)
lab(p, 3, 1, "3", dx=0.2, dy=-0.2)
lab(p, 1, 1, "4", dx=-0.2, dy=-0.2)
p.finish(out("t9_pV_rect"))

# T–p: 1(1;T0) → 2(3;3T0) по прямой через 0, 2 → 3(1,5;3T0) при T = const
p = Plot((0, 4), (0, 3.6), size=(5, 4.4))
p.axes("p", "T")
p.yticks([1, 2, 3], labels=["T₀", "2T₀", "3T₀"])
p.line([(0, 0), (1, 1)], color=MUTED, lw=1.2, dashed=True)
p.guide(1, 1, to_x=False)
p.guide(1.5, 3, to_x=False)
cycle(p, [(1, 1), (3, 3), (1.5, 3)], closed=False)
lab(p, 1, 1, "1", dx=-0.05, dy=0.22)
lab(p, 3, 3, "2", dy=0.22)
lab(p, 1.5, 3, "3", dy=0.22)
p.finish(out("t9_Tp_123"))

# p–ρ: 1(ρ0;2p0) 2(ρ0;p0) 3(2ρ0;p0)
p = Plot((0, 2.8), (0, 2.8), size=(4.8, 4.4))
p.axes("ρ", "p")
p.xticks([1, 2], labels=["ρ₀", "2ρ₀"])
p.yticks([1, 2], labels=["p₀", "2p₀"])
p.guide(1, 2)
p.guide(2, 1)
cycle(p, [(1, 2), (1, 1), (2, 1)])
lab(p, 1, 2, "1", dy=0.15)
lab(p, 1, 1, "2", dx=-0.15, dy=0.12)
lab(p, 2, 1, "3", dx=0.12, dy=0.12)
p.finish(out("t9_p_rho_triangle"))

# таблица плотности насыщенного пара
fig, ax = canvas(size=(10, 1.6))
ts = ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25"]
rs = ["1,36", "1,45", "1,54", "1,63", "1,73", "1,83", "1,94", "2,06", "2,18", "2,30"]
for r, (head, vals) in enumerate((("t, °C", ts), ("ρ, 10⁻² кг/м³", rs))):
    y = 0.7 * (1 - r)
    ax.add_patch(Rectangle((0, y), 2.6, 0.7, fc="#e0e7ff", ec=INK, lw=1.3))
    ax.text(1.3, y + 0.35, head, ha="center", va="center", fontsize=FONT - 1)
    for i, v in enumerate(vals):
        ax.add_patch(Rectangle((2.6 + i * 0.85, y), 0.85, 0.7, fc="white", ec=INK, lw=1.3))
        ax.text(2.6 + i * 0.85 + 0.425, y + 0.35, v, ha="center", va="center", fontsize=FONT - 2)
ax.set_xlim(-0.1, 11.2)
ax.set_ylim(-0.1, 1.5)
save(fig, out("t9_vapor_table"))

# p–V по клеткам: 1(2;4) 2(6;4) 3(6;2) 4(1;2); 4–1 на прямой через 0
p = Plot((0, 6), (0, 5), size=(5.2, 4.4), grid_x=rng(0, 6, 1), grid_y=rng(0, 5, 1))
p.axes("V", "p")
p.line([(0, 0), (1, 2)], color=MUTED, lw=1.2, dashed=True)
cycle(p, [(2, 4), (6, 4), (6, 2), (1, 2)])
lab(p, 2, 4, "1", dy=0.3)
lab(p, 6, 4, "2", dx=0.25, dy=0.25)
lab(p, 6, 2, "3", dx=0.25, dy=-0.3)
lab(p, 1, 2, "4", dx=-0.3, dy=0.15)
p.finish(out("t9_pV_trapezoid"))

# V–T по клеткам: A(5;10) B(11;10) C(11;4) D(2;4); DA на прямой через 0
p = Plot((0, 12), (0, 10), size=(5.6, 4.8), grid_x=rng(0, 12, 1), grid_y=rng(0, 10, 1))
p.axes("T", "V")
p.line([(0, 0), (2, 4)], color=MUTED, lw=1.2, dashed=True)
for a, b in (((2, 4), (5, 10)), ((5, 10), (11, 10)), ((11, 10), (11, 4)), ((11, 4), (2, 4))):
    p.line([a, b])
for nm, q, dx, dy in (("A", (5, 10), -0.1, 0.55), ("B", (11, 10), 0.4, 0.5), ("C", (11, 4), 0.45, -0.4),
                      ("D", (2, 4), -0.45, 0.35)):
    p.point(*q)
    lab(p, *q, nm, dx=dx, dy=dy)
p.finish(out("t9_VT_grid"))

# p–V: a → b при 2p0, b → c по изотерме pV = 2p0V0 до (2V0; p0)
p = Plot((0, 2.6), (0, 2.6), size=(5.2, 4.4))
p.axes("V", "p")
p.xticks([1, 2], labels=["V₀", "2V₀"])
p.yticks([1, 2], labels=["p₀", "2p₀"])
p.guide(1, 2)
p.guide(2, 1)
p.line([(2, 0), (2, 2)], color=MUTED, lw=1.1, dashed=True, zorder=1)
p.line([(1, 2), (2, 2)], color=MUTED, lw=1.1, dashed=True, zorder=1)
p.line([(0.3, 2), (1, 2)])
p.arrow_mid((0.3, 2), (1, 2))
p.curve(lambda v: 2 / v, 1, 2)
p.arrow_mid((1.4, 2 / 1.4), (1.45, 2 / 1.45), frac=0.5)
for nm, q, dx, dy in (("a", (0.3, 2), 0, 0.2), ("b", (1, 2), 0, 0.2), ("c", (2, 1), 0.15, 0)):
    p.point(*q)
    lab(p, *q, nm, dx=dx, dy=dy, ha="left" if nm == "c" else "center")
p.finish(out("t9_pV_abc"))

# гелий: 1(1;0,5)→2(5;0,5), 3(1;1,0)→4(3;1,0)
p = Plot((0, 6), (0, 1.25), size=(6, 4), grid_x=rng(0, 5, 1), grid_y=rng(0, 1.25, 0.25))
p.axes("V, л", "p, 10⁵ Па")
p.xticks([1, 2, 3, 4, 5])
p.yticks([0.5, 1.0], labels=["0,5", "1,0"])
cycle(p, [(1, 0.5), (5, 0.5)], closed=False)
cycle(p, [(1, 1.0), (3, 1.0)], closed=False)
lab(p, 1, 0.5, "1", dy=0.09)
lab(p, 5, 0.5, "2", dy=0.09)
lab(p, 1, 1.0, "3", dy=0.09)
lab(p, 3, 1.0, "4", dy=0.09)
p.finish(out("t9_pV_helium"))

# n(t): рост (участок 1), затем постоянна (участок 2)
p = Plot((0, 6), (0, 4), size=(5.4, 3.8))
p.axes("t", "n")
p.curve(lambda t: 1.2 + 2.2 * (1 - math.exp(-1.6 * t)) if t < 2.6 else 1.2 + 2.2 * (1 - math.exp(-1.6 * 2.6)),
        0, 5.6)
lab(p, 0.35, 3.05, "1")
lab(p, 3.8, 3.75, "2")
p.finish(out("t9_n_t"))

# два изобарных процесса неона по клеткам: 1 — при 2 клетках, V 1→5; 2 — при 4 клетках, V 2→4
p = Plot((0, 6), (0, 4), size=(5.6, 4), grid_x=rng(0, 6, 1), grid_y=rng(0, 4, 1))
p.axes("V", "p")
cycle(p, [(1, 2), (5, 2)], closed=False)
cycle(p, [(2, 4), (4, 4)], closed=False)
lab(p, 3, 2, "1", dy=-0.32)
lab(p, 3, 4, "2", dy=-0.32)
p.finish(out("t9_pV_two_neon"))

# p–T: AB и CD — на прямых через 0, BC и DA — вертикали; A→B→C→D→A
p = Plot((0, 5.4), (0, 7.6), size=(4.8, 5))
p.axes("T", "p")
A, B = (1.5, 2.4), (4.5, 7.2)
C = (4.5, 2.0)
D = (1.5, 2.0 * 1.5 / 4.5)
p.line([(0, 0), A], color=MUTED, lw=1.1, dashed=True)
p.line([(0, 0), D], color=MUTED, lw=1.1, dashed=True)
cycle(p, [A, B, C, D])
for nm, q, dx, dy in (("A", A, -0.3, 0.1), ("B", B, 0, 0.45), ("C", C, 0.3, -0.25), ("D", D, 0.3, -0.35)):
    lab(p, *q, nm, dx=dx, dy=dy)
p.finish(out("t9_pT_ABCD"))

# p–V по клеткам: 1(V0;2p0) → 2(2V0;2p0) → 3(2V0;3p0); V0 = 3 клетки, p0 = 2 клетки
p = Plot((0, 4), (0, 3.5), size=(5.8, 4.2), grid_x=rng(0, 4, 1 / 3), grid_y=rng(0, 3.5, 0.5))
p.axes("V", "p")
p.xticks([1, 2], labels=["V₀", "2V₀"])
p.yticks([1, 2, 3], labels=["p₀", "2p₀", "3p₀"])
p.guide(1, 2)
p.guide(2, 3)
cycle(p, [(1, 2), (2, 2), (2, 3)], closed=False)
lab(p, 1, 2, "1", dx=-0.15, dy=-0.25)
lab(p, 2, 2, "2", dx=0.18, dy=-0.25)
lab(p, 2, 3, "3", dx=0.18, dy=0.15)
p.finish(out("t9_pV_123"))

# V–T: AB и CD — на прямых через 0, BC — вертикаль вниз, DA — горизонталь влево
p = Plot((0, 6.2), (0, 7.4), size=(4.8, 5))
p.axes("T", "V")
A, B = (2, 2.5), (5, 6.25)
C = (5, 3.5)
D = (2.5 / 0.7, 2.5)
p.line([(0, 0), A], color=MUTED, lw=1.1, dashed=True)
p.line([(0, 0), D], color=MUTED, lw=1.1, dashed=True)
cycle(p, [A, B, C, D])
for nm, q, dx, dy in (("A", A, -0.3, 0.1), ("B", B, 0.25, 0.3), ("C", C, 0.3, 0.1), ("D", D, 0.15, -0.4)):
    lab(p, *q, nm, dx=dx, dy=dy)
p.finish(out("t9_VT_ABCD_arrows"))

# p–Ēк: 1 → 2 по прямой через 0, 2 → 3 вертикально вверх
p = Plot((0, 5), (0, 5.4), size=(4.6, 4.6))
p.axes("Ēк", "p")
p.line([(0, 0), (1, 1)], color=MUTED, lw=1.1, dashed=True)
cycle(p, [(1, 1), (3, 3), (3, 5)], closed=False)
lab(p, 1, 1, "1", dx=-0.2, dy=0.25)
lab(p, 3, 3, "2", dx=0.25)
lab(p, 3, 5, "3", dx=0.25)
p.finish(out("t9_p_Ek"))

# p–V: изохора 1 → 2 вверх
p = Plot((0, 5), (0, 5), size=(4.4, 4.4))
p.axes("V", "p")
cycle(p, [(2, 1.2), (2, 4.3)], closed=False)
lab(p, 2, 1.2, "1", dx=0.25)
lab(p, 2, 4.3, "2", dx=0.25)
p.finish(out("t9_pV_isochor"))

# p–ρ: 3(ρ0;p0) → 1(ρ0;4p0) → (четверть эллипса) → 2(2ρ0;p0) → 3
p = Plot((0, 2.6), (0, 4.6), size=(4.4, 5))
p.axes("ρ", "p")
p.xticks([1, 2], labels=["ρ₀", "2ρ₀"])
p.yticks([1, 4], labels=["p₀", "4p₀"])
p.guide(1, 4, to_x=False)
p.guide(2, 1)
p.line([(1, 1), (1, 4)])
p.arrow_mid((1, 1), (1, 4))
p.curve(lambda r: 1 + 3 * math.sqrt(max(0.0, 1 - (r - 1) ** 2)), 1, 2)
a1 = 1.6
p.arrow_mid((a1, 1 + 3 * math.sqrt(1 - (a1 - 1) ** 2)), (a1 + 0.02, 1 + 3 * math.sqrt(1 - (a1 + 0.02 - 1) ** 2)),
            frac=0.5)
p.line([(2, 1), (1, 1)])
p.arrow_mid((2, 1), (1, 1))
for nm, q, dx, dy in (("1", (1, 4), 0, 0.25), ("2", (2, 1), 0.15, -0.25), ("3", (1, 1), -0.15, -0.25)):
    p.point(*q)
    lab(p, *q, nm, dx=dx, dy=dy)
p.finish(out("t9_p_rho_circle"))


# t(Q): графики нагревания (в масштабе)
def tq(name, pts, xt, yt, xlabel, marks=(), size=(6.4, 4.4), ylim=None, guides=(), xlabels=None):
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    p = Plot((0, max(xs) * 1.05), ylim or (0, max(ys) * 1.1), size=size)
    p.axes(xlabel, "t, °C")
    p.xticks(xt, labels=xlabels)
    p.yticks(yt)
    for x, y in guides:
        p.guide(x, y)
    p.line(pts)
    for nm, x, y in marks:
        p.point(x, y, nm, dy=(p.ylim[1] - p.ylim[0]) * 0.03, ha="center")
    p.finish(out(name))


tq("t9_tQ_50_80", [(0, 0), (40, 50), (80, 50), (120, 80), (140, 80)], [40, 80, 100, 120], [50, 65, 80],
   "Q, кДж", marks=[("1", 40, 50), ("2", 80, 50), ("3", 120, 80)],
   guides=[(40, 50), (80, 50), (100, 65), (120, 80)])
tq("t9_tQ_40_180", [(0, 0), (40, 40), (80, 40), (180, 80)], [40, 80, 180], [40, 80], "Q, кДж",
   marks=[("1", 40, 40), ("2", 80, 40), ("3", 180, 80)], guides=[(40, 40), (80, 40), (180, 80)])
tq("t9_tQ_iron", [(0, 0), (70, 1535), (100, 1535), (230, 3000)], [70, 100, 230], [1535, 3000], "Q, кДж",
   marks=[("1", 70, 1535), ("2", 100, 1535), ("3", 230, 3000)], guides=[(70, 1535), (100, 1535), (230, 3000)])
# серебро: старт при 20 °C (твёрдое), плавление 961 °C (240 → 327 Дж), кипение 2170 °C с 695 Дж
tq("t9_tQ_silver", [(0, 20), (240, 961), (327, 961), (695, 2170), (790, 2170)], [240, 327, 695], [961, 2170],
   "Q, Дж", marks=[("1", 240, 961), ("2", 327, 961), ("3", 695, 2170)],
   guides=[(240, 961), (327, 961), (695, 2170)], ylim=(0, 2450))


# ───────────── ЕГЭ №10 ─────────────
def vessel(name, piston_y=3.0, ball_=False, rod=False, liquid=0.0, arrow=False, size=(3.6, 4.2)):
    fig, ax = canvas(size=size)
    w, h = 3.0, 4.2
    ax.add_patch(Rectangle((0, 0), w, piston_y, fc="#f1f5f9", ec="none", zorder=0))     # газ
    if liquid:
        ax.add_patch(Rectangle((0, 0), w, liquid, fc="#93c5fd", ec="none", zorder=1))
        ax.plot([0, w], [liquid, liquid], color=ACCENT, lw=1.6, zorder=2)
    ax.plot([0, 0, w, w], [h, 0, 0, h], color=INK, lw=LW * 1.3, zorder=3)
    ax.add_patch(Rectangle((0.03, piston_y), w - 0.06, 0.32, fc="#64748b", ec=INK, lw=1.6, zorder=4))
    if rod:
        ax.add_patch(Rectangle((w / 2 - 0.1, piston_y + 0.32), 0.2, 1.3, fc="#64748b", ec=INK, lw=1.4, zorder=4))
    if ball_:
        ball(ax, w / 2, 0.45, 0.42, fc="#cbd5e1")
    if arrow:
        ax.annotate("", xy=(w + 0.45, piston_y + 0.2), xytext=(w + 0.45, piston_y + 1.6),
                    arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2, mutation_scale=18))
    ax.set_xlim(-0.4, w + 0.9)
    ax.set_ylim(-0.3, h + (1.8 if rod else 0.3))
    save(fig, out(name))


vessel("t10_piston")
vessel("t10_ball_cylinder", ball_=True)
vessel("t10_ball_piston", ball_=True, piston_y=3.2)
vessel("t10_piston_vapor", piston_y=2.9, rod=True, liquid=0.8, arrow=True)


def through0(name, xl, yl):
    p = Plot((0, 5), (0, 5), size=(4.4, 4.4))
    p.axes(xl, yl)
    p.line([(0, 0), (1.5, 1.5)], color=MUTED, lw=1.1, dashed=True)
    cycle(p, [(1.5, 1.5), (4, 4)], closed=False)
    lab(p, 1.5, 1.5, "1", dx=-0.25, dy=0.25)
    lab(p, 4, 4, "2", dx=-0.25, dy=0.25)
    p.finish(out(name))


through0("t10_U_p", "p", "U")
through0("t10_U_V", "V", "U")
through0("t10_U_V_2", "V", "U")

p = Plot((0, 5), (0, 5), size=(4.4, 4.4))
p.axes("T", "p")
cycle(p, [(1.2, 1.6), (3.4, 1.6), (3.4, 4.2)], closed=False)
lab(p, 1.2, 1.6, "1", dy=-0.35)
lab(p, 3.4, 1.6, "2", dx=0.25, dy=-0.3)
lab(p, 3.4, 4.2, "3", dx=0.25)
p.finish(out("t10_pT_123"))


def two_proc(name, a, b):
    """Два графика А и Б рядом. a/b = (xlabel, ylabel, [(точки)], [подписи], через_ноль)."""
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    for ax, (xl, yl, pts, names, zero), L in ((axs[0], a, "А"), (axs[1], b, "Б")):
        ax.axis("off")
        for i in range(9):
            ax.plot([i * 0.5, i * 0.5], [0, 4], color=GRID, lw=0.8, zorder=0)
            ax.plot([0, 4], [i * 0.5, i * 0.5], color=GRID, lw=0.8, zorder=0)
        ax.annotate("", xy=(4.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
        ax.annotate("", xy=(0, 4.5), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
        ax.text(4.5, -0.2, xl, ha="center", va="top", fontsize=FONT)
        ax.text(0.15, 4.5, yl, ha="left", va="center", fontsize=FONT)
        ax.text(-0.1, -0.1, "0", ha="right", va="top", fontsize=FONT - 1)
        if zero:
            ax.plot([0, pts[-1][0]], [0, pts[-1][1]], color=MUTED, lw=1.1, ls=(0, (4, 4)))
        ax.plot([q[0] for q in pts], [q[1] for q in pts], color=ACCENT, lw=LW + 0.6, zorder=3)
        m = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
        ax.annotate("", xy=(m[0] + (pts[1][0] - pts[0][0]) * 0.01, m[1] + (pts[1][1] - pts[0][1]) * 0.01), xytext=m,
                    arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0, mutation_scale=22), zorder=4)
        for q, nm in zip(pts, names):
            ax.plot(*q, "o", color=ACCENT, ms=7, zorder=5)
            # подпись ставим с той стороны точки, где нет линии
            below = zero and q == pts[-1]
            ax.text(q[0] + 0.2, q[1] + (-0.45 if below else 0.15), nm, fontsize=FONT)
        badge(ax, -0.8, 4.3, L)
        ax.set_xlim(-1.3, 5.0)
        ax.set_ylim(-0.7, 4.9)
        ax.set_aspect("equal")
    save(fig, out(name))


# А: V–T, изотермическое сжатие 1 → 2; Б: p–T, изобарное охлаждение 3 → 4
two_proc("t10_match_VT_pT", ("T", "V", [(2.5, 3.5), (2.5, 1.0)], ["1", "2"], False),
         ("T", "p", [(4.0, 2.0), (2.0, 2.0)], ["3", "4"], False))
# А: V–T, изохорное нагревание 1 → 2; Б: p–V, по прямой через 0 из 3 в 4 (сжатие)
two_proc("t10_match_VT_pV", ("T", "V", [(1.0, 3.0), (4.0, 3.0)], ["1", "2"], False),
         ("V", "p", [(4.0, 4.0), (1.0, 1.0)], ["3", "4"], True))

# t(Q) — схема с участками ΔQ₁…ΔQ₅ и Δt₁…Δt₃
p = Plot((0, 7.4), (0, 5), size=(6.8, 4.4))
p.axes("Q", "t", origin="")
xs = [0, 1.2, 3.0, 4.5, 5.6, 7.0]
ys = [0.8, 2.3, 2.3, 4.1, 4.1, 5.0]
p.line(list(zip(xs, ys)))
for x, y in zip(xs[1:], ys[1:]):
    p.guide(x, y, to_y=False)
for y in (0.8, 2.3, 4.1, 5.0):
    p.line([(0, y), (7.0, y)], color=MUTED, lw=1.0, dashed=True, zorder=1)
for i in range(5):
    p.text((xs[i] + xs[i + 1]) / 2, -0.35, f"ΔQ{'₁₂₃₄₅'[i]}", ha="center", va="top")
for (y1, y2), s in (((0.8, 2.3), "Δt₁"), ((2.3, 4.1), "Δt₂"), ((4.1, 5.0), "Δt₃")):
    p.text(-0.15, (y1 + y2) / 2, s, ha="right", va="center")
p.finish(out("t10_tQ_dQ"), extra=0.8)

# «незамерзайка»: (0;−120) → (30;−60) → (60;−60) → (210;120) → (240;120)
p = Plot((0, 240), (-120, 240), size=(6.4, 5), grid_x=rng(0, 240, 30), grid_y=rng(-120, 240, 60))
p.axes("Q, кДж", "t, °C", yneg=-120)
p.xticks([60, 120, 180, 240])
p.yticks([-120, -60, 60, 120, 180, 240])
p.line([(0, -120), (30, -60), (60, -60), (210, 120), (240, 120)])
p.finish(out("t10_antifreeze"))

# ───────────── ЕГЭ №11 ─────────────
fig, ax = canvas(size=(6, 1.6))
for r, (head, vals) in enumerate((("U, В", ["2", "4", "6", "8"]), ("I, А", ["0,5", "1,0", "1,5", "2,0"]))):
    y = 0.7 * (1 - r)
    ax.add_patch(Rectangle((0, y), 1.4, 0.7, fc="#e0e7ff", ec=INK, lw=1.4))
    ax.text(0.7, y + 0.35, head, ha="center", va="center", fontsize=FONT)
    for i, v in enumerate(vals):
        ax.add_patch(Rectangle((1.4 + i * 1.1, y), 1.1, 0.7, fc="white", ec=INK, lw=1.4))
        ax.text(1.4 + i * 1.1 + 0.55, y + 0.35, v, ha="center", va="center", fontsize=FONT)
ax.set_xlim(-0.1, 5.9)
ax.set_ylim(-0.1, 1.5)
save(fig, out("table1"))

p = Plot((0, 2.4), (0, 12), size=(5, 4.4), grid_x=rng(0, 2, 0.5), grid_y=rng(0, 10, 2.5))
p.axes("U, кВ", "I, мА")
p.xticks([1, 2])
p.yticks([5, 10])
p.line([(0, 0), (2, 10)])
p.finish(out("graph22"))

p = Plot((0, 16), (0, 5), size=(5.6, 3.6))
p.axes("t, с", "I, А")
p.xticks([5, 10, 15])
p.yticks([4])
p.guide(5, 4)
p.guide(10, 4, to_y=False)
cycle(p, [(0, 0), (5, 4), (10, 4), (15, 0)], closed=False, arrows=False)
p.finish(out("graph23"))


def rheostat(c, x1, x2, y, label):
    c.resistor_on(x1, x2, y, None)
    xc = (x1 + x2) / 2
    c.ax.text(xc, y - 0.6, label, ha="center", va="top", fontsize=FONT + 1)   # ниже стрелки реостата
    c.ax.annotate("", xy=(xc + 0.55, y + 0.45), xytext=(xc - 0.55, y - 0.45),
                  arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, mutation_scale=14), zorder=5)


# ЕГЭ №11 №13: последовательно 1 Ом, 2 Ом (с вольтметром), 3 Ом, реостат 0–6 Ом, ключ, источник
c = Circuit(size=(9.4, 4.2))
c.battery(0, 1.2, vertical=True)
c.wire((0, 1.28), (0, 2.6), (0.6, 2.6))
c.key(0.6, 2.6, 1.6)
c.resistor_on(1.6, 3.8, 2.6, "1 Ом", label_side=-1)
c.resistor_on(3.8, 6.0, 2.6, "2 Ом", label_side=-1)
c.resistor_on(6.0, 8.2, 2.6, "3 Ом", label_side=-1)
c.node(3.8, 2.6)
c.node(6.0, 2.6)
c.wire((3.8, 2.6), (3.8, 3.5))
c.meter_on(3.8, 6.0, 3.5, "V")
c.wire((6.0, 3.5), (6.0, 2.6))
c.wire((8.2, 2.6), (8.6, 2.6), (8.6, 0.2), (5.2, 0.2))
rheostat(c, 3.0, 5.2, 0.2, "0–6 Ом")
c.wire((3.0, 0.2), (0, 0.2), (0, 1.12))
c.ax.text(4.9, 3.95, "1,6 В", ha="center", va="bottom", fontsize=FONT, color=ACCENT)
c.save(out("img1"))

# ЕГЭ №11 №14: ключ, амперметр, R?, 2 Ом, 3 Ом, реостат; вольтметр — на участке R? + 2 Ом + 3 Ом
c = Circuit(size=(9.8, 4.4))
c.battery(0, 1.2, vertical=True)
c.wire((0, 1.28), (0, 2.6), (0.5, 2.6))
c.key(0.5, 2.6, 1.4)
c.meter_on(1.4, 2.6, 2.6, "A")
c.resistor_on(2.6, 4.6, 2.6, "?", label_side=-1)
c.resistor_on(4.6, 6.6, 2.6, "2 Ом", label_side=-1)
c.resistor_on(6.6, 8.6, 2.6, "3 Ом", label_side=-1)
c.node(2.6, 2.6)
c.node(8.6, 2.6)
c.wire((2.6, 2.6), (2.6, 3.6))
c.meter_on(2.6, 8.6, 3.6, "V")
c.wire((8.6, 3.6), (8.6, 2.6))
c.wire((8.6, 2.6), (9.0, 2.6), (9.0, 0.2), (5.6, 0.2))
rheostat(c, 3.4, 5.6, 0.2, "0–6 Ом")
c.wire((3.4, 0.2), (0, 0.2), (0, 1.12))
c.ax.text(1.95, 2.0, "0,7 А", ha="center", va="top", fontsize=FONT, color=ACCENT)
c.ax.text(5.6, 4.05, "4,2 В", ha="center", va="bottom", fontsize=FONT, color=ACCENT)
c.save(out("img2"))

# sheme5: ток I справа налево: верх R+R, низ R+R (вольтметр на правом нижнем), затем R слева
c = Circuit(size=(9.4, 3.8))
c.wire((0, 1.5), (0.5, 1.5))
c.ax.annotate("", xy=(0, 1.5), xytext=(0.5, 1.5), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6))
c.ax.text(0.25, 1.75, "I", ha="center", fontsize=FONT + 1, style="italic", color=ACCENT)
c.resistor_on(0.5, 2.4, 1.5, "R")
c.node(2.4, 1.5)
c.wire((2.4, 1.5), (2.4, 2.7))
c.resistor_on(2.4, 4.4, 2.7, "R")
c.resistor_on(4.4, 6.4, 2.7, "R")
c.wire((2.4, 1.5), (2.4, 0.3))
c.resistor_on(2.4, 4.4, 0.3, "R", label_side=-1)
c.resistor_on(4.4, 6.4, 0.3, "R", label_side=-1)
c.wire((6.4, 2.7), (6.4, 0.3))
c.node(6.4, 1.5)
c.node(4.4, 0.3)
c.node(6.4, 0.3)
c.wire((4.4, 0.3), (4.4, 1.2))
c.meter_on(4.4, 6.4, 1.2, "V")
c.wire((6.4, 1.2), (6.4, 1.2))
c.wire((6.4, 1.5), (7.4, 1.5))
c.ax.annotate("", xy=(6.9, 1.5), xytext=(7.4, 1.5), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6))
c.ax.text(7.15, 1.75, "I", ha="center", fontsize=FONT + 1, style="italic", color=ACCENT)
c.save(out("sheme5"))

# sheme6: I0 → R → [верх: R+R, вольтметр на обоих] ∥ [низ: R + (R+R ∥ R+R)]
c = Circuit(size=(9.4, 4.6))
c.wire((0, 1.6), (0.4, 1.6))
c.ax.annotate("", xy=(0.4, 1.6), xytext=(0, 1.6), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6))
c.ax.text(0.15, 1.85, "I₀", ha="center", fontsize=FONT + 1, style="italic", color=ACCENT)
c.resistor_on(0.4, 2.0, 1.6, "R")
c.node(2.0, 1.6)
c.wire((2.0, 1.6), (2.0, 2.9))
c.node(2.4, 2.9)
c.wire((2.0, 2.9), (2.4, 2.9))
c.resistor_on(2.4, 4.4, 2.9, "R", label_side=-1)
c.resistor_on(4.4, 6.4, 2.9, "R", label_side=-1)
c.node(6.4, 2.9)
c.wire((2.4, 2.9), (2.4, 3.9))
c.meter_on(2.4, 6.4, 3.9, "V")
c.wire((6.4, 3.9), (6.4, 2.9), (7.4, 2.9), (7.4, 1.6))
c.wire((2.0, 1.6), (2.0, 0.9))
c.resistor_on(2.0, 3.6, 0.9, "R", label_side=-1)
c.node(3.6, 0.9)
c.wire((3.6, 0.9), (3.6, 1.4))
c.resistor_on(3.6, 5.4, 1.4, "R")
c.resistor_on(5.4, 7.0, 1.4, "R")
c.wire((3.6, 0.9), (3.6, 0.3))
c.resistor_on(3.6, 5.4, 0.3, "R", label_side=-1)
c.resistor_on(5.4, 7.0, 0.3, "R", label_side=-1)
c.wire((7.0, 1.4), (7.0, 0.3))
c.node(7.0, 0.9)
c.wire((7.0, 0.9), (7.4, 0.9), (7.4, 1.6))
c.node(7.4, 1.6)
c.wire((7.4, 1.6), (8.3, 1.6))
c.save(out("sheme6"))

# ───────────── ЕГЭ №12 ─────────────
p = Plot((0, 20), (0, 30), size=(6, 4.2), grid_x=rng(0, 20, 5), grid_y=rng(0, 30, 10))
p.axes("t, с", "I, мА")
p.xticks([5, 10, 15, 20])
p.yticks([10, 20, 30])
p.line([(0, 0), (5, 30), (10, 20), (15, 20), (20, 0)])
p.finish(out("t12_I_t_mA"))

p = Plot((0, 5), (0, 5), size=(5.2, 4.4), grid_x=rng(0, 5, 1), grid_y=rng(0, 5, 1))
p.axes("t, с", "I, А")
p.xticks([1, 2, 3, 4, 5])
p.yticks([1, 2, 3, 4, 5])
p.line([(0, 1), (1, 1), (3, 4), (5, 4)])
p.finish(out("t12_I_t_moment"))

p = Plot((0, 4), (0, 6), size=(4.8, 4.4), grid_x=rng(0, 4, 1), grid_y=rng(0, 6, 2))
p.axes("t, с", "I, А")
p.xticks([2, 4])
p.yticks([2, 4, 6])
p.line([(0, 0), (4, 6)])
p.finish(out("t12_I_t_flux"))

p = Plot((0, 6), (-8, 8), size=(6, 4.8))
p.axes("t, с", "Ф, Вб", yneg=-8)
p.yticks([-8, -4, 4, 8])
pts = [(0, 0), (1.1, 8), (2.1, -4), (4.0, -4), (5.5, 0)]
p.line(pts)
for q in pts:
    p.point(*q)
p.guide(1.1, 8, to_y=False)
p.guide(2.1, -4, to_y=False)
p.guide(4.0, -4, to_y=False)
for s, x, y in (("1", 0.35, 5.0), ("2", 1.85, 4.0), ("3", 3.05, -5.1), ("4", 4.95, -3.1)):
    p.text(x, y, s, ha="center", va="center", color=INK)
p.finish(out("t12_flux_segments"))
print("ok")
