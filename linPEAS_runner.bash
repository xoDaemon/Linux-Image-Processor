#!bin/bash

filesystem_path=""
linpeas_log="linpeas_log.txt"

set -e

mount --bind /mnt "$filesystem_path/mnt"

python3 ./proxy.py &
PROXY_PID=$!
echo $PROXY_PID
sleep 2

chroot "$filesystem_path" "/bin/bash" << "EOF"

cd /mnt
curl -L localhost:8080
curl -L "http://localhost:8080/proxy/https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh" | sh | tee "linpeas_log.txt"
exit

EOF

kill $PROXY_PID

mkdir -p "./linpeas_logs"
mv "/mnt/$linpeas_log" "./linpeas_logs/$linpeas_log"

umount "$filesystem_path/mnt"