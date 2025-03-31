#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json

# ./send_cmd.py "ip a show enp1s0 | grep inet6 | grep global"


def parse_args():
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	parser.add_argument("-p", "--pathfinder_paths", # This is a written output file.
						default="paths.txt")
	return parser.parse_args()


def main(args):

	communityLists = set()
	f = open(args.pathfinder_paths)
	for line in f:
		sline = line.strip()
		if sline == "":
			continue
		jline = json.loads(sline)
		paths = jline["paths"]
		for path in paths:
			communities = sorted(path[1])
			communityLists.add(tuple(communities))
	print(len(communityLists))
	communityListsList = sorted(list(communityLists), key=lambda s: len(s))

	print(communityListsList)


if __name__ == '__main__':
    main(parse_args())

