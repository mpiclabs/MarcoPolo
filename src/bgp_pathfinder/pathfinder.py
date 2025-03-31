#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import traceback
import os
import sys
import argparse
import json
import importlib
import time
import datetime
import threading
from . import bgp_utils

def get_current_human_time():
	value = datetime.datetime.fromtimestamp(time.time())
	return value.astimezone(datetime.timezone.utc).strftime('UTC %Y-%m-%d %H:%M:%S')

# If no input, defaults to command line (but can also call with parameters)
def parse_args(raw_args):
	parser = argparse.ArgumentParser()
	# This is a CAIDA AS topology.
	dirname = os.path.dirname(os.path.realpath(__file__))
	parser.add_argument("-c", "--config_dir",
	                    default=f"{dirname}/config")
	parser.add_argument("-p", "--paths_file",
	                    default="./paths.txt")
	parser.add_argument("-w", "--withdraw",
	                    default=False, action='store_true')
	parser.add_argument("-a", "--announce",
	                    default=False, action='store_true')
	parser.add_argument("-n", "--single_node",
	                    default=False, action='store_true')
	parser.add_argument("-d", "--destinations", nargs='+', default=None)
	parser.add_argument("-i", "--ip_prefixes", nargs='+', default=[])
	parser.add_argument("-o", "--communities", nargs='+', default=[])

	parser.add_argument("-s", "--setup_from_announcement_statement", default=None)
	
	return parser.parse_args(raw_args)

pathsFileWritingLock = threading.Lock()

def writeFinalPathList(pathsFileName, resultObject, finalPathList):
	print(f"{getPrefix(resultObject)} Final Path List: {json.dumps(finalPathList)}")
	resultObject["paths"] = finalPathList
	with pathsFileWritingLock:
		with open(pathsFileName, 'a') as pathsFile:
			pathsFile.write(json.dumps(resultObject))
			pathsFile.write("\n")

def getPrefix(resultObject):
	return f"[{get_current_human_time()}](s: {resultObject['src']}, d: {resultObject['dst']}) "

