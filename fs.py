import time
import uuid
import hashlib
import os
import db
import config
import magic
import re

class Image:
    conf = config.Config()
    
    def __init__(self, image_path):
        self.uuid_ = uuid.uuid4()
        self.image_path = image_path
        self.hostname = self.get_hostname()
        self.interfaces = self.get_interfaces()
        self.users = []
        self.files = []

    def get_hostname(self):
        try:
            with open(self.image_path + "/etc/hostname", "r") as hostname_file:
                return hostname_file.readline().strip()
        except FileNotFoundError:
            print("Hostname file not found.")
            return None
        
    def get_interfaces(self):
        try:
            with open(self.image_path + "/etc/network/interfaces", "r") as interfaces_obj:
                database = db.database(Image.conf.db_path)
                interfaces_file = interfaces_obj.read()
                regex_pattern = r'iface\s+(\w+)\s*.*?[\n]+\s*address\s+((?:\d{1,3}\.){3}\d{1,3})(?![\d.])'
                
                matches = re.findall(regex_pattern, interfaces_file, flags = re.DOTALL)
                interfaces = [self.Interface(self.uuid_, match[0], match[1]) for match in matches]
                for interface in interfaces:
                    database.insert_interface(interface)
                
                database.close_connection()
                return interfaces
        except FileNotFoundError:
            print("Interfaces file not found.")
            return None
        
    def process_file_system(self, verbose = False):
        database = db.database(Image.conf.db_path)
        
        print(f"Verbose mode: {verbose}")
        print("Processing filesystem...")
        print("----------------------------------")
        time.sleep(2)
        
        # test only in /var for now
        dir_path = self.image_path + "/var"
        files_read = 0
        files_perm_denied = 0
        dir_perm_denied = 0
        
        # read in DFS mode
        def read_files(dir_path):
            nonlocal files_read, dir_perm_denied, files_perm_denied
            entries = os.listdir(dir_path)
            for entry in entries:
                entry_path = os.path.join(dir_path, entry)
                try:
                    if verbose:
                        print(entry_path)
                    if os.path.isdir(entry_path):
                        read_files(entry_path)
                    elif os.path.isfile(entry_path):
                        test_read = open(entry_path, 'rb')
                        
                        try:
                            new_file = self.File(self.uuid_, entry, entry_path)
                            self.files.append(new_file)
                            if database.search_file(new_file) == False:
                                database.insert_file(new_file)
                        except OSError:
                            pass
                        
                        files_read += 1
                        
                        test_read.close()
                except PermissionError:
                    if verbose:
                        print(f"Permission denied for {entry_path}")
                    if os.path.isdir(entry_path): dir_perm_denied += 1
                    else: files_perm_denied += 1
        
        if verbose:
            print("-----------------Reading files-----------------")
        
        # print all entries, only keep files
        read_files(dir_path)
        print("----------------------------------")
        
        print("File reading complete.")
        print(f"Files read: {files_read}")
        print(f"Permission denied for: {dir_perm_denied} directories")
        print(f"Permission denied for: {files_perm_denied} files")
        if files_perm_denied > 0 or dir_perm_denied > 0:
            print("Try running as sudo to read all entries.")
        # if run as sudo, there are files like speech dispatcher that make the program to never end
        
        database.close_connection()
    
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
                   
                file_obj.close()    
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