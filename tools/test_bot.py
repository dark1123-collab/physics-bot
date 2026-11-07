"""Сквозной тест бота без Telegram: настоящие обработчики из bot.py, поддельные
сообщения/кнопки и временная база.

Запуск из корня проекта:  python tools/test_bot.py
Что проверяется:
  * обход всех меню — каждую кнопку можно нажать, обработчик не падает;
  * в каждом разделе каждый вопрос открывается, на него отвечается, итог считается;
  * всё, что бот отправляет, проходит ограничения Telegram: HTML-разметка, длина
    текста/подписи, длина текста кнопки и callback_data, файлы картинок существуют;
  * кнопки из старых сообщений (другой раздел, до перезапуска, старый формат);
  * статистика, серия дней, напоминания, донаты, админ-команды.
Код выхода 1, если есть ошибки.
"""
import asyncio
import html
import os
import random
import re
import sqlite3
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from html.parser import HTMLParser
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("BOT_TOKEN", "123456:TEST-TOKEN-NOT-REAL-aaaaaaaaaaaaaaaaaaaa")

import bot  # noqa: E402

failures: list[str] = []
checked = {"messages": 0, "buttons": 0}


def fail(msg: str) -> None:
    failures.append(msg)


# ───────────── проверка исходящих сообщений ─────────────

TG_TAGS = {"b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "a", "code", "pre",
           "tg-spoiler", "span", "blockquote", "tg-emoji"}


class TgHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.text = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag not in TG_TAGS:
            self.errors.append(f"тег <{tag}> Telegram не поддерживает")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"лишний/непарный </{tag}>")
        else:
            self.stack.pop()

    def handle_data(self, data):
        self.text.append(data)


def tg_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2  # Telegram считает длину в UTF-16


def check_html(where: str, text: str, limit: int) -> None:
    checked["messages"] += 1
    # Всё, что похоже на «<», но не тег, Telegram отвергает ("can't parse entities").
    for m in re.finditer(r"<", text):
        if not re.match(r"</?[a-z][a-z0-9-]*(\s[^<>]*)?>", text[m.start():]):
            fail(f"{where}: неэкранированный «<» → «{text[max(0, m.start() - 20):m.start() + 20]}»")
    for m in re.finditer(r"&", text):
        if not re.match(r"&(#\d+|#x[0-9a-fA-F]+|lt|gt|amp|quot);", text[m.start():]):
            fail(f"{where}: неэкранированный «&» → «{text[max(0, m.start() - 20):m.start() + 20]}»")
    p = TgHTML()
    p.feed(text)
    p.close()
    if p.stack:
        p.errors.append(f"незакрытые теги {p.stack}")
    for e in p.errors:
        fail(f"{where}: {e}")
    visible = "".join(p.text)
    if tg_len(visible) > limit:
        fail(f"{where}: длина {tg_len(visible)} > {limit}")
    if not visible.strip():
        fail(f"{where}: пустое сообщение")


def check_markup(where: str, markup) -> None:
    if markup is None or not hasattr(markup, "inline_keyboard"):
        return
    for row in markup.inline_keyboard:
        for b in row:
            checked["buttons"] += 1
            if tg_len(b.text) > 64:
                fail(f"{where}: текст кнопки длиннее 64: {b.text[:40]}…")
            if "&lt;" in b.text or "&amp;" in b.text or "<b>" in b.text:
                fail(f"{where}: HTML в тексте кнопки (покажется как есть): {b.text}")
            if b.callback_data is not None and len(b.callback_data.encode()) > 64:
                fail(f"{where}: callback_data длиннее 64 байт: {b.callback_data}")


class Sent:
    def __init__(self, kind, text, markup, photo=None):
        self.kind, self.text, self.markup, self.photo = kind, text, markup, photo

    def callbacks(self):
        if self.markup is None or not hasattr(self.markup, "inline_keyboard"):
            return []
        return [b.callback_data for row in self.markup.inline_keyboard for b in row if b.callback_data]


outbox: list[Sent] = []
context = ["?"]


