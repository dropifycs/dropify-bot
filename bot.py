import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request
import telebot

# === File Logging Setup ===
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(
    'bot.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Also log Flask (werkzeug) events
logging.getLogger('werkzeug').addHandler(file_handler)

# === Telegram Bot and Flask Setup ===
TOKEN      = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g. https://dropify-bot.onrender.com

if not TOKEN:
    logger.error("BOT_TOKEN environment variable is missing")
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_PATH = f"/{TOKEN}"

# Health-check for Render
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

# Webhook endpoint
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

# Bot command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    txt = (
        "Добро пожаловать в Dropify CS бот!\n\n"
        "/promo — Промокоды\n"
        "/daily — Халява дня\n"
        "/links — Партнёрские сайты\n"
        "/stats — Статистика канала"
    )
    logger.info(f"Handled /start from {message.chat.id}")
    bot.reply_to(message, txt)

@bot.message_handler(commands=['promo'])
def send_promo(message):
    promo = """🔥 АКТИВНЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
Farmskins — DROPIFYCS
CaseBattle — DROPIFYCS
DinoDrop — DROPIFYCS
ForceDrop — DROPIFYCS
"""
    logger.info(f"Handled /promo for {message.chat.id}")
    bot.send_message(message.chat.id, promo)

@bot.message_handler(commands=['daily'])
def send_daily(message):
    daily = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.
4. DinoDrop — бонус за вход + шанс на скин.
5. ForceDrop — бонус за депозит и фри-спины.
"""
    logger.info(f"Handled /daily for {message.chat.id}")
    bot.send_message(message.chat.id, daily)

@bot.message_handler(commands=['links'])
def send_links(message):
    links = """🔗 ПАРТНЁРСКИЕ ССЫЛКИ:

Hellcase:   https://hellcase.com/partner
Farmskins: https://farmskins.com/partner
CaseBattle: https://case-battle.com/partner
DinoDrop:   https://dino-drop.com/partner
ForceDrop:  https://forcedrop.com/partner
"""
    logger.info(f"Handled /links for {message.chat.id}")
    bot.send_message(message.chat.id, links)

@bot.message_handler(commands=['stats'])
def send_stats(message):
    try:
        count = bot.get_chat_member_count(CHANNEL_ID)
    except Exception as e:
        logger.error("Error fetching chat member count", exc_info=True)
        chat = bot.get_chat(CHANNEL_ID)
        count = chat.get("members_count", "❓")
    bot.send_message(message.chat.id, f"👥 Подписчиков на канале: {count}")

# Endpoint for external cron requests\ n@app.route("/post_daily", methods=["POST"])
def post_daily():
    daily = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.
4. DinoDrop — бонус за вход + шанс на скин.
5. ForceDrop — бонус за депозит и фри-спины.
"""
    logger.info("Posting daily update to channel")
    bot.send_message(CHANNEL_ID, daily)
    return "Posted", 200

if __name__ == "__main__":
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info("Webhook set, bot is starting")

    # Run Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
