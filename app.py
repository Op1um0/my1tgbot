import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен в переменных окружения")

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот.")

async def run_bot():
    """Запускает бота"""
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Бот запускается и слушает сообщения...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Держим бота в работе вечно
    stop_signal = asyncio.Event()
    await stop_signal.wait()

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    import threading
    port = int(os.environ.get("PORT", 5000))
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True)
    flask_thread.start()

    # Запускаем бота в главном асинхронном цикле
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
