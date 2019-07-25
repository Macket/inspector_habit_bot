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
