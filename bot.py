
import telebot

# ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = "7827263344:ААН-E407ZG29KZGSrhuhmLqzzcHWqV11vVO"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать в Dropify CS бот!

Команды:
/promo — Промокоды
/daily — Халява дня
/links — Партнёрские сайты")

@bot.message_handler(commands=['promo'])
def send_promo(message):
    promo_text = """🔥 АКТИВНЫЕ ПРОМОКОДЫ:

Hellcase — DROPIFYCS
CSGOEmpire — DROPIFY
Farmskins — DROPIFYCS
KeyDrop — DROPIFYCS
SkinClub — DROPIFY
"""
    bot.send_message(message.chat.id, promo_text)

@bot.message_handler(commands=['daily'])
def send_daily(message):
    daily_text = """🎁 ХАЛЯВА НА СЕГОДНЯ:

1. Hellcase — бесплатный бонус каждый день.
2. CSGOEmpire — получи монету с кодом DROPIFY.
3. Farmskins — колёсико халявы каждый день.

Заходи каждый день и лови дроп!
"""
    bot.send_message(message.chat.id, daily_text)

@bot.message_handler(commands=['links'])
def send_links(message):
    links_text = """🔗 ПОЛЕЗНЫЕ ССЫЛКИ:

Hellcase: https://hellcase.com/partner
CSGOEmpire: https://csgoempire.com
Farmskins: https://farmskins.com/partner
KeyDrop: https://key-drop.com/promotion
SkinClub: https://skin.club
"""
    bot.send_message(message.chat.id, links_text)

# Запуск бота
bot.polling()
