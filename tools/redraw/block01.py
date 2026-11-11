"""Блок 1: фото и рисунки «от руки» → собственные рисунки. Результат — tools/redraw/preview/."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle  # noqa: E402
from style import (ACCENT, FILL, FONT, INK, LW, barometer, dial_meter, dynamometer, save,  # noqa: E402
                   thermometer_h)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")


def out(name):
    return os.path.join(OUT, name + ".png")


# ЕГЭ №19 №1: вольтметр, клеммы «−» и «6 В», 3,4 В (по нижней шкале 1,7 В — ловушка)
fig, _ = dial_meter(scales=[(-2, 6, 2, 10), (-1, 3, 1, 10)], needle_value=3.4, scale_index=0,
                    letter="V", terminals=["−", "3 В", "6 В"], connected=["−", "6 В"])
save(fig, out("t19_voltmeter_div"))

# ОГЭ №15 №14: тот же прибор, клеммы «−» и «3 В», 1,4 В (по верхней шкале 2,8 — ловушка)
fig, _ = dial_meter(scales=[(-2, 6, 2, 10), (-1, 3, 1, 10)], needle_value=1.4, scale_index=1,
                    letter="V", terminals=["−", "3 В", "6 В"], connected=["−", "3 В"])
save(fig, out("o15_voltmeter_3v"))

# ОГЭ №15 №6: медицинский термометр, 39,6 °C, цена деления 0,1
fig, _ = thermometer_h(35, 42, 39.6, minor=10, mark=37)
save(fig, out("o15_med_thermometer"))

# ОГЭ №15 №17: барометр, 755 мм рт. ст., внутренняя шкала — гПа (≈1007)
fig, _ = barometer(755, "гПа")
save(fig, out("o15_barometer"))

# ЕГЭ №19 №5: барометр, 745 мм рт. ст., нижняя (внутренняя) шкала — кПа (≈99,3)
fig, _ = barometer(745, "кПа")
save(fig, out("t19_barometer"))

# ОГЭ №18 №9: три школьных динамометра с ограничителем внизу шкалы
fig, ax = plt.subplots(figsize=(7, 6.4))
ax.set_aspect("equal")
ax.axis("off")
# пружины разной жёсткости — допустимое растяжение (длина шкалы) разное, ограничители на разной высоте
stops = [dynamometer(ax, 0.0, 6.0, 1, 0.5, 5, 4.0, "1 Н"),
         dynamometer(ax, 2.8, 6.0, 4, 1, 4, 3.0, "4 Н"),
         dynamometer(ax, 5.6, 6.0, 5, 1, 5, 2.2, "5 Н")]
ax.annotate("ограничитель", xy=(5.65, stops[2]), xytext=(6.9, stops[2] - 1.3), fontsize=FONT - 1,
            ha="left", va="center", arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6))
ax.set_xlim(-1.2, 9.8)
ax.set_ylim(-1.8, 6.6)
save(fig, out("o18_dynamometer_stop"))


# ОГЭ №4 №13: бутылка с шариком в горячей воде (рис. 1) и надутый шарик (рис. 2)
def bottle(ax, x, y, balloon):
    body = [(x - 0.55, y), (x + 0.55, y), (x + 0.55, y + 1.5), (x + 0.2, y + 2.1), (x + 0.2, y + 2.6),
            (x - 0.2, y + 2.6), (x - 0.2, y + 2.1), (x - 0.55, y + 1.5)]
    ax.add_patch(Polygon(body, closed=True, fc="#ecfdf5", ec=INK, lw=LW, zorder=3))
    ax.add_patch(Rectangle((x - 0.24, y + 2.55), 0.48, 0.22, fc="#fde68a", ec=INK, lw=1.4, zorder=4))
    if balloon == "flat":
        ax.add_patch(Ellipse((x + 0.22, y + 3.08), 0.5, 0.75, angle=-35, fc="#fde68a", ec=INK, lw=1.6, zorder=4))
    else:
        ax.add_patch(Ellipse((x, y + 3.85), 1.9, 2.2, fc="#fde68a", ec=INK, lw=LW, zorder=4))


fig, ax = plt.subplots(figsize=(9, 4.6))
ax.set_aspect("equal")
ax.axis("off")
# сосуд с горячей водой
ax.add_patch(Rectangle((-2.1, -0.2), 4.2, 1.75, fc=FILL, ec="none", zorder=1))
ax.plot([-2.2, -2.2, 2.2, 2.2], [2.0, -0.3, -0.3, 2.0], color=INK, lw=LW, zorder=2)
ax.plot([-2.1, 2.1], [1.55, 1.55], color=ACCENT, lw=1.4, zorder=2)
bottle(ax, 0, -0.1, "flat")
for dx in (-1.5, -1.1, 1.1, 1.5):            # пар над горячей водой
    ax.plot([-0.0 + dx + 0.1 * (i % 2) for i in range(5)], [1.75 + 0.18 * i for i in range(5)], color="#94a3b8",
            lw=1.3)
ax.text(0, -0.75, "Рис. 1", ha="center", va="top", fontsize=FONT + 1)
bottle(ax, 5.2, -0.1, "full")
ax.text(5.2, -0.75, "Рис. 2", ha="center", va="top", fontsize=FONT + 1)
ax.set_xlim(-2.6, 6.8)
ax.set_ylim(-1.4, 5.1)
save(fig, out("o4_83506"))
print("ok")
