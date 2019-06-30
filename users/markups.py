from telebot import types
from users.data import preparing_habits
from users.models import User


def get_habits_markup(user_id):
    user = User.get(user_id)

    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('Бросить курить'),
        types.KeyboardButton('Не тратить время на YouTube'),
        types.KeyboardButton('Регулярно заниматься спортом'),
        types.KeyboardButton('Не тратить время Вконтакте'),
        types.KeyboardButton('Не зависать в Instagram'),
        types.KeyboardButton('Просыпаться раньше'),
        types.KeyboardButton('Регулярно читать книги'),
        types.KeyboardButton('Сбросить вес'))
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('Quit smoking'),
        types.KeyboardButton("Don't waste time on YouTube"),
        types.KeyboardButton("Don't waste time on Facebook"),
        types.KeyboardButton('Exercise regularly'),
        types.KeyboardButton('Wake up earlier'),
        types.KeyboardButton('Lose weight'),
        types.KeyboardButton('Read books regularly'))
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_languages_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        types.KeyboardButton('🇷🇺Русский'),
        types.KeyboardButton('🇬🇧English'))
    return markup


def get_days_inline_markup(user_id):
    user = User.get(user_id)
    ru_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    en_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    days = ru_days if user.language_code == 'ru' else en_days

    inline_markup = types.InlineKeyboardMarkup(row_width=7)

    inline_markup.add(*[types.InlineKeyboardButton(
        text='✔️' + day if day_of_week in preparing_habits[user_id]['days_of_week'] else day,
        callback_data='@@DAYS_REQUEST_INTRO/' + str(day_of_week))
        for day_of_week, day in enumerate(days)])

    inline_markup.add(types.InlineKeyboardButton(text='Все' if user.language_code == 'ru' else 'All',
                                                 callback_data='@@DAYS_REQUEST_INTRO/all'))

    return inline_markup


def get_ready_markup(user_id):
    user = User.get(user_id)
    ru_markup = types.ReplyKeyboardMarkup()
    ru_markup.add(types.KeyboardButton('Готово'))
    en_markup = types.ReplyKeyboardMarkup()
    en_markup.add(types.KeyboardButton('Done'))
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_location_markup(user_id):
    user = User.get(user_id)

    ru_markup = types.ReplyKeyboardMarkup()
    ru_markup.add(types.KeyboardButton('Поделиться местоположением', request_location=True))
    en_markup = types.ReplyKeyboardMarkup()
    en_markup.add(types.KeyboardButton('Share location', request_location=True))
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_fines_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        types.KeyboardButton('💲1'),
        types.KeyboardButton('💲5'),
        types.KeyboardButton('💲10'),
        types.KeyboardButton('💲50'),
        types.KeyboardButton('💲100'),
    )
    return markup


def get_promise_markup(user_id):
    user = User.get(user_id)

    ru_markup = types.ReplyKeyboardMarkup()
    ru_markup.add(types.KeyboardButton('Обещаю'))
    en_markup = types.ReplyKeyboardMarkup()
    en_markup.add(types.KeyboardButton('I promise'))
    markup = ru_markup if user.language_code == 'ru' else en_markup
    return markup
