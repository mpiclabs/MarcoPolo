import os
import subprocess
from marcopolo.paths import paths

def start_webroot_server():
    command = [
        "python3", "-m", "http.server", "80",
        "--directory", paths.CERTBOT_TOOLS / "webroot"
    ]
    with open(os.path.expanduser(paths.CERTBOT_TOOLS /"webroot_server.log"), "w") as log_file:
        subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)
    

def stop_webroot_server():
    command = [
        "pkill", "-f", "python3 -m http.server"
    ]
    subprocess.run(command)
