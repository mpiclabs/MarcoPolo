import json
import os

def load_config():
  try:
    script_dir = os.path.dirname(__file__)
    with open(f'{script_dir}/../configure/config.json', 'r') as file:
      config = json.load(file)
      return config
  except Exception as error:
    raise error
  
def load_state():
  try:
      script_dir = os.path.dirname(__file__)
      with open(f'{script_dir}/../results/state.json', 'r') as file:
          state_data = json.load(file)
      return state_data
  except Exception as error:
      raise error