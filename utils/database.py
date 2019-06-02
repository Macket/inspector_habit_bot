import psycopg2
from .conf import ConfigParser


def execute_database_command(command):
    conn = None
    try:
        config = ConfigParser()
        dbname, user, password, host = config.get_section('database').values()
        conn = psycopg2.connect(dbname=dbname, user=user,
                        password=password, host=host)
        cur = conn.cursor()
        cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