class FakeMessage:
    def __init__(self, user):
        self.from_user = user
        self.successful_payment = None
        self.text = ""

    async def answer(self, text, reply_markup=None, **_):
        where = f"[{context[0]}] текст"
        check_html(where, text, 4096)
        check_markup(where, reply_markup)
        outbox.append(Sent("text", text, reply_markup))

    async def answer_photo(self, photo, caption=None, reply_markup=None, **_):
        where = f"[{context[0]}] фото"
        path = getattr(photo, "path", None)
        if not path or not os.path.exists(path):
            fail(f"{where}: нет файла картинки {path}")
        if caption:
            check_html(where + " (подпись)", caption, 1024)
        check_markup(where, reply_markup)
        outbox.append(Sent("photo", caption or "", reply_markup, path))

    async def edit_text(self, text, reply_markup=None, **_):
        await self.answer(text, reply_markup=reply_markup)

    async def edit_reply_markup(self, reply_markup=None, **_):
        pass


USER = SimpleNamespace(id=1001, full_name="Тест <Тестович> & Ко")
alerts: list[str] = []


class FakeCallback:
    def __init__(self, data, user=USER):
        self.data = data
        self.from_user = user
        self.message = FakeMessage(user)

    async def answer(self, text=None, show_alert=False, **_):
        if text:
            alerts.append(text)


# callback_data → обработчик (повторяет фильтры декораторов в bot.py)
ROUTES = [
    (lambda d: d == "tracks", bot.back_to_tracks),
    (lambda d: d.startswith("track:"), bot.choose_track),
    (lambda d: d.startswith("group:"), bot.choose_group),
    (lambda d: d == "soon", bot.soon_section),
    (lambda d: d.startswith("section:"), bot.choose_section),
    (lambda d: d.startswith("q:"), bot.goto_question),
    (lambda d: d == "map", bot.goto_map),
    (lambda d: d.startswith("ans:"), bot.check_answer),
    (lambda d: d == "finish", bot.finish_quiz),
    (lambda d: d == "donate", bot.choose_donation),
    (lambda d: d == "mistakes", bot.mistakes_callback),
    (lambda d: d.startswith("sol:"), bot.show_full_solution),
    (lambda d: d.startswith("donate:"), bot.send_donation_invoice),
]


async def press(data, user=USER) -> list[Sent]:
    start = len(outbox)
    for match, handler in ROUTES:
        if match(data):
            try:
                await handler(FakeCallback(data, user))
            except Exception:
                fail(f"[{context[0]}] кнопка «{data}» уронила обработчик:\n{traceback.format_exc()}")
            return outbox[start:]
    fail(f"[{context[0]}] на кнопку «{data}» нет обработчика")
    return []


async def send_text(handler, text="", user=USER) -> list[Sent]:
    start = len(outbox)
    msg = FakeMessage(user)
    msg.text = text
    try:
        await handler(msg)
    except Exception:
        fail(f"[{context[0]}] команда {handler.__name__} упала:\n{traceback.format_exc()}")
    return outbox[start:]


# ───────────── сценарии ─────────────

async def test_menus() -> list[str]:
    """Обходит меню начиная с «Квиз», возвращает все кнопки разделов."""
    context[0] = "меню"
    sent = await send_text(bot.cmd_quiz)
    queue = [c for s in sent for c in s.callbacks()]
    seen, sections = set(), []
    while queue:
        data = queue.pop(0)
        if data in seen:
            continue
        seen.add(data)
        if data.startswith("section:"):
            sections.append(data)
            continue
        for s in await press(data):
            queue.extend(s.callbacks())
    if "soon" in seen:
        alerts.clear()
        await press("soon")
        if not alerts:
            fail("[меню] кнопка ⏳ не показывает сообщение")
    for key, track in bot.TRACKS.items():
        for skey, section in track["sections"].items():
            if section["questions"] and f"section:{key}:{skey}" not in sections:
                fail(f"[меню] раздел {key}:{skey} с вопросами недоступен из меню")
    return sections


