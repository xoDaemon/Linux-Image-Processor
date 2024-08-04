import time
import uuid
import os
import re
import src.database as db
import src.config as config
import src.image_utils as iu
import src.vtscan as vt

delimiter = "-------------------------------------------------------------------------"

class Image:
    conf = config.Config()
    
    def __init__(self, image_path):
        self.uuid_ = uuid.uuid4()
        self.image_path = image_path
        self.hostname = self.get_hostname()
        self.interfaces = self.get_interfaces()
        self.users = self.get_users()
        self.files = []
        self.malicious_files = []

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
                database = db.Database(Image.conf.db_path)
                interfaces_file = interfaces_obj.read()
                regex_pattern = r'iface\s+(\w+)\s*.*?[\n]+\s*address\s+((?:\d{1,3}\.){3}\d{1,3})(?![\d.])'
                
                matches = re.findall(regex_pattern, interfaces_file, flags = re.DOTALL)
                interfaces = [iu.Interface(self.uuid_, match[0], match[1]) for match in matches]
                for interface in interfaces:
                    database.insert_interface(interface)
                
                database.close_connection()
                return interfaces
        except FileNotFoundError:
            print("Interfaces file not found.")
            return None
        
    def get_users(self):
        # username:password:last_change:min:max:warn:inactive:expire:reserved
        def get_passwd_hashes():
            try:
                with open(self.image_path + "/etc/shadow", "r") as passwd_hash_obj:
                    passwd_hash_file = passwd_hash_obj.readlines()
                    passwd_hashes = {}
                    regex_pattern = r'((?:\w[/.=-]*)+|(?:[*!]))'
                    
                    for line in passwd_hash_file:
                        match = re.findall(regex_pattern, line)
                        passwd_hashes[match[0]] = match
                        
                        # print(match)
                    return passwd_hashes
            except FileNotFoundError:
                print("Shadow file not found.")
                
        # password -> algorithm:parameters(optional):salt:hash
        def get_hash_algorithm(passwd_fields):
            alg_identifier = passwd_fields[0]
            
            if len(passwd_fields) == 1:
                if alg_identifier in {'!', '*'}:
                    return None
                return "DES"                # only hash -> DES
            if alg_identifier == '1':
                return "MD5"
            if alg_identifier == '5':
                return "SHA-256"
            if alg_identifier == '6':
                if len(passwd_fields) == 3:
                    return "SHA-512"        # 3 fields -> ident:salt:hash - no room for params
                return "SHA-512-PARAM"
            if alg_identifier == 'y':
                return "YESSCRIPT"
            
            return "UNSUPPORTED"
                
        # username:password:UID:GID:GECOS:home_directory:shell
        def construct_user_data():
            with open(self.image_path + "/etc/passwd", "r") as passwd_obj:
                database = db.Database(Image.conf.db_path)
                passwd_file = passwd_obj.readlines()
                user_data = []
                user_passwd_hashes = get_passwd_hashes()
                hashes = []
                
                for line in passwd_file:
                    data_fields = line.strip().split(':')
                    
                    if data_fields[0] in user_passwd_hashes:
                        matching_hash = user_passwd_hashes[data_fields[0]]
                        if len(matching_hash) >= 6:     # treat special case for systemd-coredump!!
                            hash_alg = get_hash_algorithm(matching_hash[1:-4])
                        new_user_passwd = iu.UserPasswd(username = data_fields[0], hash_alg = hash_alg, last_passwd_change = matching_hash[-4])
                        
                        if hash_alg is not None:
                            if hash_alg == "DES":
                                new_user_passwd.hash_ = matching_hash[1]
                            if hash_alg in {"MD5", "SHA-256", "SHA-512"}:
                                new_user_passwd.salt = matching_hash[2]
                                new_user_passwd.hash_ = matching_hash[3]
                            if hash_alg in {"SHA-512-PARAM", "YESSCRIPT"}:
                                new_user_passwd.alg_param = matching_hash[2]
                                new_user_passwd.salt = matching_hash[3]
                                new_user_passwd.hash_ = matching_hash[4]
                        
                        hashes.append(new_user_passwd)
                        data_fields[1] = new_user_passwd.hash_
                        new_user = iu.User(self.uuid_, *data_fields)
                    
                    user_data.append(new_user)
                    
                    database.insert_user(new_user)
                    database.insert_user_passwd(new_user_passwd)
                
                database.close_connection()
                return user_data
        
        try:
            return construct_user_data()
        except FileNotFoundError:
            print("Passwd file not found.")
            
    def process_file_system(self, verbose = False):
        # read in DFS mode
        def read_files(dir_path):
            nonlocal files_read, dir_perm_denied, files_perm_denied
            entries = os.listdir(dir_path)
            for entry in entries:
                entry_path = os.path.join(dir_path, entry)
                
                if entry_path not in skip_list:
                    try:
                        if verbose:
                            print(entry_path)
                        if os.path.isdir(entry_path):
                            read_files(entry_path)
                        elif os.path.isfile(entry_path):
                            test_read = open(entry_path, 'rb')
                            
                            try:
                                new_file = iu.File(self.uuid_, entry, entry_path)
                                
                                # vt_scan = vt.VTscan(new_file.md5_hash, new_file.path, self.conf.VT_API_KEY, self.conf.VT_API_URL)
                                # if vt_scan.check_hash() == True:
                                #     self.malicious_files.append(new_file)
                                    
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
                        
        skip_list = Image.conf.skip_list
        database = db.Database(Image.conf.db_path)
        
        print(f"Verbose mode: {verbose}")
        print("Processing filesystem...")
        print(delimiter)
        time.sleep(2)
        
        # test only in /var for now
        dir_path = self.image_path + "/var"
        files_read = 0
        files_perm_denied = 0
        dir_perm_denied = 0
        
        
        if verbose:
            print("-----------------Reading files-----------------")
        
        # print all entries, only keep files
        read_files(dir_path)
        print(delimiter)
        
        print("Filesystem processing completed.")
        print("PROCESSING SUMMARY:")
        print("-------------------")
        print("File reading complete.")
        print(f"Files read: {files_read}")
        print(f"Permission denied for: {dir_perm_denied} directories")
        print(f"Permission denied for: {files_perm_denied} files")
        if files_perm_denied > 0 or dir_perm_denied > 0:
            print("Try running as sudo to read all entries.")
        
        print(delimiter)
        database.close_connection()
        
    def print_image(self):
        print("IMAGE SUMMARY:")
        print("--------------")
        print(f"UUID: {self.uuid_}")
        print(f"Path: {self.image_path}")
        print(f"Hostname: {self.hostname}")

        users_no = len(self.users)
        print(f"Users: {users_no} in total")
        for user in self.users:
            print(f"    {user.username} - home dir: {user.home_dir}")
        
        try:    
            interfaces_no = len(self.interfaces)
            
            if interfaces_no > 0:
                print(f"Interfaces: {interfaces_no} detected")
                for interface in self.interfaces:
                    print(f"    {interface.name} - {interface.ip}")
            else:
                print("No interfaces detected.")
        except TypeError:
            print("Interfaces file not found.")
            
        files_no = len(self.files)
        mal_no = len(self.malicious_files)
        
        if mal_no == 0:
            print(f"{files_no} files parsed, from which NONE found malicious")
        
        else:
            print(f"{files_no} files parsed, from which {mal_no} found malicious")
            for mal_file in self.malicious_files:
                print(f"    {mal_file.path}")