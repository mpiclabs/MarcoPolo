#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def pathPrioritySortingFunction(path):
	communities = path[0]
	filteredCommunities = [comm for comm in communities if "64600:" in comm]
	return (len(communities), -len(filteredCommunities))

def make_announcements_from_path_txt_file(destinations, pathstxtfile, masterConfig):
	print(f"Making announcement for destinations: {destinations} from paths file: {pathstxtfile}")
	destinationsPathMap = {}
	matchingLineCount = 0
	with open(pathstxtfile) as f:
		for line in f:
			sline = line.strip()
			if sline == "":
				continue
			jline = json.loads(sline)
			if jline["dst"] in destinations:
				destination = jline["dst"]
				matchingLineCount += 1
				if destination not in destinationsPathMap:
					destinationsPathMap[destination] = []
				destinationsPathMap[destination].extend(jline["paths"])
	print(f"Found {matchingLineCount} relevant lines in paths.txt file for destinations: {destinations}")
	prefixes = masterConfig["prefixes"]
	print(f"Found {len(prefixes)} available prefixes")
	#print(f"dst path map: {destinationsPathMap}")
	totalPathCount = 0
	for dst in destinationsPathMap:
		paths = destinationsPathMap[dst]
		simplePathsDict = {}
		for p in paths:
			pathTuple = (tuple(p[1]), tuple(p[2]))
			if pathTuple not in simplePathsDict:
				simplePathsDict[pathTuple] = 0
			simplePathsDict[pathTuple] += 1
		
		#simplePaths.add(pathTuple)
		destinationsPathMap[dst] = simplePathsDict # Convert to set to avoid duplicates.
		totalPathCount += len(simplePathsDict)
	allocatePrefixes = True
	if totalPathCount > len(prefixes):
		print(f"Not fully allocating prefixes. Found {totalPathCount} paths but only have {len(prefixes)} available.")
		allocatePrefixes = False
	announcementStatement = {}
	prefixIndex = 0
	print(f"DestinationsPathMap: {destinationsPathMap}")
	print()
	for dst in destinationsPathMap:
		announcement = []
		pathsAndCountList = sorted(list(destinationsPathMap[dst].items()), key=lambda p: -destinationsPathMap[dst][p[0]])
		print(f"Paths and counts for {dst}: {pathsAndCountList}")
		print()
		pathsList = [pac[0] for pac in pathsAndCountList]
		for path in pathsList:
			announcement.append((prefixes[prefixIndex] if prefixIndex < len(prefixes) else None,list(path[0]), list(path[1])))
			prefixIndex += 1
		# Filtering out None announcements.
		announcementStatement[dst] = [a for a in announcement if a[0] is not None]

		# With None announcements
		#announcementStatement[dst] = announcement
		#engine.make_announcement(dst, announcement) # "174:990",
	print(f"Announcement Statement: {json.dumps(announcementStatement)}")


def make_announcements_from_announcement_statement(engine, masterConfig, announcementStatementJsonString):
	announcementStatementObject = json.loads(announcementStatementJsonString)
	for node in announcementStatementObject:
		# Remove nones.
		effectiveAnnouncementStatement = [announcement for announcement in announcementStatementObject[node] if announcement[0] is not None]
		engine.make_announcement(node, effectiveAnnouncementStatement)
		
