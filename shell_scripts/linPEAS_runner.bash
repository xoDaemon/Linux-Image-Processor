#!bin/bash

filesystem_path=$1
linpeas_log="linpeas_log.txt"
delimiter="-------------------------------------------------------------------------"

set -e

echo "Binding /mnt directory to filesystem:"
mount --bind /mnt "$filesystem_path/mnt"
echo "[+] Binding successful"

echo $delimiter
echo "Starting proxy server:"
python3 ./proxy.py &
PROXY_PID=$!
echo $PROXY_PID
echo "[+] Proxy server started."
sleep 2

echo $delimiter
echo "Running linPEAS on filesystem:"
echo $delimiter
sleep 2
chroot "$filesystem_path" "/bin/bash" << "EOT"

cd /mnt
curl -L "http://localhost:8080/proxy/https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh" | sh | tee "linpeas_log.txt"
exit

EOT

kill $PROXY_PID

mkdir -p "./linpeas_logs"
mv "/mnt/$linpeas_log" "./linpeas_logs/$linpeas_log"
echo $delimiter
echo "[+] Successfully created linPEAS log."

umount "$filesystem_path/mnt"
echo $delimiter