def pathfinder(srcNode, dstNode, prefix, masterConfig, communities, engine, pathsFileName):
	resultObject = {"src": srcNode, "dst": dstNode}

	# Below code block is dummy code for testing purposes.
	#print(f"{getPrefix(resultObject)} starting dummy code on prefix {prefix}.")
	#time.sleep(2)
	#print(f"{getPrefix(resultObject)} finished dummy code on prefix {prefix}.")
	#return
	
	pathList = []
	currentCommunities = []
	currentPoisons = []
	propagationDelaySeconds = masterConfig["prpagation-delay-min"] * 60
	ignoreHopCount = masterConfig["ignore-hops"]
	# Testing code for static announcement.
	#engine.make_announcement(dstNode, [(prefix, ["64600:2914", "64600:1299", "64600:3257", "174:990"], currentPoisons)])
	#exit()



	# Make an unmodified announcement for the prefix.
	engine.make_announcement(dstNode, [(prefix, currentCommunities, currentPoisons)])
	time.sleep(propagationDelaySeconds)
	# Get the current path from the src to the destination.
	currentPath = engine.get_path(srcNode, prefix)

	if currentPath == "":
		print(f"{getPrefix(resultObject)} Script exiting. Cleaning up announcements.")
		engine.make_announcement(dstNode, [])
		writeFinalPathList(pathsFileName, resultObject, pathList)
		time.sleep(propagationDelaySeconds)
		return


	splitPath = currentPath.split(' ')

	# This is a valid path, add it to the path list.
	pathList.append((splitPath[:], currentCommunities[:], currentPoisons[:]))
	print(f"{getPrefix(resultObject)} New Path Found: {json.dumps((splitPath, currentCommunities, currentPoisons))}")
	print(f"{getPrefix(resultObject)} Current Paths: {json.dumps(pathList)}")
	
	if len(splitPath) < ignoreHopCount + 2: # We need at least two working hops, we cant poinson or do any community stuff to the origin, and then there needs to be a hop after the origin (not counting the ignore hops) that we can try to change to change the route.
		print(f"{getPrefix(resultObject)} Script exiting. Cleaning up announcements.")
		engine.make_announcement(dstNode, [])
		writeFinalPathList(pathsFileName, resultObject, pathList)
		time.sleep(propagationDelaySeconds)
		return
	workingPath = splitPath[ignoreHopCount:]

	workingIndexInPath = 1
	
	while workingIndexInPath < len(workingPath):
		if masterConfig["use-as-path-poisoning"]:
			raise NotImplementedError()

		if workingPath[workingIndexInPath] in communities:
			# There is community documentation for this AS.
			asCommunities = communities[workingPath[workingIndexInPath]]
			targetAS = workingPath[workingIndexInPath - 1]
			if f"no-export-asn-{targetAS}" in asCommunities or f"no-export-asn-X" in asCommunities:
				communityToAdd = ""
				if f"no-export-asn-{targetAS}" in asCommunities:
					communityToAdd = asCommunities[f"no-export-asn-{targetAS}"]
				else:
					communityToAdd = asCommunities[f"no-export-asn-X"]
					if isinstance(communityToAdd, list):
						communityToAdd = [community.replace("X", targetAS) for community in communityToAdd]
					else:
						communityToAdd = communityToAdd.replace("X", targetAS)
				
				# Support list communities.
				if isinstance(communityToAdd, list):
					currentCommunities.extend(communityToAdd)
				else:
					currentCommunities.append(communityToAdd)
				engine.make_announcement(dstNode, [(prefix, currentCommunities, currentPoisons)])
				time.sleep(propagationDelaySeconds)
				# Get the current path from the src to the destination.
				currentPath = engine.get_path(srcNode, prefix)
				if currentPath == "":
					# The case where we reach the null route is an exit case.
					break
				# We did not get the null route and we have a stable path. Add it to the list.
				newSplitPath = currentPath.split(' ')
				if newSplitPath == splitPath:
					# This is the case where the community we added did not work. We need to advance the working index.
					# In a more complecated script implementation we could try other techniques in this situation but here we simply advance to the next index.

					# Undo the community add.
					currentCommunities = currentCommunities[:-1]
					# Advance the working index.
					workingIndexInPath += 1
					continue
				# If we know the community worked and there is a difference, update to the new split path.
				splitPath = newSplitPath
				# We know we actually found a new path.
				pathList.append((splitPath[:], currentCommunities[:], currentPoisons[:]))
				print(f"{getPrefix(resultObject)} New Path Found: {json.dumps((splitPath, currentCommunities, currentPoisons))}")
				print(f"{getPrefix(resultObject)} Current Paths: {json.dumps(pathList)}")
				
				# This is a strange case where we got too a path that is too short to work with. Potentially this should actually be an undo and continue.
				if len(splitPath) < ignoreHopCount + 2:
					print(f"{getPrefix(resultObject)} New path found but not long enough to continue working.")
					break

				# Reset the working index and update the working path.
				workingPath = splitPath[ignoreHopCount:]
				workingIndexInPath = 1
			else:
				# We did have community documentation for this AS but it did not have the command we needed to supress this route.
				workingIndexInPath += 1
				continue

		else:
			workingIndexInPath += 1
			continue




	print(f"{getPrefix(resultObject)} Script exiting. Cleaning up announcements.")
	engine.make_announcement(dstNode, [])
	#print(engine.get_path("vultrla", "2607:f8b0:4004:832::200e"))
	#engine.make_announcement("vultrwarsaw", [])
	writeFinalPathList(pathsFileName, resultObject, pathList)
	time.sleep(propagationDelaySeconds)



