import sqlite3 as sql

class Database:
    def __init__(self, db_path):
        self.con = sql.connect(db_path)
        self.cursor = self.con.cursor()
        
    def close_connection(self):
        self.con.close()
        
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
        
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS Interface (
                    image_uuid TEXT,
                    name TEXT,
                    ip TEXT,
                    PRIMARY KEY (name)
                    FOREIGN KEY (image_uuid)
                    REFERENCES Image(uuid)
                        ON UPDATE RESTRICT
                        ON DELETE SET NULL
                )
            '''
        )
        
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS User (
                    image_uuid TEXT,
                    username TEXT,
                    passwd_hash TEXT,
                    uid NUMBER,
                    gid NUMBER,
                    gecos TEXT,
                    home_dir TEXT,
                    shell_path TEXT,
                    PRIMARY KEY (uid)
                    FOREIGN KEY (image_uuid)
                    REFERENCES Image(uuid)
                        ON UPDATE RESTRICT
                        ON DELETE SET NULL
                )
            '''
        )
        
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS UserPasswd (
                    username TEXT,
                    hash_alg TEXT,
                    alg_param TEXT,
                    salt TEXT,
                    hash TEXT,
                    last_passwd_change NUMBER,
                    PRIMARY KEY (username)
                    FOREIGN KEY (username)
                    REFERENCES User(username)
                        ON UPDATE CASCADE
                        ON DELETE SET NULL
                )
            '''
        )
        
        self.con.commit()
        
    def delete_all(self):        
        self.cursor.execute('DROP TABLE IF EXISTS Image')
        self.cursor.execute('DROP TABLE IF EXISTS File')
        self.cursor.execute('DROP TABLE IF EXISTS Interface')
        self.cursor.execute('DROP TABLE IF EXISTS User')
        self.cursor.execute('DROP TABLE IF EXISTS UserPasswd')
        
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
        
    def insert_interface(self, interface):
        query =  '''
            INSERT INTO Interface(image_uuid, name, ip)
            VALUES(?, ?, ?)
            '''
        
        self.cursor.execute(query, (str(interface.image_uuid), interface.name, interface.ip))
        
        self.con.commit()
        
    def insert_user(self, user):
        query = '''
            INSERT INTO User(image_uuid, username, passwd_hash, uid, gid, gecos, home_dir, shell_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.cursor.execute(query, (str(user.image_uuid), user.username, user.passwd_hash, user.uid, user.gid, user.gecos, user.home_dir, user.shell_path))
        
        self.con.commit()
    
    def insert_user_passwd(self, user_passwd):
        query = '''
            INSERT INTO UserPasswd(username, hash_alg, alg_param, salt, hash, last_passwd_change)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        self.cursor.execute(query, (user_passwd.username, user_passwd.hash_alg, user_passwd.alg_param, user_passwd.salt, user_passwd.hash_, user_passwd.last_passwd_change))
        
        self.con.commit()