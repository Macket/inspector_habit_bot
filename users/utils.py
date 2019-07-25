from bot import bot
import datetime
import pytz
from utils.database import execute_database_command
from checks.utils import CheckStatus
from users.models import User


@bot.message_handler(content_types=['sticker'])
def get_sticker_id(message):
    print(message.sticker.file_id)


def remove_markup(chat_id, message_id):
    bot.edit_message_reply_markup(chat_id, message_id=message_id, reply_markup=None)


def get_native_datetime(date, time, timezone):
    return pytz.timezone(timezone).localize(
                datetime.datetime.strptime(f'{date} {time}', "%Y-%m-%d %H:%M"), is_dst=None)


def get_user_naming(user, default):
    user_naming = default
    if user.first_name:
        user_naming = user.first_name
        if user.last_name:
            user_naming = user.first_name + ' ' + user.last_name

    return user_naming


def get_schedule(week_days, time_array, timezone):
    user_date_now = datetime.datetime.now(tz=pytz.timezone(timezone)).date()
    schedule_native = []
    for week_day in week_days:
        if week_day > user_date_now.weekday():
            first_day = user_date_now + datetime.timedelta(week_day - user_date_now.weekday())
        else:
            first_day = user_date_now + datetime.timedelta(7 - user_date_now.weekday() + week_day)

        second_day = first_day + datetime.timedelta(7)
        third_day = second_day + datetime.timedelta(7)

        for time in time_array:
            first_datetime_native, second_datetime_native, third_datetime_native = [
                get_native_datetime(str(day), time, timezone) for day in
                [first_day, second_day, third_day]]

            schedule_native.extend([first_datetime_native, second_datetime_native, third_datetime_native])

    schedule_native.sort()
    schedule_utc = [native_datetime.astimezone(pytz.utc) for native_datetime in schedule_native]
    return schedule_native, schedule_utc


def score_users():
    success_checks = execute_database_command('''SELECT h.user_id, h.fine FROM
        checks c JOIN habits h ON c.habit_id = h.id 
        WHERE  c.status=%s;
        ''', (CheckStatus.SUCCESS.name, ))[0]
    for success_check in success_checks:
        u = User.get(success_check[0])
        u.score += success_check[1]
        u.save()

    fail_checks = execute_database_command('''SELECT h.user_id, h.fine FROM
            checks c JOIN habits h ON c.habit_id = h.id 
            WHERE  c.status=%s;
            ''', (CheckStatus.FAIL.name,))[0]
    for fail_check in fail_checks:
        u = User.get(fail_check[0])
        u.score -= fail_check[1]
        u.save()


def send_info_to_users():
    users = execute_database_command('SELECT id, first_name, language_code FROM users;')[0]

    for user in users:
        ru_text = f'Привет{", " + user[1] if user[1] else ""}!\n\n' \
                  f'Я решил больше не церемониться. Теперь разговариваю дерзко и на "ты". ' \
                  f'Может, хотя бы это поможет тебе побороть свою лень. ' \
                  f'А ещё я теперь отправляю стикеры.\n\n' \
                  f'Короче, я теперь не унылый стандартный бот.'
        en_text = f'Hello{", " + user[1] if user[1] else ""}!\n\n' \
                  f'I decided to no longer stand on ceremony. Now I speak impertinently. ' \
                  f'Maybe at least it will help you overcome your laziness. ' \
                  f'And now I send stickers.\n\n' \
                  f'In short, I am no longer a dull standard bot.'
        text = ru_text if user[2] == 'ru' else en_text

        try:
            bot.send_message(user[0], text, parse_mode='Markdown')
            bot.send_sticker(user[0], 'CAADAgADcgADE-ZSAdekz3zzPdFUAg')
        except Exception as e:
            print(e)
