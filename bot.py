import asyncio
import logging
import os
import random
import sqlite3
from datetime import datetime, timedelta

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
from questions import TRACKS

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
CHANNEL_URL = "https://t.me/nicholas_physics"
ADMIN_ID = 881618387

QUIZ_BUTTON = "🧮 Квиз"
STATS_BUTTON = "📊 Статистика"
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=QUIZ_BUTTON), KeyboardButton(text=STATS_BUTTON)]],
    resize_keyboard=True,
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# user_id -> {"track": str, "section": str, "answers": {question_index: chosen_option_index},
#             "order": [shuffled question indices]}
user_sessions: dict[int, dict] = {}


def get_section(track_key: str, section_key: str) -> dict:
    return TRACKS[track_key]["sections"][section_key]


def get_session_section(session: dict) -> dict:
    return get_section(session["track"], session["section"])


def db_section_key(track_key: str, section_key: str) -> str:
    return f"{track_key}:{section_key}"


def section_title(db_key: str) -> str:
    """Резолвит человекочитаемое название раздела по ключу из БД. Новые записи
    хранятся как "track:section" (например "ege:mechanics"); записи, сделанные
    до появления уровней ЕГЭ/ОГЭ, хранят просто "section" — такие считаем ЕГЭ."""
    if ":" in db_key:
        track_key, section_key = db_key.split(":", 1)
        track = TRACKS.get(track_key)
        section = track["sections"].get(section_key) if track else None
        if track and section:
            return f"{track['title']} · {section['title']}"
        return db_key
    section = TRACKS["ege"]["sections"].get(db_key)
    return section["title"] if section else db_key


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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            current_streak INTEGER NOT NULL DEFAULT 0,
            longest_streak INTEGER NOT NULL DEFAULT 0,
            last_activity_date TEXT,
            last_reminder_sent TEXT
        )
        """
    )
    existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(answers)")]
    if "created_at" not in existing_columns:
        conn.execute("ALTER TABLE answers ADD COLUMN created_at TEXT")
    existing_user_columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
    if "current_streak" not in existing_user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN current_streak INTEGER NOT NULL DEFAULT 0")
    if "longest_streak" not in existing_user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN longest_streak INTEGER NOT NULL DEFAULT 0")
    if "last_activity_date" not in existing_user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN last_activity_date TEXT")
    if "last_reminder_sent" not in existing_user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN last_reminder_sent TEXT")
    conn.commit()
    conn.close()


def touch_user(user_id: int, full_name: str) -> None:
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO users (user_id, full_name, first_seen, last_seen) VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET last_seen = excluded.last_seen, full_name = excluded.full_name
        """,
        (user_id, full_name, now, now),
    )
    conn.commit()
    conn.close()


def _days_word(n: int) -> str:
    if 11 <= n % 100 <= 14:
        return "дней"
    last = n % 10
    if last == 1:
        return "день"
    if 2 <= last <= 4:
        return "дня"
    return "дней"


def update_streak(user_id: int) -> int:
    """Обновляет серию пользователя при ответе на вопрос и возвращает текущую
    длину серии. Серия растёт, если пользователь отвечал вчера, сохраняется,
    если уже отвечал сегодня, и сбрасывается до 1 при любом другом раскладе."""
    today = datetime.utcnow().date()
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT current_streak, longest_streak, last_activity_date FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    current_streak, longest_streak, last_date_str = row if row else (0, 0, None)
    current_streak = current_streak or 0
    longest_streak = longest_streak or 0
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date() if last_date_str else None

    if last_date == today:
        pass
    elif last_date == today - timedelta(days=1):
        current_streak += 1
    else:
        current_streak = 1
    longest_streak = max(longest_streak, current_streak)

    conn.execute(
        "UPDATE users SET current_streak = ?, longest_streak = ?, last_activity_date = ? WHERE user_id = ?",
        (current_streak, longest_streak, today.isoformat(), user_id),
    )
    conn.commit()
    conn.close()
    return current_streak


