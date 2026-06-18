import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = "8978439642:AAGSjQOggCU-C8_fP6Qj7QAEBvuCsgkGoRk"
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

MENUS = {
    "main": {
        "text": "🖥 <b>Информационный бот о ПК</b>\n\nПривет! Здесь ты узнаешь много интересного о компьютерах, их истории, устройстве и фактах. Выбирай раздел:",
        "buttons": [
            ("📜 История ПК", "history"),
            ("⚙️ Устройство ПК", "components"),
            ("💡 Интересные факты", "facts"),
            ("🛠 Советы по сборке", "tips"),
        ]
    },
    "history": {
        "text": "📜 <b>История ПК</b>\n\nОт гигантских машин до карманных суперкомпьютеров.",
        "buttons": [
            ("Первый компьютер", "hist_eniac"),
            ("Рождение персональных ПК", "hist_ibm"),
            ("⬅️ Назад", "main"),
        ]
    },
    "hist_eniac": {
        "text": "🦖 <b>ENIAC (1946 год)</b>\n\nПервый электронный вычислитель. Он весил 27 тонн, занимал 167 кв. метров и содержал 18 000 вакуумных ламп. По легенде, при его включении в Филадельфии гас свет из-за перегрузки сети!",
        "buttons": [("⬅️ Назад", "history")]
    },
    "hist_ibm": {
        "text": "💼 <b>IBM PC (1981 год)</b>\n\nИменно этот компьютер задал стандарты, которые мы используем до сих пор (архитектура x86). Он стоил $1565, не имел жесткого диска и имел всего 16 КБ оперативной памяти!",
        "buttons": [("⬅️ Назад", "history")]
    },
    "components": {
        "text": "⚙️ <b>Устройство ПК</b>\n\nОсновные компоненты современного компьютера.",
        "buttons": [
            ("🧠 Процессор (CPU)", "comp_cpu"),
            ("🎮 Видеокарта (GPU)", "comp_gpu"),
            ("💾 Оперативная память (RAM)", "comp_ram"),
            ("⬅️ Назад", "main"),
        ]
    },
    "comp_cpu": {
        "text": "🧠 <b>Процессор (CPU)</b>\n\n«Мозг» компьютера. Выполняет все вычисления и инструкции. Современные процессоры содержат десятки миллиардов микроскопических транзисторов и работают на частотах свыше 5 ГГц.",
        "buttons": [("⬅️ Назад", "components")]
    },
    "comp_gpu": {
        "text": "🎮 <b>Видеокарта (GPU)</b>\n\nОтвечает за вывод изображения и обработку 3D-графики. Сегодня GPU используются не только в играх, но и для обучения нейросетей (ИИ), майнинга и научных расчетов.",
        "buttons": [("⬅️ Назад", "components")]
    },
    "comp_ram": {
        "text": "💾 <b>Оперативная память (RAM)</b>\n\nСверхбыстрая, но энергозависимая память. Хранит данные, которые процессор использует «прямо сейчас». При выключении ПК она полностью очищается.",
        "buttons": [("⬅️ Назад", "components")]
    },
    "facts": {
        "text": "💡 <b>Интересные факты</b>\n\nУдивительные вещи из мира IT и железа.",
        "buttons": [
            ("Первый «баг»", "fact_bug"),
            ("Закон Мура", "fact_moore"),
            ("Смартфон vs Космос", "fact_phone"),
            ("⬅️ Назад", "main"),
        ]
    },
    "fact_bug": {
        "text": "🦋 <b>Первый компьютерный «баг»</b>\n\nВ 1947 году инженеры нашли настоящего мотылька (moth), застрявшего в реле компьютера Mark II и вызвавшего сбой. С тех пор ошибки в коде и железе называют «багами» (от англ. bug — насекомое).",
        "buttons": [("⬅️ Назад", "facts")]
    },
    "fact_moore": {
        "text": "📈 <b>Закон Мура</b>\n\nГордон Мур в 1965 году предсказал, что количество транзисторов на микросхеме будет удваиваться каждые 2 года. Это эмпирическое правило работало более 50 лет, обеспечив взрывной рост технологий!",
        "buttons": [("⬅️ Назад", "facts")]
    },
    "fact_phone": {
        "text": "📱 <b>Смартфон против Apollo</b>\n\nВаш современный смартфон в миллионы раз мощнее, чем бортовые компьютеры NASA, которые отправляли астронавтов на Луну в 1969 году. Памяти в вашем телефоне больше, чем было во всех вычислительных мощностях Земли в 1970-х.",
        "buttons": [("⬅️ Назад", "facts")]
    },
    "tips": {
        "text": "🛠 <b>Советы по сборке</b>\n\nНа что обратить внимание при выборе комплектующих?",
        "buttons": [
            ("🎮 Для игр", "tip_game"),
            ("💼 Для работы", "tip_work"),
            ("⬅️ Назад", "main"),
        ]
    },
    "tip_game": {
        "text": "🎮 <b>Игровой ПК</b>\n\nГлавное — <b>видеокарта</b>. На нее стоит тратить до 40-50% бюджета. Процессор должен быть достаточно мощным, чтобы не ограничивать видеокарту (избегать «бутылочного горлышка»), а блок питания должен иметь запас мощности в 20-30%.",
        "buttons": [("⬅️ Назад", "tips")]
    },
    "tip_work": {
        "text": "💼 <b>Рабочий ПК</b>\n\nДля монтажа видео, 3D-моделирования и программирования важны <b>многоядерный процессор</b>, <b>большой объем RAM</b> (от 32 ГБ) и <b>быстрый SSD</b> (формата NVMe). Видеокарта вторична, если вы не занимаетесь рендерингом 3D-сцен.",
        "buttons": [("⬅️ Назад", "tips")]
    }
}


def kb(buttons):
    return {"inline_keyboard": [[{"text": t, "callback_data": c}] for t, c in buttons]}


def api_call(method, **kwargs):
    try:
        r = requests.post(f"{API_URL}/{method}", json=kwargs, timeout=15)
        return r.json()
    except Exception as e:
        print(f"API error {method}: {e}")
        return None


def send_message(chat_id, text, buttons=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = kb(buttons)
    return api_call("sendMessage", **payload)


def edit_message(chat_id, message_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if buttons:
        payload["reply_markup"] = kb(buttons)
    return api_call("editMessageText", **payload)


def answer_callback(callback_id):
    api_call("answerCallbackQuery", callback_query_id=callback_id)


def show_menu(chat_id, message_id, menu_name):
    menu = MENUS[menu_name]
    edit_message(chat_id, message_id, menu["text"], menu["buttons"])


def handle_callback(chat_id, message_id, button_id):
    if button_id in MENUS:
        show_menu(chat_id, message_id, button_id)
    else:
        edit_message(chat_id, message_id, "❌ Ошибка: такого раздела нет.")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        if text.startswith("/start"):
            menu = MENUS["main"]
            send_message(chat_id, menu["text"], menu["buttons"])

    elif "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]
        button_id = cq["data"]
        answer_callback(cq["id"])
        handle_callback(chat_id, message_id, button_id)

    return jsonify(ok=True)


@app.route("/")
def index():
    return "Bot is running", 200


def setup_webhook():
    if not RENDER_URL:
        print("RENDER_EXTERNAL_URL не задан")
        return
    url = f"{RENDER_URL}/webhook"
    r = requests.post(f"{API_URL}/setWebhook", json={"url": url}, timeout=15)
    print("setWebhook:", r.text)


if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
