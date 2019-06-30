from datetime import datetime, timedelta
import pytz
import settings
from utils.database import execute_database_command
from checks.utils import CheckStatus


def fill_database_with_test_data():
    execute_database_command(f'''INSERT INTO users (id, username, first_name, last_name, timezone, language_code, is_active)
    VALUES (
    {settings.ADMIN_ID},
    'Ivan',
    '',
    '',
    'Europe/Moscow',
    'ru',
    TRUE
    )''')

    execute_database_command(f'''INSERT INTO habits (user_id, label, question, days_of_week, time_array, fine)
    VALUES (
    {settings.ADMIN_ID},
    'Не залипать',
    '',
    '[0, 1]',
    '["7:30", "19:30"]',
    5
    );''')

    for i in range(30):
        for j in range(1):
            datetime_native = pytz.timezone('Europe/Moscow').localize(datetime.now() + timedelta(minutes=i))
            datetime_utc = datetime_native.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M")
            datetime_native = datetime_native.strftime("%Y-%m-%d %H:%M")

            execute_database_command(f'''INSERT INTO checks (habit_id, datetime_native, datetime_utc, status)
            VALUES (
            1,
            '{datetime_native}',
            '{datetime_utc}',
            '{CheckStatus.PENDING.name}'
            );''')
