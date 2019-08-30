from bot import bot
from utils.database import execute_database_command
from checks.utils import status_icons
from users.markups import get_main_menu_markup
from users.models import User
from habits.models import Habit
from checks.models import Check
from users.utils import get_schedule, get_user_naming
from habits import markups


@bot.message_handler(func=lambda message:
message.text in ['🗓 Мои привычки', '🗓 My habits'], content_types=['text'])
def user_habits(message):
    checks = execute_database_command(
        f'''SELECT h.id, h.label, c.status FROM checks c JOIN habits h ON 
    c.habit_id=h.id WHERE h.user_id = {message.chat.id} ORDER BY c.datetime_utc;''')[0]
    habits = {}
    for check in checks:
        habit_id = check[0]
        label = check[1]
        status = check[2]

        if habit_id in habits:
            habits[habit_id]['checks'].append(status_icons[status])
        else:
            habits[habit_id] = {'label': label, 'checks': [status_icons[status]]}

    report = ''
    for habit in habits.values():
        report += f'*{habit["label"]}*\n{" ".join(habit["checks"])}\n\n'

    bot.send_message(message.chat.id, text=report, parse_mode='Markdown', reply_markup=get_main_menu_markup(message.chat.id))


@bot.message_handler(func=lambda message: message.text.startswith('/start judge'), commands=['start'])
def register_judge(message):
    habit_id = int(message.text.split('_')[1])
    habit = Habit.get(habit_id)

    if habit.user_id != message.chat.id:
        judge = User.get(message.chat.id)
        if habit.judge is None:
            user = User.get(habit.user_id)

            if judge:
                reply_markup = get_main_menu_markup(judge.id)
            else:
                judge = User(message.chat.id,
                             username=message.from_user.username,
                             first_name=message.from_user.first_name,
                             last_name=message.from_user.last_name,
                             language_code=message.from_user.language_code,
                             timezone='UTC',
                             )
                judge.save()
                reply_markup = markups.get_judge_register_markup(judge.id)

            habit.judge = judge.id
            habit.save()

            days_of_week = list(map(lambda x: int(x), habit.days_of_week[1:-1].split(',')))
            time_array = list(map(lambda x: x.strip(), habit.time_array[1:-1].split(',')))

            schedule_native, schedule_utc = get_schedule(
                days_of_week,
                time_array,
                user.timezone,
            )

            for check_native, check_utc in zip(schedule_native, schedule_utc):  # TODO оптимизировать
                Check(habit.id, check_native, check_utc).save()

            ru_text_judge = f'Теперь ты судья {get_user_naming(user, "своего друга")} ' \
                            f'на привычке *{habit.label}*. Я буду сообщать тебе о его успехах (и провалах😈).'
            en_text_judge = f'You just became the judge of {get_user_naming(user, "your friend")} ' \
                            f'on the habit *{habit.label}*. I will inform you of his successes (and fails😈).'
            text_judge = ru_text_judge if judge.language_code == 'ru' else en_text_judge

            ru_text_user = f'{get_user_naming(judge, "Твой друг")} стал судьёй на привычке *{habit.label}*'
            en_text_user = f'{get_user_naming(user, "Your friend")} became the judge on the habit *{habit.label}*'
            text_user = ru_text_user if user.language_code == 'ru' else en_text_user

            try:
                bot.send_message(message.chat.id, text_judge, reply_markup=reply_markup, parse_mode='Markdown')
            except Exception:
                pass
            try:
                bot.send_message(user.id, text_user, reply_markup=get_main_menu_markup(user.id), parse_mode='Markdown')
            except Exception:
                pass
        else:
            if judge:
                reply_markup = get_main_menu_markup(judge.id)
                ru_text_judge = 'На эту привычку уже назначен судья.'
                en_text_judge = 'The judge has already been assigned to this habit'
                text_judge = ru_text_judge if judge.language_code == 'ru' else en_text_judge
            else:
                judge = User(message.chat.id,
                             username=message.from_user.username,
                             first_name=message.from_user.first_name,
                             last_name=message.from_user.last_name,
                             language_code=message.from_user.language_code,
                             timezone='UTC',
                             )
                judge.save()
                reply_markup = markups.get_judge_register_markup(judge.id)
                ru_text_judge = 'На эту привычку уже назначен судья. ' \
                                'Зарегистрируйся и создай свою собственную привычку.'
                en_text_judge = 'The judge has already been assigned to this habit. ' \
                                'Register and create your own habit.'
                text_judge = ru_text_judge if judge.language_code == 'ru' else en_text_judge

            try:
                bot.send_message(message.chat.id, text_judge, reply_markup=reply_markup, parse_mode='Markdown')
            except Exception:
                pass


