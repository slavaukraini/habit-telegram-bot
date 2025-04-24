
import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
USER_DATA = {}
SCHEDULED_USERS = set()

keyboard = [["Медитація ✅", "Розтяжка ✅"],
            ["Прокинувся до 7:00 🌅", "Куріння 🚬"]]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    SCHEDULED_USERS.add(user.id)
    msg = f"Привіт, {user.first_name}! Це твій трекер звичок 🌿\n\nОбери, що ти сьогодні вже зробив 👇"
    await update.message.reply_text(msg, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    msg = update.message.text
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {}

    if date_str not in USER_DATA[user_id]:
        USER_DATA[user_id][date_str] = {
            "meditation": False,
            "stretching": False,
            "wake_early": False,
            "smoking": 0
        }

    if "Медитація" in msg:
        USER_DATA[user_id][date_str]["meditation"] = True
        await update.message.reply_text("🧘 Медитацію зафіксовано!")

    elif "Розтяжка" in msg:
        USER_DATA[user_id][date_str]["stretching"] = True
        await update.message.reply_text("🧘‍♂️ Розтяжку зафіксовано!")

    elif "Прокинувся" in msg:
        USER_DATA[user_id][date_str]["wake_early"] = True
        await update.message.reply_text("🌅 Прокинувся вчасно — молодець!")

    elif "Куріння" in msg:
        await update.message.reply_text("🚬 Напиши, скільки сьогодні сигарет викурив?")
        return

    elif msg.isdigit():
        USER_DATA[user_id][date_str]["smoking"] += int(msg)
        await update.message.reply_text(f"🚬 Занотував: {msg} сигарет")

    with open("user_data.json", "w") as f:
        json.dump(USER_DATA, f)

async def send_reminders(application):
    for user_id in SCHEDULED_USERS:
        try:
            await application.bot.send_message(
                chat_id=user_id,
                text="Доброго ранку 🌞\nЯк почався день?\n\n🔘 Прокинувся до 7:00\n🔘 Розтяжка\n🔘 Медитація\n🔘 Курив? Скільки?",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Не вдалося надіслати повідомлення {user_id}: {e}")

def schedule_daily_job(application):
    scheduler = BackgroundScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(lambda: asyncio.run(send_reminders(application)),
                      trigger='cron', hour=8, minute=0)
    scheduler.start()

def main():
    print("🚀 Бот запускається...")  # Видно у Railway
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    schedule_daily_job(app)

    print("✅ Бот запущено з щоденним нагадуванням о 8:00...")  # Railway побачить це
    app.run_polling()

if __name__ == "__main__":
    main()
