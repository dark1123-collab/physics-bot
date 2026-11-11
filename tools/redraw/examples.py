"""Образцы перерисованных картинок → tools/redraw/preview/."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import Circuit, dial_meter, graph, save  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")

# 1. ЕГЭ №1: vₓ(t), от 15 м/с до −15 м/с за 20 с, затем до 15 м/с к 30 с
fig, ax = graph([(0, 15), (20, -15), (30, 15)], "t, с", "vₓ, м/с",
                xticks=[0, 5, 10, 15, 20, 25, 30], yticks=[-15, -10, -5, 0, 5, 10, 15])
save(fig, os.path.join(OUT, "t1_v_15_to_m15.png"))

# 2. ОГЭ №20–22: R1 с вольтметром параллельно, затем R2 ∥ R3, амперметр в ветви R3
c = Circuit(size=(9, 3.4))
c.terminal(0, 0)
c.wire((0, 0), (1.0, 0)); c.node(1.0, 0)
c.resistor_on(1.0, 3.6, 0, "R₁"); c.node(3.6, 0)
c.wire((1.0, 0), (1.0, -1.0)); c.meter_on(1.0, 3.6, -1.0, "V"); c.wire((3.6, -1.0), (3.6, 0))
c.wire((3.6, 0), (4.4, 0)); c.node(4.4, 0)
c.wire((4.4, 0), (4.4, 0.75)); c.resistor_on(4.4, 7.9, 0.75, "R₂"); c.wire((7.9, 0.75), (7.9, 0))
c.wire((4.4, 0), (4.4, -0.75)); c.resistor_on(4.4, 6.6, -0.75, "R₃", label_side=-1)
c.meter_on(6.6, 7.9, -0.75, "A"); c.wire((7.9, -0.75), (7.9, 0))
c.node(7.9, 0); c.wire((7.9, 0), (8.8, 0)); c.terminal(8.8, 0)
c.save(os.path.join(OUT, "o20e_three_conductors.png"))

# 3. ЕГЭ №19: вольтметр вместо фото — две шкалы (−2…6 В и −1…3 В), подключён к «−» и «6 В», 3,4 В
fig, ax = dial_meter(scales=[(-2, 6, 2, 10), (-1, 3, 1, 10)], needle_value=3.4, scale_index=0,
                     letter="V", terminals=["−", "3 В", "6 В"], connected=["−", "6 В"])
save(fig, os.path.join(OUT, "t19_voltmeter_div.png"))
print("ok")
