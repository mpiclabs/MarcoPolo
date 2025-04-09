#!/bin/bash
# -*- coding: utf-8 -*-



SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."


./send_cmd.py "echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf"

./send_cmd.py "echo 'net.ipv6.conf.all.forwarding=1' >> /etc/sysctl.conf"
./send_cmd.py "sysctl -p"
./send_cmd.py -r "apt update" "apt install -y bird iperf" "ufw disable"



#git clone https://birgelee:personal_access_token@github.com/birgelee/performance-aware-routing.git performance-aware-routing-2
#./send_cmd.py "./performance-aware-routing-2/setup_node.sh"

#./multi_scp.py -p "~/performance-aware-routing-2/ebpf/server-module/path-ids.csv" "config/vultr/path-ids.csv"
