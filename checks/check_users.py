from datetime import datetime
from telebot import types
from utils.database import execute_database_command
from bot import bot
from users.models import User
from checks.models import Check
from habits.models import Habit
from checks.utils import CheckStatus
from checks import markups
from fines.handlers import user_violations
import ast


def check_users(last_check_utc):
    now_utc = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")  # Нужно исправить
    checks = execute_database_command('''SELECT c.id, c.habit_id, c.datetime_native, c.datetime_utc, h.label, h.user_id FROM
    checks c JOIN habits h ON c.habit_id = h.id JOIN users u ON u.id = h.user_id 
    WHERE c.datetime_utc <= %s AND c.datetime_utc > %s AND c.status=%s;
    ''', (now_utc, last_check_utc, CheckStatus.PENDING.name))[0]
    for check in checks:
        check_id, habit_id, datetime_native, datetime_utc, label, user_id = check
        c = Check(habit_id, datetime_native, datetime_utc, CheckStatus.CHECKING.name, check_id)
        c.save()

        user = User.get(user_id)
        ru_text = f'Вы обещали "{label}". Вы выполняете своё обещание?\n\n' \
                  f'Учтите, что за ответ "❌ Нет" нужно будет заплатить штраф'
        en_text = f'You promised "{label}". Are you keeping your promise?\n\n' \
                  f'Note that you will have to pay a fine for the answer "❌ No"'
        text = ru_text if user.language_code == 'ru' else en_text

        try:
            bot.send_message(user_id,
                             text,
                             reply_markup=markups.get_check_inline_markup(user_id, check_id))
        except Exception:
            pass
    return now_utc


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@CHECKS'))
def handle_check_query(call):
    data = ast.literal_eval(call.data.split('/')[1])

    check = Check.get(data['check_id'])
    check.status = data['status']
    check.save()

    habit = Habit.get(check.habit_id)

    user = User.get(call.message.chat.id)

    called_button_label = call.message.json['reply_markup']['inline_keyboard'][0][0]['text'] if \
        data['status'] == CheckStatus.SUCCESS.name else \
        call.message.json['reply_markup']['inline_keyboard'][0][1]['text']

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=call.message.text,
                          message_id=call.message.message_id,
                          reply_markup= markups.get_check_result_inline_markup(called_button_label),
                          parse_mode='HTML')

    if data['status'] == CheckStatus.SUCCESS.name:
        user.score += habit.fine
        user.save()

        ru_text = f'Отлично! Так держать👍\n\n*+{habit.fine} очков*'
        en_text = f'Great! Keep it up👍 \n\n*+{habit.fine} points*'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')
    else:
        user.score -= habit.fine
        user.save()

        ru_text = f'😭😭😭\n\n*-{habit.fine} очков*'
        en_text = f'😭😭😭\n\n*-{habit.fine} points*'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

        user_violations(call.message)


def take_points_from_debtors():
    debtors = execute_database_command('''SELECT u.id, SUM(h.fine) FROM users u JOIN 
    habits h ON u.id = h.user_id JOIN checks c ON c.habit_id = h.id 
    WHERE c.status = 'FAIL' GROUP BY u.id;
    ''', (CheckStatus.SUCCESS.name,))[0]

    for debtor in debtors:
        u = User.get(debtor[0])
        u.score -= debtor[1]
        u.save()

        ru_text = f'Ваш долг по штрафам составляет *${debtor[1]}*\n\n*-{debtor[1]} очков*'
        en_text = f'Your debt on fines *${debtor[1]}*\n\n*-{debtor[1]} points*'
        text = ru_text if u.language_code == 'ru' else en_text

        try:
            bot.send_message(u.id, text, parse_mode='Markdown')
        except Exception:
            pass


def rate_users():
    rating = execute_database_command(
        'SELECT id, score FROM users ORDER BY score DESC;',
        (CheckStatus.SUCCESS.name,))[0]

    total = len(rating)

    for place, record in enumerate(rating, 1):
        u = User.get(record[0])

        ru_text = f'Ваше место в рейтинге: *{place}/{total}*\n\n' \
                  f'Количество очков: *{record[1]}*'
        en_text = f'Your place in rating *{place}/{total}*\n\n*' \
                  f'Score: *{record[1]}*'
        text = ru_text if u.language_code == 'ru' else en_text

        try:
            bot.send_message(u.id, text, parse_mode='Markdown')
        except Exception:
            pass
