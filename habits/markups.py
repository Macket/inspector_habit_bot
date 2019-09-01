from telebot import types
from users.models import User


def get_judge_register_markup(user_id):
    user = User.get(user_id)
    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('🗝 Зарегистрироваться'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('🗝 Sign up'),
    )
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_choose_habit_type_markup(user_id):
    user = User.get(user_id)
    ru_markup = types.ReplyKeyboardMarkup(row_width=1)
    ru_markup.add(
        types.KeyboardButton('Активные'),
        types.KeyboardButton('Завершённые'),
    )
    en_markup = types.ReplyKeyboardMarkup(row_width=1)
    en_markup.add(
        types.KeyboardButton('Active'),
        types.KeyboardButton('Completed'),
    )
    markup = ru_markup if user.language_code == 'ru' else en_markup

    return markup


def get_delete_habit_markup(user_id, habit_id):
    user = User.get(user_id)
    button_label = 'Удалить' if user.language_code == 'ru' else 'Delete'

    inline_markup = types.InlineKeyboardMarkup(row_width=1)

    inline_markup.add(
        types.InlineKeyboardButton(text=button_label, callback_data=f'@@DELETE_HABIT/{habit_id}'),
    )

    return inline_markup
