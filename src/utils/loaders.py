import json
import os

from pydantic import BaseModel

from .data_objects import Config

def load_config() -> Config :
  try:
    script_dir = os.path.dirname(__file__)
    with open(f'{script_dir}/../configure/config.json', 'r') as file:
        config_data = json.load(file)
    return Config.model_validate_json(config_data)
  except Exception as error:
    raise error
  

class State(BaseModel):
    mid_test: bool
    curr_node_a: str
    curr_node_b: str

def load_state() -> State:
    try:
        script_dir = os.path.dirname(__file__)
        with open(f'{script_dir}/../results/state.json', 'r') as file:
            state_data = json.load(file)
        return State.model_validate_json(state_data)
    except Exception as error:
        raise error