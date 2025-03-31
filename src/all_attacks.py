#!/usr/bin/env python3

from .round import Round
import json
import time
import signal
import threading
import sys
import traceback
from .utils.node import Node
from .utils.loggers import http_logger, summary_logger, error_logger
from .utils.loaders import load_config, load_state
from .utils.data_objects import CertAuth


  
def initialize_result_files(ca_list: list[CertAuth], nodes: list[Node]):
  """
  For each CA, creates an emoty results file, stored at results/{ca}_results.json.
  Uses CA's to name files, and node names to name dictionary keys in file.
  """
  data: dict[str, dict[str, list[str]]] = {}
  for node in nodes:
    other_nodes: dict[str, list] = {other_node.name: [] for other_node in nodes if other_node!=node}
    data[node.name] = other_nodes
  for ca in ca_list:
    with open(f'results/{ca}_results.json', 'w') as file:
      json.dump(data, file)
      
  
def record_results(attack_results):
  """
  Updates results files.
  """
  for ca in attack_results.keys(): 
    with open(f'results/{ca}_results.json', 'r') as file:
      results = json.load(file)
    
    # Update results for the node pairs
    node_a, node_b = list(attack_results[ca].keys())[:2]
    results[node_a][node_b] = attack_results[ca][node_a]
    results[node_b][node_a] = attack_results[ca][node_b]

    with open(f'results/{ca}_results.json', 'w') as file:
      json.dump(results, file, indent=4)
  


def all_attacks():

  # Load info needed for game (loaders will raise error if anything's wrong, which should cause a quit)
  config = load_config()
  state = load_state()
  ca_list = config.certificate_authorities
  nodes = config.nodes
  # if this is a new run, reinitialize result files
  if not state.mid_test: initialize_result_files(ca_list, nodes)

  # find starting indices
  def find_index_by_name(name: str) -> int:
      return next(i for i, node in enumerate(nodes) if node.name == name)

  a_start_index = find_index_by_name(state.curr_node_a) if state.mid_test else 0
  b_start_index = find_index_by_name(state.curr_node_b) if state.mid_test else a_start_index + 1

  for i, node_a in enumerate(nodes[a_start_index:], start=a_start_index):
    for node_b in nodes[b_start_index if i==a_start_index else i+1:]:
      # update state file to current attack pair
      with open('results/state.json', 'w') as file:
        state.mid_test = True
        state.curr_node_a = node_a.name
        state.curr_node_b = node_b.name
        json.dump(state, file)
      
      #run attack and record results
      round = Round(
          cas=ca_list,
          ip_address=node_a.ip,  # Assuming you want to use node_a's IP for the round
          node_a=node_a,
          node_b=node_b
      )
      attack_results = round.execute()
      record_results(attack_results)
      for ca in ca_list:
        node_a_ips_len = len(attack_results[ca][node_a.name])
        node_b_ips_len = len(attack_results[ca][node_b.name])
        total = node_a_ips_len + node_b_ips_len
        time = attack_results[ca]['time']
        summary_logger.info(f"Pair: {node_a.name:<15}, {node_b.name:<15}:\t{node_a_ips_len:<2}, {node_b_ips_len:<2}\tTotal: {total:>2}\tTime: {time:.2f}s")


if __name__=="__main__":
  all_attacks()