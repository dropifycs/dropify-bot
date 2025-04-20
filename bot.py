import os
from flask import Flask, request
import telebot

# Читаем токен из переменных окружения
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Должен быть вида https://<ваш-домен>.onrender.com

# (Опционально) роут для health‑check
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

# Webhook-обработчик от Telegram
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Команды бота
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
    promo_text = """🔥 АКТИВНЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
Farmskins — DROPIFYCS
DinoDrop — DROPIFYCS
ForceDrop — DROPIFYCS
"""
    bot.send_message(message.chat.id, promo_text)

@bot.message_handler(commands=['daily'])
def send_daily(message):
    daily_text = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
4. DinoDrop — бонус за вход + шанс на скин каждый день.
5. ForceDrop — бонус за депозит и фри-спины ежедневно.
"""
    bot.send_message(message.chat.id, daily_text)

@bot.message_handler(commands=['links'])
def send_links(message):
    links_text = """🔗 ПОЛЕЗНЫЕ ПАРТНЁРСКИЕ ССЫЛКИ:

Hellcase: https://hellcase.com
Farmskins: https://farmskins.com
DinoDrop: https://dino-drop.com
ForceDrop: https://forcedrop.vip
"""
    bot.send_message(message.chat.id, links_text)

if __name__ == "__main__":
    # Устанавливаем webhook при старте
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")

    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
