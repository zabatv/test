import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# TOKEN оставлен в коде по вашему запросу
TOKEN = "8978439642:AAGSjQOggCU-C8_fP6Qj7QAEBvuCsgkGoRk"

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
        "text": "🦋 <b>Первый компьютерный «баг»</b>\n\nВ 1947 году инженеры нашли настоящего мотылька (moth), застрявшего в реле компьютера Mark II и вызвавшем сбой. С тех пор ошибки в коде и железе называют «багами» (от англ. bug — насекомое).",
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

def create_keyboard(buttons):
    keyboard = []
    for text, callback_data in buttons:
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
    return InlineKeyboardMarkup(keyboard)

async def show_menu(query, menu_name):
    menu = MENUS[menu_name]
    await query.edit_message_text(
        text=menu["text"],
        reply_markup=create_keyboard(menu["buttons"]),
        parse_mode="HTML"
    )

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = MENUS["main"]
    await update.message.reply_text(
        text=menu["text"],
        reply_markup=create_keyboard(menu["buttons"]),
        parse_mode="HTML"
    )

async def buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    button_id = query.data
    if button_id in MENUS:
        await show_menu(query, button_id)
    else:
        await query.edit_message_text("❌ Ошибка: такого раздела нет.")

async def run():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(buttons_handler))

    await app.initialize()
    await app.start()
    print("✅ Бот успешно запущен!")
    try:
        await app.updater.start_polling()
        await asyncio.Event().wait()
    finally:
        await app.updater.stop_polling()
        await app.stop()
        await app.shutdown()

def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
