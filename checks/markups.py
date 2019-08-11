from telebot import types
from checks.utils import CheckStatus
from users.models import User


def get_check_inline_markup(user_id, check_id):
    user = User.get(user_id)

    ru_inline_markup = types.InlineKeyboardMarkup(row_width=2)
    ru_inline_markup.add(
        types.InlineKeyboardButton(text='✅ Да', callback_data='@@CHECKS/{"check_id": ' + str(
            check_id) + ', "status": "' + CheckStatus.SUCCESS.name + '"}'),
        types.InlineKeyboardButton(text='❌ Нет', callback_data='@@CHECKS/{"check_id": ' + str(
            check_id) + ', "status": "' + CheckStatus.FAIL.name + '"}'))
    en_inline_markup = types.InlineKeyboardMarkup(row_width=2)
    en_inline_markup.add(
        types.InlineKeyboardButton(text='✅ Yes', callback_data='@@CHECKS/{"check_id": ' + str(
            check_id) + ', "status": "' + CheckStatus.SUCCESS.name + '"}'),
        types.InlineKeyboardButton(text='❌ No', callback_data='@@CHECKS/{"check_id": ' + str(
            check_id) + ', "status": "' + CheckStatus.FAIL.name + '"}'))
    inline_markup = ru_inline_markup if user.language_code == 'ru' else en_inline_markup

    return inline_markup


def get_check_result_inline_markup(text):
    inline_markup = types.InlineKeyboardMarkup(row_width=1)
    inline_markup.add(types.InlineKeyboardButton(text=text, callback_data='None'))

    return inline_markup


def get_kick_lazy_ass_markup(judge_id, habit_id):
    judge = User.get(judge_id)
    text = 'Напомнить' if judge.language_code == 'ru' else 'Remind'
    inline_markup = types.InlineKeyboardMarkup(row_width=1)
    inline_markup.add(
        types.InlineKeyboardButton(
            text=text,
            callback_data='@@KICK_LAZY_ASS/' + str(habit_id)))

    return inline_markup
