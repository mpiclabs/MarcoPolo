# paths.py
from pathlib import Path
import os

class ProjectPaths:
    # Get the project root directory (where pyproject.toml lives)
    ROOT = Path(__file__).parent

    # Define all major directories
    ATTACKS = ROOT / "attacks"
    UTILS = ROOT / "utils"
    RESULTS = ROOT / "results"
    DB = ROOT / "db"
    LOGS = ROOT / "logs"
    CONFIG = ROOT / "configure"
    CERTBOT_TOOLS = ROOT / "certbot_tools"
    # Define specific files/subdirectories


paths = ProjectPaths()