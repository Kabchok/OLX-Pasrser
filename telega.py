from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import sqlite3
from subprocess import run

TOKEN = '7720418342:AAEmY_B4csTzD5boafVspvOdLba_rbNnJS0'
app = ApplicationBuilder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📊 Показать средние цены за 1 комнатную квартиру")],
            [KeyboardButton("🔁 Обновить данные")]
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Привет! Я бот для мониторинга цен на квартиры на OLX 🏠",
        reply_markup=keyboard
    )


async def avg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Средние цены за 1 комнатную квартиру")
    conn2 = sqlite3.connect("data/pokazateli.db")
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT avg_price, avg_area, avg_price_per_m2, avg_30_35 FROM pokazateli ORDER BY id DESC LIMIT 1")
    avg_price, avg_area, avg_price_per_m2, avg_30_35 = cursor2.fetchone()
    conn2.close()
    await update.message.reply_text(
        f"🏷 Средняя цена: {avg_price} $ за среднюю площадь {avg_area} м²\n"
        f"💰 Цена за 1 м²: {avg_price_per_m2} $\n"
        f"🏘 Средняя цена (30–35 м²): {avg_30_35} $"
    )


async def update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Обновляю данные, подожди...")
    run(["python", "parcing.py"])  # запуск сбора
    await update.message.reply_text("✅ Данные обновлены!")


app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔁 Обновить данные$"), update_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📊 Показать средние цены за 1 комнатную квартиру$"), avg_handler))
app.add_handler(CommandHandler("start", start))
app.run_polling()

