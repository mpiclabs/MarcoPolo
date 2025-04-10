# paths.py
from pathlib import Path
import os

class ProjectPaths:
    # Get the project root directory (where pyproject.toml lives)
    ROOT = Path(__file__).parent

    # Define all major directories
    # These CANNOT be created by the program, they need to exist with predefined contents
    ATTACKS = ROOT / "attacks"
    UTILS = ROOT / "utils"
    RESULTS = ROOT / "results"
    DB = ROOT / "db"
    LOGS = ROOT / "logs"
    CONFIG = ROOT / "configure"
    CERTBOT_TOOLS = ROOT / "certbot_tools"
    TERRAFORM = ROOT / "terraform"
    
    # These need to exist for the program to run, because certbot will store tokens here
    WEBROOT = CERTBOT_TOOLS / "webroot"
    ACME_CHALLENGE = WEBROOT / ".well-known" / "acme-challenge" # This needs to exist for certbot to place tokens into

    # These must exist prior to program start, because loggers attach to them
    GENERAL_LOG = LOGS / "general.log"
    ERROR_LOG = LOGS / "errors.log"
    HTTP_LOG = LOGS / "http.log"
    ROUNDS_LOG = LOGS / "rounds.log"
    SUMMARY_LOG = LOGS / "summary.log"

    # This needs to exist with a default value, because it's read from when the attack starts
    STATE_FILE = RESULTS / "state.json" 

    # These all need to exist
    REQUIRED_PATHS = [
        # Logs
        LOGS,
        GENERAL_LOG,
        ERROR_LOG,
        HTTP_LOG,
        ROUNDS_LOG,
        SUMMARY_LOG,
        # Results
        RESULTS,
        STATE_FILE,
        # Certbot tools
        WEBROOT,
        ACME_CHALLENGE,
    ]

    def ensure_paths_exist(self):
        for path in self.REQUIRED_PATHS:
            if path.is_file():
                path.touch(exist_ok=True)
                print(f"Created new file at {path}")
            else:
                path.mkdir(parents=True, exist_ok=True)
                print(f"Created new directory at {path}")


paths = ProjectPaths()