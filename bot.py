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

# HTML template
HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Анонимное сообщение</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .flash-messages {
            margin-bottom: 20px;
        }
        
        .flash {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            text-align: center;
            font-size: 14px;
        }
        
        .flash.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .flash.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .flash.warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        textarea {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .info {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Напиши анонимное сообщение султану!</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash {{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <textarea name="message" placeholder="Введите ваше сообщение..." required maxlength="2000"></textarea>
            <button type="submit">Отправить</button>
        </form>
        
        <div class="info">
            Ваше сообщение полностью анонимно
        </div>
    </div>
</body>
</html>
"""

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
            flash("Введите текст сообщения.", "error")
            return redirect(url_for("index"))
        # rate limit per session
        last = session.get("last_sent_at", 0)
        now = time.time()
        if now - last < RATE_LIMIT_SECONDS:
            flash(f"Подождите {int(RATE_LIMIT_SECONDS - (now-last))} сек. перед повторной отправкой.", "warning")
            return redirect(url_for("index"))
        session["last_sent_at"] = now
        # safety: escape HTML and limit length
        safe_text = html.escape(msg)[:2000]
        final_text = f"📩 <b>Анонимное сообщение:</b>\n\n{safe_text}"
        try:
            send_message_telegram(TELEGRAM_CHAT_ID, final_text)
        except Exception as e:
            print("Send telegram error:", e)
            flash("Ошибка при отправке. Попробуйте позже.", "error")
            return redirect(url_for("index"))
        flash("Сообщение успешно отправлено!", "success")
        return redirect(url_for("index"))

    return render_template_string(HTML)

# Start polling when app starts (REPLACED before_first_request)
polling_started = False

def ensure_polling_started():
    global polling_started
    if not polling_started:
        start_polling_background()
        polling_started = True

# Use before_request to start polling on first request
@app.before_request
def before_request_handler():
    ensure_polling_started()

# Run app
if __name__ == "__main__":
    # Also start polling when running directly
    start_polling_background()
    app.run(host="0.0.0.0", port=PORT)
