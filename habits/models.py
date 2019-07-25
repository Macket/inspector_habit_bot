import abc
import ast
from utils.database import execute_database_command


class Habit:
    def __init__(self, user_id, label, days_of_week, time_array, fine, id=None, question='', judge=None):
        self.id = id
        self.user_id = user_id
        self.label = label
        self.question = question
        self.days_of_week = days_of_week
        self.time_array = time_array
        self.fine = fine
        self.judge = judge

    @abc.abstractmethod
    def get(habit_id):
        try:
            id, user_id, label, question, days_of_week, time_array, fine, judge = execute_database_command('SELECT * FROM habits WHERE id=%s', (habit_id, ))[0][0]
            return Habit(user_id, label, days_of_week, time_array, fine, id, question, judge)
        except IndexError:
            return None

    def save(self):
        if Habit.get(self.id):
            execute_database_command(
                'UPDATE habits SET user_id = %s, label = %s, question = %s, days_of_week = %s, time_array = %s, fine = %s, judge=%s WHERE id = %s',
                (self.user_id, self.label, self.question, self.days_of_week, self.time_array, self.fine, self.judge, self.id)
            )
        else:
            habit_id = execute_database_command(
                'INSERT INTO habits (user_id, label, question, days_of_week, time_array, fine, judge) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;',
                (self.user_id, self.label, self.question, self.days_of_week, self.time_array, self.fine, self.judge)
            )[0][0][0]

            self.id = habit_id

        return self

    def __str__(self):
        return f'{self.label if self.label else "No name"} (id: {self.id})'
