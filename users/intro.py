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
from checks.utils import CheckStatus


@bot.message_handler(func=lambda message: not message.text.startswith('/start judge'), commands=['start'])
def register(message):
    referrer = int(message.text[7:]) if message.text[7:] else None
    if referrer == message.chat.id:
        referrer = None
    user = User(message.chat.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
                timezone='UTC',
                referrer=referrer,
                )
    user.save()

    if user.language_code:
        greeting_and_habit_request(message)
    else:
        language_request(message)


@bot.message_handler(func=lambda message:
message.text in ['🗝 Зарегистрироваться', '🗝 Sign up'], content_types=['text'])
def greeting_and_habit_request(message):
    user = User.get(message.chat.id)
    ru_text = f'Привет{", " + user.first_name if user.first_name else ""}! ' \
              f'Я Инспектор Хэбит, борец с мировой ленью и филантроп. ' \
              f'А ты, кажется, как раз испытваешь с этим определённые проблемы.\n\n' \
              f'Короче, назначаешь себе привычку и обещаешь следовать ей, ' \
              f'а я тебя буду проверять: держишь слово — красавчик, ' \
              f'нарушаешь — ловишь денежный штраф. Размер штрафа выбираешь сам. ' \
              f'И таким образом мы работаем 3 недели.\n\n' \
              f'Всё ясно? Если да, то выбирай привычку из списка или пиши свою, ' \
              f'если нет, то не трать моё время.\n\n' \
              f'И кстати, я филантроп: 80% денег, ' \
              f'сгенерированных на твоей лени, пойдут на благотворительность'

    en_text = f'Hello{", " + user.first_name if user.first_name else ""}! ' \
              f'I am Inspector Habit, fighter with world laziness and procrastination. ' \
              f'And you seem to be experiencing certain problems with it.\n\n' \
              f'In short, you assign yourself a habit and promise to follow it, ' \
              f'and I will check you: keep your word - handsome, ' \
              f'you break - you catch a fine. The size of the fine you choose. ' \
              f'And so we work 3 weeks.\n\n' \
              f'All clear? If yes, then choose a habit from the list or write your own, ' \
              f"if not, don't waste my time.\n\n" \
              f"And by the way, I'm a philanthropist: 80% of the money " \
              f"generated on your laziness will go to charity"

    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_habits_markup(message.chat.id))
    bot.register_next_step_handler(message, habit_response)


def habit_response(message):
    user = User.get(message.chat.id)

    ru_text = f'Итак, ты  хочешь *{message.text}*'
    en_text = f'So you want *{message.text}*'
    text = ru_text if user.language_code == 'ru' else en_text

    preparing_habits[message.chat.id] = {'label': message.text, 'days_of_week': []}

    bot.send_message(message.chat.id, text, reply_markup=markups.get_ready_markup(message.chat.id), parse_mode='Markdown')
    days_request(message)


def language_request(message):
    bot.send_message(message.chat.id,
                     '🇷🇺 Выбери язык\n🇬🇧 Choose the language',
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
        location_request(message)

    except ValueError:
        ru_text = 'Кажется, ты ввёл какую-то ерунду. Попробуй ещё раз, используя формат *ЧЧ:ММ*.'
        en_text = 'It seems you have entered some nonsense. Try again using *HH:MM* format.'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text, parse_mode='Markdown')
        bot.register_next_step_handler(message, time_receive)


def location_request(message):
    user = User.get(message.chat.id)

    ru_text = 'Также мне нужно знать твой часовой пояс, чтобы проводить проверки вовремя.\n\n' \
              'Только, пожалуйста, не надо тут разводить беспокойство о своих "персональных данных".' \
              'Мне глубоко наплевать на твоё точное местоположение, просто так удобнее получить часовой пояс.'
    en_text = 'I also need to find out what time zone you live in order to perform the checks on time.\n\n' \
              "But please, don't worry about your “personal data”. " \
              "I don't give a damn about your exact location, it's just more convenient to get a time zone."
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

    if user.referrer:
        referrer = User.get(user.referrer)
        referrer.satisfy_fines(CheckStatus.WORKED.name)

        referral_name = ''
        if user.first_name:
            referral_name = user.first_name
            if user.last_name:
                referral_name = user.first_name + ' ' + user.last_name

        ru_text_ref = f'{referral_name if referral_name else "Твой друг"} ' \
                      f'назначил свою первую привычку. ' \
                      f'За успешно проведённые социальные работы ' \
                      f'с тебя снимаются все обвинения и твои штрафы аннулируются.'
        en_text_ref = f'{referral_name if referral_name else "Your friend"} ' \
                      f'has assigned his first habit. ' \
                      f'For successful social work all charges ' \
                      f'against you and your fines are canceled.'
        text_ref = ru_text_ref if referrer.language_code == 'ru' else en_text_ref

        bot.send_message(referrer.id, text_ref)

    ru_text = 'Ну что ж, посмотрим, какой ты крутой. Удачи!'
    en_text = "Well, let's see how cool you are. Good luck!"
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_main_menu_markup(message.chat.id))
    bot.send_sticker(message.chat.id, 'CAADAgADWQIAAsY4fgsQX6OJTX_IOgI')

