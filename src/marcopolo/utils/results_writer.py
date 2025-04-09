
import os
import json
import time
import signal
import threading
import sys
import traceback
import argparse

from marcopolo.paths import paths
from marcopolo.attacks.round import Round
from marcopolo.attacks.node import Node
from marcopolo.utils.loggers import http_logger, summary_logger, error_logger
from marcopolo.utils.loaders import load_config, load_state
from marcopolo.utils.data_objects import CAResults, CertAuth, RoundData


script_dir = os.path.dirname(__file__)
  
def initialize_result_files(ca_list: list[CertAuth], nodes: list[Node]):
  """
  For each CA, creates an empty results file, stored at results/{ca}_results.json.
  Uses CA's to name files, and node names to name dictionary keys in file.
  """
  data: CAResults = {}
  for node in nodes:
    other_nodes: dict[str, list] = {other_node.name: [] for other_node in nodes if other_node!=node}
    data[node.name] = other_nodes
  for ca in ca_list:
    with open(f'{paths.RESULTS}/{ca.name}_results.json', 'w') as file:
      json.dump(data, file)

def reset_state():
    with open(f'{paths.RESULTS}/state.json', 'w') as file:
        json.dump({"mid_test": False, "curr_node_a": "", "curr_node_b": ""}, file)
      
def clear_log_files():
    log_files = paths.LOGS.glob('*.log')
    for log_file in log_files:
        log_file.unlink()
  
def record_results(round_data: RoundData):
    """
    Updates results files with round data.
    """
    # Write full round data to log file
    with open(f'{paths.LOGS}/rounds.log', 'w') as file:
          json.dump(round_data.model_dump(mode='json'), file, indent=4)

    # Write attack results to CA json file
    for turn_data in round_data.turns:
        ca_name = turn_data.ca.name
        with open(f'{paths.RESULTS}/{ca_name}_results.json', 'r') as file:
            results: CAResults = json.load(file)
        
        # Update results for the node pairs
        node_a_name = turn_data.node_a.name
        node_b_name = turn_data.node_b.name
        
        if turn_data.listen_polo_data:
            assert turn_data.listen_polo_data.node_a_perspectives is not None
            assert turn_data.listen_polo_data.node_b_perspectives is not None
            results[node_a_name][node_b_name] = [str(ip) for ip in turn_data.listen_polo_data.node_a_perspectives]
            results[node_b_name][node_a_name] = [str(ip) for ip in turn_data.listen_polo_data.node_b_perspectives]
        else:
            results[node_a_name][node_b_name] = []
            results[node_b_name][node_a_name] = []

        with open(f'{paths.RESULTS}/{ca_name}_results.json', 'w') as file:
            json.dump(results, file, indent=4)

    # Write summary of attack results to log file
    for turn_data in round_data.turns:
        if not turn_data.listen_polo_data:
            summary_logger.info(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\tERROR: Listen Polo never happened") 
        else:
            node_a_ips = turn_data.listen_polo_data.node_a_perspectives
            node_b_ips = turn_data.listen_polo_data.node_b_perspectives
            if node_a_ips is not None and node_b_ips is not None:
                total = len(node_a_ips) + len(node_b_ips)
                duration = (turn_data.end_time - turn_data.start_time).total_seconds() if turn_data.end_time else 0
                summary_logger.info(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\t{len(node_a_ips):<2}, {len(node_b_ips):<2}\tTotal: {total:>2}\tTime: {duration:.2f}s")
            else:
                summary_logger.info(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\tERROR: Missing perspective data")

    