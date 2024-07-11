import sqlite3 as sql
import pandas as pd
import fs

class database:
    def __init__(self, db_path):
        self.con = sql.connect(db_path)
        self.cursor = self.con.cursor()
        
    def close_connection(self):
        self.con.close()
        
    def show_table(self, table_name):
        df = pd.read_sql_query(f'SELECT * FROM {table_name}', self.con)
        print(df)
        print(df.to_string(index=False))
        
    def create_tables(self):
        self.cursor.execute(
            '''
        CREATE TABLE IF NOT EXISTS Image (
            uuid TEXT PRIMARY KEY,
            hostname TEXT
        )
        '''
        )
        
        self.cursor.execute(
            '''
        CREATE TABLE IF NOT EXISTS File (
            uuid TEXT,
            name TEXT,
            path TEXT,
            md5 TEXT PRIMARY KEY,
            sha1 TEXT,
            FOREIGN KEY (uuid)
            REFERENCES Image(uuid)
                ON UPDATE RESTRICT 
                ON DELETE SET NULL
        )
        '''
        )
        
        self.con.commit()
        
    def insert_image(self, image : fs.Image):
        query =  '''
            INSERT INTO image(uuid, name)
            VALUES(?, ?)
            '''
        
        self.cursor.execute(query, (str(image.uuid_), image.hostname))
        
        self.con.commit()