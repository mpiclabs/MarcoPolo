# This file contains functions to create files if they don't exist. It specifically deals with files that need to exist in any version of marcopolo. it does not deal with {ca}_results.json files, because those are config spefici-- those are created in attacks/all_attacks.py
import json
import os

from marcopolo.paths import paths


def create_log_files_if_not_exist():
    # Create logs directory if it doesn't exist
    if not os.path.exists(paths.LOGS):
        os.makedirs(paths.LOGS)

    log_files = ['summary.log', 'general.log', 'errors.log', 'http.log']
    for log_file in log_files:
        log_file_path = os.path.join(paths.LOGS, log_file)
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as f:
                f.write('')  # Create an empty file

def create_results_files_if_not_exist():
    # Create results directory if it doesn't exist
    if not os.path.exists(paths.RESULTS):
        os.makedirs(paths.RESULTS)

    state_file_path = os.path.join(paths.RESULTS, 'state.json')
    if not os.path.exists(state_file_path):
        with open(state_file_path, 'w') as f:
            json.dump({"mid_test": False, "curr_node_a": "", "curr_node_b": ""}, f)

# In src/marcopolo/utils/create_files.py
def init_all_files():
    create_results_files_if_not_exist()
    create_log_files_if_not_exist()