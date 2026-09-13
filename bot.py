import asyncio
import logging
import os
import random
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from formula_render import render_formula
from questions import SECTIONS

# Токен читается из переменной окружения BOT_TOKEN (так задаётся на хостинге).
# Для удобного локального запуска, если переменной окружения нет, берётся
# значение из local_config.py — этот файл не попадает в git (см. .gitignore).
try:
    from local_config import BOT_TOKEN as _LOCAL_BOT_TOKEN
except ImportError:
    _LOCAL_BOT_TOKEN = None

BOT_TOKEN = os.environ.get("BOT_TOKEN") or _LOCAL_BOT_TOKEN
if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден токен бота. Задайте переменную окружения BOT_TOKEN "
        "или создайте local_config.py с BOT_TOKEN = \"...\"."
    )

DB_PATH = "stats.db"
OPTION_LETTERS = ["А", "Б", "В", "Г", "Д", "Е"]

QUIZ_BUTTON = "🧮 Квиз"
STATS_BUTTON = "📊 Статистика"
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=QUIZ_BUTTON), KeyboardButton(text=STATS_BUTTON)]],
    resize_keyboard=True,
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# user_id -> {"section": str, "answers": {question_index: chosen_option_index}, "order": [shuffled question indices]}
user_sessions: dict[int, dict] = {}


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            section TEXT NOT NULL,
            correct INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def record_answer(user_id: int, section: str, correct: bool) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO answers (user_id, section, correct) VALUES (?, ?, ?)",
        (user_id, section, int(correct)),
    )
    conn.commit()
    conn.close()


def get_stats(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(correct), 0) FROM answers WHERE user_id = ?",
        (user_id,),
    )
    total, correct = cur.fetchone()
    conn.close()
    return {"total": total, "correct": correct}


def get_section_stats(user_id: int) -> dict[str, dict]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT section, COUNT(*), COALESCE(SUM(correct), 0) FROM answers WHERE user_id = ? GROUP BY section",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return {section: {"total": total, "correct": correct} for section, total, correct in rows}


def progress_bar(done: int, total: int, length: int = 10) -> str:
    if total <= 0:
        return "⬜" * length
    filled = max(0, min(length, round(done / total * length)))
    return "🟩" * filled + "⬜" * (length - filled)


def result_tier(percentage: int) -> str:
    if percentage == 100:
        return "🏆 Идеально! Формулы знаешь на отлично."
    if percentage >= 80:
        return "🥇 Отличный результат!"
    if percentage >= 60:
        return "🥈 Хорошо, но есть куда расти."
    if percentage >= 40:
        return "🥉 Неплохо, но стоит повторить теорию."
    return "📚 Стоит подтянуть формулы — попробуй ещё раз."


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "⚡️ <b>Physics Bot</b>\n"
        "Тренажёр формул по физике\n\n"
        "Проверь, как хорошо ты знаешь формулы: выбирай раздел, отвечай на вопросы "
        "и сразу получай разбор с правильной формулой.\n\n"
        "Пользуйся кнопками внизу 👇",
        reply_markup=MAIN_KEYBOARD,
    )


@dp.message(Command("quiz"))
@dp.message(F.text == QUIZ_BUTTON)
async def cmd_quiz(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    for key, section in SECTIONS.items():
        count = len(section["questions"])
        builder.button(text=f"{section['title']} · {count} вопросов", callback_data=f"section:{key}")
    builder.adjust(1)
    await message.answer("📚 <b>Выберите раздел:</b>", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("section:"))
async def choose_section(callback: CallbackQuery) -> None:
    section_key = callback.data.split(":", 1)[1]
    order = list(range(len(SECTIONS[section_key]["questions"])))
    random.shuffle(order)
    user_sessions[callback.from_user.id] = {"section": section_key, "answers": {}, "order": order}
    await callback.answer()
    await show_map(callback.from_user.id, callback.message)


async def show_map(user_id: int, message: Message) -> None:
    session = user_sessions[user_id]
    section = SECTIONS[session["section"]]
    questions = section["questions"]
    answers = session["answers"]
    order = session["order"]

    builder = InlineKeyboardBuilder()
    for position, i in enumerate(order):
        if i in answers:
            is_correct = answers[i] == questions[i]["correct"]
            label = f"{'✅' if is_correct else '❌'}{position + 1}"
        else:
            label = str(position + 1)
        builder.button(text=label, callback_data=f"q:{i}")
    builder.adjust(5)
    builder.row(InlineKeyboardButton(text="🏁 Завершить и посмотреть итог", callback_data="finish"))

    correct = sum(1 for i, c in answers.items() if c == questions[i]["correct"])
    text = (
        f"<b>{section['title']}</b>\n"
        f"Отвечено: {len(answers)}/{len(questions)} · Правильно: {correct}\n\n"
        f"📋 Выберите вопрос (порядок перемешан):"
    )
    await message.answer(text, reply_markup=builder.as_markup())


def nav_buttons(index: int, order: list[int]) -> list[InlineKeyboardButton]:
    position = order.index(index)
    buttons = []
    if position > 0:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"q:{order[position - 1]}"))
    buttons.append(InlineKeyboardButton(text="📋 Список", callback_data="map"))
    if position < len(order) - 1:
        buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"q:{order[position + 1]}"))
    return buttons


