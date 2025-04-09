#!/bin/bash
# -*- coding: utf-8 -*-



SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

./send_cmd.py "tmux new -s iperf0s -d 'iperf -V -s -u -i 1 -B 2604:4540:80::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf0s.log 500M'"
./send_cmd.py "tmux new -s iperf1s -d 'iperf -V -s -u -i 1 -B 2604:4540:81::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf1s.log 500M'"
./send_cmd.py "tmux new -s iperf2s -d 'iperf -V -s -u -i 1 -B 2604:4540:82::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf2s.log 500M'"
./send_cmd.py "tmux new -s iperf3s -d 'iperf -V -s -u -i 1 -B 2604:4540:83::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf3s.log 500M'"
./send_cmd.py "tmux new -s iperf4s -d 'iperf -V -s -u -i 1 -B 2604:4540:84::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf4s.log 500M'"
./send_cmd.py "tmux new -s iperf5s -d 'iperf -V -s -u -i 1 -B 2604:4540:85::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf5s.log 500M'"
./send_cmd.py "tmux new -s iperf6s -d 'iperf -V -s -u -i 1 -B 2604:4540:86::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf6s.log 500M'"
./send_cmd.py "tmux new -s iperf7s -d 'iperf -V -s -u -i 1 -B 2604:4540:87::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf7s.log 500M'"
./send_cmd.py "tmux new -s iperf8s -d 'iperf -V -s -u -i 1 -B 2604:4540:88::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf8s.log 500M'"
./send_cmd.py "tmux new -s iperf9s -d 'iperf -V -s -u -i 1 -B 2604:4540:89::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperf9s.log 500M'"
./send_cmd.py "tmux new -s iperfas -d 'iperf -V -s -u -i 1 -B 2604:4540:8a::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfas.log 500M'"
./send_cmd.py "tmux new -s iperfbs -d 'iperf -V -s -u -i 1 -B 2604:4540:8b::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfbs.log 500M'"
./send_cmd.py "tmux new -s iperfcs -d 'iperf -V -s -u -i 1 -B 2604:4540:8c::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfcs.log 500M'"
./send_cmd.py "tmux new -s iperfds -d 'iperf -V -s -u -i 1 -B 2604:4540:8d::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfds.log 500M'"
./send_cmd.py "tmux new -s iperfes -d 'iperf -V -s -u -i 1 -B 2604:4540:8e::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperfes.log 500M'"
./send_cmd.py "tmux new -s iperffs -d 'iperf -V -s -u -i 1 -B 2604:4540:8f::1 | rotatelogs -p /root/performance-aware-routing-2/compress-log.sh -c logs/iperffs.log 500M'"