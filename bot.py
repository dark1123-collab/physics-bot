import asyncio
import logging
import os
import random
import re
import secrets
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    KeyboardButton,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from formula_render import render_formula
from questions import LEGACY_SECTION_TITLES, TRACKS

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

DONATE_BUTTON = "⭐ Поддержать бота"
DONATE_AMOUNTS = [10, 25, 50, 100, 250, 500]  # варианты суммы в Telegram Stars

QUIZ_BUTTON = "🧮 Квиз"
STATS_BUTTON = "📊 Статистика"
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=QUIZ_BUTTON), KeyboardButton(text=STATS_BUTTON)],
        [KeyboardButton(text=DONATE_BUTTON)],
    ],
    resize_keyboard=True,
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# user_id -> {"track": str, "section": str, "answers": {question_index: chosen_option_index},
#             "order": [shuffled question indices],
#             "sid": метка сессии — пишется в callback кнопок вопросов}
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
    # Разделы до перехода на номера заданий (ege:mechanics и т.п.) и совсем старые
    # записи без префикса — названия из LEGACY_SECTION_TITLES.
    return LEGACY_SECTION_TITLES.get(db_key, db_key)


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
    # Донаты звёздами. charge_id нужен для возврата (refundStarPayment).
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT,
            stars INTEGER NOT NULL,
            charge_id TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            refunded INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def record_donation(user_id: int, full_name: str, stars: int, charge_id: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO donations (user_id, full_name, stars, charge_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, full_name, stars, charge_id, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def mark_donation_refunded(charge_id: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE donations SET refunded = 1 WHERE charge_id = ?", (charge_id,))
    conn.commit()
    conn.close()


def get_donation_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    count, stars = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(stars), 0) FROM donations WHERE refunded = 0"
    ).fetchone()
    last = conn.execute(
        "SELECT full_name, stars, created_at FROM donations WHERE refunded = 0 ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return {"count": count, "stars": stars, "last": last}


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


TRACKS_TEXT = "🎯 <b>Выберите уровень подготовки:</b>"


def tracks_markup():
    builder = InlineKeyboardBuilder()
    for key, track in TRACKS.items():
        builder.button(text=track["title"], callback_data=f"track:{key}")
    builder.adjust(1)
    return builder.as_markup()


async def show_menu(callback: CallbackQuery, text: str, markup) -> None:
    """Навигация по меню квиза меняет одно и то же сообщение, а не шлёт новые.
    Если отредактировать нельзя (старое сообщение, картинка) — отправляем новое."""
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=markup)


@dp.message(Command("quiz"))
@dp.message(F.text == QUIZ_BUTTON)
async def cmd_quiz(message: Message) -> None:
    touch_user(message.from_user.id, message.from_user.full_name)
    await message.answer(TRACKS_TEXT, reply_markup=tracks_markup())


@dp.callback_query(F.data == "tracks")
async def back_to_tracks(callback: CallbackQuery) -> None:
    await callback.answer()
    await show_menu(callback, TRACKS_TEXT, tracks_markup())


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
    menu = track.get("menu")
    if menu:
        # ЕГЭ/ОГЭ: сначала группы (Часть 1, Часть 2, Теория), потом марафон и формулы.
        for group in menu:
            count = sum(
                len(s["questions"]) for s in sections.values() if s.get("group") == group["key"]
            )
            builder.button(
                text=f"{group['title']} · {count}", callback_data=f"group:{track_key}:{group['key']}"
            )
        top_level = {k: s for k, s in sections.items() if "group" not in s}
    else:
        top_level = sections
    for key, section in top_level.items():
        count = len(section["questions"])
        builder.button(
            text=f"{section['title']} · {count} вопросов",
            callback_data=f"section:{track_key}:{key}",
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="tracks"))
    await show_menu(callback, f"📚 <b>{track['title']} · выберите раздел:</b>", builder.as_markup())


