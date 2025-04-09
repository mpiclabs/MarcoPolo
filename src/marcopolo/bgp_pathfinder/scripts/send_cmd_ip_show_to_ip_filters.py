#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json

# ./send_cmd.py "ip a show enp1s0 | grep inet6 | grep global"


def parse_args():
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	parser.add_argument("-s", "--send_cmd_output", # This is a written output file.
						default="send-cmd-output.txt")
	return parser.parse_args()


def main(args):
	f = open(args.send_cmd_output)
	for line in f:
		sline = line.strip()
		if sline == "":
			continue
		mainLine = "]".join(sline.split("]")[1:])
		if not mainLine.startswith(" Result of "):
			continue
		
		ip = mainLine.split("inet6 ")[2].split(" scope")[0].split("/")[0]

		ipSplit = ip.split(":")
		if len(ipSplit) < 8:
			for i in range(len(ipSplit)):
				if ipSplit[i] == "":
					extraZeroSectionsNeeded = 8 - len(ipSplit)
					ipSplit = ipSplit[:i] + ([""] * extraZeroSectionsNeeded) + ipSplit[i:]
					break

		resList = []
		for block in ipSplit:
			while len(block) < 4:
				block = "0" + block
			resList.append(f"0x{block[:2]},0x{block[2:]}")
		print("{{{}}},".format(",".join(resList)))

if __name__ == '__main__':
    main(parse_args())

