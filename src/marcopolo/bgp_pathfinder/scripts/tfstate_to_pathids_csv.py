#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json

def parse_args():
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	parser.add_argument("-t", "--tfstate_file",
						default="../terraform/terraform.tfstate")
	parser.add_argument("-p", "--pathids_csv", # This is a written output file.
						default="../config/vultr/path-ids.csv")
	parser.add_argument("-c", "--config_dir",
	                    default="../config")
	return parser.parse_args()


def main(args):
	masterConfig = json.load(open(args.config_dir + "/master.json"))
	tfstate = json.load(open(args.tfstate_file))
	# path-ids.csv's format is: <path_id>,<src>,<dst>,<comment>

	# Path id format is <type><src><dst> where type is 10 for vultr ip to BGP announced IP, or 20 for BGP announced IP to vultr IP.
	# <src> is the src address.
	# <dst> is the dst address.

	with open(args.pathids_csv, 'w') as pathsIDFile:

		resources = tfstate["resources"]


		instancePathIDCounter = 0
		for resource in resources:
			hostname = resource["name"]
			instance = resource["instances"][0]
			mainIPv6 = instance["attributes"]["v6_main_ip"]
	
			prefixPathIDCounter = 0
			for prefix in masterConfig["prefixes"]:
				bgpAnnouncedIP = prefix.split("/")[0] + "1" # Assume we are only using the ::1 address for each prefix.
				pathsIDFile.write(f"10{instancePathIDCounter:02d}{prefixPathIDCounter:02d},{mainIPv6},{bgpAnnouncedIP},{hostname}_to_{prefix}\n")
				pathsIDFile.write(f"20{prefixPathIDCounter:02d}{instancePathIDCounter:02d},{bgpAnnouncedIP},{mainIPv6},{prefix}_to_{hostname}\n")
				prefixPathIDCounter += 1

			instancePathIDCounter += 1

if __name__ == '__main__':
    main(parse_args())