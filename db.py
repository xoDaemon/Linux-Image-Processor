import sqlite3 as sql
import pandas as pd

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
            uuid TEXT,
            hostname TEXT,
            PRIMARY KEY (uuid)
        )
        '''
        )
        
        self.cursor.execute(
            '''
        CREATE TABLE IF NOT EXISTS File (
            image_uuid TEXT,
            name TEXT,
            mime_type TEXT,
            path TEXT,
            md5 TEXT,
            sha1 TEXT,
            PRIMARY KEY (name, md5)
            FOREIGN KEY (image_uuid)
            REFERENCES Image(uuid)
                ON UPDATE RESTRICT
                ON DELETE SET NULL
        )
        '''
        )
        
        self.con.commit()
        
    def insert_image(self, image):
        query =  '''
            INSERT INTO Image(uuid, hostname)
            VALUES(?, ?)
            '''
        
        self.cursor.execute(query, (str(image.uuid_), image.hostname))
        
        self.con.commit()
        
    def insert_file(self, file):
        query =  '''
            INSERT INTO File(image_uuid, name, mime_type, path, md5, sha1)
            VALUES(?, ?, ?, ?, ?, ?)
            '''
        
        self.cursor.execute(query, (str(file.image_uuid), file.name, file.mime_type, file.path, file.md5_hash, file.sha1_hash))
        
        self.con.commit()
        
    def search_file(self, file):
        query = '''
            SELECT * FROM File
            WHERE name = ?
            AND md5 = ?
        '''
        
        self.cursor.execute(query, (file.name, file.md5_hash))
        res = self.cursor.fetchone()
        if res == None:
            return False
        return True
        
    def delete_all(self):
        query1 =  '''
            DROP TABLE Image
            '''
        query2 = '''
            DROP TABLE File
        '''
        
        self.cursor.execute(query1)
        self.cursor.execute(query2)
        
        self.con.commit()