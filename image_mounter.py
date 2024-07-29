import subprocess

def image_mounter(ewf_file, phy_mount_path, log_mount_path):
    subprocess.run(["sudo", "bash", "image_mounter.bash", ewf_file, phy_mount_path, log_mount_path])