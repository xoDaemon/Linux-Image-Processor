import hashlib
import magic

class File:
    def __init__(self, image_uuid, name, path):
        self.image_uuid = image_uuid
        self.name = name
        self.path = path
        self.mime_type = self.get_file_type(self.path)
        try:
            self.md5_hash, self.sha1_hash = self.calculate_hashes()
        except TypeError: pass
        
        
    def calculate_hashes(self):
        try:
            with open(self.path, "rb") as file_obj:
                file = file_obj.read().strip()
            
                md5_hash = self.calculate_md5(file)
                sha1_hash = self.calculate_sha1(file)
                
            return md5_hash, sha1_hash
            
        except OSError:
            print(f"Error while calculating hashes for {self.path} - type: {self.mime_type}")
            raise
            
    def calculate_md5(self, file):    
        return hashlib.md5(file).hexdigest()

    def calculate_sha1(self, file):
        return hashlib.sha1(file).hexdigest()
    
    def get_file_type(self, file_path):
        mime = magic.Magic(mime = True)
        file_type = mime.from_file(file_path)
        
        return file_type
    
class Interface:
    def __init__(self, image_uuid, name, ip):
        self.image_uuid = image_uuid
        self.name = name
        self.ip = ip
        
class User:
    def __init__(self, image_uuid, username, passwd_hash, uid, gid, gecos, home_dir, shell_path):
        self.image_uuid = image_uuid
        self.username = username
        self.passwd_hash = passwd_hash
        self.uid = uid
        self.gid = gid
        self.gecos = gecos
        self.home_dir = home_dir
        self.shell_path = shell_path
        
class UserPasswd:
    def __init__(self, username, hash_alg = None, alg_param = None, salt = None, hash_ = None, last_passwd_change = 0):
        self.username = username
        self.hash_alg = hash_alg
        self.alg_param = alg_param
        self.salt = salt
        self.hash_ = hash_
        self.last_passwd_change = last_passwd_change