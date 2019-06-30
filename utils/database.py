import psycopg2
from .conf import ConfigParser
from users.db_commands import DROP_USERS_TABLE, CREATE_USERS_TABLE
from habits.db_commands import DROP_HABITS_TABLE, CREATE_HABITS_TABLE
from checks.db_commands import DROP_CHECKS_TABLE, CREATE_CHECKS_TABLE


def execute_database_command(command, args=None):
    conn = None
    results = []
    try:
        config = ConfigParser()
        dbname, user, password, host = config.get_section('database').values()
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        cur = conn.cursor()
        cur.execute(command, args)
        try:
            results.append(cur.fetchall())  # Поправить
        except psycopg2.ProgrammingError as error:
            print('ProgrammingError:', error)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print('DatabaseError:', error)
    finally:
        if conn is not None:
            conn.close()
            return results


def init_database():
    for command in [DROP_CHECKS_TABLE, DROP_HABITS_TABLE, DROP_USERS_TABLE, CREATE_USERS_TABLE, CREATE_HABITS_TABLE, CREATE_CHECKS_TABLE]:
        execute_database_command(command)
    print('bot has been started')
