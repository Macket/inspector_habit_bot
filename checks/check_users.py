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

    called_button_label = call.message.json['reply_markup']['inline_keyboard'][0][0]['text'] if \
        data['status'] == CheckStatus.SUCCESS.name else \
        call.message.json['reply_markup']['inline_keyboard'][0][1]['text']

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=call.message.text,
                          message_id=call.message.message_id,
                          reply_markup= markups.get_check_result_inline_markup(called_button_label),
                          parse_mode='HTML')

    if data['status'] == CheckStatus.SUCCESS.name:
        user = User.get(call.message.chat.id)
        ru_text = 'Отлично! Так держать👍'
        en_text = 'Great! Keep it up👍'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(call.message.chat.id, text)
    else:
        user_violations(call.message)
        # fine = Habit.get(check.habit_id).fine
        # user = User.get(call.message.chat.id)
        # ru_text = f'Вам назначен штраф в размере 💲{fine}.\n\n' \
        #           f'К сожалению, ко мне ещё не подключена платёжная система. ' \
        #           f'Как только это будет сделано, я отправлю вам счёт на оплату штрафа.'
        # en_text = f'You are fined 💲{fine}.\n\n' \
        #           f'Unfortunately, the payment system is not connected to me yet. ' \
        #           f'Once this is done, I will send you a bill to pay the fine.'
        # text = ru_text if user.language_code == 'ru' else en_text
        #
        # bot.send_message(call.message.chat.id, text)
