#!/usr/bin/env python3

import json
import os

#This file take config.json in this file and copies it into the three places it's needed in the pathfinder module-- 
# vultr/config.json, cmd.json, master.json. The first  
def update_pathfinder_config():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{this_dir}/config.json", 'r') as file:
        nodes = {node['name']: node['ip'] for node in json.load(file)["nodes"]}
        print(nodes)

    # update vultr nodes
    with open(f"{this_dir}/pathfinder_config/vultr/nodes.json", 'r') as file:
        vultr_json = json.load(file)

    vultr_json.update(nodes)

    with open(f"{this_dir}/pathfinder_config/vultr/nodes.json", 'w') as file:
        json.dump(vultr_json, file, indent=2)

    # update cmd nodes
    with open(f"{this_dir}/pathfinder_config/cmd.json", 'r') as file:
        cmd_json = json.load(file)

    cmd_json["nodes"] = list(nodes.keys())

    with open(f"{this_dir}/pathfinder_config/cmd.json", 'w') as file:
        json.dump(cmd_json, file, indent=2)

    # update master nodes
    with open(f"{this_dir}/pathfinder_config/master.json", 'r') as file:
        master_json = json.load(file)

    master_json["nodes"] = list(nodes.keys())

    with open(f"{this_dir}/pathfinder_config/master.json", 'w') as file:
        json.dump(master_json, file, indent=2)

    print('Updated pathfinder_config files.')

if __name__ == "__main__":
    update_pathfinder_config()

    
