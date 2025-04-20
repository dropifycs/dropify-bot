import os
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
Добро пожаловать в Dropify CS бот!

Команды:
/promo — Промокоды
/daily — Халява дня
/links — Партнёрские сайты
"""
    bot.reply_to(message, welcome_text.strip())

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

if __name__ == '__main__':
    bot.polling()
