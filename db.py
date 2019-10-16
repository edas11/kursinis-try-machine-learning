import sqlite3
from sqlite3 import Error

def create_connection(db_file = 'data.db'):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
        raise e
    return connection

def execute_sql(connection, sql, data = None):
    try:
        c = connection.cursor()
        if data != None:
            c.execute(sql, data)
        else:
            c.execute(sql)
        return c
    except Error as e:
        print(e)