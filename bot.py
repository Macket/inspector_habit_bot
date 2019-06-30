import telebot
import settings


if settings.DEBUG:
    telebot.apihelper.proxy = {'https': settings.PROXY}

bot = telebot.TeleBot(settings.BOT_TOKEN)