@dp.callback_query(F.data.startswith("group:"))
async def choose_group(callback: CallbackQuery) -> None:
    _, track_key, group_key = callback.data.split(":", 2)
    track = TRACKS[track_key]
    group = next(g for g in track["menu"] if g["key"] == group_key)
    await callback.answer()

    group_sections = [(k, s) for k, s in track["sections"].items() if s.get("group") == group_key]
    builder = InlineKeyboardBuilder()

    if group_key == "theory":
        # Темы теории — по одной в строке, названия короткие и целиком помещаются.
        for key, section in group_sections:
            builder.button(
                text=f"{section['title']} · {len(section['questions'])}",
                callback_data=f"section:{track_key}:{key}",
            )
        builder.adjust(1)
        text = f"📚 <b>{track['title']} · {group['title']}</b>\n\nВыберите тему:"
    else:
        # Номера заданий: полные названия — списком в тексте, кнопки — компактная
        # сетка из одних номеров (в кнопке помещается ~10 символов, названия обрезались).
        lines = []
        for key, section in group_sections:
            count = len(section["questions"])
            if count:
                lines.append(f"{section['title']} — <b>{count}</b>")
                builder.button(text=section["button"], callback_data=f"section:{track_key}:{key}")
            else:
                lines.append(f"<i>{section['title']} — скоро</i>")
                builder.button(text=f"{section['button']} ⏳", callback_data="soon")
        builder.adjust(4 if len(group_sections) > 8 else 3)
        text = (
            f"📚 <b>{track['title']} · {group['title']}</b>\n\n"
            + "\n".join(lines)
            + "\n\n👇 Выберите номер задания (⏳ — задачи скоро появятся):"
        )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"track:{track_key}"))
    await show_menu(callback, text, builder.as_markup())


@dp.callback_query(F.data == "soon")
async def soon_section(callback: CallbackQuery) -> None:
    await callback.answer("🚧 Задачи по этому номеру скоро появятся!", show_alert=True)


@dp.callback_query(F.data.startswith("section:"))
async def choose_section(callback: CallbackQuery) -> None:
    _, track_key, section_key = callback.data.split(":", 2)
    section = TRACKS.get(track_key, {}).get("sections", {}).get(section_key)
    if not section or not section["questions"]:
        # Кнопка из старого сообщения: после перехода на номера заданий таких разделов нет.
        await callback.answer("Разделы обновились — открой меню заново: «🧮 Квиз»", show_alert=True)
        return
    order = list(range(len(section["questions"])))
    random.shuffle(order)
    user_sessions[callback.from_user.id] = {
        "track": track_key,
        "section": section_key,
        "answers": {},
        "order": order,
        "sid": secrets.token_hex(3),
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
        builder.button(text=label, callback_data=f"q:{session['sid']}:{i}")
    builder.adjust(5)
    builder.row(InlineKeyboardButton(text="🏁 Завершить и посмотреть итог", callback_data="finish"))

    correct = sum(1 for i, c in answers.items() if c == questions[i]["correct"])
    text = (
        f"<b>{section['title']}</b>\n"
        f"Отвечено: {len(answers)}/{len(questions)} · Правильно: {correct}\n\n"
        f"📋 Выберите вопрос (порядок перемешан):"
    )
    await message.answer(text, reply_markup=builder.as_markup())


def nav_buttons(index: int, session: dict) -> list[InlineKeyboardButton]:
    order = session["order"]
    sid = session["sid"]
    position = order.index(index)
    buttons = []
    if position > 0:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"q:{sid}:{order[position - 1]}"))
    buttons.append(InlineKeyboardButton(text="📋 Список", callback_data="map"))
    if position < len(order) - 1:
        buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"q:{sid}:{order[position + 1]}"))
    return buttons


STALE_BUTTON_TEXT = "Это кнопка из прошлого теста. Открой вопрос из текущего списка: «📋 Список»"


def parse_session_callback(callback: CallbackQuery) -> tuple[dict, list[int]] | None:
    """Разбирает callback вида "q:<sid>:<i>" / "ans:<sid>:<i>:<c>". Кнопки содержат
    метку сессии, чтобы нажатие в старом сообщении (из другого раздела или прошлого
    прохода) не открывало и не засчитывало чужой вопрос текущего теста."""
    session = user_sessions.get(callback.from_user.id)
    parts = callback.data.split(":")[1:]
    if not session or len(parts) < 2 or parts[0] != session["sid"]:
        return None
    try:
        return session, [int(p) for p in parts[1:]]
    except ValueError:
        return None


CAPTION_LIMIT = 1024


def visible_length(html_text: str) -> int:
    return len(re.sub(r"<[^>]+>", "", html_text))


