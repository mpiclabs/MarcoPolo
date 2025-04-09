#!/bin/bash
# -*- coding: utf-8 -*-



SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

./send_cmd.py "tmux new -s iperf0 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:80::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf0.log 500M'"
./send_cmd.py "tmux new -s iperf1 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:81::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf1.log 500M'"
./send_cmd.py "tmux new -s iperf2 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:82::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf2.log 500M'"
./send_cmd.py "tmux new -s iperf3 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:83::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf3.log 500M'"
./send_cmd.py "tmux new -s iperf4 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:84::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf4.log 500M'"
./send_cmd.py "tmux new -s iperf5 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:85::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf5.log 500M'"
./send_cmd.py "tmux new -s iperf6 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:86::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf6.log 500M'"
./send_cmd.py "tmux new -s iperf7 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:87::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf7.log 500M'"
./send_cmd.py "tmux new -s iperf8 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:88::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf8.log 500M'"
./send_cmd.py "tmux new -s iperf9 -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:89::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf9.log 500M'"
./send_cmd.py "tmux new -s iperfa -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:8a::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfa.log 500M'"
./send_cmd.py "tmux new -s iperfb -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:8b::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfb.log 500M'"
./send_cmd.py "tmux new -s iperfc -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:8c::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfc.log 500M'"
./send_cmd.py "tmux new -s iperfd -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:8d::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfd.log 500M'"
./send_cmd.py "tmux new -s iperfe -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:8e::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfe.log 500M'"
./send_cmd.py "tmux new -s iperff -d 'iperf -t 50000000 -i 1 -V -M 100 -u -length .1k -c 2604:4540:8f::1 -b .1M | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperff.log 500M'"
