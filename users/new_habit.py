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
from users.utils import get_user_naming


@bot.message_handler(func=lambda message:
message.text in ['🎯 Новая привычка', '🎯 New habit'], content_types=['text'])
def new_habit(message):
    preparing_habits[message.chat.id] = {'with_judge': False}
    habit_request(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@NEW_HABIT_FROM_SUGGESTION'))
def new_habit_from_suggestion(call):
    preparing_habits[call.message.chat.id] = {'with_judge': False}
    habit_request(call.message)


@bot.message_handler(func=lambda message:
message.text in ['👨‍⚖️ Новая привычка с судьёй', '👨‍⚖️ New habit with judge'], content_types=['text'])
def new_habit_with_judge(message):
    preparing_habits[message.chat.id] = {'with_judge': True}
    habit_request(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@NEW_HABIT_WITH_JUDGE_FROM_SUGGESTION'))
def new_habit_with_judge_from_suggestion(call):
    preparing_habits[call.message.chat.id] = {'with_judge': True}
    habit_request(call.message)


def habit_request(message):
    user = User.get(message.chat.id)
    ru_text = 'А ты любишь рисковать😁\n\nВыбери привычку из списка или напиши свою.'

    en_text = 'Do you like to risk😁\n\nChoose a habit from the list or write your own.'

    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_habits_markup(message.chat.id))
    bot.register_next_step_handler(message, habit_receive)


def habit_receive(message):
    user = User.get(message.chat.id)

    if message.text in ['Другое...', 'Other...']:
        ru_text = 'Напиши привычку, над которой будем работать'
        en_text = 'Write the habit we will work on'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id,
                         text,
                         reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, habit_receive)
    else:
        ru_text = f'Итак, ты хочешь *{message.text}*'
        en_text = f'So you want *{message.text}*'
        text = ru_text if user.language_code == 'ru' else en_text

        preparing_habits[message.chat.id]['label'] = message.text
        preparing_habits[message.chat.id]['days_of_week'] = []

        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_ready_markup(message.chat.id),
                         parse_mode='Markdown')
        days_request(message)


def days_request(message):
    user = User.get(message.chat.id)

    ru_text = 'Теперь выбери дни недели, когда я буду приходить к тебе с проверкой.'
    en_text = "Now choose the days of the week when I will come to you with a check"
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

    ru_text = f'Отлично, выбери время проверки, например, *19:30*. ' \
              f'Можно выбрать несколько проверок через пробел, например, *7:30 19:30*'
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

        ru_text = f'Хорошо, я буду проверять тебя в *{message.text}* по *{check_days}*.'
        en_text = f"Okay, I'll check you at *{message.text}* on *{check_days}*"
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id,
                         text,
                         parse_mode="Markdown")
        fine_request(message)

    except ValueError:
        ru_text = 'Кажется, ты ввёл какую-то ерунду. Попробуй ещё раз, используя формат *ЧЧ:ММ*.'
        en_text = 'It seems you have entered some nonsense. Try again using *HH:MM* format.'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text, parse_mode='Markdown')
        bot.register_next_step_handler(message, time_receive)


def fine_request(message):
    user = User.get(message.chat.id)

    ru_text = 'Выбери размер штрафа. Только смотри не переборщи, ' \
              'потому что платить придётся всякий раз, когда нарушишь обещание.'
    en_text = 'Choose a fine. Just do not overdo, ' \
              'because you have to pay every time you break a promise.'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_fines_markup())
    bot.register_next_step_handler(message, fine_receive)


def fine_receive(message):
    try:
        preparing_habits[message.chat.id]['fine'] = int(message.text.split('💲')[1])
        promise_request(message)
    except (ValueError, IndexError):
        user = User.get(message.chat.id)
        ru_text = 'Ты отправил что-то не то'
        en_text = 'You sent something wrong'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text)
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

    habit = Habit(message.chat.id,
                  preparing_habits[message.chat.id]['label'],
                  preparing_habits[message.chat.id]['days_of_week'],
                  preparing_habits[message.chat.id]['time_array'],
                  preparing_habits[message.chat.id]['fine']).save()

    if preparing_habits[message.chat.id]['with_judge']:
        ru_text = 'Осталось назначить судью. Просто отправь другу сообщение ниже👇'
        en_text = 'It remains to assign the judge. Just send the message below to a friend👇'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())

        ru_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        en_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        days = ru_days if user.language_code == 'ru' else en_days

        check_days = re.sub(r'\s+', ' ', ' '.join(
            [day if day_of_week in preparing_habits[message.chat.id]['days_of_week'] else '' for day_of_week, day in
             enumerate(days)]))
        check_time = ' '.join(preparing_habits[message.chat.id]['time_array'])

        ru_text = f'{get_user_naming(user, "Твой друг")} хочет, ' \
                  f'чтобы ты стал его судьёй на привычке *{habit.label}*.\n\n' \
                  f'Дни недели: *{check_days}*\n' \
                  f'Время проверки: *{check_time}*\n' \
                  f'Длительность: *3 недели*\n\n' \
                  f'За каждый провал {get_user_naming(user, "твой друг")} обязуется заплатить тебе *${habit.fine}*'
        en_text = f'{get_user_naming(user, "Your friend")} wants you' \
                  f'to be the jadge on the habit *{habit.label}*.\n\n' \
                  f'Days of week: *{check_days}*\n' \
                  f'Checks time: *{check_time}*\n' \
                  f'Duration: *3 weeks*\n\n' \
                  f'For each fail {get_user_naming(user, "your friend")} agrees to pay you *${habit.fine}*'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text, reply_markup=markups.get_judge_markup(user.id, habit.id), parse_mode='Markdown')
    else:
        ru_text = 'Ну что ж, посмотрим, какой ты крутой. Удачи!'
        en_text = "Well, let's see how cool you are. Good luck!"
        text = ru_text if user.language_code == 'ru' else en_text

        schedule_native, schedule_utc = get_schedule(
            preparing_habits[message.chat.id]['days_of_week'],
            preparing_habits[message.chat.id]['time_array'],
            User.get(message.chat.id).timezone,
        )

        for check_native, check_utc in zip(schedule_native, schedule_utc):  # нужно оптимизировать
            Check(habit.id, check_native, check_utc).save()

        bot.send_message(message.chat.id, text, reply_markup=markups.get_main_menu_markup(message.chat.id))
        bot.send_sticker(message.chat.id, 'CAADAgADWQIAAsY4fgsQX6OJTX_IOgI')

    del preparing_habits[message.chat.id]
