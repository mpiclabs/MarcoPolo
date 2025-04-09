import os
import subprocess

def run_config_script():
    script_path = os.path.join(os.path.dirname(__file__), 'config.sh')
    subprocess.run(['bash', script_path], check=True)
