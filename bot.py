import os
from flask import Flask, request
import telebot

# Токен и ID канала из окружения
TOKEN      = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]  # строка, либо "@dropifycs", либо "-1001234567890"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL  = os.environ["WEBHOOK_URL"]  # https://dropify-bot.onrender.com

# Health‑check для Render
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

# Webhook-роут
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    txt = (
        "Добро пожаловать в Dropify CS бот!\n\n"
        "/promo — Промокоды\n"
        "/daily — Халява дня\n"
        "/links — Партнёрские сайты\n"
        "/stats — Статистика канала"
    )
    bot.reply_to(message, txt)

# Команда /promo
@bot.message_handler(commands=['promo'])
def send_promo(message):
    promo = """🔥 АКТУАЛЬНЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
Farmskins — DROPIFYCS
CaseBattle — DROPIFYCS
DinoDrop — DROPIFYCS
ForceDrop — DROPIFYCS
"""
    bot.send_message(message.chat.id, promo)

# Команда /daily
@bot.message_handler(commands=['daily'])
def send_daily(message):
    daily = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.
4. DinoDrop — бонус за вход + шанс на скин.
5. ForceDrop — бонус за депозит и фри-спины.
"""
    bot.send_message(message.chat.id, daily)

# Команда /links
@bot.message_handler(commands=['links'])
def send_links(message):
    links = """🔗 ПАРТНЁРСКИЕ ССЫЛКИ:

Hellcase:   https://hellcase.com/partner
Farmskins: https://farmskins.com/partner
CaseBattle: https://case-battle.com/partner
DinoDrop:   https://dino-drop.com/partner
ForceDrop:  https://forcedrop.com/partner
"""
    bot.send_message(message.chat.id, links)

# Команда /stats
@bot.message_handler(commands=['stats'])
def send_stats(message):
    try:
        count = bot.get_chat_member_count(CHANNEL_ID)
    except Exception:
        # fallback: попробуем через get_chat
        chat = bot.get_chat(CHANNEL_ID)
        count = chat.get("members_count", "❓")
    bot.send_message(message.chat.id, f"👥 Подписчиков на канале: {count}")

# Эндпоинт для внешнего cron‑запроса
@app.route("/post_daily", methods=["POST"])
def post_daily():
    daily = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.
4. DinoDrop — бонус за вход + шанс на скин.
5. ForceDrop — бонус за депозит и фри-спины.
"""
    bot.send_message(CHANNEL_ID, daily)
    return "Posted", 200

if __name__ == "__main__":
    # устанавливаем webhook
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    # запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
