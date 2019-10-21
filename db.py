import sqlite3
from sqlite3 import Error

def create_connection(db_file = 'data.db'):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        raise e
    return connection

def execute_sql(connection, sql, data = ()):
    try:
        c = connection.cursor()
        c.execute(sql, data)
        return c
    except Error as e:
        print(e)