async def send_question_message(message: Message, q: dict, text: str, markup) -> None:
    image_path = q.get("image")
    if image_path and visible_length(text) <= CAPTION_LIMIT:
        await message.answer_photo(photo=FSInputFile(image_path), caption=text, reply_markup=markup)
    elif image_path:
        await message.answer_photo(photo=FSInputFile(image_path))
        await message.answer(text, reply_markup=markup)
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
        builder.row(*nav_buttons(index, session))
        markup = builder.as_markup()

        # После ответа могут прийти ещё картинки: формула и решение (например, фото
        # собранной установки в ОГЭ №17). Кнопки навигации вешаем на последнее
        # сообщение, чтобы они не уезжали вверх над картинками.
        extras = []
        formula_latex = q.get("formula")
        if formula_latex:
            extras.append((render_formula(formula_latex), "📐 <b>Формула</b>"))
        solution_image = q.get("solution_image")
        if solution_image:
            extras.append((solution_image, "✏️ <b>Решение</b>"))

        await send_question_message(message, q, text, None if extras else markup)
        for k, (path, caption) in enumerate(extras):
            await message.answer_photo(
                photo=FSInputFile(path),
                caption=caption,
                reply_markup=markup if k == len(extras) - 1 else None,
            )
    else:
        builder = InlineKeyboardBuilder()
        for i, option in enumerate(q["options"]):
            builder.button(text=f"{OPTION_LETTERS[i]}) {option}",
                           callback_data=f"ans:{session['sid']}:{index}:{i}")
        builder.adjust(1)
        builder.row(*nav_buttons(index, session))
        await send_question_message(message, q, header, builder.as_markup())


@dp.callback_query(F.data.startswith("q:"))
async def goto_question(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    if user_id not in user_sessions:
        await callback.answer("Начните тест заново: нажмите «Квиз»", show_alert=True)
        return
    parsed = parse_session_callback(callback)
    if not parsed or len(parsed[1]) != 1:
        await callback.answer(STALE_BUTTON_TEXT, show_alert=True)
        return
    _, (index,) = parsed
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

    parsed = parse_session_callback(callback)
    if not parsed or len(parsed[1]) != 2:
        await callback.answer(STALE_BUTTON_TEXT, show_alert=True)
        return
    _, (index, choice) = parsed

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
    builder.row(InlineKeyboardButton(text=DONATE_BUTTON, callback_data="donate"))

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

    # Показываем только разделы, где есть ответы: номеров заданий стало много,
    # список «нет данных» по каждому был бы бесполезно длинным. Старые разделы
    # (до перехода на номера) тоже попадают сюда со своими названиями.
    lines = []
    for db_key, s in sorted(section_stats.items(), key=lambda kv: section_title(kv[0])):
        if s["total"] > 0:
            pct = round(s["correct"] / s["total"] * 100)
            lines.append(f"{section_title(db_key)}: <b>{s['correct']}/{s['total']}</b> ({pct}%)")
    breakdown = "\n".join(lines)

    await message.answer(
        "📊 <b>Твоя статистика</b>\n\n"
        f"{progress_bar(stats['correct'], stats['total'])}\n"
        f"Отвечено вопросов: <b>{stats['total']}</b>\n"
        f"Правильно: <b>{stats['correct']}</b>\n"
        f"Точность: <b>{accuracy}%</b>\n"
        f"{streak_line}\n\n"
        f"{result_tier(accuracy)}\n\n"
        f"📚 <b>По разделам:</b>\n{breakdown}",
        reply_markup=InlineKeyboardBuilder().button(text=DONATE_BUTTON, callback_data="donate").as_markup(),
    )


# ───────────── Поддержка бота звёздами (Telegram Stars) ─────────────
# Валюта XTR, provider_token не нужен. Telegram требует у платных ботов /paysupport и /terms.

DONATE_TEXT = (
    "⭐ <b>Поддержать бота</b>\n\n"
    "Сервер и пополнение базы задач стоят денег и времени. "
    "Если бот помогает готовиться — можно поддержать его звёздами Telegram. "
    "Поддержка добровольная: сейчас все задачи открыты для всех.\n\n"
    "Выбери сумму 👇"
)


def donate_markup():
    builder = InlineKeyboardBuilder()
    for amount in DONATE_AMOUNTS:
        builder.button(text=f"⭐ {amount}", callback_data=f"donate:{amount}")
    builder.adjust(3)
    return builder.as_markup()


@dp.message(Command("donate"))
@dp.message(F.text == DONATE_BUTTON)
async def cmd_donate(message: Message) -> None:
    await message.answer(DONATE_TEXT, reply_markup=donate_markup())


@dp.callback_query(F.data == "donate")
async def choose_donation(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(DONATE_TEXT, reply_markup=donate_markup())


@dp.callback_query(F.data.startswith("donate:"))
async def send_donation_invoice(callback: CallbackQuery) -> None:
    amount = int(callback.data.split(":", 1)[1])
    if amount not in DONATE_AMOUNTS:
        await callback.answer()
        return
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Поддержка Physics Bot",
        description=f"Добровольная поддержка бота: {amount} ⭐. Спасибо, что помогаешь проекту!",
        payload=f"donate:{amount}",
        currency="XTR",
        prices=[LabeledPrice(label="Поддержка бота", amount=amount)],
    )


@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery) -> None:
    # Подтверждаем только наши счета на поддержку; Telegram ждёт ответ не дольше 10 секунд.
    ok = query.currency == "XTR" and query.invoice_payload.startswith("donate:")
    await query.answer(ok=ok, error_message=None if ok else "Платёж не распознан, попробуй ещё раз.")