async def test_section(data: str, rng: random.Random) -> None:
    context[0] = data
    sent = await press(data)
    session = bot.user_sessions.get(USER.id)
    if not session:
        fail(f"[{data}] сессия не создана")
        return
    questions = bot.get_session_section(session)["questions"]
    map_buttons = [c for s in sent for c in s.callbacks() if c.startswith("q:")]
    if len(map_buttons) != len(questions):
        fail(f"[{data}] в списке {len(map_buttons)} кнопок, вопросов {len(questions)}")
    for n, qbtn in enumerate(map_buttons):
        context[0] = f"{data} вопрос {n + 1}"
        shown = await press(qbtn)
        answer_buttons = [c for s in shown for c in s.callbacks() if c.startswith("ans:")]
        if len(answer_buttons) != 4:
            fail(f"[{context[0]}] кнопок ответа {len(answer_buttons)}, нужно 4")
            continue
        # Длинные варианты не должны обрезаться на телефоне: либо кнопка короткая,
        # либо вариант целиком напечатан в тексте вопроса.
        q_shown = questions[int(answer_buttons[0].split(":")[2])]
        texts = [b.text for s in shown if s.markup for row in s.markup.inline_keyboard for b in row
                 if (b.callback_data or "").startswith("ans:")]
        if any(len(t) > bot.BUTTON_FIT for t in texts):
            fail(f"[{context[0]}] текст кнопки ответа не влезет на телефоне: {max(texts, key=len)}")
        if not bot.options_fit_buttons(q_shown["options"]):
            body = " ".join(s.text for s in shown)
            if not all(o in body for o in q_shown["options"]):
                fail(f"[{context[0]}] длинные варианты не напечатаны в тексте вопроса")
        choice = rng.randrange(4)
        index = int(answer_buttons[choice].split(":")[2])
        q = questions[index]
        alerts.clear()
        after = await press(answer_buttons[choice])
        expected = "Верно! ✅" if choice == q["correct"] else "Неверно ❌"
        if alerts[:1] != [expected]:
            fail(f"[{context[0]}] всплывашка {alerts[:1]}, ожидалось {expected}")
        if session["answers"].get(index) != choice:
            fail(f"[{context[0]}] ответ не записан в сессию")
        if not after:
            fail(f"[{context[0]}] после ответа ничего не пришло")
            continue
        # кнопки навигации — на последнем сообщении (после картинок формулы/решения)
        if not any(c.startswith("q:") or c == "map" for c in after[-1].callbacks()):
            fail(f"[{context[0]}] у последнего сообщения после ответа нет навигации")
        if q.get("solution_image") and not any(s.photo and s.photo.endswith(q["solution_image"].split("/")[-1]) for s in after):
            fail(f"[{context[0]}] не показана картинка решения")
        if q.get("formula") and not any(s.kind == "photo" and "Формула" in s.text for s in after):
            fail(f"[{context[0]}] не показана формула")
        sol_buttons = [c for s in after for c in s.callbacks() if c.startswith("sol:")]
        if bool(sol_buttons) != bool(q.get("solution") or q.get("solution_images")):
            fail(f"[{context[0]}] кнопка «Полное решение» есть/нет не по данным вопроса")
        if sol_buttons:
            sol = await press(sol_buttons[0])
            photos = [s.photo for s in sol if s.kind == "photo"]
            if len(photos) != len(q.get("solution_images") or []):
                fail(f"[{context[0]}] в полном решении не все картинки")
            if q.get("solution") and not any("Решение" in s.text for s in sol if s.kind == "text"):
                fail(f"[{context[0]}] не показан текст решения")
            if not sol or not any(c.startswith("q:") or c == "map" for c in sol[-1].callbacks()):
                fail(f"[{context[0]}] после полного решения нет навигации")
        # повторное нажатие ответа не должно засчитываться второй раз
        alerts.clear()
        await press(answer_buttons[(choice + 1) % 4])
        if session["answers"][index] != choice or "уже отвечали" not in " ".join(alerts):
            fail(f"[{context[0]}] повторный ответ засчитан или нет предупреждения")
    context[0] = data
    finish = await press("finish")
    score = sum(1 for i, c in session["answers"].items() if c == questions[i]["correct"])
    if not finish or f"{score}/{len(questions)}" not in finish[-1].text:
        fail(f"[{data}] итог не совпадает со счётом {score}/{len(questions)}")


