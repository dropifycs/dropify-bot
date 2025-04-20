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
logging.getLogger('werkzeug').addHandler(file_handler)  # log Flask events

# === Telegram Bot & Flask Setup ===
TOKEN       = os.environ.get("BOT_TOKEN")
CHANNEL_ID  = os.environ.get("CHANNEL_ID")    # e.g. "-1001234567890"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")   # e.g. "https://dropify-bot.onrender.com"

if not TOKEN:
    logger.error("BOT_TOKEN environment variable is missing")
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
WEBHOOK_PATH = f"/{TOKEN}"

# === Subscribers ===
SUBSCRIBERS_FILE = 'subscribers.json'
try:
    with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
        subscribers = set(json.load(f))
except Exception:
    subscribers = set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(subscribers), f, ensure_ascii=False, indent=2)

# === Contest state ===
contest_active = False
claimed_users = set()

# === Routes ===
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(
        url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        allowed_updates=["message", "channel_post"]
    )

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
    promo = """🔥 НОВЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
Farmskins — DROPIFYCS
CaseBattle — DROPIFYCS
DinoDrop — DROPIFYCS
ForceDrop — DROPIFYCS
"""
    logger.info("Notifying subscribers of new promo")
    removed = []
    for user_id in list(subscribers):
        try:
            bot.send_message(user_id, promo)
        except Exception:
            removed.append(user_id)
    for rid in removed:
        subscribers.discard(rid)
    save_subscribers()
    return "Notified", 200

@app.route("/post_daily", methods=["POST"])
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

# === Personal command handlers ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    txt = (
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
    logger.info(f"Handled /start from {message.chat.id}")
    bot.reply_to(message, txt)

@bot.message_handler(commands=['promo'])
def send_promo(message):
    promo_text = """🔥 АКТИВНЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
Farmskins — DROPIFYCS
CaseBattle — DROPIFYCS
DinoDrop — DROPIFYCS
ForceDrop — DROPIFYCS
"""
    logger.info(f"Handled /promo for {message.chat.id}")
    bot.send_message(message.chat.id, promo_text)

@bot.message_handler(commands=['daily'])
def send_daily(message):
    daily_text = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.
4. DinoDrop — бонус за вход + шанс на скин.
5. ForceDrop — бонус за депозит и фри-спины.
"""
    logger.info(f"Handled /daily for {message.chat.id}")
    bot.send_message(message.chat.id, daily_text)

@bot.message_handler(commands=['links'])
def send_links(message):
    links_text = """🔗 ПАРТНЁРСКИЕ ССЫЛКИ:

Hellcase:   https://hellcase.com/partner
Farmskins: https://farmskins.com/partner
CaseBattle: https://case-battle.com/partner
DinoDrop:   https://dino-drop.com/partner
ForceDrop:  https://forcedrop.com/partner
"""
    logger.info(f"Handled /links for {message.chat.id}")
    bot.send_message(message.chat.id, links_text)

@bot.message_handler(commands=['stats'])
def send_stats(message):
    try:
        count = bot.get_chat_members_count(CHANNEL_ID)
    except Exception:
        logger.error("Error fetching chat member count", exc_info=True)
        count = "❓"
    bot.send_message(message.chat.id, f"👥 Подписчиков на канале: {count}")

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    subscribers.add(message.chat.id)
    save_subscribers()
    bot.reply_to(message, "✅ Вы подписались на личные уведомления о новых промокодах.")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    subscribers.discard(message.chat.id)
    save_subscribers()
    bot.reply_to(message, "❌ Вы отписались от личных уведомлений.")

@bot.message_handler(commands=['start_contest'])
def start_contest(message):
    global contest_active, claimed_users
    contest_active = True
    claimed_users.clear()
    bot.reply_to(message, "🏁 Конкурс запущен! Первый, кто отправит /claim — получит бонус!")

@bot.message_handler(commands=['stop_contest'])
def stop_contest(message):
    global contest_active
    contest_active = False
    bot.reply_to(message, "⏹ Конкурс завершён.")

@bot.message_handler(commands=['claim'])
def claim(message):
    global contest_active, claimed_users
    if not contest_active:
        return bot.reply_to(message, "❌ Конкурс сейчас не активен.")
    if message.chat.id in claimed_users:
        return bot.reply_to(message, "⚠️ Вы уже заявлялись.")
    claimed_users.add(message.chat.id)
    if len(claimed_users) == 1:
        bot.reply_to(message, "🎉 Поздравляем! Вы первый! Вот ваш эксклюзивный бонус: EXTRADROP2025")
    else:
        bot.reply_to(message, "✅ Вы заявились! Но приз уже забрал кто-то другой.")

# === Channel post handlers ===
@bot.channel_post_handler(commands=['promo'])
def channel_send_promo(channel_post):
    promo_text = """🔥 АКТИВНЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
Farmskins — DROPIFYCS
CaseBattle — DROPIFYCS
DinoDrop — DROPIFYCS
ForceDrop — DROPIFYCS
"""
    bot.send_message(channel_post.chat.id, promo_text)

@bot.channel_post_handler(commands=['daily'])
def channel_send_daily(channel_post):
    daily_text = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. Farmskins — колёсико халявы каждый день.
3. CaseBattle — розыгрыши и бонусы по коду DROPIFYCS.
4. DinoDrop — бонус за вход + шанс на скин.
5. ForceDrop — бонус за депозит и фри-спины.
"""
    bot.send_message(channel_post.chat.id, daily_text)

@bot.channel_post_handler(commands=['links'])
def channel_send_links(channel_post):
    links_text = """🔗 ПАРТНЁРСКИЕ ССЫЛКИ:

Hellcase:   https://hellcase.com/partner
Farmskins: https://farmskins.com/partner
CaseBattle: https://case-battle.com/partner
