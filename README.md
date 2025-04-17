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
git update-index --skip-worktree bgp_pathfinder/config/master.json
git update-index --skip-worktree bgp_pathfinder/config/cmd.json
git update-index --skip-worktree bgp_pathfinder/config/vultr/nodes.json

git update-index --skip-worktree configure/pathfinder_config/master.json
git update-index --skip-worktree configure/pathfinder_config/cmd.json
git update-index --skip-worktree configure/pathfinder_config/vultr/nodes.json
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
   - **To automatically provision servers**:
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
need authenticator.sh, cleanup.sh, webroot, webroot_server.log
python server running as follows: 
python3 -m http.server 80 --directory ~/certbot_tools/webroot > ~/certbot_tools/webroot_server.log 2>&1 &
ufw allow 80 
include openMpic key as env var if you'll be testing that

some things that have been missing:
opemmpic key in envvar, vultr key and ssh id in variables.tf, ssh key in vultr.pem or wasn't configured to 700, 

Troubleshooting:
cert req times out-- probably because the server for the domain isn't actually running, so perspectives don't get any response.
1) ensure the domain ip is responsive-- ping it.
2) ensure the domain ip block was properly announced-- check on looking glass.
3) check that bird is properly connecting to BGP session with vultr-- on the server attempting to announce the block, run 
```bash
birdc show protocols all
```
You should get 
you can verify that the server is running by going to the vultr server and checking the docker container-- which you can enter with 'docker exec -it [container name] /bin/bash'

Troubleshooting:


debug log: 
cert req times out-- the BGP announcement wasn't actually happening because BIRD wasn't connected to vultr's BGP server. Had to restart bird. Never really figured out what happened, I assume it was docker interfering with it.
LE requests weren't passing-- I forgot that the nodes were coded to forward requests to a hardcoded ip address (the central server), so they were never getting to my local machine. more generally, you need to make sure that the web root folder is being served, so that requests (which will come in the form '/.well-known/acme-challenge/{TOKEN}') actually return the token and pass the challenge. Btw, it's only called web root because it's the root document being served-- all paths are resolved relative to it. you can call it anything, as long as it has the necessary file system within it (namely .well-known/acme-challenge). 
wasn't writing to logs-- the problem was that clear logs was actually deleting the log files after they had been connected to the loggers (which happens on import)-- that was breaking the logger's link to the file, so it could no longer write to it.

How are we actually recording the communications between perspectives and our nodes, and matching them to specific attacks? Well, the key lies in the use of tokens by CA's. When you request a cert through CertBot, it will come up with a random token, and tell you to put a validation file at the path ending in that token (the validation file is a combination of the token and a unique identifier of your account). Taking advantage of this, we simply captured the token used and stored it as a marker for that attack. We could then search through the logs on each node (which were configured to store ./well-known requests) for requests that included that token in the path-- the ip addresses of these requests were the perspectives that routed to that node after BGP propogation from both victim and attacker. It was easier for our mock CAs-- or each of our networks we set it up such that upon receiving a cert req with a unique token, each perspective simply made a request to {DOMAIN}/.well-known/{ca_identifier}, and we could track those down the same way. For OpenMPIC, the terminology is slightly different-- the token refers to the challenge, and the path at which it is to be stored is explicated as a parameter. So we put the token as the path, and leave out the 'challenge.'