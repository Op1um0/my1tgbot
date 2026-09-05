import os
import random
import requests
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

# --- СПИСОК ШУТОК ТАРАНТИНО (10 старых + 10 новых = 20) ---
TARANTINO_QUOTES = [
    # Старые
    "«Это забавно: насколько всё меняется, когда начинаешь говорить правду» — Криминальное чтиво",
    "«Зэд мёртв, детка. Зэд мёртв» — Криминальное чтиво",
    "«Вы будете лаять весь день, маленький пёсик? Или вы укусите?» — Бешеные псы",
    "«Когда попадёшь в ад, Джон, скажи им, что тебя послала Дэйзи» — Омерзительная восьмёрка",
    "«Меня зовут Шошанна Дрейфус, и это лицо… еврейской мести!» — Бесславные ублюдки",
    "«Английский, мать твою, ты говоришь на нём?» — Криминальное чтиво",
    "«Я, может, и ублюдок, но я не гребаный ублюдок» — От заката до рассвета",
    "«Мы в бизнесе убийства нацистов. И дела идут отлично» — Бесславные ублюдки",
    "«Итак, когда ты вырастешь, я буду ждать» — Убить Билла",
    "«Королевский с сыром» — Криминальное чтиво",
    # Новые 10 шуток
    "«Мне плевать, что ты говоришь, мне плевать, что ты делаешь, но не смей называть меня негодяем!» — Бешеные псы",
    "«Ты не знаешь, кто я такой, но я знаю, кто ты. И я найду тебя» — Убить Билла",
    "«Я хочу сыграть в игру. Угадай, что в моей руке?» — Джанго освобождённый",
    "«Сюрприз, сука! Я уверен, ты не ожидал меня увидеть» — Бесславные ублюдки",
    "«Если ты хочешь добиться успеха, ты должен верить в себя. Но не слишком сильно, иначе ты поверишь в то, что ты можешь летать» — Джанго освобождённый",
    "«Это очень плохой день для того, чтобы быть предателем» — Бешеные псы",
    "«Они съели мою собаку. Это было очень плохо. Я съел их» — Омерзительная восьмёрка",
    "«Я играю роль самого себя. Ты просто играешь роль самого себя. Все мы просто играем роли самих себя» — Криминальное чтиво",
    "«Если в этом мире есть одна вещь, которую я ненавижу, так это то, когда люди не доводят начатое до конца» — Бесславные ублюдки",
    "«Я не убийца. Я просто человек, который любит решать проблемы. Просто иногда мои решения кровавые» — Убить Билла"
]

# --- КОМАНДЫ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я универсальный бот.\n"
        "Команды:\n"
        "/help - список команд\n"
        "/quote - случайная цитата из фильмов Тарантино\n"
        "/btc - курс Биткоина\n"
        "/moex - индекс МосБиржи\n"
        "/weather - погода в Ростове-на-Дону"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/quote - случайная цитата из фильмов Тарантино\n"
        "/btc - курс Биткоина (USD)\n"
        "/moex - индекс МосБиржи (IMOEX)\n"
        "/weather - погода в Ростове-на-Дону"
    )

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = random.choice(TARANTINO_QUOTES)
    await update.message.reply_text(joke)

async def btc_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=10)
        data = response.json()
        price = data['bitcoin']['usd']
        await update.message.reply_text(f"💰 Курс Биткоина (BTC/USD): ${price:,.2f}")
    except Exception as e:
        await update.message.reply_text("Не удалось получить курс Биткоина. Попробуйте позже.")

async def moex_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Добавляем заголовок User-Agent, чтобы API не блокировало запрос
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = "https://iss.moex.com/iss/statistics/engines/stock/markets/index/securities/IMOEX.json"
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        current_price = None
        if 'marketdata' in data and 'columns' in data['marketdata']:
            cols = data['marketdata']['columns']
            rows = data['marketdata']['data']
            for row in rows:
                if 'CURRENTVALUE' in cols:
                    index = cols.index('CURRENTVALUE')
                    current_price = row[index]
                    break
        
        if current_price:
            await update.message.reply_text(f"📈 Индекс МосБиржи (IMOEX): {current_price}")
        else:
            await update.message.reply_text("Не удалось получить данные индекса МосБиржи (сервер вернул пустоту).")
    except Exception as e:
        await update.message.reply_text("Не удалось получить данные индекса МосБиржи. Скорее всего, API блокирует запросы из-за границы.")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get('https://wttr.in/Rostov-on-Don?format=j1', timeout=10)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        desc = current['weatherDesc'][0]['value']
        feels_like = current['FeelsLikeC']
        await update.message.reply_text(
            f"🌤️ Погода в Ростове-на-Дону:\n"
            f"Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"Описание: {desc}"
        )
    except Exception as e:
        await update.message.reply_text("Не удалось получить данные о погоде.")

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Запуск бота...")
    
    import threading
    port = int(os.environ.get("PORT", 5000))
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True)
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quote", quote))
    application.add_handler(CommandHandler("btc", btc_price))
    application.add_handler(CommandHandler("moex", moex_index))
    application.add_handler(CommandHandler("weather", weather))

    print("Бот запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
