from telebot import types
from users.models import User
import settings


def get_punishment_markup(user_id):
    user = User.get(user_id)
    ru_punishments = ['💰 Оплата штрафов', '👥 Социальные работы']
    en_punishments = ['💰 Pay fines', '👥 Social works']
    punishments = ru_punishments if user.language_code == 'ru' else en_punishments

    inline_markup = types.InlineKeyboardMarkup(row_width=1)

    inline_markup.add(
        types.InlineKeyboardButton(text=punishments[0], callback_data='@@PUNISHMENT/pay'),
        types.InlineKeyboardButton(text=punishments[1], callback_data='@@PUNISHMENT/work'),
    )

    return inline_markup


def get_social_work_markup(user_id):
    user = User.get(user_id)
    ru_button = 'Помочь другу'
    en_button = 'Help friend'
    button = ru_button if user.language_code == 'ru' else en_button

    inline_markup = types.InlineKeyboardMarkup(row_width=1)

    url = f'https://t.me/BotoKatalabot?start={user_id}' if settings.DEBUG \
        else f'https://t.me/inspector_habit_bot?start={user_id}'
    inline_markup.add(
        types.InlineKeyboardButton(text=button, url=url),
    )

    return inline_markup


def get_judge_payment_report_markup(user_id, judge_id):
    judge = User.get(judge_id)
    button1_label = '💰 Штрафы оплачены' if judge.language_code == 'ru' else '💰 Fines paid'
    button2_label = '😡 Напомнить о долге' if judge.language_code == 'ru' else '😡 Remind about debt'

    inline_markup = types.InlineKeyboardMarkup(row_width=1)

    inline_markup.add(
        types.InlineKeyboardButton(text=button1_label, callback_data=f'@@JUDGE_PAYMENT_REPORT/{user_id}'),
        types.InlineKeyboardButton(text=button2_label, callback_data=f'@@JUDGE_DEBT_REMIND/{user_id}'),
    )

    return inline_markup
