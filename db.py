import sqlite3
from sqlite3 import Error

class database:
    def __init__(self, db_file = 'data.db'):
        self.db_file = db_file
        self.connection = self.create_connection()

    def create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
            raise e
        return connection

    def execute_sql(self, sql, data = ()):
        try:
            c = self.connection.cursor()
            c.execute(sql, data)
            return c
        except Error as e:
            print(e)