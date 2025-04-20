import os
import json
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
logging.getLogger('werkzeug').addHandler(file_handler)

# === Telegram Bot & Flask ===
TOKEN       = os.environ.get("BOT_TOKEN")
CHANNEL_ID  = os.environ.get("CHANNEL_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not TOKEN:
    logger.error("BOT_TOKEN environment variable missing")
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
WEBHOOK_PATH = f"/{TOKEN}"

# === Subscribers ===
SUBSCRIBERS_FILE = 'subscribers.json'
try:
    with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
        subscribers = set(json.load(f))
except:
    subscribers = set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(subscribers), f, ensure_ascii=False, indent=2)

# === Contest ===
contest_active = False
claimed_users = set()

# === Routes ===
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/notify_promo", methods=["POST"])
def notify_promo():
    promo_text = (
        "🔥 НОВЫЕ ПРОМОКОДЫ:\n\n"
        "Hellcase — DROPIFYCS\n"
        "Farmskins — DROPIFYCS\n"
        "CaseBattle — DROPIFYCS\n"
        "DinoDrop — DROPIFYCS\n"
        "ForceDrop — DROPIFYCS"
    )
    logger.info("Notifying promo subscribers")
    removed = []
    for user_id in list(subscribers):
        try:
            bot.send_message(user_id, promo_text)
        except:
            removed.append(user_id)
    for rid in removed:
        subscribers.discard(rid)
    save_subscribers()
    return "Notified", 200

@app.route("/post_daily", methods=["POST"])
def post_daily():
    daily_text = (
        "🎁 ХАЛЯВА НА СЕГОДНЯ:\n\n"
        "1. Hellcase — бесплатный бонус каждый день.\n"
        "2. Farmskins — колёсико халявы каждый день.\n"
        "3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.\n"
        "4. DinoDrop — бонус за вход + шанс на скин.\n"
        "5. ForceDrop — бонус за депозит и фри-спины."
    )
    logger.info("Posting daily update to channel")
    bot.send_message(CHANNEL_ID, daily_text)
    return "Posted", 200

# === Personal Handlers ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    text = (
        "Добро пожаловать в Dropify CS бот!\n\n"
        "/promo — Промокоды\n"
        "/daily — Халява дня\n"
        "/links — Партнёрские сайты\n"
        "/stats — Статистика канала\n"
        "/subscribe — Личные уведомления\n"
        "/unsubscribe — Отписаться от уведомлений\n"
        "/start_contest — Запустить конкурс\n"
        "/stop_contest — Остановить конкурс\n"
        "/claim — Участвовать в конкурсе"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['promo'])
def handle_promo(message):
    promo = (
        "🔥 АКТИВНЫЕ ПРОМОКОДЫ:\n\n"
        "Hellcase — DROPIFYCS\n"
        "Farmskins — DROPIFYCS\n"
        "CaseBattle — DROPIFYCS\n"
        "DinoDrop — DROPIFYCS\n"
        "ForceDrop — DROPIFYCS"
    )
    bot.send_message(message.chat.id, promo)

@bot.message_handler(commands=['daily'])
def handle_daily(message):
    daily = (
        "🎁 ХАЛЯВА НА СЕГОДНЯ:\n\n"
        "1. Hellcase — бесплатный бонус каждый день.\n"
        "2. Farmskins — колёсико халявы каждый день.\n"
        "3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.\n"
        "4. DinoDrop — бонус за вход + шанс на скин.\n"
        "5. ForceDrop — бонус за депозит и фри-спины."
    )
    bot.send_message(message.chat.id, daily)

@bot.message_handler(commands=['links'])
def handle_links(message):
    links = (
        "🔗 ПАРТНЁРСКИЕ ССЫЛКИ:\n\n"
        "Hellcase: https://hellcase.com/partner\n"
        "Farmskins: https://farmskins.com/partner\n"
        "CaseBattle: https://case-battle.com/partner\n"
        "DinoDrop: https://dino-drop.com/partner\n"
        "ForceDrop: https://forcedrop.com/partner"
    )
    bot.send_message(message.chat.id, links)

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    try:
        count = bot.get_chat_members_count(CHANNEL_ID)
    except:
        count = '❓'
    bot.send_message(message.chat.id, f"👥 Подписчиков на канале: {count}")

@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    subscribers.add(message.chat.id)
    save_subscribers()
    bot.reply_to(message, "✅ Подписка оформлена!")

@bot.message_handler(commands=['unsubscribe'])
def handle_unsubscribe(message):
    subscribers.discard(message.chat.id)
    save_subscribers()
    bot.reply_to(message, "❌ Подписка отключена.")

@bot.message_handler(commands=['start_contest'])
def handle_start_contest(message):
    global contest_active, claimed_users
    contest_active = True
    claimed_users.clear()
    bot.reply_to(message, "🏁 Конкурс запущен! Первый — получит бонус!")

@bot.message_handler(commands=['stop_contest'])
def handle_stop_contest(message):
    global contest_active
    contest_active = False
    bot.reply_to(message, "⏹ Конкурс завершён.")

@bot.message_handler(commands=['claim'])
def handle_claim(message):
    global contest_active, claimed_users
    if not contest_active:
        return bot.reply_to(message, "❌ Конкурс не активен.")
    if message.chat.id in claimed_users:
        return bot.reply_to(message, "⚠️ Уже заявлялись.")
    claimed_users.add(message.chat.id)
    if len(claimed_users) == 1:
        bot.reply_to(message, "🎉 Вы первый! Ваш бонус: EXTRADROP2025")
    else:
        bot.reply_to(message, "✅ Заявка принята, но приз уже взят.")

# === Channel Handlers ===
@bot.channel_post_handler(commands=['promo'])
def channel_promo(post):
    promo = (
        "🔥 АКТИВНЫЕ ПРОМОКОДЫ:\n\n"
        "Hellcase — DROPIFYCS\n"
        "Farmskins — DROPIFYCS\n"
        "CaseBattle — DROPIFYCS\n"
        "DinoDrop — DROPIFYCS\n"
        "ForceDrop — DROPIFYCS"
    )
    bot.send_message(post.chat.id, promo)

@bot.channel_post_handler(commands=['daily'])
def channel_daily(post):
    daily = (
        "🎁 ХАЛЯВА НА СЕГОДНЯ:\n\n"
        "1. Hellcase — бесплатный бонус каждый день.\n"
        "2. Farmskins — колёсико халявы каждый день.\n"
        "3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.\n"
        "4. DinoDrop — бонус за вход + шанс на скин.\n"
        "5. ForceDrop — бонус за депозит и фри-спины."
    )
    bot.send_message(post.chat.id, daily)

@bot.channel_post_handler(commands=['links'])
def channel_links(post):
    links = (
        "🔗 ПАРТНЁРСКИЕ ССЫЛКИ:\n\n"
        "Hellcase: https://hellcase.com/partner\n"
        "Farmskins: https://farmskins.com/partner\n"
        "CaseBattle: https://case-battle.com/partner\n"
        "DinoDrop: https://dino-drop.com/partner\n"
        "ForceDrop: https://forcedrop.com/partner"
    )
    bot.send_message(post.chat.id, links)

@bot.channel_post_handler(commands=['stats'])
def channel_stats(post):
    try:
        count = bot.get_chat_members_count(post.chat.id)
    except:
        count = '❓'
    bot.send_message(post.chat.id, f"👥 Подписчиков: {count}")

# === Run App ===
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        allowed_updates=["message", "channel_post"]
    )
    logger.info("Webhook set with allowed_updates, starting Flask")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
