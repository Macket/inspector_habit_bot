from bot import bot
from utils.database import execute_database_command
from checks.utils import status_icons
from users.markups import get_main_menu_markup
from users.models import User
from habits.models import Habit
from checks.models import Check
from users.utils import get_schedule, get_user_naming
from habits import markups
import re


@bot.message_handler(func=lambda message:
message.text in ['🗓 Мои привычки', '🗓 My habits'], content_types=['text'])
def habits_type_request(message):
    text = 'Активные или завершённые?' if \
        message.text == '🗓 Мои привычки' else 'Active or completed?'

    try:
        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_choose_habit_type_markup(message.chat.id),
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, habits_type_receive)
    except:
        pass


def habits_type_receive(message):
    if message.text in ['Активные', 'Active']:
        active_habits(message)
    else:
        completed_habits(message)


def completed_habits(message):
    habit_ids = execute_database_command(
        f'SELECT id FROM habits WHERE user_id = {message.chat.id}')[0]
    completed_habits_report = {}
    for habit_id in habit_ids:
        habit_id = habit_id[0]
        habit = Habit.get(habit_id)
        if not habit.get_remaining_checks():
            check_statuses = execute_database_command(
                f'SELECT status FROM checks WHERE habit_id = {habit_id} ORDER BY datetime_utc;')[0]

            for check_status in check_statuses:
                check_status = check_status[0]
                if habit_id in completed_habits_report:
                    completed_habits_report[habit_id]['checks'].append(status_icons[check_status])
                else:
                    completed_habits_report[habit_id] = \
                        {'label': habit.label, 'checks': [status_icons[check_status]]}

    if completed_habits_report:
        report = ''
        for habit in completed_habits_report.values():
            report += f'*{habit["label"]}*\n{" ".join(habit["checks"])}\n\n'
    else:
        user = User.get(message.chat.id)
        ru_report = 'Нет ни одной завершённой привычки'
        en_report = 'There are no completed habits'
        report = ru_report if user.language_code == 'ru' else en_report

    try:
        bot.send_message(message.chat.id,
                         text=report,
                         parse_mode='Markdown',
                         reply_markup=get_main_menu_markup(message.chat.id))
    except:
        pass


def active_habits(message):
    user = User.get(message.chat.id)
    habit_ids = execute_database_command(
        f'SELECT id FROM habits WHERE user_id = {message.chat.id}')[0]

    active_habits_ids = []
    for habit_id in habit_ids:
        habit_id = habit_id[0]
        habit = Habit.get(habit_id)
        if habit.get_remaining_checks():
            active_habits_ids.append(habit_id)
            check_statuses = execute_database_command(
                f'SELECT status FROM checks WHERE habit_id = {habit_id} ORDER BY datetime_utc;')[0]

            check_report = ''
            for check_status in check_statuses:
                check_report += status_icons[check_status[0]]

            # TODO убрать дублирование кода с Intro
            ru_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            en_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
            days = ru_days if user.language_code == 'ru' else en_days

            days_of_week = list(map(lambda x: int(x), habit.days_of_week[1:-1].split(',')))
            print(days_of_week)
            time_array = list(map(lambda x: x.strip(), habit.time_array[1:-1].split(',')))
            print(time_array)
            check_days = re.sub(r'\s+', ' ', ' '.join(
                [day if day_of_week in days_of_week else '' for day_of_week, day in
                 enumerate(days)]))
            print(check_days)
            check_time = ' '.join(time_array)
            print(check_time)

            ru_text = f'Привычка: *{habit.label}*.\n' \
                      f'Дни недели: *{check_days}*\n' \
                      f'Время проверки: *{check_time}*\n' \
                      f'Длительность: *3 недели*\n' \
                      f'Штраф: *${habit.fine}*\n\n' \
                      f'Прогресс\n'
            en_text = f'Habit: *{habit.label}*.\n' \
                      f'Days of week: *{check_days}*\n' \
                      f'Checks time: *{check_time}*\n' \
                      f'Duration: *3 weeks*\n' \
                      f'Fine: *${habit.fine}*\n\n' \
                      f'Progress\n'
            text = ru_text if user.language_code == 'ru' else en_text

            text += check_report

            bot.send_message(message.chat.id, text=text, parse_mode='Markdown',
                             reply_markup=markups.get_delete_habit_markup(message.chat.id, habit_id))

    if active_habits_ids:
        text = 'Это всё' if user.language_code == 'ru' else "That's all"
        bot.send_message(message.chat.id, text=text, reply_markup=get_main_menu_markup(message.chat.id))
    else:
        ru_report = 'Нет ни одной активной привычки'
        en_report = 'There are no active habits'
        report = ru_report if user.language_code == 'ru' else en_report
        try:
            bot.send_message(message.chat.id,
                             text=report,
                             parse_mode='Markdown',
                             reply_markup=get_main_menu_markup(message.chat.id))
        except:
            pass


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


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@DELETE_HABIT'))
def delete_habit(call):
    user = User.get(call.message.chat.id)
    habit_id = int(call.data.split('/')[1])
    habit = Habit.get(habit_id)
    if habit:
        execute_database_command(f'DELETE FROM habits WHERE id = {habit_id};')
        ru_text = f'Привычка *{habit.label}* удалена'
        en_text = f'The habit *{habit.label}* has been deleted'
        text = ru_text if user.language_code == 'ru' else en_text
    else:
        ru_text = f'Такой привычки не существует'
        en_text = f'This habit does not exists'
        text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(user.id, text, reply_markup=get_main_menu_markup(user.id), parse_mode='Markdown')
