#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import importlib
import time
import datetime
import threading
import sys

sys.path.append('../')
from .. import bgp_utils


def parse_args():
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	parser.add_argument("-c", "--config_dir",
	                    default="../config")
	parser.add_argument("-p", "--paths_file",
	                    default="../data/paths.txt")
	parser.add_argument("-d", "--destinations", nargs='+', default=None)
	return parser.parse_args()


def main(args):
	masterConfig = json.load(open(args.config_dir + "/master.json"))


	bgp_utils.make_announcements_from_path_txt_file(args.destinations, args.paths_file, masterConfig)	

		

	

if __name__ == '__main__':
    main(parse_args())
