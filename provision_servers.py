import subprocess
import json
import os

from marcopolo.paths import paths
from marcopolo.utils.loaders import load_config

def run_terraform_command(command):
    """
    Run a Terraform command with the given options.

    :param command: The Terraform command to run.
    :param options: A dictionary of options to pass to the command.
    :return: The output of the command.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = [
        'terraform',
        f'-chdir={script_dir}/terraform',
        command,
        f'-var=machines_to_run={machines_to_run}',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Error running Terraform {command}: {result.stderr}")
    return result.stdout

def plan_terraform():
    return run_terraform_command('plan')

def apply_terraform(options):
    return run_terraform_command('apply')


def apply_terraform_with_variable(machines_to_run):
    """
    Apply Terraform configurations with the given machine names.

    :param machines_to_run: A list of machine names to be created.
    """
    # Convert the list to a JSON string
    machine_json = json.dumps(machines_to_run)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    #First, plan the changes and confirm user approval
    plan_cmd = [
        'terraform', f'-chdir={script_dir}/terraform', 'plan', # specifies where config file is found
        f'-var=machines_to_run={machine_json}', "-out=plan.tfplan" 
    ]
    
    print("Running Terraform plan...")
    plan_result = subprocess.run(plan_cmd, capture_output=True, text=True)
    print(plan_result.stdout)
    
    response = input("Do you want to proceed with Terraform apply? (yes/no): ")
    
    if response.lower() == "yes":
        apply_cmd = [
            'terraform', f'-chdir={script_dir}/terraform', 'apply', 'plan.tfplan', # specifies where config file is found
        ]
        print("Running Terraform apply...")
        
        # Print in real time 
        with subprocess.Popen(apply_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # Continuously read output from stdout line by line
            for line in process.stdout:
                print(line, end='')  # Print each line as it is outputted
            # Optionally, handle stderr if needed
            stderr_output = process.stderr.read()
            if stderr_output:
                print(stderr_output, end='')  # Print any error output

        # Check for errors and print the output
        if process.wait() != 0:
            print("terraform apply has failed, exiting...")
            exit()
        else:
            # Generate config.json file
            output = subprocess.check_output(["terraform", f"-chdir={script_dir}/terraform", "output", "-json"])
            output_dict = json.loads(output)
            nodes_data = output_dict["node_ips"]["value"]

            # Create a list of Node objects using the Pydantic model
            nodes = [{"name": name, "ip": ip} for name, ip in nodes_data.items()]

            with open(f"{paths.CONFIG}/config.json", "r") as file:
                config = json.load(file)
            config["nodes"] = nodes
            with open(f"{paths.CONFIG}/config.json", "w") as file:
                json.dump(config, file, indent=4)
            print("Generated config.json file")
    else:
        print("Terraform apply cancelled.")
        exit()



def provision():
    # This creates all instances except Honolulu and Sao Paolo (they don't use the same plan as the rest, must be spun up separately)
    # because they use different plans
    config = load_config()
    name_region_dict = config.vultr_regions
    apply_terraform_with_variable(name_region_dict)

def destroy():
    run_terraform_command('destroy')

if __name__ == "__main__":
    provision()