@dp.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    payment = message.successful_payment
    record_donation(
        message.from_user.id,
        message.from_user.full_name,
        payment.total_amount,
        payment.telegram_payment_charge_id,
    )
    await message.answer(
        f"💛 Спасибо за поддержку — {payment.total_amount} ⭐!\n"
        "Это правда помогает держать бота на плаву и добавлять новые задачи. Удачной подготовки!",
        reply_markup=MAIN_KEYBOARD,
    )
    try:
        await bot.send_message(
            ADMIN_ID,
            f"⭐ Донат: <b>{payment.total_amount}</b> от {message.from_user.full_name} "
            f"(id {message.from_user.id})\ncharge_id: <code>{payment.telegram_payment_charge_id}</code>",
        )
    except Exception:
        logging.exception("Не удалось уведомить админа о донате")


@dp.message(Command("paysupport"))
async def cmd_paysupport(message: Message) -> None:
    await message.answer(
        "💬 <b>Вопросы по оплате</b>\n\n"
        "Если с поддержкой звёздами что-то пошло не так или ты хочешь вернуть платёж — "
        "напиши автору бота через канал @nicholas_physics, указав дату и сумму. "
        "Ответим и при необходимости вернём звёзды."
    )


@dp.message(Command("terms"))
async def cmd_terms(message: Message) -> None:
    await message.answer(
        "📄 <b>Условия</b>\n\n"
        "Physics Bot — тренажёр по физике для подготовки к ОГЭ и ЕГЭ. "
        "Кнопка «Поддержать бота» — добровольный платёж в поддержку проекта; "
        "сам по себе он не открывает дополнительного доступа. "
        "Состав бесплатных и платных возможностей может меняться — об изменениях сообщаем заранее. "
        "Возврат платежа возможен по запросу через /paysupport."
    )


@dp.message(Command("refund"))
async def cmd_refund(message: Message) -> None:
    """Только для админа: /refund <user_id> <charge_id> — вернуть звёзды."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = (message.text or "").split()
    if len(parts) != 3 or not parts[1].isdigit():
        await message.answer("Формат: /refund <user_id> <charge_id> (оба есть в уведомлении о донате)")
        return
    user_id, charge_id = int(parts[1]), parts[2]
    try:
        await bot.refund_star_payment(user_id=user_id, telegram_payment_charge_id=charge_id)
    except TelegramBadRequest as e:
        await message.answer(f"Не получилось вернуть: {e.message}")
        return
    mark_donation_refunded(charge_id)
    await message.answer("✅ Звёзды возвращены.")


@dp.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    stats = get_admin_stats()
    donations = get_donation_stats()
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
        f"🏆 <b>Топ разделов по числу ответов:</b>\n{top_text}\n\n"
        f"⭐ <b>Поддержка:</b> {donations['count']} платежей, всего <b>{donations['stars']}</b> звёзд"
        + "".join(f"\n· {name}: {stars} ⭐ ({created[:10]})" for name, stars, created in donations["last"])
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
    await bot.set_my_commands([
        BotCommand(command="quiz", description="🧮 Квиз"),
        BotCommand(command="stats", description="📊 Статистика"),
        BotCommand(command="donate", description="⭐ Поддержать бота"),
        BotCommand(command="paysupport", description="Вопросы по оплате"),
        BotCommand(command="terms", description="Условия"),
    ])
    asyncio.create_task(daily_reminder_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
