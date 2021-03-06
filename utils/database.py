import psycopg2
import settings
from users.db_commands import DROP_USERS_TABLE, CREATE_USERS_TABLE
from habits.db_commands import DROP_HABITS_TABLE, CREATE_HABITS_TABLE
from checks.db_commands import DROP_CHECKS_TABLE, CREATE_CHECKS_TABLE
import urllib.parse as urlparse


def execute_database_command(command, args=None):
    conn = None
    results = []
    try:
        if settings.DEBUG:
            conn = psycopg2.connect(dbname=settings.DB_NAME, user=settings.DB_USER, password=settings.DB_PASSWORD, host=settings.DB_HOST)
        else:
            url = urlparse.urlparse(settings.DATABASE_URL)
            dbname = url.path[1:]
            user = url.username
            password = url.password
            host = url.hostname
            port = url.port

            conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
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
    if settings.DEBUG:
        commands = [DROP_CHECKS_TABLE, DROP_HABITS_TABLE, DROP_USERS_TABLE, CREATE_USERS_TABLE, CREATE_HABITS_TABLE, CREATE_CHECKS_TABLE]
    else:
        commands = [CREATE_USERS_TABLE, CREATE_HABITS_TABLE, CREATE_CHECKS_TABLE]
    for command in commands:
        execute_database_command(command)
    print('bot has been started')
