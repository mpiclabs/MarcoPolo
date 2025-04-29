#!/usr/bin/env python3
import requests
import re
import os
import sys
import time
import textwrap
import random
import datetime
import subprocess
import json

from marcopolo.bgp_pathfinder.pathfinder import main as pathfinder
from marcopolo.attacks.turn import TurnFactory
from marcopolo.attacks.node import Node, NodeRequestError, NodeResponseError
from marcopolo.utils.data_objects import RoundData, CertAuth
from marcopolo.paths import paths

dir_path = os.path.dirname(os.path.realpath(__file__)) 
from pydantic import BaseModel, IPvAnyAddress
from typing import List

class Round(BaseModel):
  """
  Can execute a round of the Marco-Polo.
  Input:
      ca_names: list of names of the certificate authorities
      ca_endpoints: list of endpoints of the certificate authorities
      node_a: Node object for the first node
      node_b: Node object for the second node
  """
  cas: list[CertAuth]
  bgp_prefix: str
  node_a: Node
  node_b: Node
  rpki: bool

  def execute(self) -> RoundData:
    """
    Executes the round of Marco-Polo for the given certificate authorities and nodes. Consists of making
    BGP announcements, executing Marco-Polo turns for each CA, and collecting the results.

    Args:
        None (arguments set in constructor)

    Returns:
        RoundData: An object containing the results of the round, including the start and end times, 
                   the results of each turn, and any errors encountered.

    Side Effects:
        - Makes BGP announcements.
        - Waits for five minutes.
        - Writes to the http.log file.
        - Prints the total time taken for the round.
    """
    round_data = RoundData(
        node_a=self.node_a,
        node_b=self.node_b,
        start_time=datetime.datetime.now(),
        cas=self.cas,
        bgp_prefix=self.bgp_prefix,
        turns=[]
    )
    args = ["-d", self.node_a.name, self.node_b.name, "-i", self.bgp_prefix]
    pathfinder(["-w"])  # make announcements
    pathfinder(args)    # make announcements

    # wait four minutes
    time.sleep(240)
    
    with open(f"{paths.LOGS}/http.log", 'a') as file:
        file.write(f"{self.node_a.name}, {self.node_b.name}:\n")
    
    for ca in self.cas:
      turn = TurnFactory.create(ca, self.node_a, self.node_b)
      turn_data = turn.execute()
      round_data.turns.append(turn_data)


    round_data.end_time = datetime.datetime.now()
    print("Total time for all attacks between this pair of nodes= ", round_data.end_time - round_data.start_time)
    
    return round_data

if __name__ == "__main__":
  script_dir = os.path.dirname(os.path.abspath(__file__))

  # check correct number of arguments
  if len(sys.argv)==1: 
    print("Please add arguments.")
    exit()
  if len(sys.argv)%2 == 0: #script call throws off by 1
    print("Number of args must be even. Number is", len(sys.argv)-1)
    exit()

    
    

# [1] currently run at main bc it's set up with everything. Once this entire module is downloaded to a server fully fitted with certbot 
# and everything, can run certbot command locally. technically each cert has different requirements for request to be run: cf uses curl,
# so it actually can be run anywhere, let's encrypt uses certbot so it needs that, google requires gcloud sign-in. 