def get_streak(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT current_streak, longest_streak, last_activity_date FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    if not row:
        return {"current": 0, "longest": 0}
    current, longest, last_date_str = row
    current = current or 0
    longest = longest or 0
    if last_date_str:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        if last_date < datetime.utcnow().date() - timedelta(days=1):
            current = 0  # серия прервалась, но ещё не сброшена в БД до следующего ответа
    return {"current": current, "longest": longest}


INACTIVITY_THRESHOLD_DAYS = 3
INACTIVITY_REPEAT_DAYS = 7

MOTIVATIONAL_MESSAGES = [
    "Привет! 👋 Соскучились по формулам? Загляни на пару вопросов — займёт 5 минут, а прогресс не остановится.",
    "🎯 Экзамен не ждёт, а вот пара вопросов по физике точно не займёт много времени. Возвращайся, когда будет момент!",
    "🔥 Даже 3 вопроса в день — это уже привычка, которая сработает на экзамене. Не теряй темп!",
    "📚 Физика не забывается сама — но и не выучивается без повторения. Загляни в квиз, когда будет минутка.",
    "💪 Маленькие шаги каждый день дают большой результат на ЕГЭ. Формулы ждут!",
    "⏰ Давно не заходил — как насчёт освежить пару тем прямо сейчас?",
    "🚀 Каждый решённый вопрос — на шаг ближе к высокому баллу. Не откладывай надолго!",
]


def get_inactive_users() -> list[int]:
    """Пользователи, которые не заходили INACTIVITY_THRESHOLD_DAYS дней и которым
    не отправляли напоминание последние INACTIVITY_REPEAT_DAYS дней (чтобы не
    надоедать тем, кто уже давно ушёл и не отвечает)."""
    now = datetime.utcnow()
    inactive_before = (now - timedelta(days=INACTIVITY_THRESHOLD_DAYS)).isoformat()
    repeat_before = (now - timedelta(days=INACTIVITY_REPEAT_DAYS)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT user_id FROM users
        WHERE last_seen < ?
        AND (last_reminder_sent IS NULL OR last_reminder_sent < ?)
        """,
        (inactive_before, repeat_before),
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]


def mark_reminder_sent(user_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE users SET last_reminder_sent = ? WHERE user_id = ?",
        (datetime.utcnow().isoformat(), user_id),
    )
    conn.commit()
    conn.close()


def get_streak_reminder_users() -> list[tuple[int, int]]:
    """Пользователи, у которых серия жива, но сегодня они ещё не отвечали —
    им и напоминаем не терять серию."""
    yesterday = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT user_id, current_streak FROM users WHERE last_activity_date = ?",
        (yesterday,),
    ).fetchall()
    conn.close()
    return rows


def record_answer(user_id: int, section: str, correct: bool) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO answers (user_id, section, correct, created_at) VALUES (?, ?, ?, ?)",
        (user_id, section, int(correct), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_admin_stats() -> dict:
    now = datetime.utcnow()
    today_start = now.strftime("%Y-%m-%d")
    week_ago = (now - timedelta(days=7)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    new_today = conn.execute("SELECT COUNT(*) FROM users WHERE first_seen >= ?", (today_start,)).fetchone()[0]
    new_week = conn.execute("SELECT COUNT(*) FROM users WHERE first_seen >= ?", (week_ago,)).fetchone()[0]
    active_today = conn.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (today_start,)).fetchone()[0]
    active_week = conn.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (week_ago,)).fetchone()[0]
    total_answers = conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
    answers_today = conn.execute(
        "SELECT COUNT(*) FROM answers WHERE created_at >= ?", (today_start,)
    ).fetchone()[0]
    top_sections = conn.execute(
        "SELECT section, COUNT(*) c FROM answers GROUP BY section ORDER BY c DESC LIMIT 5"
    ).fetchall()
    conn.close()

    return {
        "total_users": total_users,
        "new_today": new_today,
        "new_week": new_week,
        "active_today": active_today,
        "active_week": active_week,
        "total_answers": total_answers,
        "answers_today": answers_today,
        "top_sections": top_sections,
    }


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
    touch_user(message.from_user.id, message.from_user.full_name)
    await message.answer(
        "⚡️ <b>Physics Bot</b>\n"
        "Тренажёр формул по физике\n\n"
        "Проверь, как хорошо ты знаешь формулы: выбирай раздел, отвечай на вопросы "
        "и сразу получай разбор с правильной формулой.\n\n"
        "Пользуйся кнопками внизу 👇",
        reply_markup=MAIN_KEYBOARD,
    )

    channel_builder = InlineKeyboardBuilder()
    channel_builder.button(text="📢 Перейти в канал", url=CHANNEL_URL)
    await message.answer(
        "Кстати — если готовишься к ЕГЭ по физике, загляни на канал "
        "<b>@nicholas_physics</b>: разборы задач, формулы, лайфхаки и мотивация, "
        "чтобы не сдуться на финишной прямой 💪",
        reply_markup=channel_builder.as_markup(),
    )


@dp.message(Command("quiz"))
@dp.message(F.text == QUIZ_BUTTON)
async def cmd_quiz(message: Message) -> None:
    touch_user(message.from_user.id, message.from_user.full_name)
    builder = InlineKeyboardBuilder()
    for key, track in TRACKS.items():
        builder.button(text=track["title"], callback_data=f"track:{key}")
    builder.adjust(1)
    await message.answer("🎯 <b>Выберите уровень подготовки:</b>", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("track:"))
async def choose_track(callback: CallbackQuery) -> None:
    track_key = callback.data.split(":", 1)[1]
    track = TRACKS[track_key]
    sections = track["sections"]
    await callback.answer()

    if not sections:
        await callback.message.answer(
            f"🚧 Раздел «{track['title']}» пока в разработке — вопросы скоро здесь появятся.\n"
            f"А пока загляни в 🎓 ЕГЭ — там уже много вопросов по всем темам!"
        )
        return

    builder = InlineKeyboardBuilder()
    for key, section in sections.items():
        count = len(section["questions"])
        builder.button(
            text=f"{section['title']} · {count} вопросов",
            callback_data=f"section:{track_key}:{key}",
        )
    builder.adjust(1)
    await callback.message.answer(
        f"📚 <b>{track['title']} · выберите раздел:</b>", reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("section:"))
async def choose_section(callback: CallbackQuery) -> None:
    _, track_key, section_key = callback.data.split(":", 2)
    order = list(range(len(get_section(track_key, section_key)["questions"])))
    random.shuffle(order)
    user_sessions[callback.from_user.id] = {
        "track": track_key,
        "section": section_key,
        "answers": {},
        "order": order,
    }
    await callback.answer()
    await show_map(callback.from_user.id, callback.message)


async def show_map(user_id: int, message: Message) -> None:
    session = user_sessions[user_id]
    section = get_session_section(session)
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
    section = get_session_section(session)
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

    q = get_session_section(session)["questions"][index]
    is_correct = choice == q["correct"]
    session["answers"][index] = choice
    record_answer(user_id, db_section_key(session["track"], session["section"]), is_correct)
    touch_user(user_id, callback.from_user.full_name)
    update_streak(user_id)

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

    section = get_session_section(session)
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
    builder.row(InlineKeyboardButton(text="📢 Канал с разборами и мотивацией", url=CHANNEL_URL))

    await callback.message.answer(
        f"🏁 <b>Итог по разделу «{section['title']}»</b>\n\n"
        f"{progress_bar(score, total)}\n"
        f"Результат: <b>{score}/{total}</b> ({percentage}%){note}\n\n"
        f"{result_tier(percentage)}\n\n"
        f"Выбери другой раздел — кнопка 🧮 Квиз\n"
        f"А чтобы не терять мотивацию между тренировками — подпишись на @nicholas_physics 👇",
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
    streak = get_streak(message.from_user.id)
    streak_line = f"🔥 Серия: <b>{streak['current']} {_days_word(streak['current'])}</b> подряд"
    if streak["longest"] > streak["current"]:
        streak_line += f" (рекорд: {streak['longest']})"

    lines = []
    for track_key, track in TRACKS.items():
        sections = track["sections"]
        if not sections:
            continue
        lines.append(f"\n<b>{track['title']}</b>")
        for key, section in sections.items():
            s = section_stats.get(db_section_key(track_key, key))
            if not s and track_key == "ege":
                s = section_stats.get(key)  # записи до появления уровней ЕГЭ/ОГЭ
            if s and s["total"] > 0:
                pct = round(s["correct"] / s["total"] * 100)
                lines.append(f"{section['title']}: <b>{s['correct']}/{s['total']}</b> ({pct}%)")
            else:
                lines.append(f"{section['title']}: <i>нет данных</i>")
    breakdown = "\n".join(lines).strip()

    await message.answer(
        "📊 <b>Твоя статистика</b>\n\n"
        f"{progress_bar(stats['correct'], stats['total'])}\n"
        f"Отвечено вопросов: <b>{stats['total']}</b>\n"
        f"Правильно: <b>{stats['correct']}</b>\n"
        f"Точность: <b>{accuracy}%</b>\n"
        f"{streak_line}\n\n"
        f"{result_tier(accuracy)}\n\n"
        f"📚 <b>По разделам:</b>\n{breakdown}"
    )


@dp.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    stats = get_admin_stats()
    if stats["top_sections"]:
        top_lines = [
            f"{section_title(key)}: <b>{count}</b>" for key, count in stats["top_sections"]
        ]
        top_text = "\n".join(top_lines)
    else:
        top_text = "пока нет данных"

    await message.answer(
        "🛠 <b>Админ-статистика</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
        f"🆕 Новых сегодня: <b>{stats['new_today']}</b> · за неделю: <b>{stats['new_week']}</b>\n"
        f"🔥 Активных сегодня: <b>{stats['active_today']}</b> · за неделю: <b>{stats['active_week']}</b>\n\n"
        f"📝 Всего ответов: <b>{stats['total_answers']}</b>\n"
        f"📝 Ответов сегодня: <b>{stats['answers_today']}</b>\n\n"
        f"🏆 <b>Топ разделов по числу ответов:</b>\n{top_text}"
    )


async def daily_reminder_loop() -> None:
    """Раз в сутки в 16:00 UTC (19:00 МСК):
    1) напоминает пользователям с живой серией, которые ещё не отвечали сегодня, не терять её;
    2) ненавязчиво напоминает о боте тем, кто не заходил INACTIVITY_THRESHOLD_DAYS+ дней,
       не чаще раза в INACTIVITY_REPEAT_DAYS дней, случайным мотивационным сообщением."""
    while True:
        now = datetime.utcnow()
        target = now.replace(hour=16, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

        for user_id, streak in get_streak_reminder_users():
            try:
                await bot.send_message(
                    user_id,
                    f"🔥 Не теряй серию из {streak} {_days_word(streak)} подряд — "
                    f"реши хотя бы один вопрос сегодня, иначе она обнулится!\n\n"
                    f"Жми 🧮 Квиз 👇",
                    reply_markup=MAIN_KEYBOARD,
                )
            except Exception:
                logging.exception("Не удалось отправить напоминание пользователю %s", user_id)

        for user_id in get_inactive_users():
            try:
                await bot.send_message(
                    user_id,
                    random.choice(MOTIVATIONAL_MESSAGES),
                    reply_markup=MAIN_KEYBOARD,
                )
                mark_reminder_sent(user_id)
            except Exception:
                logging.exception("Не удалось отправить напоминание неактивному пользователю %s", user_id)


async def main() -> None:
    init_db()
    asyncio.create_task(daily_reminder_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