def main(raw_args=None):
	dirname = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(dirname)  # Add the directory containing the engines package to the Python path
	args = parse_args(raw_args)
	masterConfig = json.load(open(args.config_dir + "/master.json"))
	communities = json.load(open(args.config_dir + "/communities.json"))
	engineName = masterConfig["engine"]
	engine = importlib.import_module(f"engines.{engineName}")
	pathsFileName = args.paths_file
	availablePrefixes = masterConfig["prefixes"][:]
	nodeCombinations = []
	nodes = masterConfig["nodes"]
	if args.withdraw:
		threads = []
		for node in nodes:
			t = threading.Thread(target=lambda node, engine: engine.make_announcement(node, []), args=(node, engine))
			t.start()
			threads.append(t)
		for t in threads:
			t.join()
		return

	# Anycast from everywhere.
	if args.announce:
		threads = []
		for node in nodes:
			t = threading.Thread(target=lambda node, engine: engine.make_announcement(node, [(availablePrefixes[0], [], [])]), args=(node, engine))
			t.start()
			threads.append(t)
		for t in threads:
			t.join()
		return

	if args.single_node:
		# Single node code to launch stealthy attack at vultrnj2 with Cogent no export community.
		engine.make_announcement("vultrnj2", [(availablePrefixes[0], ["20473:6601", "64600:2914", "64600:1299", "64600:3257", "174:990", "64600:7922"], [])]) # "174:990",
		return

	if args.destinations is not None:
		
		# We are in single announcement mode.
		prefixes = args.ip_prefixes
		communities = args.communities #[c.replace(",", ":") for c in args.communities]
		announcementObject = [(prefix, communities, []) for prefix in prefixes]
		threads = []
		for node in args.destinations:
			t = threading.Thread(target=lambda node, engine, announcementObject: engine.make_announcement(node, announcementObject), args=(node, engine, announcementObject))
			t.start()
			threads.append(t)
		for t in threads:
			t.join(timeout=300)
			if t.is_alive():
				print(f"Thread {t.name} is hung. Inspecting call stack:")
				for thread_id, frame in sys._current_frames().items():
					if thread_id == t.ident:
						print(f"\nCall stack for thread {t.name} (ID: {thread_id}):")
						traceback.print_stack(frame)
				raise Exception("Thread hung")
		
		return
	if args.setup_from_announcement_statement is not None:
		bgp_utils.make_announcements_from_announcement_statement(engine, masterConfig, args.setup_from_announcement_statement)
		return

	for src in nodes:
		for dst in nodes:
			if src != dst:
				nodeCombinations.append((src, dst))
	activeThreads = [] # Contains a tuples with (thread, prefix used, src used)
	print(f"[{get_current_human_time()}] Starting script on prefixes: {availablePrefixes} and nodes: {nodes}.")
	print(f"[{get_current_human_time()}] {len(nodeCombinations)} node combinations to test using {len(availablePrefixes)} prefixes. {float(len(nodeCombinations))/len(availablePrefixes)} nodes per prefix.")
	print(f"[{get_current_human_time()}] {len(communities)} community dictionary size")
	
	while len(nodeCombinations) > 0: # While there are still node combos left.
		# Cleanup active thread list.
		breakOuter = False
		while not breakOuter:
			for i in range(len(activeThreads)):
				t, prefix, dst = activeThreads[i]
				if not t.is_alive():
					availablePrefixes.append(prefix)
					del activeThreads[i]
					break
			# Check if we actually cleared up all inactive threads.
			if all([t.is_alive() for t, _, _ in activeThreads]):
				breakOuter = True


		# Check available prefixes.
		while len(availablePrefixes) == 0:
			for i in range(len(activeThreads)):
				t, prefix, dst = activeThreads[i]
				if not t.is_alive():
					availablePrefixes.append(prefix)
					del activeThreads[i]
					break
			if len(availablePrefixes) == 0:
				time.sleep(10)
		# We found our prefix.
		prefix = availablePrefixes[0]
		availablePrefixes = availablePrefixes[1:]
		print(f"[{get_current_human_time()}] Free prefix {prefix} found. Checking for node combo with free dst.")
		


		# Check for available source.
		nodeComboIndexToUse = None
		while nodeComboIndexToUse is None:
			activeDestinations = [dst for _, _, dst in activeThreads]
			for i in range(len(nodeCombinations)):
				src, dst = nodeCombinations[i]
				if dst not in activeDestinations:
					# We found a free src and we already have a free prefix. Start a run.
					nodeComboIndexToUse = i
			if nodeComboIndexToUse is None:
				time.sleep(10) # 10 second sleep to see if a thread became inactive.
				for i in range(len(activeThreads)):
					t, prefix, dst = activeThreads[i]
					if not t.is_alive():
						availablePrefixes.append(prefix)
						del activeThreads[i]
						break
		
		# Get the src and dst
		src, dst = nodeCombinations[nodeComboIndexToUse]
		# Remove this index from the node combinations.
		del nodeCombinations[nodeComboIndexToUse]
		print(f"[{get_current_human_time()}] Starting thread for node combination: {src}, {dst} with prefix {prefix}.")
		newThread = threading.Thread(target=pathfinder, args=(src, dst, prefix, masterConfig, communities, engine, pathsFileName))
		newThread.start()
		activeThreads.append((newThread, prefix, dst))

	print(f"[{get_current_human_time()}] Final node pairs running. Waiting for them to exit.")
	for t, prefix, dst in activeThreads:
		t.join()
	print(f"[{get_current_human_time()}] Clean exit from control thread.")
	
		

	

if __name__ == '__main__':
    main()
