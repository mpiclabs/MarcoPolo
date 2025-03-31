#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import importlib
import time
import datetime
import threading
import os
import sys

def get_current_human_time():
	value = datetime.datetime.fromtimestamp(time.time())
	return value.astimezone(datetime.timezone.utc).strftime('UTC %Y-%m-%d %H:%M:%S')


def parse_args(raw_args):
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	dirname = os.path.dirname(os.path.realpath(__file__))
	parser.add_argument("-c", "--config_dir",
	                    default=f"{dirname}/config") #this file's directory
	parser.add_argument("-r", "--install_route",
	                    default=False, action='store_true')
	parser.add_argument('cmds', type=str, nargs='+',
                    help='The commands to run at the nodes.')
	parser.add_argument("-d", "--destinations", nargs='+', default=None)
	return parser.parse_args(raw_args)


def printAndExecCmds(cmds, engine, nodeName, install_route):
	if install_route:
		print(f"[{get_current_human_time()}] Installing mss-limited route at {nodeName}: {engine.install_mss_lmited_route(nodeName)}")
	for cmd in cmds:
		print(f"[{get_current_human_time()}] Result of \"{cmd}\" at {nodeName}: {engine.run_cmd_at_node_name(nodeName, cmd)}")
	


def main(raw_args=None):
	dirname = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(dirname)  # Add the directory containing the engines package to the Python path
	args = parse_args(raw_args)
	masterConfig = json.load(open(args.config_dir + "/cmd.json"))
	engineName = masterConfig["engine"]
	engine = importlib.import_module(f"engines.{engineName}")
	threadList = []
	for nodeName in args.destinations or masterConfig["nodes"]:     # if destination args are specified, they're used, otherwise default config is used
		threadList.append(threading.Thread(target=printAndExecCmds, args=(args.cmds, engine, nodeName, args.install_route)))
	for t in threadList:
		t.start()
	for t in threadList:
		t.join()
		
if __name__ == '__main__':
    main()
