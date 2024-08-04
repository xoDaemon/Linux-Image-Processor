import subprocess

def persistence_detector(filesystem_path, log_name):
    subproc = subprocess.run(["bash", "./shell_scripts/linPEAS_runner.bash", filesystem_path])
    if subproc.returncode != 0:
        raise subprocess.CalledProcessError(subproc.returncode, "linPEAS_runner.bash", \
                                            "Error while executing linPEAS runner: {subproc.returncode}") from None
    
    pe_indicator = "[1;31;103"
    skip_sequences = {
        "  [1;31;103mRED/YELLOW[0m: 95% a PE vector\n",
        "  [1;31;103mYOU ARE ALREADY ROOT!!![0m (it could take longer to complete execution)\n",
    }
    pe_vectors = []
    
    with open(f"./linpeas_logs/{log_name}", "r") as log_obj:
        log_file = log_obj.readlines()
        
        for line in log_file:
            if line in skip_sequences:
                continue
            if pe_indicator in line:
                pe_vectors.append(line)
                
    print("LinPEAS found the following PE vectors:")
    print("(It is recommended to review them manually)")
    print("----------------------------------")
    for pe_vector in pe_vectors:
        print(pe_vector)
    
    print("Check out https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS for more info!")