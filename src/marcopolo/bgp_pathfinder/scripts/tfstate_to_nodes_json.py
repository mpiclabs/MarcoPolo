#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json

def parse_args():
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	parser.add_argument("-t", "--tfstate_file",
						default="../terraform/terraform.tfstate")
	parser.add_argument("-n", "--nodes_json_output", # This is a written output file.
						default="../config/vultr/nodes.json")
	return parser.parse_args()


def main(args):
	tfstate = json.load(open(args.tfstate_file))

	nodesJsonObject = {}
	nodesJsonObject["__default"] = {
		"key": "vultr.pem",
		"user": "root",
		"template": "bird6-default.conf"
	}


	resources = tfstate["resources"]
	for resource in resources:
		hostname = resource["name"]
		instance = resource["instances"][0]
		mainIP = instance["attributes"]["main_ip"]
		nodesJsonObject[hostname] = mainIP

	with open(args.nodes_json_output, 'w') as f:
		json.dump(nodesJsonObject, f)


if __name__ == '__main__':
    main(parse_args())