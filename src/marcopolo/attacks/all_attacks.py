#!/usr/bin/env python3

import os
import json
import time
import signal
import threading
import sys
import traceback
import argparse

from marcopolo.bgp_pathfinder.pathfinder import main as pathfinder
from marcopolo.paths import paths
from marcopolo.attacks.round import Round
from marcopolo.attacks.node import Node
from marcopolo.utils.logs_writer import http_logger, summary_logger, error_logger, general_logger
from marcopolo.utils.loaders import load_config, load_state
from marcopolo.utils.data_objects import CAResults, CertAuth, RoundData
from marcopolo.utils.results_writer import initialize_result_files, reset_state, record_results
from marcopolo.utils.logs_writer import clear_log_files


   
def all_attacks(force_restart: bool = False, clear_logs: bool = False):
  """
  Executes a series of attacks between pairs of nodes using different certificate authorities.

  This function orchestrates the entire attack sequence by:
  1. Loading the necessary configuration and state information.
  2. Initializing result files if this is a new run.
  3. Iterating through all pairs of nodes to execute the attack.
  4. Recording the results of each attack in the specified format.

  Parameters:
  - force_restart (bool): If True, the test will restart from the beginning, ignoring the current state.
  - clear_logs (bool): If True, all log files will be cleared before starting the attacks.

  Returns:
  None
  """
  general_logger.debug("Starting all attacks")

  if force_restart:
    reset_state()
  if clear_logs:
    clear_log_files()

  # Load info needed for game (loaders will raise error if anything's wrong, which should cause a quit)
  config = load_config()
  state = load_state()
  ca_list = config.certificate_authorities
  nodes = config.nodes
  
  # if this is a new run, reinitialize result files
  if not state.mid_test: 
     initialize_result_files(ca_list, nodes)

  # find starting indices
  def find_index_by_name(name: str) -> int:
      return next(i for i, node in enumerate(nodes) if node.name == name)
  
  a_start_index = find_index_by_name(state.curr_node_a) if state.mid_test else 0
  b_start_index = find_index_by_name(state.curr_node_b) if state.mid_test else a_start_index + 1

  if state.mid_test:
     general_logger.info(f"Mid test: starting from {state.curr_node_a} and {state.curr_node_b}")

  for i, node_a in enumerate(nodes[a_start_index:], start=a_start_index):
    for node_b in nodes[b_start_index if i==a_start_index else i+1:]:
      # update state file to current attack pair
      with open(f'{paths.RESULTS}/state.json', 'w') as file:
        state.mid_test = True
        state.curr_node_a = node_a.name
        state.curr_node_b = node_b.name
        json.dump(state.model_dump(), file)

      #run attack and record results
      round = Round(
          cas=ca_list,
          bgp_prefix="66.180.191.0/24",
          bgp_propagation_delay=config.bgp_propagation_delay,
          node_a=node_a,
          node_b=node_b
      )
      round_data = round.execute()
      record_results(round_data)

  reset_state()
      
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the Marco-Polo attacks."""
    parser = argparse.ArgumentParser(description='Run Marco-Polo attacks')
    parser.add_argument('--force-restart', action='store_true', help='Force restart the test from the beginning')
    parser.add_argument('--clear-logs', action='store_true', help='Clear all log files before starting')
    parser.add_argument(
        '--custom-attacks-file',
        type=argparse.FileType('r'),
        help="Path to a file containing node pairs, one per line, formatted as 'nodeA,nodeB'"
    )
    return parser.parse_args()


def main() -> None:
    # Basically only exists so we can call it from command line with arguments as a package (e.g. marcopolo.attacks.all_attacks.main --force-restart --clear-logs)
    args = parse_arguments()
    if args.custom_attacks_file:
        pairs = [tuple(line.strip().split(",")) for line in args.custom_attacks_file if line.strip()]
        run_custom_attacks(pairs)
    else:
        all_attacks(force_restart=args.force_restart, clear_logs=args.clear_logs)
    pathfinder(["-w"]) # withdraw all announcements


def run_custom_attacks(pairs: list[tuple[str, str]]):
  general_logger.debug("Starting custom attacks for the following pairs:")
  for pair in pairs:
      general_logger.debug(f"  {pair[0]}, {pair[1]}")

  # Load info needed for game (loaders will raise error if anything's wrong, which should cause a quit)
  config = load_config()
  ca_list = config.certificate_authorities
  nodes = config.nodes
  
  for node_a_name, node_b_name in pairs:
      node_a = next((node for node in nodes if node.name == node_a_name), None)
      node_b = next((node for node in nodes if node.name == node_b_name), None)
      if not node_a or not node_b:
          general_logger.error(f"Could not find node objects for {node_a_name} and/or {node_b_name}")
          continue
      print(f"Running custom attack between {node_a} and {node_b}")
      #run attack and record results
      round = Round(
          cas=ca_list,
          bgp_prefix="66.180.191.0/24",
          bgp_propagation_delay=config.bgp_propagation_delay,
          node_a=node_a,
          node_b=node_b
      )
      round_data = round.execute()
      record_results(round_data)


if __name__=="__main__":
    main()