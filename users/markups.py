from telebot import types
from users.data import preparing_habits
from users.models import User
import settings


def get_main_menu_markup(user_id):
    user = User.get(user_id)
    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('🎯 Новая привычка'),
        types.KeyboardButton('👨‍⚖️ Новая привычка с судьёй'),
        types.KeyboardButton('🗓 Мои привычки'),
        types.KeyboardButton('❗️ Мои нарушения'),
        types.KeyboardButton('⚙️ Настройки'),
        types.KeyboardButton('🤨 Куда пойдут мои деньги?'),
        types.KeyboardButton('✉️ Написать разработчикам'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('🎯 New habit'),
        types.KeyboardButton('👨‍⚖️ New habit with judge'),
        types.KeyboardButton('🗓 My habits'),
        types.KeyboardButton('❗ My violations'),
        types.KeyboardButton('⚙️ Settings'),
        types.KeyboardButton('🤨 Where will my money go?'),
        types.KeyboardButton('✉️ Contact developers'),
    )
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_cancel_markup(user_id):
    user = User.get(user_id)
    ru_markup = types.ReplyKeyboardMarkup()
    ru_markup.add(types.KeyboardButton('❌ Отмена'))
    en_markup = types.ReplyKeyboardMarkup()
    en_markup.add(types.KeyboardButton('❌ Cancel'))
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_habits_markup(user_id):
    user = User.get(user_id)

    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('Бросить курить'),
        types.KeyboardButton('Не тратить время на YouTube'),
        types.KeyboardButton('Регулярно заниматься спортом'),
        types.KeyboardButton('Не зависать в Instagram'),
        types.KeyboardButton('Просыпаться раньше'),
        types.KeyboardButton('Регулярно читать книги'),
        types.KeyboardButton('Сбросить вес'),
        types.KeyboardButton('Другое...'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('Quit smoking'),
        types.KeyboardButton("Don't waste time on YouTube"),
        types.KeyboardButton('Exercise regularly'),
        types.KeyboardButton('Wake up earlier'),
        types.KeyboardButton('Lose weight'),
        types.KeyboardButton('Read books regularly'),
        types.KeyboardButton('Other...'),
    )
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

    ru_markup = types.ReplyKeyboardMarkup(row_width=1)

    ru_markup.add(
        types.KeyboardButton('Поделиться местоположением', request_location=True),
        types.KeyboardButton('Указать вручную'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('Share location', request_location=True),
        types.KeyboardButton('Specify manually'),
    )
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_timezone_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row('GMT')
    markup.row('GMT-0', 'GMT+0')
    markup.row('GMT-1', 'GMT+1')
    markup.row('GMT-2', 'GMT+2')
    markup.row('GMT-3', 'GMT+3')
    markup.row('GMT-4', 'GMT+4')
    markup.row('GMT-5', 'GMT+5')
    markup.row('GMT-6', 'GMT+6')
    markup.row('GMT-7', 'GMT+7')
    markup.row('GMT-8', 'GMT+8')
    markup.row('GMT-9', 'GMT+9')
    markup.row('GMT-10', 'GMT+10')
    markup.row('GMT-11', 'GMT+11')
    markup.row('GMT-12', 'GMT+12')
    markup.row('GMT+13')
    markup.row('GMT+14')

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


def get_money_intention_markup(user_id):
    user = User.get(user_id)

    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('Другу'),
        types.KeyboardButton('На благотворительность'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('To a friend'),
        types.KeyboardButton('To charity'),
    )
    markup = ru_markup if user.language_code == 'ru' else en_markup
    return markup


def get_judge_markup(user_id, habit_id):
    user = User.get(user_id)
    ru_button = 'Стать судьёй'
    en_button = 'Become the judge'
    button = ru_button if user.language_code == 'ru' else en_button

    inline_markup = types.InlineKeyboardMarkup(row_width=1)

    url = f'https://t.me/BotoKatalabot?start=judge_{habit_id}' if settings.DEBUG \
        else f'https://t.me/inspector_habit_bot?start=judge_{habit_id}'
    inline_markup.add(
        types.InlineKeyboardButton(text=button, url=url),
    )

    return inline_markup


def get_settings_markup(user_id):
    user = User.get(user_id)

    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('🇷🇺 Язык'),
        types.KeyboardButton('🕒 Часовой пояс'),
        types.KeyboardButton('❌ Отмена'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('🇬🇧 Language'),
        types.KeyboardButton('🕒 Timezone'),
        types.KeyboardButton('❌ Cancel'),
    )
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_language_confirm_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(
        types.KeyboardButton('🇷🇺Нет / 🇬🇧No'),
        types.KeyboardButton('🇷🇺Да / 🇬🇧Yes'),
    )

    return markup
