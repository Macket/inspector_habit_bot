import telebot
from utils.conf import ConfigParser

config = ConfigParser()

telebot.apihelper.proxy = {'https': config.get('telegram', 'proxy')}
bot = telebot.TeleBot(config.get('telegram', 'token'))
