import abc
from utils.database import execute_database_command


class Habit:
    def __init__(self, user_id, label, days_of_week, time_array, fine, id=None, question=''):
        self.id = id
        self.user_id = user_id
        self.label = label
        self.question = question
        self.days_of_week = days_of_week
        self.time_array = time_array
        self.fine = fine

    @abc.abstractmethod
    def get(habit_id):
        try:
            id, user_id, label, question, days_of_week, time_array, fine = execute_database_command('SELECT * FROM habits WHERE id=%s', (habit_id, ))[0][0]
            return Habit(user_id, label, days_of_week, time_array, fine, id, question)
        except IndexError:
            return None

    def save(self):
        # execute_database_command((f'''UPDATE habits
        # SET username = '{self.username if self.username else ''}',
        # first_name = '{self.first_name if self.first_name else ''}',
        # last_name = '{self.last_name if self.last_name else ''}',
        # timezone = '{self.timezone if self.timezone else ''}',
        # language_code = '{self.language_code if self.language_code else ''}',
        # monday = {self.monday}
        # tuesday = {self.tuesday}
        # wednesday = {self.wednesday}
        # thursday = {self.thursday}
        # friday = {self.friday}
        # saturday = {self.saturday}
        # is_active = {self.is_active} WHERE id = {self.id}''',))
    #     else:
        habit_id = execute_database_command(
            'INSERT INTO habits (user_id, label, question, days_of_week, time_array, fine) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;',
            (self.user_id, self.label, self.question, self.days_of_week, self.time_array, self.fine)
        )[0][0][0]
        return Habit(self.user_id,
                     self.label,
                     self.days_of_week,
                     self.time_array,
                     self.fine,
                     habit_id,
                     self.question,)
        # habit_id =  execute_database_command((f'''INSERT INTO habits (user_id, label, question, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
        # VALUES (
        # {self.user_id},
        # '{self.label if self.label else ''}',
        # '{self.question if self.question else ''}',
        # {self.monday},
        # {self.tuesday},
        # {self.wednesday},
        # {self.thursday},
        # {self.friday},
        # {self.saturday},
        # {self.sunday}
        # ) RETURNING id;''',))[0][0][0]
        # return Habit(self.user_id,
        #              self.label,
        #              habit_id,
        #              self.question,
        #              self.monday,
        #              self.tuesday,
        #              self.wednesday,
        #              self.thursday,
        #              self.friday,
        #              self.saturday,
        #              self.sunday)
    #
    # def __str__(self):
    #     return f'{self.name if self.name else "No name"} (id: {self.id})'
