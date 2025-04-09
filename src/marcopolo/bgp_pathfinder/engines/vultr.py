#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import datetime
import time
import random
import os

dirname = os.path.dirname(os.path.abspath(__file__))

def get_current_human_time():
	value = datetime.datetime.fromtimestamp(time.time())
	return value.astimezone(datetime.timezone.utc).strftime('UTC %Y-%m-%d %H:%M:%S')


def run_cmd(cmdAndArgsList):
	#print(cmdAndArgsList)
	retryCount = 10
	out = b''
	err = b''
	for i in range(retryCount):
		p = subprocess.Popen(cmdAndArgsList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			out, err = p.communicate(timeout=500)
		except subprocess.TimeoutExpired:
			print(f"[{get_current_human_time()}] Timeout expired for cmd {cmdAndArgsList}")
			p.kill()  # kill the subprocess
			continue
        
		if err == b'':
			return out.decode('utf-8')
		elif "kex_exchange_identification" in err.decode('utf-8'): # Just try again in this case.
			continue
		else:
			# Assume this is an ssh connection error.
			print(f"[{get_current_human_time()}] stderr: \"{err.decode('utf-8')}\" from cmd {cmdAndArgsList}") # This could go to stderr or stdio.
			return out.decode('utf-8')
		#pass
		#raise IOError(f"Non-empty error: {err.decode('utf-8')}")
	print(f"[{get_current_human_time()}] Max retries ({retryCount}) reached. stderr: \"{err.decode('utf-8')}\" from cmd {cmdAndArgsList}") # This could go to stderr or stdio.
	return out.decode('utf-8')
		

def run_cmd_at_node(nodeConfig, cmd):
	# change to "-oStrictHostKeyChecking=accept-new" for increased security on newer systems. "-oStrictHostKeyChecking=no",
	return run_cmd(["ssh", f"-i{dirname}/../keys/vultr/{nodeConfig['key']}", "-oStrictHostKeyChecking=accept-new", f"{nodeConfig['user']}@{nodeConfig['ip']}", cmd])

def run_cmd_at_node_name(node, cmd):
	print(f"[{get_current_human_time()}] Running CMD \"{cmd}\" at node {node}")
	nodeConfig = load_node_config(node)
	return run_cmd_at_node(nodeConfig, cmd)




# scp -i ~/vultr.pem config/vultr/templates/bird6-la.conf scp://root@45.32.70.253/root
# f"scp://{nodeConfig['user']}@{nodeConfig['ip']}/{remotePath}"
def copy_file_to_node(localPath, nodeConfig, remotePath):
	return run_cmd(["scp", "-r", f"-i{dirname}/../keys/vultr/{nodeConfig['key']}", localPath, f"{nodeConfig['user']}@{nodeConfig['ip']}:{remotePath}"])

# f"scp://{nodeConfig['user']}@{nodeConfig['ip']}/{remotePath}"x
def copy_file_from_node(remotePath, nodeConfig, localPath):
	return run_cmd(["scp", "-r", f"-i{dirname}/../keys/vultr/{nodeConfig['key']}", f"{nodeConfig['user']}@{nodeConfig['ip']}:{remotePath}", localPath])


def copy_file_to_node_name(localPath, node, remotePath):
	nodeConfig = load_node_config(node)
	return copy_file_to_node(localPath, nodeConfig, remotePath)

def copy_file_from_node_name(remotePath, node, localPath):
	nodeConfig = load_node_config(node)
	return copy_file_from_node(remotePath, nodeConfig, localPath)


# announcementList is of the format [("CIDR-format-prefix", ["BGP:community", ...], ["poison ASN", ...]), ...]
def make_announcement(node, announcementList):
	print(f"[{get_current_human_time()}] Starting announcement at node {node} for {announcementList}")
	nodeConfig = load_node_config(node)
	
	templateFile = open(f"{dirname}/../config/vultr/templates/{nodeConfig['template']}")
	template = templateFile.read()
	templateFile.close()

	templateFile4 = open(f"{dirname}/../config/vultr/templates/{nodeConfig['template4']}")
	template4 = templateFile4.read()
	templateFile4.close()


	routes = ""
	filters = ""

	routes4 = ""
	filters4 = ""

	announcementList = [announcement for announcement in announcementList if announcement[0] is not None]
	for prefix, communities, asPathPoisons in announcementList:
		if len(asPathPoisons) > 0:
			raise IOError(f"Vultr does not support AS-path poisons. Problem announcement: {(prefix, communities, asPathPoisons)}")
		
		if ":" in prefix:
			# IPv6 prefix case
			routes += f"route {prefix} unreachable;\n"
			filters += f"if ( net = {prefix} ) then {{\n"
			for community in communities:
				birdCommunity = community.replace(":", ",")
				filters += f"bgp_community.add(({birdCommunity}));\n"
			filters += f"accept;\n"
			filters += "}\n"
		else:
			# IPv4 prefix case
			routes4 += f"route {prefix} unreachable;\n"
			filters4 += f"if ( net = {prefix} ) then {{\n"
			for community in communities:
				birdCommunity = community.replace(":", ",")
				filters4 += f"bgp_community.add(({birdCommunity}));\n"
			filters4 += f"accept;\n"
			filters4 += "}\n"
	

	nodeV6Address = run_cmd_at_node(nodeConfig, "ip addr show dev enp1s0 | grep inet6 | grep global").split("/")[0].split("inet6 ")[1]

	tmpConfigPath = f"{dirname}/../config/vultr/templates/{nodeConfig['template']}.{int(random.random() * 1000000)}.tmp"
	tmpConfigFile = open(tmpConfigPath, 'w')
	tmpConfigFile.write(template
		.replace("!!!ROUTES_LIST!!!", routes)
		.replace("!!!FILTER_LIST!!!", filters)
		.replace("!!!NODE_IPV4_ADDRESS!!!", nodeConfig['ip'])
		.replace("!!!NODE_IPV6_ADDRESS!!!", nodeV6Address)
		)
	tmpConfigFile.close()

	tmpConfigPath4 = f"{dirname}/../config/vultr/templates/{nodeConfig['template4']}.{int(random.random() * 1000000)}.tmp"
	tmpConfigFile4 = open(tmpConfigPath4, 'w')
	tmpConfigFile4.write(template4
		.replace("!!!ROUTES_LIST!!!", routes4)
		.replace("!!!FILTER_LIST!!!", filters4)
		.replace("!!!NODE_IPV4_ADDRESS!!!", nodeConfig['ip'])
		.replace("!!!NODE_IPV6_ADDRESS!!!", nodeV6Address)
		)
	tmpConfigFile4.close()



	copy_file_to_node(tmpConfigPath, nodeConfig, "/etc/bird/bird6.conf")
	copy_file_to_node(tmpConfigPath4, nodeConfig, "/etc/bird/bird.conf")

	run_cmd(["rm", tmpConfigPath])
	run_cmd(["rm", tmpConfigPath4])

	configCheck = run_cmd_at_node(nodeConfig, "birdc6 -- config check")
	goodConfig = False
	for line in configCheck.split("\n"):
		sline = line.strip()
		if sline == "Configuration OK":
			goodConfig = True
	if not goodConfig:
		raise IOError(f"Bad config for {announcementList} with error: {configCheck}")
	print(f"[{get_current_human_time()}] Loaded config to remote node.")
	

	configCheck4 = run_cmd_at_node(nodeConfig, "birdc -- config check")
	goodConfig = False
	for line in configCheck4.split("\n"):
		sline = line.strip()
		if sline == "Configuration OK":
			goodConfig = True
	if not goodConfig:
		raise IOError(f"Bad config4 for {announcementList} with error: {configCheck4}")
	print(f"[{get_current_human_time()}] Loaded config4 to remote node.")



	reconfigureCheck = run_cmd_at_node(nodeConfig, "birdc6 -- config")
	goodConfig = False
	for line in reconfigureCheck.split("\n"):
		sline = line.strip()
		if sline == "Reconfigured":
			goodConfig = True
		if sline == "Reconfiguration in progress":
			goodConfig = True
	if not goodConfig:
		raise IOError(f"Bad config for {announcementList} when loading with error: {reconfigureCheck}")
	
	reconfigureCheck4 = run_cmd_at_node(nodeConfig, "birdc -- config")
	goodConfig = False
	for line in reconfigureCheck4.split("\n"):
		sline = line.strip()
		if sline == "Reconfigured":
			goodConfig = True
		if sline == "Reconfiguration in progress":
			goodConfig = True
	if not goodConfig:
		raise IOError(f"Bad config4 for {announcementList} when loading with error: {reconfigureCheck4}")
	

	print(f"[{get_current_human_time()}] Reconfigured remote node.")
	
def load_node_config(node):
	dirname = os.path.dirname(os.path.realpath(__file__))
	fullNodesConfig = json.load(open(f"{dirname}/../config/vultr/nodes.json"))
	nodeConfig = fullNodesConfig[node]
	defaultConfig = fullNodesConfig["__default"]
	if isinstance(nodeConfig, str):
		defaultConfig["ip"] = nodeConfig
	else:
		for key in nodeConfig:
			defaultConfig[key] = nodeConfig[key]
	return defaultConfig

def get_path(node, prefix):
	nodeConfig = load_node_config(node)
	cmdOutput = run_cmd_at_node(nodeConfig, f"birdc6 -- show route for {prefix} all")
	for line in cmdOutput.split("\n"):
		sline = line.strip()
		if sline.startswith("BGP.as_path: "):
			return sline.replace("BGP.as_path: ", "")
		if sline.startswith("::/0"):
			return "" # Return empty string in the no route case.
	
	raise IOError(f"No AS_Path found in cmd output: {cmdOutput}")

def get_default_gateway(node):
	return run_cmd_at_node_name(node, "ip -6 route ls | grep default").split("via ")[1].split(" dev ")[0]

def install_mss_lmited_route(node):
	defaultGateway = get_default_gateway(node)
	run_cmd_at_node_name(node, "ip -6 rule add from all lookup 12 priority 12")
	return run_cmd_at_node_name(node, f"ip -6 route add default via {defaultGateway} dev enp1s0 proto ra metric 100 mtu 1500 advmss 1400 table 12")
