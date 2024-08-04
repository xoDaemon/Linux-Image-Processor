import os
import requests
from colorama import Fore, init

init(autoreset = True)

class VTscan:
    def __init__(self, file_md5, file_path, VT_API_KEY, VT_API_URL):
        self.VT_API_KEY = VT_API_KEY
        self.VT_API_URL = VT_API_URL
        
        self.headers = {
            "x-apikey" : self.VT_API_KEY,
            "User-Agent" : "python-vtscan",
            "Accept-Encoding" : "gzip, deflate",
        }
        
        self.file_md5 = file_md5
        self.file_path = file_path
        self.marked_as = {
            "malicious" : False,
            "suspicious" : False,
            "harmless" : False,
            "undetected" : False,
            "type-unsupported" :False,
        }
        
        # self.not_vt = False
    
    def check_hash(self):
        # print(f"Checking hash for {Fore.MAGENTA}{self.file_path}{Fore.RESET}...")
                
        upload_url = os.path.join(self.VT_API_URL, "files", self.file_md5)
        
        req = requests.get(url = upload_url, headers = self.headers)
        if req.status_code == 200:
            # print(f"{Fore.GREEN}Successfully sent hash.")
            # print("Analysing results...")
            
            result = req.json()
            
            self.av_verdicts = result.get("data").get("attributes").get("last_analysis_results")
            self.stats = result.get("data").get("attributes").get("last_analysis_stats")
            
            for mark in self.marked_as.keys():
                if self.stats.get(mark) > 0:
                    self.marked_as[mark] = True
                    
            # print(f"{Fore.GREEN}Analysis was successful.")
            # print()
            
            return self.marked_as["malicious"]
        
        elif req.status_code == 404:
            pass
        elif req.status_code == 429:
            print("Exceed daily VT API calls quota.")
            return None
        else:
            print(f"{Fore.RED}Failed to analyse file hash: code {str(req.status_code)}")
            return None
            
    def display_vt(self):
            print("Summary:")
            print(f"Marked as {Fore.RED}malicious{Fore.RESET} by {Fore.RED}{str(self.stats.get('malicious'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.YELLOW}suspicious{Fore.RESET} by {Fore.YELLOW}{str(self.stats.get('suspicious'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.GREEN}harmless{Fore.RESET} by {Fore.GREEN}{str(self.stats.get('harmless'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.MAGENTA}undetected{Fore.RESET} by {Fore.MAGENTA}{str(self.stats.get('undetected'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.BLUE}type-unsupported{Fore.RESET} by {Fore.BLUE}{str(self.stats.get('type-unsupported'))}{Fore.RESET} AVs")
            print()

            if self.marked_as["malicious"] is True:     
                print(f"Displaying {Fore.RED}malicious{Fore.RESET} detections:")
                print()
                
                for key in self.av_verdicts:
                    if self.av_verdicts[key].get("category") == "malicious":
                        print("============================================")
                        print(f"{Fore.BLUE}{self.av_verdicts[key].get('engine_name')}{Fore.RESET}")
                        
                        print(f"version : {self.av_verdicts[key].get('engine_version')}")
                        print(f"last update : {self.av_verdicts[key].get('engine_update')}")
                        print(f"result : {Fore.RED}{self.av_verdicts[key].get('result')}")
                        print(f"method : {self.av_verdicts[key].get('method')}")
                        print("============================================")
                        print()