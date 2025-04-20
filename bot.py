import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # зададим чуть позже

# Обработчики бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Добро пожаловать в Dropify CS бот!\n\n"
        "/promo — Промокоды\n"
        "/daily — Халява дня\n"
        "/links — Партнёрские сайты"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['promo'])
def send_promo(message):
    bot.send_message(message.chat.id, 
        "🔥 АКТИВНЫЕ ПРОМОКОДЫ:\n\n"
        "Hellcase — DROPIFYCS\n"
        "CSGOEmpire — DROPIFY\n"
        "Farmskins — DROPIFYCS\n"
        "KeyDrop — DROPIFYCS\n"
        "SkinClub — DROPIFY"
    )

@bot.message_handler(commands=['daily'])
def send_daily(message):
    bot.send_message(message.chat.id, 
        "🎁 ХАЛЯВА НА СЕГОДНЯ:\n\n"
        "1. Hellcase — бесплатный бонус каждый день.\n"
        "2. CSGOEmpire — получи монету с кодом DROPIFY.\n"
        "3. Farmskins — колёсико халявы каждый день."
    )

@bot.message_handler(commands=['links'])
def send_links(message):
    bot.send_message(message.chat.id, 
        "🔗 ПОЛЕЗНЫЕ ССЫЛКИ:\n\n"
        "Hellcase: https://hellcase.com/partner\n"
        "CSGOEmpire: https://csgoempire.com\n"
        "Farmskins: https://farmskins.com/partner\n"
        "KeyDrop: https://key-drop.com/promotion\n"
        "SkinClub: https://skin.club"
    )

# Обработка webhook-запросов от Telegram
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    # Устанавливаем webhook при старте
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