async def send_question_message(message: Message, q: dict, text: str, markup) -> None:
    image_path = q.get("image")
    if image_path:
        await message.answer_photo(photo=FSInputFile(image_path), caption=text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def show_question(user_id: int, message: Message, index: int) -> None:
    session = user_sessions[user_id]
    section = SECTIONS[session["section"]]
    questions = section["questions"]
    order = session["order"]
    total = len(questions)
    position = order.index(index)
    q = questions[index]
    answers = session["answers"]

    header = f"<b>{section['title']}</b> · Вопрос {position + 1}/{total}\n\n❓ {q['text']}"

    if index in answers:
        chosen = answers[index]
        is_correct = chosen == q["correct"]
        if is_correct:
            result_line = "✅ <b>Отвечено верно</b>"
        else:
            result_line = (
                f"❌ <b>Отвечено неверно.</b> Ваш ответ: "
                f"{OPTION_LETTERS[chosen]}) {q['options'][chosen]}\n"
                f"Правильный ответ: <b>{OPTION_LETTERS[q['correct']]}) {q['options'][q['correct']]}</b>"
            )
        text = f"{header}\n\n{result_line}\n\n💡 {q['explanation']}"
        source = q.get("source")
        if source:
            text += f"\n\n📚 <i>Источник: {source}</i>"
        builder = InlineKeyboardBuilder()
        builder.row(*nav_buttons(index, order))
        await send_question_message(message, q, text, builder.as_markup())

        formula_latex = q.get("formula")
        if formula_latex:
            await message.answer_photo(
                photo=FSInputFile(render_formula(formula_latex)),
                caption="📐 <b>Формула</b>",
            )

        solution_image = q.get("solution_image")
        if solution_image:
            await message.answer_photo(
                photo=FSInputFile(solution_image),
                caption="✏️ <b>Решение</b>",
            )
    else:
        builder = InlineKeyboardBuilder()
        for i, option in enumerate(q["options"]):
            builder.button(text=f"{OPTION_LETTERS[i]}) {option}", callback_data=f"ans:{index}:{i}")
        builder.adjust(1)
        builder.row(*nav_buttons(index, order))
        await send_question_message(message, q, header, builder.as_markup())


@dp.callback_query(F.data.startswith("q:"))
async def goto_question(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    if user_id not in user_sessions:
        await callback.answer("Начните тест заново: нажмите «Квиз»", show_alert=True)
        return
    index = int(callback.data.split(":", 1)[1])
    await callback.answer()
    await show_question(user_id, callback.message, index)


@dp.callback_query(F.data == "map")
async def goto_map(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    if user_id not in user_sessions:
        await callback.answer("Начните тест заново: нажмите «Квиз»", show_alert=True)
        return
    await callback.answer()
    await show_map(user_id, callback.message)


@dp.callback_query(F.data.startswith("ans:"))
async def check_answer(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        await callback.answer("Начните тест заново: нажмите «Квиз»", show_alert=True)
        return

    _, index_str, choice_str = callback.data.split(":")
    index = int(index_str)
    choice = int(choice_str)

    if index in session["answers"]:
        await callback.answer("Вы уже отвечали на этот вопрос")
        return

    q = SECTIONS[session["section"]]["questions"][index]
    is_correct = choice == q["correct"]
    session["answers"][index] = choice
    record_answer(user_id, session["section"], is_correct)

    await callback.answer("Верно! ✅" if is_correct else "Неверно ❌")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await show_question(user_id, callback.message, index)


@dp.callback_query(F.data == "finish")
async def finish_quiz(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        await callback.answer("Начните тест заново: нажмите «Квиз»", show_alert=True)
        return
    await callback.answer()

    section = SECTIONS[session["section"]]
    questions = section["questions"]
    total = len(questions)
    answers = session["answers"]
    score = sum(1 for i, c in answers.items() if c == questions[i]["correct"])
    percentage = round(score / total * 100) if total else 0

    note = ""
    if len(answers) < total:
        note = f"\n\n⚠️ Отвечено на {len(answers)} из {total} вопросов."

    builder = InlineKeyboardBuilder()
    builder.button(text="📋 К списку вопросов", callback_data="map")
    builder.adjust(1)

    await callback.message.answer(
        f"🏁 <b>Итог по разделу «{section['title']}»</b>\n\n"
        f"{progress_bar(score, total)}\n"
        f"Результат: <b>{score}/{total}</b> ({percentage}%){note}\n\n"
        f"{result_tier(percentage)}\n\n"
        f"Выбери другой раздел — кнопка 🧮 Квиз",
        reply_markup=builder.as_markup(),
    )


@dp.message(Command("stats"))
@dp.message(F.text == STATS_BUTTON)
async def cmd_stats(message: Message) -> None:
    stats = get_stats(message.from_user.id)
    if stats["total"] == 0:
        await message.answer(
            "У тебя пока нет статистики.\n\nНачни тест командой /quiz — и здесь появятся цифры."
        )
        return

    accuracy = round(stats["correct"] / stats["total"] * 100)
    section_stats = get_section_stats(message.from_user.id)

    lines = []
    for key, section in SECTIONS.items():
        s = section_stats.get(key)
        if s and s["total"] > 0:
            pct = round(s["correct"] / s["total"] * 100)
            lines.append(f"{section['title']}: <b>{s['correct']}/{s['total']}</b> ({pct}%)")
        else:
            lines.append(f"{section['title']}: <i>нет данных</i>")
    breakdown = "\n".join(lines)

    await message.answer(
        "📊 <b>Твоя статистика</b>\n\n"
        f"{progress_bar(stats['correct'], stats['total'])}\n"
        f"Отвечено вопросов: <b>{stats['total']}</b>\n"
        f"Правильно: <b>{stats['correct']}</b>\n"
        f"Точность: <b>{accuracy}%</b>\n\n"
        f"{result_tier(accuracy)}\n\n"
        f"📚 <b>По разделам:</b>\n{breakdown}"
    )


async def main() -> None:
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
