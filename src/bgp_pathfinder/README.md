# bgp-pathfinder
A tool to stratigically enumerate BGP paths between two points.



## Create infrastrucutre
```
cd terraform
terraform init
terraform apply
cd ..
```

## Update nodes.json
```
cd scripts
./tfstate_to_nodes_json.py
cd ..
```

## Check config/vultr/master.json and onfig/vultr/cmd.json to use the correct nodes list


## Configure nodes
```
cd scripts
./configure_nodes.sh
cd ..
```

## Install clean bird configs by running withdrawl.
```
./announce -w
```