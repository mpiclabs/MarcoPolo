
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
from marcopolo.utils.logs_writer import http_logger, summary_logger, error_logger, general_logger
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
      general_logger.debug(f"Results file {ca.name}_results.json created")

def reset_state():
    with open(f'{paths.RESULTS}/state.json', 'w') as file:
        json.dump({"mid_test": False, "curr_node_a": "", "curr_node_b": ""}, file)
        general_logger.debug("State reset")
      
  
def record_results(round_data: RoundData):
    """
    Records the results of a round of attacks between nodes, updating the corresponding CA results files and logging the process.

    This function performs the following tasks:
    1. Logs the full round data to a log file for detailed tracking.
    2. Writes the ips collected from each node to the corresponding CA results file.
    3. Logs the summary of the attack results in the log, indicating any errors or the number of perspectives gathered.

    Parameters:
    - round_data (RoundData): The data object containing information about the round of attacks, including node perspectives and timing.

    Returns:
    None
    """
    general_logger.debug("Recording results")
    print("General Logger Handlers in results_writer:", general_logger.handlers)

    # Write full round data to log file
    with open(f'{paths.LOGS}/rounds.log', 'a') as file:
        json.dump(round_data.model_dump(mode='json'), file, indent=4)
        general_logger.debug("Round data recorded")

    # Write attack results to CA json file
    for turn_data in round_data.turns:
        ca_name = turn_data.ca.name
        ca_results_path = paths.RESULTS/f'{ca_name}_results.json'
        with open(ca_results_path, 'r') as file:
            results: CAResults = json.load(file)
            general_logger.debug(f"Results loaded for {ca_name} from {ca_results_path}")
            
        # Update results for the node pairs
        node_a_name = turn_data.node_a.name
        node_b_name = turn_data.node_b.name
        
        if turn_data.listen_polo_data:
            assert turn_data.listen_polo_data.node_a_perspectives is not None
            assert turn_data.listen_polo_data.node_b_perspectives is not None
            results[node_a_name][node_b_name] = [str(ip) for ip in turn_data.listen_polo_data.node_a_perspectives]
            results[node_b_name][node_a_name] = [str(ip) for ip in turn_data.listen_polo_data.node_b_perspectives]
            general_logger.debug("Perspectives for both nodes are not None, extracted ips to be written to results file")
        else:
            results[node_a_name][node_b_name] = []
            results[node_b_name][node_a_name] = []
            general_logger.debug("Listen_polo_data, node_a_perspectives, or node_b_perspectives is None-- empty lists to be written to results file")

        with open(ca_results_path, 'w') as file:
            json.dump(results, file, indent=4)
            general_logger.debug(f"Updated results for {ca_name} written to {ca_results_path}")

    # Write summary of attack results to log file
    total_round_duration = (round_data.end_time - round_data.start_time).total_seconds() if round_data.end_time else -1
    summary_logger.debug(f"Pair: {round_data.node_a.name:<15}, {round_data.node_b.name:<15}:\tCA: {round_data.turns[0].ca.name:<3}\tTime: {total_round_duration:.2f}s")
    for turn_data in round_data.turns:
        if not turn_data.listen_polo_data:
            summary_logger.error(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\tCA: {turn_data.ca.name:<3}\tERROR: Listen Polo never happened") 
        else:
            node_a_ips = turn_data.listen_polo_data.node_a_perspectives
            node_b_ips = turn_data.listen_polo_data.node_b_perspectives
            if node_a_ips is not None and node_b_ips is not None:
                total = len(node_a_ips) + len(node_b_ips)
                duration = (turn_data.end_time - turn_data.start_time).total_seconds() if turn_data.end_time else -1
                summary_logger.debug(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\tCA: {turn_data.ca.name:<3}\t{len(node_a_ips):<2}, {len(node_b_ips):<2}\tTotal: {total:>2}\tTime: {duration:.2f}s")
                if turn_data.ca.num_perspectives is not None and total<turn_data.ca.num_perspectives:
                    error_logger.error(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\tCA: {turn_data.ca.name:<3}\tERROR: Not enough perspectives collected ({total}/{turn_data.ca.num_perspectives})")
            else:
                summary_logger.debug(f"Pair: {turn_data.node_a.name:<15}, {turn_data.node_b.name:<15}:\tCA: {turn_data.ca.name:<3}\tERROR: Missing perspective data")

    summary_logger.debug("--------------------------------")