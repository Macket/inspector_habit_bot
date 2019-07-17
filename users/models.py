import abc
from utils.database import execute_database_command
from checks.utils import CheckStatus


class User:
    def __init__(self, telegram_id, username=None, first_name=None, last_name=None, timezone=None, language_code=None, is_active=True, referrer=None, score=0):
        self.id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.timezone = timezone
        self.language_code = language_code
        self.is_active = is_active
        self.referrer = referrer
        self.score = score

    @abc.abstractmethod
    def get(telegram_id):
        try:
            id, username, first_name, last_name, timezone, language_code, is_active, referrer, score = execute_database_command('SELECT * FROM users WHERE id=%s', (telegram_id, ))[0][0]
            return User(id, username, first_name, last_name, timezone, language_code, is_active, referrer, score)
        except IndexError:
            return None

    def save(self):
        if User.get(self.id):
            execute_database_command(
                'UPDATE users SET username = %s, first_name = %s, last_name = %s, timezone = %s, language_code = %s, is_active = %s, referrer=%s, score=%s WHERE id = %s',
                (self.username, self.first_name, self.last_name, self.timezone, self.language_code, self.is_active, self.referrer, self.score, self.id)
            )
        else:
            execute_database_command(
                'INSERT INTO users (id, username, first_name, last_name, timezone, language_code, is_active, referrer, score)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (self.id, self.username, self.first_name, self.last_name, self.timezone, self.language_code, self.is_active, self.referrer, self.score)
            )

    def get_fines(self):
        res = execute_database_command(
            'SELECT h.label, c.datetime_native, h.fine FROM checks c JOIN habits h ON c.habit_id = h.id WHERE c.status = %s AND h.user_id = %s;',
            (CheckStatus.FAIL.name, self.id)
        )[0]
        return res

    def satisfy_fines(self, satisfaction_type):
        execute_database_command(
            'UPDATE checks SET status = %s FROM habits WHERE habits.id = checks.habit_id AND habits.user_id = %s AND checks.status = %s;',
            (satisfaction_type, self.id, CheckStatus.FAIL.name)
        )

    def __str__(self):
        return f'{self.username if self.username else "No name"} (id: {self.id})'
