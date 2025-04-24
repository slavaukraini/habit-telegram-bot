
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from datetime import datetime
import json

# Встановлення логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Заміни на свій токен
TOKEN = "7952224923:AAE6tWMZTQSrjz7Zj1dbCRki-Y0b3ZOQSCw"

# Дані користувача (тестова реалізація в JSON)
USER_DATA = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [["Медитація ✅", "Розтяжка ✅"],
                ["Прокинувся до 7:00 🌅", "Куріння 🚬"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"Привіт, {user.first_name}! Це твій трекер звичок 🌿

Обери, що ти сьогодні вже зробив 👇",
        reply_markup=reply_markup
    )

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

    # Зберегти у файл (можна змінити на базу)
    with open("user_data.json", "w") as f:
        json.dump(USER_DATA, f)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    main()
