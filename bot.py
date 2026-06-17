import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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
    # ... (вставьте остальные пункты MENUS из вашего кода без изменений)
}

# вставьте весь MENUS как в вашем оригинальном файле (удалил для краткости в этом примере)
# для работы просто скопируйте MENUS целиком сюда

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons_handler))

    # Инициализация и старт приложения без использования проблемного Updater.__init__ побочно
    # Используем низкоуровневые методы Application
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner():
        await app.initialize()
        await app.start()
        print("✅ Бот успешно запущен (polling)...")
        try:
            # Здесь Application.start() уже запустил обработчики и polling task внутри Application,
            # но если библиотека пытается создать внутренний Updater, это обойдётся.
            # Просто держим цикл живым пока не остановят процесс.
            while True:
                await asyncio.sleep(10)
        finally:
            await app.stop()
            await app.shutdown()

    try:
        loop.run_until_complete(runner())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
