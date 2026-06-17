from flask import Flask, request, render_template_string, redirect, url_for, flash
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")  # для flash

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HTML = """
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Анонимное сообщение</title>
<style>
  :root{--bg:#0f1724;--card:#0b1220;--accent:#7c3aed;--muted:#9aa4b2;--glass:rgba(255,255,255,0.04)}
  body{margin:0;height:100vh;display:flex;align-items:center;justify-content:center;background:
    radial-gradient( circle at 10% 10%, rgba(124,58,237,0.12), transparent 10%),
    linear-gradient(180deg,#071029 0%, var(--bg) 100%);font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,'Helvetica Neue',Arial;}
  .card{width:100%;max-width:720px;padding:36px;border-radius:12px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));box-shadow:0 8px 30px rgba(2,6,23,0.7);backdrop-filter: blur(6px);border:1px solid rgba(255,255,255,0.03)}
  h1{margin:0 0 8px;color:#ffffff;font-size:20px;text-align:center;letter-spacing:0.4px}
  p.lead{margin:0 0 18px;color:var(--muted);text-align:center;font-size:14px}
  form{display:flex;flex-direction:column;gap:12px}
  textarea{min-height:140px;padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,0.04);background:var(--glass);color:#e6eef8;resize:vertical;font-size:15px}
  .row{display:flex;gap:8px}
  .btn{background:linear-gradient(90deg,var(--accent),#5b21b6);color:white;padding:12px 16px;border-radius:10px;border:0;cursor:pointer;font-weight:600}
  .btn:disabled{opacity:0.6;cursor:not-allowed}
  .muted{color:var(--muted);font-size:13px;text-align:center}
  .footer{margin-top:10px;text-align:center;color:var(--muted);font-size:12px}
  .flash{background:#06374a;color:#d1f5ff;padding:10px;border-radius:8px;text-align:center}
  @media (max-width:520px){.card{padding:20px}}
</style>
</head>
<body>
  <div class="card" role="main">
    <h1>АНОНИМНОЕ СООБЩЕНИЕ СУЛТАНУ!</h1>
    <p class="lead">Напишите сообщение — оно будет отправлено в Telegram. Без имени.</p>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}

    <form method="post" action="/">
      <textarea name="message" placeholder="Ваше анонимное сообщение..." required maxlength="2000">{{ request.form.get('message','') }}</textarea>
      <div class="row">
        <button class="btn" type="submit">Отправить анонимно</button>
      </div>
    </form>

    <div class="footer">Макс. длина 2000 символов • Сообщения проходят через Telegram Bot API</div>
  </div>
</body>
</html>
"""

def send_telegram(text: str):
    token = TELEGRAM_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    if not token or not chat_id:
        raise EnvironmentError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не заданы")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, data=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        if not msg:
            flash("Введите текст сообщения.")
            return redirect(url_for("index"))
        # Собираем финальный текст — можно добавить метаданные, но по заданию — анонимно
        try:
            send_telegram(msg)
        except Exception as e:
            flash("Ошибка при отправке. Попробуйте позже.")
            return redirect(url_for("index"))
        flash("Сообщение успешно отправлено!")
        return redirect(url_for("index"))

    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
