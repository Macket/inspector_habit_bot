import abc
from utils.database import execute_database_command


class User:
    def __init__(self, telegram_id, username=None, first_name=None, last_name=None, timezone=None, language_code=None, is_active=True):
        self.id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.timezone = timezone
        self.language_code = language_code
        self.is_active = is_active

    @abc.abstractmethod
    def get(telegram_id):
        try:
            id, username, first_name, last_name, timezone, language_code, is_active = execute_database_command('SELECT * FROM users WHERE id=%s', (telegram_id, ))[0][0]
            return User(id, username, first_name, last_name, timezone, language_code, is_active)
        except IndexError:
            return None

    def save(self):
        if User.get(self.id):
            execute_database_command(
                'UPDATE users SET username = %s, first_name = %s, last_name = %s, timezone = %s, language_code = %s, is_active = %s WHERE id = %s',
                (self.username, self.first_name, self.last_name, self.timezone, self.language_code, self.is_active, self.id)
            )
        else:
            execute_database_command(
                'INSERT INTO users (id, username, first_name, last_name, timezone, language_code, is_active)  VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (self.id, self.username, self.first_name, self.last_name, self.timezone, self.language_code, self.is_active)
            )

    def __str__(self):
        return f'{self.username if self.username else "No name"} (id: {self.id})'