async def test_stale_buttons(sections: list[str]) -> None:
    context[0] = "старые кнопки"
    a, b = sections[0], sections[-1]
    await press(a)
    old_q = [c for c in outbox[-1].callbacks() if c.startswith("q:")][0]
    shown = await press(old_q)
    old_ans = [c for s in shown for c in s.callbacks() if c.startswith("ans:")][0]
    old_nav = [c for s in shown for c in s.callbacks() if c.startswith("q:")]
    await press(b)
    session_b = bot.user_sessions[USER.id]
    for data in [old_q, old_ans, *old_nav, "q:0", "ans:0:1", "q:zz:1", "ans:x:y", "q:", "ans:"]:
        alerts.clear()
        n = len(outbox)
        await press(data)
        if len(outbox) != n or session_b["answers"]:
            fail(f"[{context[0]}] кнопка «{data}» из чужого теста сработала")
        if not alerts:
            fail(f"[{context[0]}] на кнопку «{data}» нет объяснения пользователю")
    # кнопки меню, которых больше нет
    for data in ["section:ege:mechanics", "section:nope:x", "track:nope", "group:ege:nope",
                 "group:nope:x", "donate:7", "donate:abc"]:
        alerts.clear()
        await press(data)


async def test_restart(sections: list[str]) -> None:
    """Перезапуск бота (деплой) не должен ломать начатый тест."""
    context[0] = "перезапуск"
    await press(sections[0])
    q = [c for c in outbox[-1].callbacks() if c.startswith("q:")][0]
    shown = await press(q)
    ans = [c for s in shown for c in s.callbacks() if c.startswith("ans:")][0]
    await press(ans)
    before = dict(bot.user_sessions[USER.id]["answers"])
    bot.user_sessions.clear()  # так выглядит память процесса после рестарта
    alerts.clear()
    after_map = await press("map")
    if not after_map:
        fail(f"[{context[0]}] после перезапуска «📋 Список» не работает: {alerts}")
        return
    session = bot.user_sessions.get(USER.id)
    if not session or session["answers"] != before:
        fail(f"[{context[0]}] прогресс теста потерян после перезапуска")
    nxt = [c for c in shown[-1].callbacks() if c.startswith("q:")]
    if nxt:
        n = len(outbox)
        await press(nxt[-1])
        if len(outbox) == n:
            fail(f"[{context[0]}] ▶️ из сообщения до перезапуска не работает")


