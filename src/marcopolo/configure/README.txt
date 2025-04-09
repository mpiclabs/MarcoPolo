/*******************************************************/
COMPONENTS:

config-pathfinder--  the config file that the bgp-pathfinder needs to use. Normally it would be a submodule in bgp-pathfinder, but because it's so tightly coupled with the mpdv module it needed to be incorporated directly. 

update-pathfinder-config-- python script that uses nodes.json to update the config-pathfinder files

nodes.json-- used to update config pathfinder files. This should contain all information that affects the state of the network, such as ip's, names, and address blocks we can announce.

testing-tools-- contains all files and directories that need to be on a node in order to run and and record data for a single BGP attack. Should contain all changes to a given node, any file that is added or manipulated must be represented here. 

config.sh-- runs the full configuration of a node. After this is called, all attacks and measurement should be possible with simple commands. 

README.txt-- you're looking at it.
/*******************************************************/
Instructions
1) you write the nodes and corresponding ip's you want included in the nodes.json file.
2) Run config.sh

Config.sh does the following:
1) Run update-pathfinder-config, which at this point is the following:
	a) Adding nodes to dictionary in config-pathfinder/vultr/nodes.json (either adds if not present, or replaces value if key is there)
	b) Setting config-pathfinder/cmd.json "nodes" to just your nodes
	c) setting config-pathfinder/master.json "nodes" to just your nodes
	d) setting config-pathfinder/master.json "prefixes" to your prefixes (??? TODO)
	e) Test some generic thing works for all nodes, if not flags some error
	f) Runs some generic command at all nodes (probably "hostname")
	g) Run configure at all nodes
2) Copy pathfinder-config into bgp-pathfinder (where it'll actually be used)
4) Scp suit-up into all nodes
5) Run suit-up on all nodes
6) End.