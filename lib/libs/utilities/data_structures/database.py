import sqlite3

from libs.logging.verbose import Verbose


class Database():

    def __init__(self, file_path):
        self.connection = sqlite3.connect(file_path)
        self.cursor = self.connection.cursor()

    def create(self, table_name, *attributes):
        args_str = ", ".join(attributes)
        command = "CREATE TABLE IF NOT EXISTS '%s' (%s);" % (table_name, args_str)
        return self.execute(command)

    def execute(self, command):
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def insert(self, table_name, *values):
        args_str = "', '".join(values)
        args_str = "'" + args_str + "'"
        command = "INSERT INTO '%s' VALUES (%s)" % (table_name, args_str)
        return self.execute(command)

    def drop(self, table_name):
        command = "DROP TABLE IF EXISTS '%s'" % (table_name)
        return self.execute(command)

    def select(self, attribute, table_name):
        command = "SELECT %s FROM '%s'" % (attribute, table_name)
        return self.execute(command)

    def close(self):
        self.connection.commit()
        Verbose.green("Closing database")
        self.connection.close()
