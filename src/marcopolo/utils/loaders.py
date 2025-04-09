import json
import os

from pydantic import BaseModel

from .data_objects import Config
from marcopolo.paths import paths

def load_config() -> Config :
  try:
    script_dir = os.path.dirname(__file__)
    with open(f'{paths.CONFIG}/config.json', 'r') as file:
        config_data = json.load(file)
    return Config.model_validate(config_data)
  except Exception as error:
    raise error
  

class State(BaseModel):
    mid_test: bool
    curr_node_a: str
    curr_node_b: str

def load_state() -> State:
    try:
        with open(f'{paths.RESULTS}/state.json', 'r') as file:
            state_data = json.load(file)
        return State.model_validate(state_data)
    except Exception as error:
        raise error