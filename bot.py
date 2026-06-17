import time
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

TOKEN = "8978439642:AAGSjQOggCU-C8_fP6Qj7QAEBvuCsgkGoRk"

# Встроенные тексты и кнопки (без словаря MENUS)
MAIN_TEXT = "🖥 <b>Информационный бот о ПК</b>\n\nПривет! Здесь ты узнаешь много интересного о компьютерах, их истории, устройстве и фактах. Выбирай раздел:"
MAIN_BUTTONS = [
    ("📜 История ПК", "history"),
    ("⚙️ Устройство ПК", "components"),
    ("💡 Интересные факты", "facts"),
    ("🛠 Советы по сборке", "tips"),
]

HISTORY_TEXT = "📜 <b>История ПК</b>\n\nОт гигантских машин до карманных суперкомпьютеров."
HISTORY_BUTTONS = [
    ("Первый компьютер", "hist_eniac"),
    ("Рождение персональных ПК", "hist_ibm"),
    ("⬅️ Назад", "main"),
]

HIST_ENIAC_TEXT = "🦖 <b>ENIAC (1946 год)</b>\n\nПервый электронный вычислитель. Он весил 27 тонн, занимал 167 кв. метров и содержал 18 000 вакуумных ламп. По легенде, при его включении в Филадельфии гас свет из-за перегрузки сети!"
HIST_IBM_TEXT = "💼 <b>IBM PC (1981 год)</b>\n\nИменно этот компьютер задал стандарты, которые мы используем до сих пор (архитектура x86). Он стоил $1565, не имел жесткого диска и имел всего 16 КБ оперативной памяти!"

COMPONENTS_TEXT = "⚙️ <b>Устройство ПК</b>\n\nОсновные компоненты современного компьютера."
COMPONENTS_BUTTONS = [
    ("🧠 Процессор (CPU)", "comp_cpu"),
    ("🎮 Видеокарта (GPU)", "comp_gpu"),
    ("💾 Оперативная память (RAM)", "comp_ram"),
    ("⬅️ Назад", "main"),
]
COMP_CPU_TEXT = "🧠 <b>Процессор (CPU)</b>\n\n«Мозг» компьютера. Выполняет все вычисления и инструкции."
COMP_GPU_TEXT = "🎮 <b>Видеокарта (GPU)</b>\n\nОтвечает за вывод изображения и обработку 3D-графики."
COMP_RAM_TEXT = "💾 <b>Оперативная память (RAM)</b>\n\nСверхбыстрая, но энергозависимая память."

FACTS_TEXT = "💡 <b>Интересные факты</b>\n\nУдивительные вещи из мира IT и железа."
FACTS_BUTTONS = [
    ("Первый «баг»", "fact_bug"),
    ("Закон Мура", "fact_moore"),
    ("Смартфон vs Космос", "fact_phone"),
    ("⬅️ Назад", "main"),
]
FACT_BUG_TEXT = "🦋 <b>Первый компьютерный «баг»</b>\n\nВ 1947 году инженеры нашли мотылька в реле Mark II."
FACT_MOORE_TEXT = "📈 <b>Закон Мура</b>\n\nКоличество транзисторов удваивалось каждые ~2 года."
FACT_PHONE_TEXT = "📱 <b>Смартфон против Apollo</b>\n\nСовременный смартфон мощнее бортового компьютера Apollo."

TIPS_TEXT = "🛠 <b>Советы по сборке</b>\n\nНа что обратить внимание при выборе комплектующих?"
TIPS_BUTTONS = [
    ("🎮 Для игр", "tip_game"),
    ("💼 Для работы", "tip_work"),
    ("⬅️ Назад", "main"),
]
TIP_GAME_TEXT = "🎮 <b>Игровой ПК</b>\n\nГлавное — видеокарта; процессор и БП с запасом."
TIP_WORK_TEXT = "💼 <b>Рабочий ПК</b>\n\nМногоядерный CPU, много RAM и быстрый NVMe SSD."

def create_keyboard(buttons):
    kb = []
    for t, d in buttons:
        kb.append([InlineKeyboardButton(t, callback_data=d)])
    return InlineKeyboardMarkup(kb)

def get_content_by_key(key):
    # возвращает (text, keyboard) по callback_data/ключу
    if key == "main":
        return MAIN_TEXT, create_keyboard(MAIN_BUTTONS)
    if key == "history":
        return HISTORY_TEXT, create_keyboard(HISTORY_BUTTONS)
    if key == "hist_eniac":
        return HIST_ENIAC_TEXT, create_keyboard([("⬅️ Назад", "history")])
    if key == "hist_ibm":
        return HIST_IBM_TEXT, create_keyboard([("⬅️ Назад", "history")])
    if key == "components":
        return COMPONENTS_TEXT, create_keyboard(COMPONENTS_BUTTONS)
    if key == "comp_cpu":
        return COMP_CPU_TEXT, create_keyboard([("⬅️ Назад", "components")])
    if key == "comp_gpu":
        return COMP_GPU_TEXT, create_keyboard([("⬅️ Назад", "components")])
    if key == "comp_ram":
        return COMP_RAM_TEXT, create_keyboard([("⬅️ Назад", "components")])
    if key == "facts":
        return FACTS_TEXT, create_keyboard(FACTS_BUTTONS)
    if key == "fact_bug":
        return FACT_BUG_TEXT, create_keyboard([("⬅️ Назад", "facts")])
    if key == "fact_moore":
        return FACT_MOORE_TEXT, create_keyboard([("⬅️ Назад", "facts")])
    if key == "fact_phone":
        return FACT_PHONE_TEXT, create_keyboard([("⬅️ Назад", "facts")])
    if key == "tips":
        return TIPS_TEXT, create_keyboard(TIPS_BUTTONS)
    if key == "tip_game":
        return TIP_GAME_TEXT, create_keyboard([("⬅️ Назад", "tips")])
    if key == "tip_work":
        return TIP_WORK_TEXT, create_keyboard([("⬅️ Назад", "tips")])
    return "❌ Ошибка: такого раздела нет.", None

def handle_update(bot: Bot, update):
    try:
        if update.message:
            txt = (update.message.text or "").strip()
            chat_id = update.message.chat.id
            if txt.startswith("/start"):
                text, kb = get_content_by_key("main")
                bot.send_message(chat_id=chat_id, text=text, reply_markup=kb, parse_mode="HTML")
        elif update.callback_query:
            cq = update.callback_query
            data = cq.data
            chat_id = cq.message.chat.id
            message_id = cq.message.message_id
            text, kb = get_content_by_key(data)
            if kb is None:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)
            else:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=kb, parse_mode="HTML")
            try:
                bot.answer_callback_query(callback_query_id=cq.id)
            except Exception:
                pass
    except TelegramError as e:
        print("TelegramError:", e)

def main():
    bot = Bot(token=TOKEN)
    offset = None
    print("✅ Bot started (get_updates loop)")
    while True:
        try:
            updates = bot.get_updates(offset=offset, timeout=30, allowed_updates=["message", "callback_query"])
            for upd in updates:
                offset = (upd.update_id or 0) + 1
                handle_update(bot, upd)
        except TelegramError as e:
            print("TelegramError in get_updates:", e)
            time.sleep(5)
        except Exception as e:
            print("Unexpected error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
