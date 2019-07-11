from bot import bot
from utils.database import execute_database_command
from checks.utils import status_icons
from users.markups import get_main_menu_markup


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
