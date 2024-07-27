#!bin/bash

ewf_file=""
phy_mount_path=""
log_mount_path=""

delimiter="-------------------------------------------------------------------------"

set -e

echo $delimiter
echo "File info for $ewf_file:"
ewfinfo $ewf_file
sleep 1

echo $delimiter
echo "Mounting volume system at $phy_mount_path:"
sudo ewfmount $ewf_file $phy_mount_path
sleep 2
echo "[+] Volume system mounted successfully."

echo $delimiter
echo "Partition layout:"
sudo mmls "$phy_mount_path/ewf1"

linux_partitions=$(sudo mmls "$phy_mount_path/ewf1" | grep -e "Linux")
echo $delimiter
echo "Found following Linux partitions:"
echo $linux_partitions

declare -A partition_array

while IFS= read -r line
do
    i=$(echo $line | awk '{printf "%d",$1}')
    partition_array[$i]=$(echo $line | awk '{printf "%d",$3}')
done < <(echo $linux_partitions)

echo $delimiter
echo "Enter index of partition to be mounted:"
read index

echo $delimiter
echo "Calculating offset..."
res_offset=$(( ${partition_array[$index]} * 512 ))
echo $res_offset
sleep 1

MOUNT_RO="sudo mount -o ro,loop,norecovery,offset=$res_offset $phy_mount_path/ewf1 $log_mount_path"
echo $delimiter
echo "[+] $MOUNT_RO"
echo $delimiter

$MOUNT_RO 
if [[ $? -eq 0 ]]; then
    echo "[+] Successfully mounted Linux partition at $log_mount_path."
else
    echo "[-] Failed to mount Linux partition at $log_mount_path."
fi

echo $delimiter