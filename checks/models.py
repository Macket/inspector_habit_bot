import abc
from utils.database import execute_database_command
from checks.utils import CheckStatus


class Check:
    def __init__(self, habit_id, datetime_native, datetime_utc, status=CheckStatus.PENDING.name, id=None):
        self.habit_id = habit_id
        self.datetime_native = datetime_native
        self.datetime_utc = datetime_utc
        self.status = status
        self.id = id

    @abc.abstractmethod
    def get(check_id):
        try:
            id, habit_id, datetime_native, datetime_utc, status = execute_database_command('SELECT * FROM checks WHERE id=%s', (check_id, ))[0][0]
            return Check(habit_id, datetime_native, datetime_utc, status, id)
        except IndexError:
            return None

    def save(self):
        if Check.get(self.id):
            execute_database_command(
                f'UPDATE checks SET '
                f'habit_id = %s,'
                f'''datetime_native = '{self.datetime_native}','''
                f'''datetime_utc = '{self.datetime_utc}','''
                f'status = %s WHERE id = %s',
                (self.habit_id, self.status, self.id)
            )
        else:
            check_id = execute_database_command(
                'INSERT INTO checks (habit_id, datetime_native, datetime_utc, status) '
                f'''VALUES (%s, '{self.datetime_native}', '{self.datetime_utc}', %s) RETURNING id;''',
                (self.habit_id, self.status))[0][0][0]
            return Check(self.habit_id, self.datetime_native, self.datetime_utc, self.status, check_id)
    #
    # def __str__(self):
    #     return f'{self.name if self.name else "No name"} (id: {self.id})'