async def test_mistakes(sections: list[str]) -> None:
    """Работа над ошибками: ошибки попадают в список, верный ответ убирает вопрос,
    ответ пишется в родной раздел вопроса."""
    context[0] = "ошибки"
    user = SimpleNamespace(id=5005, full_name="Ошибающийся")
    out = await send_text(bot.cmd_mistakes, user=user)
    if not out or "нет" not in out[0].text:
        fail("[ошибки] без ошибок не сказано, что разбирать нечего")

    # отвечаем неверно на 3 вопроса раздела и верно на 1
    data = next(s for s in sections if s.endswith(":task09"))
    await press(data, user)
    session = bot.user_sessions[user.id]
    questions = bot.get_session_section(session)["questions"]
    wrong_ids = []
    for n, i in enumerate(session["order"][:4]):
        q = questions[i]
        choice = q["correct"] if n == 3 else (q["correct"] + 1) % 4
        await press(f"ans:{session['sid']}:{i}:{choice}", user)
        if n < 3:
            wrong_ids.append(q["id"])
    if set(bot.get_mistakes(user.id)) != set(wrong_ids):
        fail(f"[ошибки] список ошибок {bot.get_mistakes(user.id)} ≠ {wrong_ids}")

    finish = await press("finish", user)
    if not finish or "mistakes" not in finish[-1].callbacks():
        fail("[ошибки] в итоге нет кнопки «Работа над ошибками»")

    out = await press("mistakes", user)
    ms = bot.user_sessions[user.id]
    if ms["track"] != bot.MISTAKES_TRACK or ms["qids"] != bot.get_mistakes(user.id):
        fail("[ошибки] сессия работы над ошибками собрана неверно")
    if len([c for s in out for c in s.callbacks() if c.startswith("q:")]) != 3:
        fail("[ошибки] в списке не 3 вопроса")

    # проходим все вопросы режима: открыть → ответить верно, проверить заголовок и раздел записи
    for pos, i in enumerate(ms["order"]):
        context[0] = f"ошибки вопрос {pos + 1}"
        shown = await press(f"q:{ms['sid']}:{i}", user)
        if not shown or "📍" not in (shown[-1].text or shown[0].text):
            fail(f"[{context[0]}] не показано, из какого номера вопрос")
        q = bot.get_session_section(ms)["questions"][i]
        await press(f"ans:{ms['sid']}:{i}:{q['correct']}", user)
    conn = sqlite3.connect(bot.DB_PATH)
    sections_written = {r[0] for r in conn.execute(
        "SELECT section FROM answers WHERE user_id=?", (user.id,))}
    conn.close()
    if sections_written != {data.split(":", 1)[1]}:
        fail(f"[ошибки] ответы записаны не в родной раздел: {sections_written}")
    if bot.get_mistakes(user.id):
        fail("[ошибки] после верных ответов ошибки остались в списке")
    finish = await press("finish", user)
    if not finish or "Все ошибки разобраны" not in finish[-1].text:
        fail("[ошибки] итог не сообщает, что всё разобрано")

    # перезапуск посреди работы над ошибками
    context[0] = "ошибки + перезапуск"
    await press(data, user)
    s2 = bot.user_sessions[user.id]
    i = s2["order"][0]
    q = bot.get_session_section(s2)["questions"][i]
    await press(f"ans:{s2['sid']}:{i}:{(q['correct'] + 1) % 4}", user)
    await press("mistakes", user)
    bot.user_sessions.clear()
    if not await press("map", user) or bot.user_sessions[user.id]["track"] != bot.MISTAKES_TRACK:
        fail("[ошибки] после перезапуска работа над ошибками не восстановилась")

    # статистика показывает число ошибок и кнопку
    out = await send_text(bot.cmd_stats, user=user)
    if not out or "Ошибок к разбору: <b>1</b>" not in out[0].text or "mistakes" not in out[0].callbacks():
        fail("[ошибки] в статистике нет числа ошибок или кнопки")


async def test_stats_and_streak() -> None:
    context[0] = "статистика"
    new_user = SimpleNamespace(id=2002, full_name="Новичок")
    out = await send_text(bot.cmd_stats, user=new_user)
    if not out or "нет статистики" not in out[0].text:
        fail("[статистика] новичку не сказано, что статистики нет")
    out = await send_text(bot.cmd_stats)
    if not out or "Отвечено вопросов" not in out[0].text:
        fail("[статистика] после ответов нет статистики")
    bot.record_answer(USER.id, "mechanics", True)          # запись самого старого формата
    bot.record_answer(USER.id, "ege:mechanics", False)     # до перехода на номера
    bot.record_answer(USER.id, "ege:удалённый", True)      # раздел, которого уже нет
    await send_text(bot.cmd_stats)

    context[0] = "серия"
    uid = 3003
    bot.touch_user(uid, "Серия")
    conn = sqlite3.connect(bot.DB_PATH)

    def set_last(days_ago, streak):
        d = (datetime.utcnow().date() - timedelta(days=days_ago)).isoformat()
        conn.execute("UPDATE users SET last_activity_date=?, current_streak=? WHERE user_id=?", (d, streak, uid))
        conn.commit()

    cases = [(None, 0, 1), (0, 5, 5), (1, 5, 6), (2, 5, 1), (30, 9, 1)]
    for days_ago, streak, expected in cases:
        if days_ago is None:
            conn.execute("UPDATE users SET last_activity_date=NULL, current_streak=0 WHERE user_id=?", (uid,))
            conn.commit()
        else:
            set_last(days_ago, streak)
        got = bot.update_streak(uid)
        if got != expected:
            fail(f"[серия] было {streak}, последний ответ {days_ago} дн. назад → {got}, ожидалось {expected}")
    set_last(2, 7)
    if bot.get_streak(uid)["current"] != 0:
        fail("[серия] прерванная серия показывается как живая")
    conn.close()
    for n, word in [(1, "день"), (2, "дня"), (5, "дней"), (11, "дней"), (21, "день"), (22, "дня"), (111, "дней")]:
        if bot._days_word(n) != word:
            fail(f"[серия] {n} {bot._days_word(n)}, ожидалось {word}")


