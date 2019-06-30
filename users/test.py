from telebot import types
from bot import bot


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    ru = types.KeyboardButton('🇷🇺Russian')
    en = types.KeyboardButton('🇬🇧English')
    markup.add(ru, en)
    bot.send_message(message.chat.id, 'Выберите язык, пожалуйста\nChoose the language please', reply_markup=markup)
    # create_user(message.chat.id)
    bot.register_next_step_handler(message, send_habit)


def send_habit(message):
    markup = types.ReplyKeyboardRemove()
    if message.text == '🇷🇺Russian':
        bot.send_message(message.chat.id, 'Отлично, вы выбрали русский', reply_markup=markup)
    elif message.text == '🇬🇧English':
        bot.send_message(message.chat.id, 'Good, you choose English', reply_markup=markup)
    else:
        bot.register_next_step_handler(message, send_habit)
