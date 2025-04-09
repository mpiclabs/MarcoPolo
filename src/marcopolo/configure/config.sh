#!/bin/bash


# directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Update the config files for pathfinder
python3 "$SCRIPT_DIR/update_pathfinder_config.py"
cp -r "$SCRIPT_DIR/pathfinder_config/"* "$SCRIPT_DIR/../bgp_pathfinder/config/"
echo "*******UPDATED PATHFINDER CONFIG FILES*******"

# Test that everything works
python3 "$SCRIPT_DIR/../bgp_pathfinder/send_cmd.py" "hostname"

# Wait for all background jobs to finish
wait