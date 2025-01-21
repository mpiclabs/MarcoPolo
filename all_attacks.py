#!/usr/bin/env python3

from round import attack
import json
import time
import signal
import threading
import sys
import traceback
from utils.node import Node
from utils.loggers import http_logger, summary_logger, error_logger
from utils.loaders import load_config, load_state



  
def initialize_result_files(ca_list, node_names):
  """
  For each CA, creates an emoty results file, stored at results/{ca}_results.json.
  Uses CA's to name files, and node names to name dictionary keys in file.
  """
  data = {}
  for node in node_names:
    other_nodes = {other_node: [] for other_node in node_names if other_node!=node}
    data[node] = other_nodes
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

  # Load info needed for game
  config = load_config()
  state = load_state()
  ca_list = config['certificate_authorities']
  node_objects = [Node(name, ip) for name, ip in config['nodes'].items()]
  node_names = list(config['nodes'].keys())

  # if this is a new run, reinitialize result files
  initialize_result_files(ca_list, node_names)
  # starting point depends on whether we're continuing a previous run
  a_start_index = node_names.index(state['curr_node_a']) if state['mid_test'] == True else 0
  b_start_index = node_names.index(state['curr_node_b']) if state['mid_test'] == True else a_start_index+1

  for i, node_a in enumerate(node_objects[a_start_index:], start=a_start_index):
    for node_b in node_objects[b_start_index if i==a_start_index else i+1:]:
      # update state file to current attack pair
      with open('results/state.json', 'w') as file:
        state['mid_test'] = True
        state['curr_node_a'] = node_a.name
        state['curr_node_b'] = node_b.name
        json.dump(state, file)
      
      #run attack and record results
      attack_results = attack(ca_list, node_a, node_b)
      record_results(attack_results)
      for ca in ca_list:
        node_a_ips_len = len(attack_results[ca][node_a.name])
        node_b_ips_len = len(attack_results[ca][node_b.name])
        total = node_a_ips_len + node_b_ips_len
        time = attack_results[ca]['time']
        summary_logger.info(f"Pair: {node_a.name:<15}, {node_b.name:<15}:\t{node_a_ips_len:<2}, {node_b_ips_len:<2}\tTotal: {total:>2}\tTime: {time:.2f}s")


if __name__=="__main__":
  all_attacks()