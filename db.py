import sqlite3
import os


class DataBase:
    def __init__(self, config):
        self.file = config["database"]

    def exists(self):
        return os.path.exists(self.file)

    def add_record(self, price):
        self.conn.execute("insert into log(price) values (" + str(price) + ")")
        self.conn.commit()

    def get_last_record(self):
        self.cursor = self.conn.cursor()
        query = "SELECT price FROM log ORDER BY id DESC LIMIT 1"
        self.cursor .execute(query)
        row = self.cursor.fetchone()
        self.cursor.close()
        return row

    def migrate(self):
        self.conn.execute("""create table log (
                              id integer primary key autoincrement,
                              price real
                        )""")

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.file)
            return True
        except Exception:
            return False
