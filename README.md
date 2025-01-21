# README

## Overview

This codebase tests the resilience of a Certificate Authority (CA) implementation using Multiple Perspective Issuance Control (MPIC). It sets up or takes an existing configuration of multiple servers and runs simulated hijacks between every pair of servers. For each hijack, it records which perspective (server) contacted which target server, providing insights into the CA’s MPIC resilience.

## For Developers
- There are three kinds of files that should not be modified by anyone other than the maintainer of this codebase:
   - Configuration/state files-- these are specific to each attack sequence (servers, CA information, last attack, etc.)
   - Sensitive files-- these are specific to a user, and contain secret information (API/SSH keys)
   - Log files-- these log the results of an attack
If you plan on modifying and pushing any code, run the following commands before doing so:
```bash
git update-index --skip-worktree terraform/variables.tf
git update-index --skip-worktree results/*.log
git update-index --skip-worktree results/*.json
```
This ensures that no sensitive or instance-specific files are pushed to the remote repository, which is visible to others.
This will ensure you will not accidentally push configuration state files, which are unique to a users configuration
## Using this package

### Configuration Setup

Ensure you have Terraform downloaded onto your computer. Before running the code, you need to provide specific configuration details. Follow these steps:

1. **Create Configuration File**:
   - From the root directory, run
     ```bash
     cp configure/config.template configure/config.json
     ```

2. **Configure (or create) servers to use as nodes**:
   - The attack sequence requires a set of geographically dispersed Vultr nodes using the same SSH key. You can either use your own existing set, or have servers be automatically provisioned. 
   - **To use existing servers**: 
      - In configure/config.json, set `nodes` to a list of server names mapped to their IP addresses. 
         - Note that the server names used are not required to match any external configuration-- they will simply be the names used to identify the servers throughout this attack. But for the sake of clarity, we recommend using their hostnames.
      - Create a directory bgp_pathfinder/keys/vultr, and in that create a file called vultr.pem. Place in it the SSH private key being used by your servers--they should all use the same one--followed by a newline. Set the permissons for that the file to 700.
   - **To automatically provisioning servers**:
      - If you want the code to create servers for you, do the following:
         - In terraform/variables.tf, insert your Vultr API key
         - In `config.json`, set 'regions' to a list of node names mapped to the Vultr regions you want them in
            - Note that the server names used are not required to match any external configuration-- they will simply be the names used to identify the servers throughout this attack. But for the sake of clarity, we recommend using their hostnames.
         - Create a directory bgp_pathfinder/keys/vultr, and in that create a file called vultr.pem. Place in it the SSH private key being used by your servers--they should all use the same one--followed by a newline. Set the permissons for that the file to 700.
         - In the root directory, run 
         ```bash 
         python provision_servers.py
         ```
         Terraform will summarize the infrastructure changes it will make as a 'plan'. If you haven't used Terraform to create any servers within this project yet, the plan should only consist of creating the servers you specified in the config file. If all looks good, type 'yes' when prompted.
         - If the servers are successfully provisioned, the config file will automatically be updated to include the server names and IP addresses (see 'To use existing servers' above). Otherwise, the error will be displayed.
      - Once the servers are created, their details will automatically be added to `config.json`.
      
3. **Configure Nodes**:
   - Once the nodes are specified, they must be configured with the tools needed to run the attack. From the root directory, run ./configure/config.sh

### Running the attack
- From the root directory, run 
   ```bash
   screen -L -Logfile screenlog.0 -S hijacks -dm bash -c 'python all_attacks.py'
   ```
   This will create a new screen session with the attack sequence running, and all console output will be written to screenlog.0. Check that file to see where the attack is up to at any given point. Once the attack is over, the screen session will terminate.
   - While the attack runs, it will log it's progress to summary.log, http.log, and errors.log
   - As the attack sequence occurs, results/state.json is updated to reference the next attack. If something goes wrong and the program crashes before completion, running all_attacks.py again will pick up where the last attack left off. To override this behavior, go to state.json and set 'mid_test' to false.
   -Note: This attack simulation can be time-consuming, depending on the number of nodes configured. The attack duration scales with the number of pairwise combinations of nodes, with each attack taking approximately 5–7 minutes.

### Deprovisioning servers
 **Deprovision Servers**
   - If you provisioned servers for this attack, it is critical that you deprovision them once they're no longer needed to avoid accumulating charges. To do so, simply run
   ```bash
   cd terraform
   terraform destroy
   ```
   and then confirm when prompted. 
   Any servers that were not provisioned in this module will need to be deprovisioned seperately.


To run this on a new server:
install snapd, install cerbot. take the server IP address and hardcode that into the test node flask app. 
need authenticator.sh, cleanup.sh, webroot, certbot_server.log
python server running as follows: 
python3 -m http.server 80 --directory ~/certbot_tools/webroot > ~/certbot_tools/certbot_server.log 2>&1 &
ufw allow 80 
include openMpic key as env var if you'll be testing that

some things that have been missing:
opemmpic key in envvar, vultr key and ssh id in variables.tf, ssh key in vultr.pem or wasn't configured to 700, 