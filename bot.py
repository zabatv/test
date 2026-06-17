import os
import time
import threading
import requests
import html
from flask import Flask, request, render_template_string, redirect, url_for, flash, session

# Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

# Configuration from env
TELEGRAM_TOKEN = "8978439642:AAGSjQOggCU-C8_fP6Qj7QAEBvuCsgkGoRk"
TELEGRAM_CHAT_ID = CHAT_ID = 5244188429

PORT = int(os.environ.get("PORT", 5000))

if TELEGRAM_TOKEN:
    API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
else:
    API = None

# Simple in-memory rate limit per session (not persistent)
RATE_LIMIT_SECONDS = 10  # минимальный интервал между отправками от одной сессии

# HTML template (центрированная карточка)
HTML = """..."""  # (скопируйте HTML из предыдущего ответа сюда; чтобы не дублировать в примере)

# --- Telegram helper functions ---
def make_keyboard(buttons):
    keyboard = []
    for text, cb in buttons:
        keyboard.append([{"text": text, "callback_data": cb}])
    return {"inline_keyboard": keyboard}

def send_message_telegram(chat_id, text, reply_markup=None, parse_mode="HTML"):
    if not API:
        raise EnvironmentError("TELEGRAM_TOKEN не задан")
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = requests.post(API + "/sendMessage", json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    if not API:
        return
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = requests.post(API + "/editMessageText", json=payload, timeout=20)
    return r.json()

def answer_callback(callback_query_id):
    if not API:
        return
    try:
        requests.post(API + "/answerCallbackQuery", json={"callback_query_id": callback_query_id}, timeout=5)
    except Exception:
        pass

# --- Telegram polling logic (runs in background thread) ---
def process_update(u):
    try:
        # message with /start
        if "message" in u and "text" in u["message"]:
            text = u["message"]["text"]
            chat_id = u["message"]["chat"]["id"]
            if text.strip().startswith("/start"):
                menu = MENUS["main"]
                send_message_telegram(chat_id, menu["text"], reply_markup=make_keyboard(menu["buttons"]))
        # callback_query from inline buttons
        if "callback_query" in u:
            cq = u["callback_query"]
            data = cq.get("data")
            cb_id = cq["id"]
            # acknowledge
            answer_callback(cb_id)
            msg = cq.get("message")
            if not msg:
                return
            chat_id = msg["chat"]["id"]
            message_id = msg["message_id"]
            if data in MENUS:
                menu = MENUS[data]
                edit_message(chat_id, message_id, menu["text"], reply_markup=make_keyboard(menu["buttons"]))
            else:
                edit_message(chat_id, message_id, "❌ Ошибка: такого раздела нет.")
    except Exception as e:
        print("process_update error:", e)

def get_updates(offset=None, timeout=30):
    if not API:
        return {"ok": False, "result": []}
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    r = requests.get(API + "/getUpdates", params=params, timeout=timeout+10)
    return r.json()

def polling_loop():
    print("Запуск Telegram polling...")
    offset = None
    while True:
        try:
            res = get_updates(offset=offset, timeout=30)
            if not res.get("ok"):
                time.sleep(2)
                continue
            for u in res.get("result", []):
                process_update(u)
                offset = u["update_id"] + 1
        except Exception as e:
            print("Polling error:", e)
            time.sleep(3)

def start_polling_background():
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_TOKEN не задан — polling не запущен")
        return
    t = threading.Thread(target=polling_loop, daemon=True)
    t.start()

# --- Flask routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        if not msg:
            flash("Введите текст сообщения.")
            return redirect(url_for("index"))
        # rate limit per session
        last = session.get("last_sent_at", 0)
        now = time.time()
        if now - last < RATE_LIMIT_SECONDS:
            flash(f"Подождите {int(RATE_LIMIT_SECONDS - (now-last))} сек. перед повторной отправкой.")
            return redirect(url_for("index"))
        session["last_sent_at"] = now
        # safety: escape HTML and limit length
        safe_text = html.escape(msg)[:2000]
        final_text = safe_text  # можно добавить префикс/метаданные
        try:
            send_message_telegram(TELEGRAM_CHAT_ID, final_text)
        except Exception as e:
            print("Send telegram error:", e)
            flash("Ошибка при отправке. Попробуйте позже.")
            return redirect(url_for("index"))
        flash("Сообщение успешно отправлено!")
        return redirect(url_for("index"))

    return render_template_string(HTML)

# Start polling when app starts (Render will create processes; thread starts in main)
@app.before_first_request
def before_first_request():
    start_polling_background()

# Run app
if __name__ == "__main__":
    start_polling_background()
    app.run(host="0.0.0.0", port=PORT)
