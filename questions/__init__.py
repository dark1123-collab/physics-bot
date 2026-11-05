"""Сборка всех вопросов бота из папки questions/.

Как устроено:
  questions/ege/task01.py … task26.py  — прототипы задания ЕГЭ с этим номером
  questions/ege/theory_*.py            — теория и формулы по темам (раздел «📐 Формулы и теория»)
  questions/oge/task01.py … task19.py,
  questions/oge/task20m/20t/20e.py     — то же для ОГЭ (№20–22 разбиты по темам)
  questions/grades_7_9.py              — 7–9 класс (разделы по темам)

Чтобы добавить задачу — допишите её в QUESTIONS нужного файла. Код бота трогать не нужно:
номер с задачами сам появится в меню, пустой номер показывается с пометкой «скоро».
Формат вопроса — см. questions/README.md.
"""
import hashlib
import importlib

from .grades_7_9 import GRADES_7_9_SECTIONS

# (ключ группы, кнопка в меню, номера заданий)
EGE_PARTS = [
    ("part1", "📝 Часть 1 · №1–20", [*range(1, 21)]),
    ("part2", "✍️ Часть 2 · №21–26", [*range(21, 27)]),
]
OGE_PARTS = [
    ("part1", "📝 Часть 1 · №1–16", [*range(1, 17)]),
    ("part2", "✍️ Часть 2 · №17–22", [*range(17, 20), "20m", "20t", "20e"]),
]
EGE_THEORY = [
    "mechanics", "circular_motion", "thermodynamics", "electrostatics",
    "current", "magnetism", "optics", "quantum", "nuclear",
]
OGE_THEORY = ["mechanics", "thermal", "electromagnetism", "quantum"]

THEORY_GROUP = ("theory", "📐 Формулы и теория")


def _task_label(number) -> str:
    return "№20–22" if str(number).startswith("20") and not isinstance(number, int) else f"№{number}"


def _build_track(track: str, parts: list, theory_topics: list) -> tuple[dict, list]:
    sections = {}
    menu = []
    for group, button, numbers in parts:
        menu.append({"key": group, "title": button})
        for n in numbers:
            key = f"task{n:02d}" if isinstance(n, int) else f"task{n}"
            mod = importlib.import_module(f".{track}.{key}", __name__)
            label = _task_label(n)
            sections[key] = {
                "title": f"{label} {mod.TITLE}",
                "short": f"{label} {mod.SHORT}",
                # Текст кнопки в сетке номеров: только номер (у №20–22 ОГЭ — значок темы).
                "button": f"{getattr(mod, 'ICON', '')} {label}".strip(),
                "questions": mod.QUESTIONS,
                "group": group,
            }
    menu.append({"key": THEORY_GROUP[0], "title": THEORY_GROUP[1]})
    for topic in theory_topics:
        mod = importlib.import_module(f".{track}.theory_{topic}", __name__)
        sections[f"theory_{topic}"] = {
            "title": mod.TITLE,
            "short": mod.TITLE,
            "questions": mod.QUESTIONS,
            "group": THEORY_GROUP[0],
        }
    return sections, menu


def _build_aggregates(sections: dict) -> None:
    """Добавляет два автосборных раздела: "Хард марафон" (все вопросы вперемешку)
    и "Только формулы" (вопросы, где правильный ответ — формула, т.е. содержит "=")."""
    all_questions = [q for s in sections.values() for q in s["questions"]]
    sections["hard"] = {"title": "🔥 Хард марафон", "questions": all_questions}
    sections["formulas"] = {
        "title": "📐 Только формулы",
        "questions": [q for q in all_questions if "=" in q["options"][q["correct"]]],
    }


EGE_SECTIONS, EGE_MENU = _build_track("ege", EGE_PARTS, EGE_THEORY)
_build_aggregates(EGE_SECTIONS)

OGE_SECTIONS, OGE_MENU = _build_track("oge", OGE_PARTS, OGE_THEORY)
_build_aggregates(OGE_SECTIONS)

_build_aggregates(GRADES_7_9_SECTIONS)

# TRACKS — верхний уровень выбора в боте: ЕГЭ / ОГЭ / 7–9 класс.
# "menu" — группы (Часть 1, Часть 2, Теория); у 7–9 класса групп нет, разделы идут списком.
TRACKS = {
    "ege": {"title": "🎓 ЕГЭ", "sections": EGE_SECTIONS, "menu": EGE_MENU},
    "oge": {"title": "📘 ОГЭ", "sections": OGE_SECTIONS, "menu": OGE_MENU},
    "grades_7_9": {"title": "📗 7-9 класс", "sections": GRADES_7_9_SECTIONS},
}

AGGREGATE_SECTIONS = ("hard", "formulas")

# Постоянный id вопроса — по тексту (номера в списке меняются при добавлении задач).
# Нужен «Работе над ошибками»: в stats.db ответ пишется вместе с id вопроса.
# QUESTION_INDEX: id -> (трек, раздел, вопрос); раздел — «родной», не марафон.
QUESTION_INDEX = {}
for _track_key, _track in TRACKS.items():
    for _section_key, _section in _track["sections"].items():
        if _section_key in AGGREGATE_SECTIONS:
            continue
        for _q in _section["questions"]:
            _qid = f"{_track_key}:" + hashlib.sha1(_q["text"].encode("utf-8")).hexdigest()[:10]
            _q.setdefault("id", _qid)
            QUESTION_INDEX.setdefault(_q["id"], (_track_key, _section_key, _q))

# Разделы, которые были до перехода на номера заданий. Старые ответы в stats.db
# записаны с этими ключами — по ним статистика показывается с понятными названиями.
LEGACY_SECTION_TITLES = {
    "ege:mechanics": "🎓 ЕГЭ · ⚙️ Механика (старый раздел)",
    "ege:thermodynamics": "🎓 ЕГЭ · 🌡 МКТ и термодинамика (старый раздел)",
    "ege:electrostatics": "🎓 ЕГЭ · ⚡ Электростатика (старый раздел)",
    "ege:current": "🎓 ЕГЭ · 🔌 Электрический ток (старый раздел)",
    "ege:circular_motion": "🎓 ЕГЭ · 🔄 Кинематика окружности и колебания (старый раздел)",
    "ege:magnetism": "🎓 ЕГЭ · 🧲 Магнетизм и ЭМИ (старый раздел)",
    "ege:optics": "🎓 ЕГЭ · 🔬 Оптика (старый раздел)",
    "ege:quantum": "🎓 ЕГЭ · 💡 Кванты (старый раздел)",
    "ege:nuclear": "🎓 ЕГЭ · ☢️ Ядерная физика (старый раздел)",
    "oge:mechanics": "📘 ОГЭ · ⚙️ Механические явления (старый раздел)",
    "oge:thermal": "📘 ОГЭ · 🌡 Тепловые явления (старый раздел)",
    "oge:electromagnetism": "📘 ОГЭ · ⚡ Электромагнитные явления (старый раздел)",
    "oge:quantum": "📘 ОГЭ · ☢️ Квантовые явления (старый раздел)",
}
# Совсем старые записи (до появления ЕГЭ/ОГЭ) хранятся без префикса — это ЕГЭ.
for _key, _title in list(LEGACY_SECTION_TITLES.items()):
    if _key.startswith("ege:"):
        LEGACY_SECTION_TITLES[_key[4:]] = _title
LEGACY_SECTION_TITLES.update({"hard": "🎓 ЕГЭ · 🔥 Хард марафон", "formulas": "🎓 ЕГЭ · 📐 Только формулы"})
