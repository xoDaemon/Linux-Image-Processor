import sqlite3 as sql
import pandas as pd

class database:
    def __init__(self):
        self.con = sql.connect("test.db")
        self.cursor = self.con.cursor()
        
    def close_connection(self):
        self.con.close()
        
    def show_table(self, table_name):
        df = pd.read_sql_query(format("SELECT * FROM {}", table_name), self.con)
        print(df)
        print(df.to_string(index=False))
        
    def create_tables(self):
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS files (
            uuid TEXT PRIMARY KEY,
            name TEXT,
            path TEXT,
            md5 TEXT,
            sha1 TEXT
        )
        """
        )
