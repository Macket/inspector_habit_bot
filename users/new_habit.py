from telebot import types
from bot import bot
from users.models import User
from datetime import datetime
from tzwhere import tzwhere
import re
import users.markups as markups
from users.utils import get_schedule
from checks.models import Check
from habits.models import Habit
from users.data import preparing_habits


@bot.message_handler(func=lambda message:
message.text in ['🎯 Новая привычка', '🎯 New habit'], content_types=['text'])
def new_habit(message):
    habit_request(message)


def habit_request(message):
    user = User.get(message.chat.id)
    ru_text = f'{user.first_name + ", я рад " if user.first_name else "Рад"}, ' \
              f'что вы не останавливаетесь на достигнутом! ' \
              f'Какую новую полезную привычку вы хотите приобрести? ' \
              f'Или вы хотите избавиться от какой-нибудь вредной привычки?\n\n' \
              f'Напишите или выберите из предложенных.'

    en_text = f'{user.first_name + "," if user.first_name else ""}, ' \
              f'I am glad that you do not stop there ' \
              f'What new good habit would you like to develop? ' \
              f'Or you want to break some bad habit?\n\n' \
              f'Write or choose from the list.' \

    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_habits_markup(message.chat.id))
    bot.register_next_step_handler(message, habit_response)


def habit_response(message):
    user = User.get(message.chat.id)

    ru_text = f'Итак, вы хотите *{message.text}*'
    en_text = f'So you want *{message.text}*'
    text = ru_text if user.language_code == 'ru' else en_text

    preparing_habits[message.chat.id] = {'label': message.text, 'days_of_week': []}

    bot.send_message(message.chat.id,
                     text,
                     reply_markup=markups.get_ready_markup(message.chat.id),
                     parse_mode='Markdown')
    days_request(message)


def days_request(message):
    user = User.get(message.chat.id)

    ru_text = 'Теперь давайте выберем дни недели, когда я буду приходить к вам с проверкой.'
    en_text = "Now let's choose the days of the week when I will come to you with a check"
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id,
                     text,
                     reply_markup=markups.get_days_inline_markup(message.chat.id))
    bot.register_next_step_handler(message, time_request)


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@DAYS_REQUEST_INTRO'))
def handle_days_query(call):
    if call.data == '@@DAYS_REQUEST_INTRO/all':
        preparing_habits[call.message.chat.id]['days_of_week'] = [0, 1, 2, 3, 4, 5, 6]
    else:
        selected_day = int(call.data.split('/')[1])
        if selected_day in preparing_habits[call.message.chat.id]['days_of_week']:
            preparing_habits[call.message.chat.id]['days_of_week'].remove(selected_day)
        else:
            preparing_habits[call.message.chat.id]['days_of_week'].append(selected_day)
            preparing_habits[call.message.chat.id]['days_of_week'].sort()
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=call.message.text,
                          message_id=call.message.message_id,
                          reply_markup=markups.get_days_inline_markup(call.message.chat.id),
                          parse_mode='HTML')


def time_request(message):
    user = User.get(message.chat.id)

    ru_text = f'Отлично, выберите время проверки, например, *19:30*. ' \
              f'Можете выбрать несколько проверок через пробел, например, *7:30 19:30*'
    en_text = 'Good, choose a check time, for example, *19:30*. ' \
              'You can select multiple checks via space, for example, *7:30 19:30*'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id,
                     text,
                     parse_mode='Markdown',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, time_receive)


def time_receive(message):
    user = User.get(message.chat.id)
    ru_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    en_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    days = ru_days if user.language_code == 'ru' else en_days

    time_array = message.text.split(' ')

    try:
        for time in time_array:
            timeformat = '%H:%M'
            datetime.strptime(time, timeformat)

        preparing_habits[message.chat.id]['time_array'] = time_array
        check_days = re.sub(r'\s+', ' ', ' '.join(
            [day if day_of_week in preparing_habits[message.chat.id]['days_of_week'] else '' for day_of_week, day in enumerate(days)]))

        ru_text = f'Хорошо, буду проверять вас в *{message.text}* по *{check_days}*.'
        en_text = f"Okay, I'll check you at *{message.text}* on *{check_days}*"
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id,
                         text,
                         parse_mode="Markdown")
        fine_request(message)

    except ValueError:
        ru_text = 'Кажется, вы ввели что-то не то. Попробуйте ещё раз, используя формат *ЧЧ:ММ*.'
        en_text = 'It seems you have entered something wrong. Try again using *HH:MM* format.'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text, parse_mode='Markdown')
        bot.register_next_step_handler(message, time_receive)


def fine_request(message):
    user = User.get(message.chat.id)

    ru_text = f'Назначьте себе штраф за нарушение обещания.'
    en_text = f'Set yourself a fine for breaking the promise.'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_fines_markup())
    bot.register_next_step_handler(message, fine_receive)


def fine_receive(message):
    try:
        preparing_habits[message.chat.id]['fine'] = int(message.text.split('💲')[1])
        promise_request(message)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'Вы отправили что-то не то')
        bot.register_next_step_handler(message, fine_receive)


def promise_request(message):
    user = User.get(message.chat.id)

    ru_text = f'Время дать обещание:\n\n' \
              f'"Я обещаю *{preparing_habits[message.chat.id]["label"]}* и заплачу штраф' \
              f'*💲{preparing_habits[message.chat.id]["fine"]}* за нарушение своего обещания."'
    en_text = f"It's time to commit:\n\n" \
              f'"I promise *{preparing_habits[message.chat.id]["label"]}*.' \
              f'I will pay a *{preparing_habits[message.chat.id]["fine"]}* fine for breaking my promise."'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_promise_markup(message.chat.id), parse_mode='Markdown')
    bot.register_next_step_handler(message, promise_receive)


def promise_receive(message):
    user = User.get(message.chat.id)

    ru_text = 'Вы смелый человек. Удачи!'
    en_text = 'You are a brave man. Good luck!'
    text = ru_text if user.language_code == 'ru' else en_text

    print(preparing_habits)
    schedule_native, schedule_utc = get_schedule(
        preparing_habits[message.chat.id]['days_of_week'],
        preparing_habits[message.chat.id]['time_array'],
        User.get(message.chat.id).timezone,
    )
    habit = Habit(message.chat.id,
                  preparing_habits[message.chat.id]['label'],
                  preparing_habits[message.chat.id]['days_of_week'],
                  preparing_habits[message.chat.id]['time_array'],
                  preparing_habits[message.chat.id]['fine']).save()
    for check_native, check_utc in zip(schedule_native, schedule_utc):  # нужно оптимизировать
        Check(habit.id, check_native, check_utc).save()
    del preparing_habits[message.chat.id]

    bot.send_message(message.chat.id, text, reply_markup=markups.get_main_menu_markup(message.chat.id))
