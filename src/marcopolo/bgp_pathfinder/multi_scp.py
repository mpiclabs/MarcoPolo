#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import importlib
import time
import datetime
import threading
import os

def get_current_human_time():
	value = datetime.datetime.fromtimestamp(time.time())
	return value.astimezone(datetime.timezone.utc).strftime('UTC %Y-%m-%d %H:%M:%S')


def parse_args():
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	dirname = os.path.dirname(os.path.realpath(__file__))
	parser.add_argument("-c", "--config_dir",
	                    default=f"{dirname}/config")
	parser.add_argument("-p", "--push",
	                    default=False, action="store_true")
	parser.add_argument('remote_path', type=str,
                    help='The path of the file on the remote node.')
	parser.add_argument('local_path', type=str,
                    help='The path of the file on the local node.')
	return parser.parse_args()


def scpFile(remotePath, localPath, engine, nodeName, push):
	if not push:
		print(f"[{get_current_human_time()}] Result of copy \"{remotePath}\" to \"{localPath}\" at {nodeName}: {engine.copy_file_from_node_name(remotePath, nodeName, localPath)}")
	else:
		print(f"[{get_current_human_time()}] Result of copy \"{localPath}\" to \"{remotePath}\" at {nodeName}: {engine.copy_file_to_node_name(localPath, nodeName, remotePath)}")
	
	


def main(args):
	masterConfig = json.load(open(args.config_dir + "/cmd.json"))
	
	engineName = masterConfig["engine"]
	engine = importlib.import_module(f"engines.{engineName}")
	threadList = []
	for nodeName in masterConfig["nodes"]:
		effectiveLocalPath = args.local_path
		if not args.push:
			effectiveLocalPath = f"{args.local_path}.{nodeName}"
		threadList.append(threading.Thread(target=scpFile, args=(args.remote_path, effectiveLocalPath, engine, nodeName, args.push)))
	for t in threadList:
		t.start()
	for t in threadList:
		t.join()
		
if __name__ == '__main__':
    main(parse_args())
