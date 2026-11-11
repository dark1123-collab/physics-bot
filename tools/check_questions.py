"""Проверка банка вопросов перед коммитом/выкладкой.

Запуск из корня проекта:  python tools/check_questions.py
Код выхода 1, если найдены ошибки (предупреждения выход не роняют).
"""
import io
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import questions as Q  # noqa: E402

CAPTION_LIMIT = 1024   # подпись к фото: длиннее — бот шлёт текст отдельным сообщением
MESSAGE_LIMIT = 4096
BUTTON_LIMIT = 64

errors, warnings = [], []


def visible(text):
    return re.sub(r"<[^>]+>", "", text)


def norm(text):
    return re.sub(r"\W+", "", visible(text).lower())


def variant_code(line):
    """'Вариант 2: 1, 3, 4' -> '134'; 'Вариант 1: Давление — 2, Объём — 3' -> '23'."""
    body = line.split(":", 1)[1]
    if "—" in body:
        return "".join(re.findall(r"—\s*(\d)", body))
    return "".join(re.findall(r"\d", body))


try:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.mathtext import math_to_image
except ImportError:  # на сервере matplotlib есть, локально — тоже; на всякий случай
    math_to_image = None

seen = defaultdict(list)
total = 0
for track_key, track in Q.TRACKS.items():
    for key, section in track["sections"].items():
        if key in ("hard", "formulas"):
            continue
        for i, q in enumerate(section["questions"]):
            total += 1
            where = f"{track_key}/{key}#{i + 1}"
            opts = q.get("options", [])
            if len(opts) != 4 or len(set(opts)) != 4:
                errors.append(f"{where}: нужно 4 разных варианта ответа")
            if not isinstance(q.get("correct"), int) or not 0 <= q["correct"] < len(opts):
                errors.append(f"{where}: неверный индекс correct")
                continue
            for o in opts:
                if len(o) > BUTTON_LIMIT:
                    errors.append(f"{where}: вариант длиннее {BUTTON_LIMIT} символов: {o[:30]}…")
            for field in ("image", "solution_image"):
                if q.get(field) and not os.path.exists(q[field]):
                    errors.append(f"{where}: нет файла {q[field]}")
            for path in q.get("solution_images") or []:
                if not os.path.exists(path):
                    errors.append(f"{where}: нет файла {path}")
            # Полное решение (2 часть) бот режет по абзацам — один абзац должен влезать в сообщение.
            for para in (q.get("solution") or "").split("\n\n"):
                if len(visible(para)) > MESSAGE_LIMIT - 200:
                    errors.append(f"{where}: абзац решения длиннее {MESSAGE_LIMIT - 200} симв.")
            if not q.get("explanation"):
                errors.append(f"{where}: нет объяснения")
            # Текст уходит в Telegram как HTML: «a < b» ломает разметку — писать «&lt;».
            for field in ("text", "explanation", "source", "solution"):
                value = q.get(field) or ""
                if re.search(r"<(?!/?(b|i|u|s|pre|code|a)( [^<>]*)?>)", value):
                    errors.append(f"{where}: в {field} знак «<» — замените на &lt;")
                if re.search(r"&(?!(#\d+|#x[0-9a-fA-F]+|lt|gt|amp|quot);)", value):
                    errors.append(f"{where}: в {field} знак «&» — замените на &amp;")
            for o in opts:
                if re.search(r"&(lt|gt|amp|quot);|</?b>", o):
                    errors.append(f"{where}: HTML в варианте ответа (на кнопке покажется как есть): {o}")
            text_len = len(visible(q["text"]))
            if text_len > MESSAGE_LIMIT - 200:
                errors.append(f"{where}: текст {text_len} симв. — не влезет в сообщение")
            if q.get("formula"):
                f = q["formula"]
                if not (f.startswith("$") and f.endswith("$")):
                    errors.append(f"{where}: formula должна быть в $...$")
                elif math_to_image:
                    try:
                        math_to_image(f, io.BytesIO(), format="png")
                    except Exception as e:  # noqa: BLE001
                        errors.append(f"{where}: формула не рендерится: {e}")
            if opts and opts[0] == "Вариант 1":
                lines = re.findall(r"^Вариант \d:.*$", q["text"], flags=re.M)
                m = re.search(r"Код:\s*(\d+)", q["explanation"])
                if not lines:
                    pass  # варианты записаны полными утверждениями (ОГЭ №5) — код сверять нечем
                elif len(lines) != 4:
                    errors.append(f"{where}: в тексте не 4 строки «Вариант N: …»")
                elif not m:
                    warnings.append(f"{where}: в объяснении нет «Код: …»")
                elif variant_code(lines[q["correct"]]) != m.group(1):
                    errors.append(
                        f"{where}: код в объяснении {m.group(1)} ≠ правильному варианту "
                        f"{variant_code(lines[q['correct']])}"
                    )
                codes = [variant_code(l) for l in lines]
                if len(set(codes)) != len(codes):
                    errors.append(f"{where}: два одинаковых варианта кода")
            seen[norm(q["text"])].append(where)

for where_list in seen.values():
    if len(where_list) > 1:
        sections = [w.split("#")[0] for w in where_list]
        if len(set(sections)) < len(sections):
            # Повтор внутри одного раздела — почти наверняка вопросы дописали в файл дважды.
            errors.append("один вопрос дважды в разделе: " + ", ".join(where_list))
        else:
            warnings.append("одинаковый текст: " + ", ".join(where_list))

print(f"Проверено вопросов: {total}")
for w in warnings:
    print("⚠", w)
for e in errors:
    print("✗", e)
print("OK" if not errors else f"Ошибок: {len(errors)}")
sys.exit(1 if errors else 0)
