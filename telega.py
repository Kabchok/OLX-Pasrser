from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import sqlite3, os
from subprocess import run
from dotenv import load_dotenv

load_dotenv("token.env")
TOKEN = os.getenv('TOKEN')
app = ApplicationBuilder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📊 Показать средние цены за 1-комн.")],
            [KeyboardButton("📊 Показать средние цены за 2-комн.")],
            [KeyboardButton("📊 Показать средние цены за 3-комн.")],
            [KeyboardButton("🔁 Обновить данные")]
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Привет! Я бот для мониторинга цен на квартиры на OLX 🏠",
        reply_markup=keyboard
    )


async def avg_handler_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Средние цены за 1 комнатную квартиру")
    conn2 = sqlite3.connect("data/pokazateli.db")
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT avg_price, avg_area, avg_price_per_m2, avg_30_35 FROM pokazateli ORDER BY id DESC LIMIT 1")
    row = cursor2.fetchone()
    conn2.close()

    if row:
        avg_price, avg_area, avg_price_per_m2, avg_30_35 = row
        await update.message.reply_text(
            f"🏷 Средняя цена: {avg_price} $ за среднюю площадь {avg_area} м²\n"
            f"💰 Цена за 1 м²: {avg_price_per_m2} $\n"
            f"🏘 Средняя цена (30–35 м²): {avg_30_35} $"
        )
    else:
        await update.message.reply_text("⛔ Данных пока нет.")


async def avg_handler_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Средние цены за 2 комнатную квартиру")
    conn2 = sqlite3.connect("data/pokazateli2.db")
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT avg_price, avg_area, avg_price_per_m2, avg_46_55 FROM pokazateli2 ORDER BY id DESC LIMIT 1")
    row = cursor2.fetchone()
    conn2.close()
    if row:
        avg_price, avg_area, avg_price_per_m2, avg_46_55 = row
        await update.message.reply_text(
            f"🏷 Средняя цена: {avg_price} $ за среднюю площадь {avg_area} м²\n"
            f"💰 Цена за 1 м²: {avg_price_per_m2} $\n"
            f"🏘 Средняя цена (46–55 м²): {avg_46_55} $"
        )
    else:
        await update.message.reply_text("⛔ Данных пока нет.")


async def avg_handler_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Средние цены за 3 комнатную квартиру")
    conn2 = sqlite3.connect("data/pokazateli3.db")
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT avg_price, avg_area, avg_price_per_m2, avg_60_70 FROM pokazateli3 ORDER BY id DESC LIMIT 1")
    row = cursor2.fetchone()
    conn2.close()
    if row:
        avg_price, avg_area, avg_price_per_m2, avg_60_70 = row
        await update.message.reply_text(
            f"🏷 Средняя цена: {avg_price} $ за среднюю площадь {avg_area} м²\n"
            f"💰 Цена за 1 м²: {avg_price_per_m2} $\n"
            f"🏘 Средняя цена (60-70 м²): {avg_60_70} $"
        )
    else:
        await update.message.reply_text("⛔ Данных пока нет.")


async def update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Обновляю данные, подожди...")

    errors = []

    try:
        run(["python", "parcing.py"], check=True)
    except Exception as e:
        errors.append("1-комн.: ❌ " + str(e))

    try:
        run(["python", "parcing_2.py"], check=True)
    except Exception as e:
        errors.append("2-комн.: ❌ " + str(e))

    try:
        run(["python", "parcing_3.py"], check=True)
    except Exception as e:
        errors.append("3-комн.: ❌ " + str(e))

    if errors:
        await update.message.reply_text("⚠️ Обновление завершено с ошибками:\n" + "\n".join(errors))
    else:
        await update.message.reply_text("✅ Все данные успешно обновлены!")


app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📊 Показать средние цены за 1-комн\.$"), avg_handler_1))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📊 Показать средние цены за 2-комн\.$"), avg_handler_2))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📊 Показать средние цены за 3-комн\.$"), avg_handler_3))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🔁 Обновить данные$"), update_handler))
app.run_polling()

