import os
import requests
from colorama import Fore, init
import fs

init(autoreset = True)

class VTscan:
    mark_list = ["malicious", "suspicious", "harmless", "undetected", "type-unsopported"]
    
    def __init__(self, file : fs.Image.File):
        self.headers = {
            "x-apikey" : VT_API_KEY,
            "User-Agent" : "python-vtscan",
            "Accept-Encoding" : "gzip, deflate",
        }
        
        self.file = file
        self.marked_as = {
            "malicious" : True,
            "suspicious" : True,
            "harmless" : True,
            "undetected" : True,
            "type-unsopported" : True
        }          
    
    def check_hash(self):
        print(f"Checking hash for {Fore.MAGENTA}{self.file.path}{Fore.RESET}...")
                
        upload_url = os.path.join(VT_API_URL, "files", self.file.md5_hash)
        
        req = requests.get(url = upload_url, headers = self.headers)
        if req.status_code == 200:
            print(f"{Fore.GREEN}Successfully sent hash.")
            print("Analysing results...")
            
            result = req.json()
            
            av_verdicts = result.get("data").get("attributes").get("last_analysis_results")
            stats = result.get("data").get("attributes").get("last_analysis_stats")
            
            for mark in VTscan.mark_list:
                if stats.get(mark) > 0:
                    self.marked_as[mark] = True
            
            print("Summary:")
            print(f"Marked as {Fore.RED}malicious{Fore.RESET} by {Fore.RED}{str(stats.get('malicious'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.YELLOW}suspicious{Fore.RESET} by {Fore.YELLOW}{str(stats.get('suspicious'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.GREEN}harmless{Fore.RESET} by {Fore.GREEN}{str(stats.get('harmless'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.MAGENTA}undetected{Fore.RESET} by {Fore.MAGENTA}{str(stats.get('undetected'))}{Fore.RESET} AVs")
            print(f"Marked as {Fore.BLUE}type-unsupported{Fore.RESET} by {Fore.BLUE}{str(stats.get('type-unsupported'))}{Fore.RESET} AVs")
            print()

            if self.marked_as["malicious"] is True:     
                print(f"Displaying {Fore.RED}malicious{Fore.RESET} detections:")
                print()
                
                for key in av_verdicts:
                    if av_verdicts[key].get("category") == "malicious":
                        print("============================================")
                        print(f"{Fore.BLUE}{av_verdicts[key].get('engine_name')}{Fore.RESET}")
                        
                        print(f"version : {av_verdicts[key].get('engine_version')}")
                        print(f"last update : {av_verdicts[key].get('engine_update')}")
                        print(f"result : {Fore.RED}{av_verdicts[key].get('result')}")
                        print(f"method : {av_verdicts[key].get('method')}")
                        print("============================================")
                        print()
                    
            print(f"{Fore.GREEN}Analysis was successful.")
            print()
            
        else:
            print(f"{Fore.RED}Failed to analyse file hash: code {str(req.status_code)}")