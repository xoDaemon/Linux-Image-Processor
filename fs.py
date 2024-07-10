import time
import uuid
import hashlib
import os

class Image:
    def __init__(self, image_path):
        self.image_path = image_path
        self.hostname = self.get_hostname()
        self.uuid_ = uuid.uuid4()
        self.users = []
        self.interfaces = []
        self.files = []

    def get_hostname(self):
        try:
            with open(self.image_path + "/etc/hostname", "r") as hostname_file:
                return hostname_file.readline().strip()
        except FileNotFoundError:
            print("Hostname file not found.")
            return None
        
    def process_file_system(self):
        print("Processing filesystem...")
        time.sleep(2)
        
        # test only in /var for now
        dir_path = self.image_path + "/var"
        files_read = 0
        files_perm_denied = 0
        dir_perm_denied = 0
        
        # should i pass once or twice?
        def read_files(file_list, dir_path):
            nonlocal files_read, dir_perm_denied, files_perm_denied
            entries = os.listdir(dir_path)
            for entry in entries:
                entry_path = os.path.join(dir_path, entry)
                try:
                    print(entry_path)
                    # time.sleep(1)
                    if os.path.isdir(entry_path):
                        read_files(file_list, entry_path)
                    elif os.path.isfile(entry_path):
                        test_read = open(entry_path, 'rb')
                        
                        file_list.append(self.File(entry, entry_path))
                        files_read += 1
                        
                        test_read.close()
                except PermissionError:
                    print(f"Permission denied for {entry_path}")
                    if os.path.isdir(entry_path): dir_perm_denied += 1
                    else: files_perm_denied += 1
        
        file_list = []
        print("-----------------Reading files-----------------")
        # print all entries, only keep files
        read_files(file_list, dir_path)
        print("----------------------------------")
        
        print("File reading complete.")
        print(f"Files read: {files_read}")
        print(f"Permission denied for: {dir_perm_denied} directories")
        print(f"Permission denied for: {files_perm_denied} files")
        if files_perm_denied > 0 or dir_perm_denied > 0:
            print("Try running as sudo to read all entries.")
        # if run as sudo, there are files like speech dispatcher that make the program to never end
    
    class File:
        def __init__(self, name, path):
            self.name = name
            self.path = path
            try:
                self.md5_hash, self.sha1_hash = self.calculate_hashes()
            except TypeError: pass
            
            
        def calculate_hashes(self):
            try:
                with open(self.path, "rb") as file_obj:
                    file = file_obj.read().strip()
                
                    md5_hash = self.calculate_md5(file)
                    sha1_hash = self.calculate_sha1(file)
                   
                file_obj.close()    
                return md5_hash, sha1_hash
                
            except OSError:
                print(f"Error while calculating hashes for {self.path}")
                
        def calculate_md5(self, file):    
            return hashlib.md5(file).hexdigest()

        def calculate_sha1(self, file):
            return hashlib.sha1(file).hexdigest()