async def test_misc_commands() -> None:
    context[0] = "команды"
    await send_text(bot.cmd_start)
    await send_text(bot.cmd_donate)
    await send_text(bot.cmd_paysupport)
    await send_text(bot.cmd_terms)
    invoices = []

    async def fake_invoice(**kw):
        invoices.append(kw)

    bot.bot.send_invoice = fake_invoice
    for amount in bot.DONATE_AMOUNTS:
        await press(f"donate:{amount}")
    if len(invoices) != len(bot.DONATE_AMOUNTS) or any(i["currency"] != "XTR" for i in invoices):
        fail("[донат] счета выставлены неправильно")
    await press("donate:7")
    if len(invoices) != len(bot.DONATE_AMOUNTS):
        fail("[донат] выставлен счёт на сумму не из списка")

    admin = SimpleNamespace(id=bot.ADMIN_ID, full_name="Админ")
    stranger_out = await send_text(bot.cmd_admin)
    if stranger_out:
        fail("[админ] /admin отвечает не админу")
    await send_text(bot.cmd_admin, user=admin)
    await send_text(bot.cmd_refund, "/refund", user=admin)
    if await send_text(bot.cmd_refund, "/refund 1 x"):
        fail("[админ] /refund отвечает не админу")

    bot.record_donation(5, "Донатер <script>", 50, "charge-1")
    bot.record_donation(5, "Донатер <script>", 50, "charge-1")  # повтор того же платежа
    if bot.get_donation_stats()["count"] != 1:
        fail("[донат] повторное уведомление о платеже посчитано дважды")
    await send_text(bot.cmd_admin, user=admin)

    # напоминания: не трогаем активных, не повторяем чаще раза в неделю
    context[0] = "напоминания"
    conn = sqlite3.connect(bot.DB_PATH)
    old = (datetime.utcnow() - timedelta(days=10)).isoformat()
    conn.execute("INSERT OR REPLACE INTO users (user_id, full_name, first_seen, last_seen) VALUES (4004,'x',?,?)", (old, old))
    conn.commit()
    conn.close()
    if 4004 not in bot.get_inactive_users() or USER.id in bot.get_inactive_users():
        fail("[напоминания] неверный список неактивных")
    bot.mark_reminder_sent(4004)
    if 4004 in bot.get_inactive_users():
        fail("[напоминания] напоминание повторяется сразу")


async def main() -> None:
    tmp = tempfile.mkdtemp(prefix="physbot-test-")
    bot.DB_PATH = os.path.join(tmp, "stats.db")
    bot.init_db()
    bot.init_db()  # повторный запуск на существующей базе не должен падать
    rng = random.Random(42)

    sections = await test_menus()
    print(f"Разделов в меню: {len(sections)}")
    for data in sections:
        await test_section(data, rng)
    await test_stale_buttons(sections)
    await test_restart(sections)
    await test_mistakes(sections)
    await test_stats_and_streak()
    await test_misc_commands()

    print(f"Сообщений проверено: {checked['messages']}, кнопок: {checked['buttons']}")
    uniq = list(dict.fromkeys(failures))
    for f in uniq[:80]:
        print("✗", f)
    if len(uniq) > 80:
        print(f"… и ещё {len(uniq) - 80}")
    print("OK" if not uniq else f"Ошибок: {len(uniq)}")
    sys.exit(1 if uniq else 0)


if __name__ == "__main__":
    asyncio.run(main())
