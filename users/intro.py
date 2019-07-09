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


@bot.message_handler(commands=['start'])
def register(message):
    referrer = message.text[7:] if message.text[7:] else None
    user = User(message.chat.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
                referrer=referrer,
                )
    user.save()

    if user.language_code:
        greeting_and_habit_request(message)
    else:
        language_request(message)


def greeting_and_habit_request(message):
    user = User.get(message.chat.id)
    ru_text = f'Здравствуйте{", " + user.first_name if user.first_name else ""}! ' \
              f'Я Инспектор Хэбит, борец с мировой ленью и прокрастинацией. ' \
              f'Под моим чутким надзором люди приобретают полезные привычки и избавляются от вредных.' \
              f'\n\nВсё дело в том, что я знаю самый действенный способ! ' \
              f'Давайте я покажу вам. Уверен, что у вас есть какая-нибудь вредная привычка, от которой никак ' \
              f'не получается избавиться. Или же наоборот, вы давным-давно мечтаете ' \
              f'выработать какую-нибудь полезную привычку? Напишите, чего бы вам хотелось, ' \
              f'или выберите из списка.'

    en_text = f'Hello{", " + user.first_name if user.first_name else ""}! ' \
              f'I am Inspector Habit, fighter with world laziness and procrastination. ' \
              f'Under my strict control, people develop good habits and break bad habits.\n\n' \
              f'The thing is, I know the most powerful way! ' \
              f'Let me show you. I am sure that you have any bad habit you want to break.' \
              f'Or, on the contrary, did you long ago want to develop some good habit? ' \
              f'Write what you would like, or select from the list.'

    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_habits_markup(message.chat.id))
    bot.register_next_step_handler(message, habit_response)


def habit_response(message):
    user = User.get(message.chat.id)

    ru_text = f'Итак, вы хотите *{message.text}*'
    en_text = f'So you want *{message.text}*'
    text = ru_text if user.language_code == 'ru' else en_text

    preparing_habits[message.chat.id] = {'label': message.text, 'days_of_week': []}

    bot.send_message(message.chat.id, text, reply_markup=markups.get_ready_markup(message.chat.id), parse_mode='Markdown')
    days_request(message)


def language_request(message):
    bot.send_message(message.chat.id,
                     '🇷🇺 Выберите язык, пожалуйста\n🇬🇧 Choose the language please',
                     reply_markup=markups.get_languages_markup())
    bot.register_next_step_handler(message, language_response)


def language_response(message):
    user = User.get(message.chat.id)

    if message.text in ('🇷🇺Русский', '🇬🇧English'):
        # set user language
        user.language_code = 'ru' if message.text == '🇷🇺Русский' else 'en'
        user.save()
        greeting_and_habit_request(message)
    else:
        bot.register_next_step_handler(message, language_response)


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
        location_request(message)

    except ValueError:
        ru_text = 'Кажется, вы ввели что-то не то. Попробуйте ещё раз, используя формат *ЧЧ:ММ*.'
        en_text = 'It seems you have entered something wrong. Try again using *HH:MM* format.'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text, parse_mode='Markdown')
        bot.register_next_step_handler(message, time_receive)


def location_request(message):
    user = User.get(message.chat.id)

    ru_text = 'Также мне нужно узнать, какой у вас часовой пояс, чтобы проводить проверки вовремя.'
    en_text = 'I also need to find out what time zone you live in order to perform the checks on time.'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_location_markup(message.chat.id))
    bot.register_next_step_handler(message, location_receive)


def location_receive(message):
    if message.location:
        tzw = tzwhere.tzwhere()
        timezone_str = tzw.tzNameAt(message.location.latitude, message.location.longitude)
        user = User.get(message.chat.id)
        user.timezone = timezone_str
        user.save()
        fine_request(message)
    else:
        bot.register_next_step_handler(message, location_receive)


def fine_request(message):
    user = User.get(message.chat.id)

    ru_text = f'И наконец, самое главное. Помните, я сказал, что знаю самый эффективный способ? ' \
              f'Он заключается в том, что вы даёте обещание "{preparing_habits[message.chat.id]["label"]}" ' \
              f'и получаете денежный штраф, каждый раз, когда нарушаете его в течение 3 недель. ' \
              f'Благодаря такому подходу люди выполняют свои обещания в 3 раза чаще!\n\n' \
              f'Какой штраф вы готовы заплатить за нарушение своего обещания?'
    en_text = f'And finally, the most important thing. Remember, I said that I know the most effective way? ' \
              f'It lies in the fact that you make a promise "{preparing_habits[message.chat.id]["label"]}" ' \
              f'and get a monetary fine every time you break it over the next 3 weeks. ' \
              f'Thanks to this approach, people fulfill their promises 3 times more often!\n\n' \
              f'What fine are you willing to pay for breaking your promise?'
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

    bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())
