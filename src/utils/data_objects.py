from typing import Final, List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, HttpUrl, IPvAnyAddress

from .node import Node


class SayMarcoData(BaseModel):
    token: Optional[str] = None
    response: Optional[str] = None
    num_tries: int
    error_message: Optional[str] = None
    failed: bool = False


class TurnData(BaseModel):
    ca_name: str
    ca_endpoint: str
    node_a: Node
    node_b: Node
    start_time: datetime
    end_time: Optional[datetime] = None
    marco_num_tries: int = 0
    marco_response: Optional[str] = None
    say_marco_succeeded: Optional[bool] = None 
    token: Optional[str] = None 
    listen_polo_succeeded: Optional[bool] = None 
    polos_num_tries: int = 0 
    polo_results_node_a: List[str] = []   # Node -> Count of polos
    polo_results_node_b: List[str] = []   # Node -> Count of polos
    error: Optional[str] = None


class RoundData(BaseModel):
    node_a_name: str 
    node_a_ip: IPvAnyAddress
    node_b_name: str  
    node_b_ip: IPvAnyAddress
    ca_names: List[str]
    ip_announced: IPvAnyAddress
    start_time: datetime
    turns: List[TurnData] = []
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    something_failed: bool = False


class Game(BaseModel):
    game_id: str
    nodes: List[str]  # All nodes participating in the game
    cas: List[str]  # Certificate authorities involved
    rounds: List[RoundData] = []
    summary: Dict[str, int] = {}

from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl, IPvAnyAddress
from typing import Literal

Region = Literal[
    "ams",
    "atl",
    "blr",
    "bom",
    "cdg",
    "del",
    "dfw",
    "ewr",
    "fra",
    "icn",
    "itm",
    "jnb",
    "lax",
    "lhr",
    "mad",
    "man",
    "mel",
    "mex",
    "mia",
    "nrt",
    "ord",
    "scl",
    "sea",
    "sgp",
    "sjc",
    "sto",
    "syd",
    "tlv",
    "waw",
    "yto",
    "sao",
    "hnl",
]

class CertAuth(BaseModel):
    name: str
    url: Optional[HttpUrl]

class Config(BaseModel):
    nodes: List[Node]
    vultr_regions: Dict[str, str]
    certificate_authorities: List[CertAuth]
